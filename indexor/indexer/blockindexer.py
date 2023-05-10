import binascii
import logging
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

from psycopg2.errors import UniqueViolation
from psycopg2.extensions import cursor

from indexor.bitcoin.blockfetcher import BlockFetcher
from indexor.bitcoin.rpc import Rpc
from indexor.db.db import Db
from indexor.indexer.txindexer import TxIndexer

relevant_tables = ["transactions", "inputs", "outputs"]

insert_block = """
INSERT INTO blocks (hash, height, time, size, weight)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
"""


class BlockIndexer:
    db: Db
    rpc: Rpc
    tx_idx: TxIndexer

    def __init__(self, db: Db, rpc: Rpc) -> None:
        self.db = db
        self.rpc = rpc
        self.tx_idx = TxIndexer()

    async def index(self, start: int, end: int) -> None:
        logging.info("Indexing blocks %d to %d", start, end)

        with self.db.conn.cursor() as cur, ThreadPoolExecutor() as executor:
            BlockIndexer._disable_triggers(cur)

            rpc_threads = max(multiprocessing.cpu_count() - 1, 1)
            logging.debug("Using %d RPC threads", rpc_threads)
            block_fetcher = BlockFetcher(
                self.rpc,
                executor,
                rpc_threads,
            )
            block_fetcher.start(start, end)

            for _ in range(start, end + 1):
                block = await block_fetcher.get()

                logging.info(
                    "Got block %d (%s) with %d transactions",
                    block["height"],
                    block["hash"],
                    len(block["tx"]),
                )

                block_fetcher.add()

                try:
                    cur.execute(
                        insert_block,
                        (
                            binascii.unhexlify(block["hash"]),
                            block["height"],
                            block["time"],
                            block["size"],
                            block["weight"],
                        ),
                    )
                except UniqueViolation:
                    logging.debug(
                        "Already got block %d (%s) in database",
                        block["height"],
                        block["hash"],
                    )
                    self.db.conn.rollback()
                    continue

                block_id = cur.fetchone()[0]
                self.tx_idx.index_txs(cur, block_id, block["tx"])
                self.db.conn.commit()

            BlockIndexer._enable_triggers(cur)

    @staticmethod
    def _disable_triggers(cur: cursor) -> None:
        for table in relevant_tables:
            cur.execute(f"ALTER TABLE public.{table} DISABLE TRIGGER ALL;")

    @staticmethod
    def _enable_triggers(cur: cursor) -> None:
        for table in relevant_tables:
            cur.execute(f"ALTER TABLE public.{table} ENABLE TRIGGER ALL;")

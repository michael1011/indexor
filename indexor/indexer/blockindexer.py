import binascii
import logging

from indexor.bitcoin.rpc import Rpc
from indexor.db.db import Db
from indexor.indexer.txindexer import TxIndexer

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

    def index(self, start: int, end: int) -> None:
        logging.info("Indexing block %d to %d", start, end)

        cur = self.db.conn.cursor()

        for height in range(start, end + 1):
            block = self.rpc.get_block_by_number(height)
            logging.debug(
                "Got block %d (%s) with %d transactions",
                block["height"],
                block["hash"],
                len(block["tx"]),
            )

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

            block_id = cur.fetchone()
            if block_id is None:
                continue

            block_id = block_id[0]

            for tx in block["tx"]:
                self.tx_idx.index_tx(cur, block_id, tx)

            self.db.conn.commit()

        cur.close()

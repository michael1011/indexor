import logging

from indexor.bitcoin.rpc import Rpc
from indexor.db.db import Db
from indexor.indexer.blockindexer import BlockIndexer

select_highest_block = """
SELECT MAX(height) FROM blocks;
"""


class Indexer:
    db: Db
    rpc: Rpc
    block_idx: BlockIndexer

    def __init__(self, db: Db, rpc: Rpc) -> None:
        self.db = db
        self.rpc = rpc
        self.block_idx = BlockIndexer(db, rpc)

    def index_blocks(self, start: int, end: int) -> None:
        if end == -1:
            end = self._get_latest_block()

        self.block_idx.index(start, end)

    def update(self) -> None:
        con = self.db.conn.cursor()
        con.execute(select_highest_block)
        highest_known = con.fetchone()[0] + 1
        con.close()

        highest_block = self._get_latest_block()
        delta = highest_block - highest_known
        if delta < 1:
            logging.info("No new blocks to index")
            return

        logging.info("Found %d new blocks", highest_block - highest_known)
        self.index_blocks(highest_known, highest_block)

    def _get_latest_block(self) -> int:
        return self.rpc.rpc.getblockchaininfo()["blocks"]

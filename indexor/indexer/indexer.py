from indexor.bitcoin.rpc import Rpc
from indexor.db.db import Db
from indexor.indexer.blockindexer import BlockIndexer


class Indexer:
    block_idx: BlockIndexer

    def __init__(self, db: Db, rpc: Rpc) -> None:
        self.block_idx = BlockIndexer(db, rpc)

    def index_blocks(self, start: int, end: int) -> None:
        self.block_idx.index(start, end)

import logging
from argparse import ArgumentParser

from .bitcoin.rpc import Rpc
from .config.config import parse_config
from .db.db import Db
from .indexer.indexer import Indexer


def cli() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.DEBUG,
    )
    logging.getLogger("BitcoinRPC").setLevel(logging.WARNING)

    parser = ArgumentParser(description="Index the Bitcoin chain")

    parser.add_argument(
        "config",
        help="Path to config file",
        nargs="?",
        type=str,
        default="indexor.toml",
    )

    args = parser.parse_args()
    logging.debug("Reading config file: %s", args.config)

    cfg = parse_config(args.config)

    db = Db(cfg.db)
    rpc = Rpc(cfg.bitcoin)

    idx = Indexer(db, rpc)

    highest = 788410
    lowest = highest - 100

    idx.index_blocks(lowest, highest)

    db.close()

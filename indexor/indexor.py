import asyncio
import logging
import sys
from argparse import ArgumentParser, Namespace

from .bitcoin.rpc import with_cookie
from .config.config import parse_config
from .db.db import Db
from .indexer.indexer import Indexer


def setup(args: Namespace) -> tuple[Indexer, Db]:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.DEBUG,
    )
    logging.getLogger("BitcoinRPC").setLevel(logging.WARNING)

    logging.debug("Reading config file: %s", args.config)

    cfg = parse_config(args.config)

    db = Db(cfg.db)
    rpc = with_cookie(cfg.bitcoin)

    logging.debug(
        "Connected to Bitcoin: %s",
        rpc.rpc.getnetworkinfo()["subversion"],
    )

    return Indexer(db, rpc), db


async def update(args: Namespace) -> None:
    idx, db = setup(args)
    await idx.update()
    db.close()


async def range_index(args: Namespace) -> None:
    idx, db = setup(args)
    await idx.index_blocks(args.start, args.end)
    db.close()


async def add_indexes(args: Namespace) -> None:
    _, db = setup(args)
    db.create_indexes()
    db.close()


def cli() -> None:
    parser = ArgumentParser(description="Index the Bitcoin chain")

    parser.add_argument(
        "-c",
        "--config",
        help="Path to config file",
        default="indexor.toml",
        type=str,
    )

    subparsers = parser.add_subparsers(title="Commands")

    update_parser = subparsers.add_parser("update")
    update_parser.set_defaults(func=update)

    range_parser = subparsers.add_parser("range")
    range_parser.set_defaults(func=range_index)

    range_parser.add_argument(
        "start",
        help="Block height to start indexing",
        type=int,
    )
    range_parser.add_argument(
        "end",
        help="Block height to stop indexing (-1 for latest block)",
        type=int,
    )

    add_indexes_parser = subparsers.add_parser("add-indexes")
    add_indexes_parser.set_defaults(func=add_indexes)

    args = parser.parse_args()

    if "func" not in args:
        print("No command specified")
        print()
        parser.print_help()
        sys.exit(1)

    asyncio.run(args.func(args))

#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser, Namespace

from .bitcoin.rpc import Rpc
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
    rpc = Rpc(cfg.bitcoin)

    return Indexer(db, rpc), db


def update(args: Namespace) -> None:
    idx, db = setup(args)
    idx.update()
    db.close()


def range_index(args: Namespace) -> None:
    idx, db = setup(args)
    idx.index_blocks(args.start, args.end)
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

    args = parser.parse_args()

    if "func" not in args:
        print("No command specified")
        print()
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    cli()

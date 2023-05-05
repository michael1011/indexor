import logging
from pathlib import Path

from bitcoinrpc.authproxy import AuthServiceProxy

from indexor.config.config import BitcoinConfig


class Rpc:
    rpc: AuthServiceProxy

    def __init__(self, config: BitcoinConfig) -> None:
        with Path(config.cookie).open() as cookie:
            cookie_parts = cookie.read().split(":")
            self.rpc = AuthServiceProxy("http://{}:{}@{}:{}".format(
                cookie_parts[0],
                cookie_parts[1],
                config.host,
                config.port,
            ))

            logging.debug(
                "Connected to Bitcoin: %s",
                self.rpc.getnetworkinfo()["subversion"],
            )

    def get_block_by_number(self, height: int) -> dict:
        block_hash = self.rpc.getblockhash(height)
        return self.rpc.getblock(block_hash, 2)

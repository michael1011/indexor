from pathlib import Path

from bitcoinrpc.authproxy import AuthServiceProxy

from indexor.config.config import BitcoinConfig


class Rpc:
    rpc: AuthServiceProxy
    auth_str: str

    def __init__(self, auth_str: str) -> None:
        self.auth_str = auth_str
        self.rpc = AuthServiceProxy(self.auth_str)

    def get_block_by_number(self, height: int) -> dict:
        block_hash = self.rpc.getblockhash(height)
        return self.rpc.getblock(block_hash, 2)


def with_cookie(config: BitcoinConfig) -> Rpc:
    with Path(config.cookie).open() as cookie:
        cookie_parts = cookie.read().split(":")
        return Rpc("http://{}:{}@{}:{}".format(
            cookie_parts[0],
            cookie_parts[1],
            config.host,
            config.port,
        ))

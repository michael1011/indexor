from dataclasses import dataclass
from pathlib import Path

import tomli


@dataclass
class BitcoinConfig:
    host: str
    port: int
    cookie: str

    @classmethod
    def from_dict(cls: type["BitcoinConfig"], obj: dict):
        return cls(
            host=obj["host"],
            port=obj["port"],
            cookie=obj["cookie"],
        )


@dataclass
class DbConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_dict(cls: type["DbConfig"], obj: dict):
        return cls(
            host=obj["host"],
            port=obj["port"],
            user=obj["user"],
            password=obj["password"],
            database=obj["database"],
        )


@dataclass
class Config:
    db: DbConfig
    bitcoin: BitcoinConfig

    @classmethod
    def from_dict(cls: type["Config"], obj: dict):
        return cls(
            db=DbConfig.from_dict(obj["db"]),
            bitcoin=BitcoinConfig.from_dict(obj["bitcoin"]),
        )


def parse_config(file: str) -> Config:
    with Path(file).open(mode="r+b") as f:
        data = tomli.load(f)
        return Config.from_dict(data)

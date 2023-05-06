import logging

import psycopg2
import psycopg2.extensions

from indexor.config.config import DbConfig

creates = [
    """
    CREATE TABLE IF NOT EXISTS blocks (
        id SERIAL PRIMARY KEY,
        hash BYTEA NOT NULL UNIQUE,
        height INTEGER NOT NULL,
        time INTEGER NOT NULL,
        size INTEGER NOT NULL,
        weight INTEGER NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id BIGSERIAL PRIMARY KEY,
        txid BYTEA NOT NULL UNIQUE DEFERRABLE INITIALLY DEFERRED,
        block SERIAL REFERENCES blocks (id),
        size INTEGER NOT NULL,
        weight INTEGER NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS inputs (
        tx BIGSERIAL REFERENCES transactions (id),
        vin SMALLINT,
        PRIMARY KEY (tx, vin),
        -- No reference because we might not have that tx in the db
        -- Allow NULL for coinbase transactions
        tx_in BYTEA,
        vout SMALLINT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS output_types (
        id SMALLSERIAL PRIMARY KEY,
        name VARCHAR(24) NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS outputs (
        tx BIGSERIAL REFERENCES transactions (id),
        vout SMALLINT,
        PRIMARY KEY (tx, vout),
        type SMALLSERIAL REFERENCES output_types (id),
        value BIGINT NOT NULL
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS blocks_height_idx ON blocks (height);
    CREATE INDEX IF NOT EXISTS transactions_block_id ON transactions (block);
    CREATE INDEX IF NOT EXISTS inputs_tx_in ON inputs USING HASH (tx_in);
    """,
]


class Db:
    conn: psycopg2.extensions.connection

    def __init__(self, config: DbConfig) -> None:
        self.conn = psycopg2.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )

        with self.conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            version = cur.fetchone()
            logging.debug("Connected to PostgreSQL: %s", version)
            cur.close()

        self._create_tables()

    def close(self) -> None:
        self.conn.close()

    def _create_tables(self) -> None:
        with self.conn.cursor() as cur:
            for stat in creates:
                cur.execute(stat)

            self.conn.commit()
            cur.close()

import binascii

from psycopg2.extensions import cursor

from indexor.indexer.outputtypes import OutputTypes

insert_tx = """
INSERT INTO transactions (txid, block, size, weight)
    VALUES (%s, %s, %s, %s)
    RETURNING id;
"""

insert_input = """
INSERT INTO inputs (tx, vin, tx_in, vout) VALUES (%s, %s, %s, %s);
"""

insert_output = """
INSERT INTO outputs (tx, vout, type, value) VALUES (
    %s,
    %s,
    %s,
    %s
);
"""

sat_factor = 10 ** 8


class TxIndexer:
    outt: OutputTypes

    def __init__(self) -> None:
        self.outt = OutputTypes()

    def index_tx(self, cur: cursor, block_id: int, tx: dict) -> None:
        cur.execute(
            insert_tx,
            (
                binascii.unhexlify(tx["txid"]),
                block_id,
                tx["size"],
                tx["weight"],
            ),
        )

        tx_id = cur.fetchone()
        if tx_id is None:
            return

        tx_id = tx_id[0]

        TxIndexer.index_inputs(cur, tx_id, tx["vin"])
        self.index_outputs(cur, tx_id, tx["vout"])

    @staticmethod
    def index_inputs(cur: cursor, tx_id: int, vins: dict) -> None:
        for i, vin in enumerate(vins):
            is_coinbase = "coinbase" in vin
            cur.execute(
                insert_input,
                (
                    tx_id,
                    i,
                    None if is_coinbase else binascii.unhexlify(vin["txid"]),
                    None if is_coinbase else vin["vout"],
                ),
            )

    def index_outputs(self, cur: cursor, tx_id: int, vouts: dict) -> None:
        for i, vout in enumerate(vouts):
            cur.execute(
                insert_output,
                (
                    tx_id,
                    i,
                    self.outt.get_output_id(cur, vout["scriptPubKey"]["type"]),
                    vout["value"] * sat_factor,
                ),
            )

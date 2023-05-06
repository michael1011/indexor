import binascii

from psycopg2.extensions import cursor
from psycopg2.extras import execute_batch, execute_values

from indexor.indexer.outputtypes import OutputTypes

insert_tx = """
INSERT INTO transactions (txid, block, size, weight) VALUES %s RETURNING id;
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


page_size = 10_000
sat_factor = 10 ** 8


class TxIndexer:
    outt: OutputTypes

    def __init__(self) -> None:
        self.outt = OutputTypes()

    def index_txs(self, cur: cursor, block_id: int, txs: list[dict]) -> None:
        tx_data = []

        for tx in txs:
            tx_data.append(
                (
                    binascii.unhexlify(tx["txid"]),
                    block_id,
                    tx["size"],
                    tx["weight"],
                ),
            )

        input_data = []
        output_data = []

        for tx, tx_id in zip(
                txs,
                execute_values(cur, insert_tx, tx_data, fetch=True),
                strict=True,
        ):
            input_data += TxIndexer._index_inputs(tx_id, tx["vin"])
            output_data += self._index_outputs(cur, tx_id, tx["vout"])

        execute_batch(cur, insert_input, input_data, page_size=page_size)
        execute_batch(cur, insert_output, output_data, page_size=page_size)

    @staticmethod
    def _index_inputs(tx_id: bytes, vins: dict) -> list[tuple]:
        inputs = []
        for i, vin in enumerate(vins):
            is_coinbase = "coinbase" in vin
            inputs.append((
                tx_id,
                i,
                None if is_coinbase else binascii.unhexlify(vin["txid"]),
                None if is_coinbase else vin["vout"],
            ))

        return inputs

    def _index_outputs(self, cur: cursor, tx_id: bytes, vouts: dict) -> list[tuple]:
        outputs = []
        for i, vout in enumerate(vouts):
            outputs.append((
                tx_id,
                i,
                self.outt.get_output_id(cur, vout["scriptPubKey"]["type"]),
                vout["value"] * sat_factor,
            ))

        return outputs


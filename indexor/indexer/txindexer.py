import binascii

from indexor.indexer.outputtypes import OutputTypes

insert_tx = """
INSERT INTO transactions (txid, block, size, weight)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT DO NOTHING
    RETURNING id;
"""

insert_input = """
INSERT INTO inputs (tx, vin, tx_in, vout) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;
"""

insert_output = """
INSERT INTO outputs (tx, vout, type, value) VALUES (
    %s,
    %s,
    %s,
    %s
) ON CONFLICT DO NOTHING;
"""

sat_factor = 10 ** 8


class TxIndexer:
    outt: OutputTypes

    def __init__(self):
        self.outt = OutputTypes()

    def index_tx(self, cur, block_id, tx):
        cur.execute(
            insert_tx,
            (
                binascii.unhexlify(tx["txid"]),
                block_id,
                tx["size"],
                tx["weight"],
            )
        )

        tx_id = cur.fetchone()
        if tx_id is None:
            return

        tx_id = tx_id[0]

        TxIndexer.index_inputs(cur, tx_id, tx["vin"])
        self.index_outputs(cur, tx_id, tx["vout"])

    @staticmethod
    def index_inputs(cur, tx_id, vins):
        for i, vin in enumerate(vins):
            is_coinbase = "coinbase" in vin
            cur.execute(
                insert_input,
                (
                    tx_id,
                    i,
                    None if is_coinbase else binascii.unhexlify(vin["txid"]),
                    None if is_coinbase else vin["vout"],
                )
            )

    def index_outputs(self, cur, tx_id, vouts):
        for i, vout in enumerate(vouts):
            cur.execute(
                insert_output,
                (
                    tx_id,
                    i,
                    self.outt.get_output_id(cur, vout["scriptPubKey"]["type"]),
                    vout["value"] * sat_factor,
                )
            )
select_output_types = """
SELECT id, name FROM output_types;
"""

insert_output_types = """
INSERT INTO output_types (name) VALUES (%s) RETURNING id;
"""


class OutputTypes:
    types = {}

    def get_output_id(self, cur, output_type: str) -> int:
        if len(self.types) == 0:
            self._fetch_outputs(cur)

        if output_type in self.types:
            return self.types[output_type]

        cur.execute(insert_output_types, (output_type,))
        output_id = cur.fetchone()[0]
        self.types[output_type] = output_id

        return output_id

    def _fetch_outputs(self, cur) -> None:
        cur.execute(select_output_types)

        for row in cur.fetchall():
            self.types[row[1]] = row[0]

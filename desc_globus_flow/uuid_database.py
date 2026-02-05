import os
import sqlite3
import pandas as pd

__all__ = ["UuidDatabase"]


TABLE_COLUMNS = {
    "flows": ["flow", "uuid"],
    "functions": ["flow", "function", "uuid"],
    "collections": ["site", "collection", "uuid"],
    "endpoints": ["site", "endpoint", "uuid"],
}


class UuidDatabase:
    def __init__(self, db_file):
        self.db_file = db_file
        if not os.path.isfile(db_file):
            self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_file) as con:
            for table, columns in TABLE_COLUMNS.items():
                df = pd.DataFrame(columns=columns, dtype=str)
                df.to_sql(table, con)

    def _condition(self, table, row):
        if not set(TABLE_COLUMNS[table][:-1]) == set(row.keys()):
            raise RuntimeError(f"{row} does not match {table} schema.")
        conditions = [f"{k}='{v}'" for k, v in row.items()]
        return " and ".join(conditions)

    def get(self, table, row):
        condition = self._condition(table, row)
        query = f"select uuid from {table} where {condition}"
        with sqlite3.connect(self.db_file) as con:
            results = [_ for _ in con.execute(query)][0]
            if len(results) != 1:
                raise RuntimeError(f"Error for query {query}:\n"
                                   f"results: {results}")
            return results[0]

    def set(self, uuid, table, row):
        condition = self._condition(table, row)
        query = f"select uuid from {table} where {condition}"
        with sqlite3.connect(self.db_file) as con:
            results = [_ for _ in con.execute(query)]
        if results:
            self._update(uuid, table, condition)
        else:
            self._insert(uuid, table, row)

    def _execute_and_commit(self, query):
        with sqlite3.connect(self.db_file) as con:
            con.execute(query)
            con.commit()

    def _update(self, uuid, table, condition):
        query = f"update {table} set uuid='{uuid}' where {condition}"
        self._execute_and_commit(query)

    def _insert(self, uuid, table, row):
        columns = [f"{_}" for _ in row.keys()] + ["uuid"]
        values = [f"'{_}'" for _ in row.values()] + [f"'{uuid}'"]
        query = (
            f"insert into {table} ({', '.join(columns)}) "
            f"values ({', '.join(values)})"
        )
        self._execute_and_commit(query)

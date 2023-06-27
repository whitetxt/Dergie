import sqlite3
from typing import Any, List


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DictDB(sqlite3.Connection):
    path: str

    def __init__(self, path):
        self.path = path
        super().__init__(self.path)
        self.row_factory = dict_factory

    def insert(self, query: str, params: List[Any] = []):
        self.cur = self.cursor()
        self.cur.execute(query, params)
        self.commit()

    def fetchall(self, query: str, params: List[Any] = []):
        self.cur = self.cursor()
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def delete(self, query: str, params: List[Any] = []):
        self.cur = self.cursor()
        self.cur.execute(query, params)
        self.commit()

    def exists(self, table: str, column: str, param: Any):
        self.cur = self.cursor()
        self.cur.execute(f"SELECT {column} FROM {table} WHERE {column} = ?", (param,))
        res = self.cur.fetchall()
        return len(res) != 0

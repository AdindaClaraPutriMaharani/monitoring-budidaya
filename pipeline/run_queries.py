import re
import sqlite3
import sys
from pathlib import Path
 
import pandas as pd
 
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "monitoring.db"
SQL_FILE = ROOT / "sql" / "queries.sql"
 
 
def baca_query(path=SQL_FILE):
    """Mengembalikan dict {nama: sql} dari file dengan penanda '-- name: ...'."""
    teks = path.read_text(encoding="utf-8")
    bagian = re.split(r"^-- name:\s*(\w+)\s*$", teks, flags=re.M)
    return {bagian[i]: bagian[i + 1].strip() for i in range(1, len(bagian), 2)}
 
 
def jalankan(nama, con):
    return pd.read_sql_query(baca_query()[nama], con)
 
 
def main():
    queries = baca_query()
    pilih = sys.argv[1:] or list(queries)
    with sqlite3.connect(DB) as con:
        for nama in pilih:
            print(f"\n=== {nama} ===")
            print(pd.read_sql_query(queries[nama], con).to_string(index=False))
 
 
if __name__ == "__main__":
    main()

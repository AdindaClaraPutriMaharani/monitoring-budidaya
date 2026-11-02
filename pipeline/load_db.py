import sqlite3
from pathlib import Path
 
import pandas as pd
 
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "monitoring.db"
 
SKEMA = """
DROP VIEW  IF EXISTS v_laporan;
DROP TABLE IF EXISTS masalah_data;
DROP TABLE IF EXISTS laporan;
DROP TABLE IF EXISTS lokasi;
 
CREATE TABLE lokasi (
    unit_id    TEXT PRIMARY KEY,
    provinsi   TEXT NOT NULL,
    kabupaten  TEXT NOT NULL,
    komoditas  TEXT NOT NULL CHECK (komoditas IN ('Nila', 'Lele'))
);
 
CREATE TABLE laporan (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id      TEXT NOT NULL REFERENCES lokasi(unit_id),
    tanggal      TEXT NOT NULL,  -- format ISO: YYYY-MM-DD
    produksi_kg  REAL NOT NULL CHECK (produksi_kg >= 0),
    status       TEXT NOT NULL CHECK (status IN ('aktif', 'perawatan', 'tidak_aktif')),
    sumber_file  TEXT NOT NULL,
    UNIQUE (unit_id, tanggal)
);
CREATE INDEX idx_laporan_tanggal ON laporan(tanggal);
 
CREATE TABLE masalah_data (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    sumber_file  TEXT,
    baris_asal   INTEGER,
    unit_id      TEXT,
    tanggal      TEXT,
    komoditas    TEXT,
    produksi_kg  REAL,
    status       TEXT,
    alasan       TEXT NOT NULL
);
 
-- minggu = hari Senin pada pekan laporan, supaya laporan bisa dikelompokkan per minggu
CREATE VIEW v_laporan AS
SELECT l.id, l.unit_id, lk.provinsi, lk.kabupaten, lk.komoditas,
       l.tanggal, date(l.tanggal, 'weekday 0', '-6 days') AS minggu,
       l.produksi_kg, l.status
FROM laporan l
JOIN lokasi lk USING (unit_id);
"""
 
 
def main():
    master = pd.read_csv(ROOT / "data" / "reference" / "lokasi_master.csv")
    bersih = pd.read_csv(ROOT / "data" / "processed" / "laporan_bersih.csv")
    masalah = pd.read_csv(ROOT / "data" / "processed" / "data_bermasalah.csv")
 
    with sqlite3.connect(DB) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(SKEMA)
        master.to_sql("lokasi", con, if_exists="append", index=False)
        bersih[["unit_id", "tanggal", "produksi_kg", "status", "sumber_file"]].to_sql(
            "laporan", con, if_exists="append", index=False)
        masalah.to_sql("masalah_data", con, if_exists="append", index=False)
 
        for tabel in ["lokasi", "laporan", "masalah_data"]:
            n = con.execute(f"SELECT COUNT(*) FROM {tabel}").fetchone()[0]
            print(f"{tabel:<14}: {n} baris")
    print(f"\nSelesai. Database: {DB}")
 
 
if __name__ == "__main__":
    main()
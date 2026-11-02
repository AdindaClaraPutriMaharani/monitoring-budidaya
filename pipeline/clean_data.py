from pathlib import Path
 
import pandas as pd
 
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REF = ROOT / "data" / "reference"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
 
# Batas wajar produksi per laporan mingguan (kg). Ini ASUMSI untuk simulasi,
# bukan standar resmi. Ubah sesuai logika yang bisa kamu jelaskan.
MAKS_PRODUKSI_KG = 500
 
BULAN_ID = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6,
            "Jul": 7, "Agu": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12}
 
STATUS_BAKU = {
    "aktif": "aktif", "beroperasi": "aktif",
    "perawatan": "perawatan",
    "tidak aktif": "tidak_aktif", "nonaktif": "tidak_aktif", "tidak beroperasi": "tidak_aktif",
}
 
 
def parse_tanggal_indonesia(nilai):
    """'12 Okt 2026' -> Timestamp. Gagal -> NaT."""
    try:
        hari, bulan, tahun = str(nilai).strip().split()
        return pd.Timestamp(year=int(tahun), month=BULAN_ID[bulan.title()], day=int(hari))
    except (ValueError, KeyError, AttributeError):
        return pd.NaT
 
 
# Satu entri per sumber: cara membaca, pemetaan kolom, format tanggal, faktor satuan.
SUMBER = [
    {
        "file": "laporan_jabar.xlsx", "provinsi": "Jawa Barat",
        "baca": lambda p: pd.read_excel(p),
        "kolom": {"Kode Unit": "unit_id", "Kabupaten": "kabupaten", "Tanggal Lapor": "tanggal",
                  "Komoditas": "komoditas", "Produksi (kg)": "produksi_kg", "Status": "status"},
        "tanggal": lambda s: pd.to_datetime(s, format="%d/%m/%Y", errors="coerce"),
        "faktor_kg": 1,
    },
    {
        "file": "data_jateng.csv", "provinsi": "Jawa Tengah",
        "baca": lambda p: pd.read_csv(p),
        "kolom": {"id_unit": "unit_id", "kab_kota": "kabupaten", "tgl": "tanggal",
                  "jenis_ikan": "komoditas", "hasil_panen_ton": "produksi_kg", "kondisi": "status"},
        "tanggal": lambda s: pd.to_datetime(s, format="%Y-%m-%d", errors="coerce"),
        "faktor_kg": 1000,  # sumber ini melapor dalam TON
    },
    {
        "file": "rekap_jatim.xlsx", "provinsi": "Jawa Timur",
        "baca": lambda p: pd.read_excel(p),
        "kolom": {"UNIT": "unit_id", "KABUPATEN": "kabupaten", "TANGGAL": "tanggal",
                  "KOMODITAS": "komoditas", "PRODUKSI_KG": "produksi_kg", "STATUS_UNIT": "status"},
        "tanggal": lambda s: s.map(parse_tanggal_indonesia),
        "faktor_kg": 1,
    },
    {
        "file": "sulsel_laporan.csv", "provinsi": "Sulawesi Selatan",
        "baca": lambda p: pd.read_csv(p, sep=";", decimal=","),
        "kolom": {"no_unit": "unit_id", "kabupaten": "kabupaten", "tanggal_laporan": "tanggal",
                  "komoditas": "komoditas", "produksi_kg": "produksi_kg", "status": "status"},
        "tanggal": lambda s: pd.to_datetime(s, format="%d-%m-%y", errors="coerce"),
        "faktor_kg": 1,
    },
]
 
 
def muat_dan_seragamkan(cfg):
    df = cfg["baca"](RAW / cfg["file"]).rename(columns=cfg["kolom"])
    df = df[list(cfg["kolom"].values())].copy()
    df["baris_asal"] = df.index + 2  # +2: baris 1 adalah header, indeks mulai dari 0
    df["sumber_file"] = cfg["file"]
    df["provinsi"] = cfg["provinsi"]
    df["tanggal"] = cfg["tanggal"](df["tanggal"])
    df["produksi_kg"] = pd.to_numeric(df["produksi_kg"], errors="coerce") * cfg["faktor_kg"]
    return df
 
 
def normalisasi_teks(df):
    df["unit_id"] = df["unit_id"].astype("string").str.strip().str.upper()
    df["kabupaten"] = df["kabupaten"].astype("string").str.strip().str.title()
    df["komoditas"] = df["komoditas"].astype("string").str.strip().str.title()
    df["status"] = df["status"].astype("string").str.strip().str.lower().map(STATUS_BAKU)
    return df
 
 
def validasi(df, master):
    df = df.merge(
        master[["unit_id", "komoditas"]].rename(columns={"komoditas": "komoditas_master"}),
        on="unit_id", how="left",
    )
    aturan = pd.DataFrame({
        "tanggal_kosong_atau_tidak_valid": df["tanggal"].isna(),
        "komoditas_kosong": df["komoditas"].isna(),
        "produksi_kosong": df["produksi_kg"].isna(),
        "produksi_di_luar_batas": df["produksi_kg"].notna()
        & ((df["produksi_kg"] < 0) | (df["produksi_kg"] > MAKS_PRODUKSI_KG)),
        "unit_tidak_dikenal": ~df["unit_id"].isin(master["unit_id"]),
        "komoditas_beda_dengan_master": df["komoditas"].notna() & df["komoditas_master"].notna()
        & (df["komoditas"] != df["komoditas_master"]),
        "status_tidak_dikenal": df["status"].isna(),
        "duplikat": df.duplicated(subset=["unit_id", "tanggal", "komoditas", "produksi_kg"], keep="first"),
    })
    df["alasan"] = aturan.apply(lambda baris: "; ".join(baris.index[baris]), axis=1)
    return df
 
 
def main():
    master = pd.read_csv(REF / "lokasi_master.csv")
    gabungan = pd.concat([muat_dan_seragamkan(c) for c in SUMBER], ignore_index=True)
    gabungan = normalisasi_teks(gabungan)
    hasil = validasi(gabungan, master)
 
    kolom_bersih = ["unit_id", "provinsi", "kabupaten", "tanggal", "komoditas",
                    "produksi_kg", "status", "sumber_file"]
    bersih = hasil[hasil["alasan"] == ""][kolom_bersih].sort_values(["tanggal", "unit_id"])
    bermasalah = hasil[hasil["alasan"] != ""][
        ["sumber_file", "baris_asal", "unit_id", "tanggal", "komoditas", "produksi_kg", "status", "alasan"]
    ]
 
    bersih.to_csv(OUT / "laporan_bersih.csv", index=False)
    bermasalah.to_csv(OUT / "data_bermasalah.csv", index=False)
 
    ringkasan = (bermasalah["alasan"].str.split("; ").explode().value_counts()
                 .rename_axis("alasan").reset_index(name="jumlah"))
    ringkasan.to_csv(OUT / "ringkasan_kualitas.csv", index=False)
 
    total = len(hasil)
    print(f"Total baris dibaca : {total}")
    print(f"Baris bersih       : {len(bersih)} ({len(bersih) / total:.1%})")
    print(f"Baris bermasalah   : {len(bermasalah)} ({len(bermasalah) / total:.1%})")
    print("\nMasalah per alasan (satu baris bisa punya lebih dari satu alasan):")
    print(ringkasan.to_string(index=False))
    print("\nBaris bermasalah per sumber:")
    print(bermasalah["sumber_file"].value_counts().to_string())
    print(f"\nSelesai. Hasil ada di: {OUT}")
 
 
if __name__ == "__main__":
    main()
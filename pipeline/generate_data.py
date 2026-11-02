"""
Generator data SIMULASI laporan unit budi daya dari 4 provinsi.

Semua angka dan status di sini adalah KARANGAN untuk keperluan portofolio,
bukan data resmi instansi mana pun. Nama wilayah memakai daftar umum.

Hasil:
  data/reference/lokasi_master.csv   daftar resmi unit (dipakai untuk validasi)
  data/raw/laporan_jabar.xlsx        format A: tanggal dd/mm/yyyy, kg
  data/raw/data_jateng.csv           format B: tanggal ISO, satuan TON
  data/raw/rekap_jatim.xlsx          format C: tanggal "12 Okt 2026", huruf campur
  data/raw/sulsel_laporan.csv        format D: pemisah ';' dan desimal koma

Jalankan dari folder utama proyek:
  python pipeline/generate_data.py
"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REF = ROOT / "data" / "reference"
RAW.mkdir(parents=True, exist_ok=True)
REF.mkdir(parents=True, exist_ok=True)

WILAYAH = {
    "Jawa Barat": ("JB", ["Bogor", "Sukabumi", "Cianjur", "Garut", "Tasikmalaya"]),
    "Jawa Tengah": ("JT", ["Banyumas", "Cilacap", "Klaten", "Boyolali", "Purbalingga"]),
    "Jawa Timur": ("JI", ["Malang", "Blitar", "Tulungagung", "Jember", "Banyuwangi"]),
    "Sulawesi Selatan": ("SS", ["Gowa", "Maros", "Bone", "Wajo", "Pinrang"]),
}
UNIT_PER_KAB = 6
JUMLAH_MINGGU = 8
MINGGU_TERAKHIR = date(2026, 10, 26)
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

weeks = [MINGGU_TERAKHIR - timedelta(weeks=i) for i in range(JUMLAH_MINGGU - 1, -1, -1)]


def buat_master():
    units = []
    for prov, (kode, kabs) in WILAYAH.items():
        n = 0
        for kab in kabs:
            for _ in range(UNIT_PER_KAB):
                n += 1
                units.append({
                    "unit_id": f"MR-{kode}-{n:03d}",
                    "provinsi": prov,
                    "kabupaten": kab,
                    "komoditas": random.choice(["Nila", "Lele"]),
                })
    return pd.DataFrame(units)


def buat_laporan(master):
    ids = list(master["unit_id"])
    jarang = set(random.sample(ids, 10))  # unit yang jarang melapor
    berhenti = set(random.sample([i for i in ids if i not in jarang], 8))  # berhenti 3 minggu terakhir
    rows = []
    for u in master.to_dict("records"):
        for wi, w in enumerate(weeks):
            if u["unit_id"] in berhenti and wi >= JUMLAH_MINGGU - 3:
                continue
            p = 0.4 if u["unit_id"] in jarang else 0.93
            if random.random() > p:
                continue
            status = random.choices(["aktif", "perawatan", "tidak aktif"], [90, 7, 3])[0]
            base = 95 if u["komoditas"] == "Nila" else 110
            if status == "aktif":
                prod = round(max(5, random.gauss(base, 25)), 1)
            elif status == "perawatan":
                prod = round(random.uniform(0, 20), 1)
            else:
                prod = 0.0
            rows.append({
                "unit_id": u["unit_id"],
                "provinsi": u["provinsi"],
                "kabupaten": u["kabupaten"],
                "tanggal": w + timedelta(days=random.randint(0, 4)),
                "komoditas": u["komoditas"],
                "produksi_kg": prod,
                "status": status,
            })
    return pd.DataFrame(rows)


def kotori(df):
    """Sisipkan masalah data yang realistis: duplikat, kosong, outlier, unit asing."""
    df = df.copy().reset_index(drop=True)
    df["tanggal"] = df["tanggal"].astype(object)
    df["komoditas"] = df["komoditas"].astype(object)

    idx = df.sample(frac=0.02, random_state=random.randint(0, 9999)).index
    df.loc[idx, "produksi_kg"] = None
    idx = df.sample(frac=0.01, random_state=random.randint(0, 9999)).index
    df.loc[idx, "tanggal"] = None
    idx = df.sample(frac=0.01, random_state=random.randint(0, 9999)).index
    df.loc[idx, "komoditas"] = None
    idx = df.sample(frac=0.01, random_state=random.randint(0, 9999)).index
    df.loc[idx, "produksi_kg"] = [random.choice([-50.0, 99999.0]) for _ in idx]

    dup = df.sample(frac=0.03, random_state=random.randint(0, 9999))
    asing = df.sample(3, random_state=random.randint(0, 9999)).copy()
    asing["unit_id"] = "MR-XX-999"
    df = pd.concat([df, dup, asing])
    return df.sample(frac=1, random_state=random.randint(0, 9999)).reset_index(drop=True)


def fmt_tanggal(d, pola):
    if pd.isna(d):
        return None
    return d.strftime(pola)


def variasi_teks(s):
    if pd.isna(s):
        return s
    return random.choice([s, s.lower(), s.upper(), s + " "])


def simpan_jabar(df):
    out = pd.DataFrame({
        "Kode Unit": df["unit_id"],
        "Kabupaten": df["kabupaten"],
        "Tanggal Lapor": df["tanggal"].map(lambda d: fmt_tanggal(d, "%d/%m/%Y")),
        "Komoditas": df["komoditas"],
        "Produksi (kg)": df["produksi_kg"],
        "Status": df["status"].str.capitalize(),
    })
    out.to_excel(RAW / "laporan_jabar.xlsx", index=False)
    return len(out)


def simpan_jateng(df):
    out = pd.DataFrame({
        "id_unit": df["unit_id"],
        "kab_kota": df["kabupaten"],
        "tgl": df["tanggal"].map(lambda d: fmt_tanggal(d, "%Y-%m-%d")),
        "jenis_ikan": df["komoditas"],
        "hasil_panen_ton": (df["produksi_kg"] / 1000).round(4),
        "kondisi": df["status"].replace({"tidak aktif": "nonaktif"}),
    })
    out.to_csv(RAW / "data_jateng.csv", index=False)
    return len(out)


def simpan_jatim(df):
    def tgl(d):
        return None if pd.isna(d) else f"{d.day} {BULAN[d.month - 1]} {d.year}"

    out = pd.DataFrame({
        "UNIT": df["unit_id"].map(lambda u: random.choice([u, u.lower(), f" {u}"])),
        "KABUPATEN": df["kabupaten"].str.upper(),
        "TANGGAL": df["tanggal"].map(tgl),
        "KOMODITAS": df["komoditas"].map(variasi_teks),
        "PRODUKSI_KG": df["produksi_kg"],
        "STATUS_UNIT": df["status"].str.upper(),
    })
    out.to_excel(RAW / "rekap_jatim.xlsx", index=False)
    return len(out)


def simpan_sulsel(df):
    sinonim = {"aktif": ["Aktif", "Beroperasi"], "perawatan": ["Perawatan"], "tidak aktif": ["Tidak Beroperasi"]}
    out = pd.DataFrame({
        "no_unit": df["unit_id"],
        "kabupaten": df["kabupaten"],
        "tanggal_laporan": df["tanggal"].map(lambda d: fmt_tanggal(d, "%d-%m-%y")),
        "komoditas": df["komoditas"],
        "produksi_kg": df["produksi_kg"],
        "status": df["status"].map(lambda s: random.choice(sinonim[s])),
    })
    out.to_csv(RAW / "sulsel_laporan.csv", index=False, sep=";", decimal=",")
    return len(out)


def main():
    master = buat_master()
    master.to_csv(REF / "lokasi_master.csv", index=False)
    laporan = buat_laporan(master)

    penyimpan = {
        "Jawa Barat": simpan_jabar,
        "Jawa Tengah": simpan_jateng,
        "Jawa Timur": simpan_jatim,
        "Sulawesi Selatan": simpan_sulsel,
    }
    print(f"Unit terdaftar : {len(master)}")
    print(f"Laporan bersih : {len(laporan)} baris (sebelum dikotori)")
    for prov, fn in penyimpan.items():
        df = kotori(laporan[laporan["provinsi"] == prov])
        print(f"{prov:<18}: {fn(df)} baris ditulis")
    print(f"\nSelesai. Cek folder: {RAW}")


if __name__ == "__main__":
    main()

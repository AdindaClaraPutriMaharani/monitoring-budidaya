import sqlite3
import sys
from pathlib import Path
 
import altair as alt
import pandas as pd
import streamlit as st
 
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
DB = ROOT / "data" / "monitoring.db"
 
import clean_data  # noqa: E402
import generate_data  # noqa: E402
import load_db  # noqa: E402
import run_queries  # noqa: E402
 
st.set_page_config(page_title="Monitoring unit budi daya", layout="wide")
 
TEAL, BLUE, ORANGE, CORAL = "#0E7C86", "#1B6CA8", "#F4A259", "#E4572E"
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
 
CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
.stAppDeployButton {display: none;}
.stApp {background: #F3F7F9;}
.block-container {padding-top: 1.6rem; max-width: 1200px;}
.hero {background: linear-gradient(120deg, #0B5D68 0%, #0E7C86 55%, #2FA4A9 100%); color: #fff;
       border-radius: 18px; padding: 26px 32px; display: flex; justify-content: space-between;
       align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 18px;}
.hero .judul-hero {font-size: 2rem; font-weight: 700; margin: 8px 0 2px; line-height: 1.2;}
.hero .deskripsi {margin: 0; opacity: .92;}
.chip {display: inline-block; background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.4);
       border-radius: 999px; padding: 2px 12px; font-size: .72rem; letter-spacing: .08em;}
.hero-side {text-align: right; font-size: .85rem; opacity: .95;}
.hero-side b {font-size: 1.25rem;}
.kartu {background: #fff; border-radius: 14px; padding: 16px 18px; border: 1px solid #E3ECF0;
        border-left: 6px solid var(--aksen); box-shadow: 0 1px 3px rgba(16,42,67,.06);}
.kartu .label {color: #5B7083; font-size: .82rem;}
.kartu .nilai {color: #12263A; font-size: 1.9rem; font-weight: 700; line-height: 1.25;}
.kartu .catatan {color: #5B7083; font-size: .78rem;}
.kartu .progres {height: 6px; background: #E3ECF0; border-radius: 99px; margin-top: 8px;}
.kartu .progres div {height: 100%; border-radius: 99px; background: var(--aksen);}
.judul-panel {color: #12263A; font-weight: 700; font-size: 1.05rem; margin: 0;}
.sub-panel {color: #5B7083; font-size: .82rem; margin: 0 0 8px;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 14px;}
</style>
"""
 
 
def siapkan_database():
    if not DB.exists():
        with st.spinner("Menyiapkan data simulasi..."):
            generate_data.main()
            clean_data.main()
            load_db.main()
 
 
@st.cache_data
def ambil(nama):
    with sqlite3.connect(DB) as con:
        return run_queries.jalankan(nama, con)
 
 
def tanggal_id(teks):
    d = pd.Timestamp(teks)
    return f"{d.day} {BULAN[d.month - 1]} {d.year}"
 
 
def kartu(label, nilai, catatan, aksen, persen=None):
    bar = f'<div class="progres"><div style="width:{persen}%"></div></div>' if persen is not None else ""
    return (f'<div class="kartu" style="--aksen:{aksen}"><div class="label">{label}</div>'
            f'<div class="nilai">{nilai}</div><div class="catatan">{catatan}</div>{bar}</div>')
 
 
def judul_panel(judul, keterangan):
    st.markdown(f'<p class="judul-panel">{judul}</p><p class="sub-panel">{keterangan}</p>',
                unsafe_allow_html=True)
 
 
siapkan_database()
st.markdown(CSS, unsafe_allow_html=True)
 
ringkasan = ambil("ringkasan").iloc[0]
tren = ambil("tren_produksi_mingguan")
progres = ambil("progres_per_provinsi")
minggu_terakhir = tren["minggu"].max()
 
st.markdown(
    f"""<div class="hero"><div><span class="chip">DATA SIMULASI</span>
    <div class="judul-hero">Monitoring unit budi daya</div>
    <p class="deskripsi">Pemantauan pelaporan dan produksi unit nila dan lele di {len(progres)} provinsi</p></div>
    <div class="hero-side">Minggu pelaporan terakhir<br><b>{tanggal_id(minggu_terakhir)}</b></div></div>""",
    unsafe_allow_html=True,
)
 
k1, k2, k3, k4 = st.columns(4)
total = int(ringkasan["lokasi_terdaftar"])
lapor = int(ringkasan["sudah_lapor_minggu_terakhir"])
k1.markdown(kartu("Lokasi terdaftar", total, f"tersebar di {len(progres)} provinsi", TEAL), unsafe_allow_html=True)
k2.markdown(kartu("Sudah melapor", f"{ringkasan['persen_lapor']:.1f}%",
                  f"{lapor} dari {total} lokasi, minggu terakhir", BLUE, persen=ringkasan["persen_lapor"]),
            unsafe_allow_html=True)
k3.markdown(kartu("Produksi bulan terakhir", f"{ringkasan['produksi_bulan_terakhir_ton']:.1f} ton",
                  "nila dan lele", "#2A9D8F"), unsafe_allow_html=True)
k4.markdown(kartu("Data bermasalah", int(ringkasan["baris_bermasalah"]),
                  "baris dikeluarkan dari perhitungan", CORAL), unsafe_allow_html=True)
 
st.write("")
kiri, kanan = st.columns(2)
 
with kiri, st.container(border=True):
    judul_panel("Progres pelaporan per provinsi", "Persentase lokasi yang melapor pada minggu terakhir. Merah: terendah.")
    dasar = alt.Chart(progres).encode(
        y=alt.Y("provinsi:N", sort="-x", title=None),
        x=alt.X("persen:Q", scale=alt.Scale(domain=[0, 100]), title="% lokasi yang melapor"),
        tooltip=["provinsi", "terdaftar", "sudah_lapor", "persen"],
    )
    warna = alt.condition(f"datum.persen == {progres['persen'].min()}", alt.value(CORAL), alt.value(TEAL))
    batang = dasar.mark_bar(cornerRadiusEnd=5, size=26).encode(color=warna)
    angka = dasar.mark_text(align="left", dx=5, fontWeight="bold").encode(text=alt.Text("persen:Q", format=".1f"))
    st.altair_chart((batang + angka).properties(height=230, width="container"))
 
with kanan, st.container(border=True):
    judul_panel("Perlu ditindaklanjuti", "Lokasi tanpa laporan dalam 2 minggu terakhir, yang terlama di atas.")
    belum = ambil("belum_lapor_2_minggu").copy()
    acuan = pd.Timestamp(minggu_terakhir) + pd.Timedelta(days=6)
    belum["hari_tanpa_laporan"] = (acuan - pd.to_datetime(belum["laporan_terakhir"])).dt.days
    belum["laporan_terakhir"] = belum["laporan_terakhir"].fillna("belum pernah")
    pilihan = st.selectbox("Filter provinsi", ["Semua"] + sorted(belum["provinsi"].unique()))
    if pilihan != "Semua":
        belum = belum[belum["provinsi"] == pilihan]
    st.dataframe(
        belum, hide_index=True, height=240,
        column_config={
            "unit_id": "Unit", "provinsi": "Provinsi", "kabupaten": "Kabupaten",
            "laporan_terakhir": "Laporan terakhir",
            "hari_tanpa_laporan": st.column_config.NumberColumn("Hari tanpa laporan", format="%d"),
        },
    )
    st.caption(f"{len(belum)} lokasi")
 
st.write("")
bawah_kiri, bawah_kanan = st.columns(2)
 
with bawah_kiri, st.container(border=True):
    judul_panel("Produksi mingguan", "Total produksi seluruh lokasi (kg)")
    dasar = alt.Chart(tren).encode(
        x=alt.X("minggu:T", title=None, axis=alt.Axis(format="%d %b")),
        y=alt.Y("produksi_kg:Q", title="kg"),
        tooltip=["minggu:T", "unit_melapor", "produksi_kg"],
    )
    area = dasar.mark_area(opacity=0.15, color=TEAL)
    garis = dasar.mark_line(color=TEAL, strokeWidth=3, point=alt.OverlayMarkDef(color=TEAL, size=70))
    st.altair_chart((area + garis).properties(height=260, width="container"))
 
with bawah_kanan, st.container(border=True):
    judul_panel("Produksi per komoditas", "Total per bulan (ton)")
    per_bulan = ambil("produksi_per_komoditas_bulan")
    st.altair_chart(
        alt.Chart(per_bulan).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("bulan:N", title=None),
            xOffset="komoditas:N",
            y=alt.Y("produksi_ton:Q", title="Ton"),
            color=alt.Color("komoditas:N", title=None,
                            scale=alt.Scale(domain=["Nila", "Lele"], range=[TEAL, ORANGE])),
            tooltip=["bulan", "komoditas", "produksi_ton", "jumlah_laporan"],
        ).properties(height=260, width="container")
    )
 
st.write("")
with st.expander("Kualitas data dari pipeline"):
    st.caption("Baris yang gagal validasi saat pembersihan data, dicatat di log beserta alasannya.")
    st.dataframe(ambil("kualitas_data_per_sumber"), hide_index=True)
 
st.caption("Dibuat dengan Python, pandas, SQLite, Altair, dan Streamlit. Semua data adalah simulasi.")
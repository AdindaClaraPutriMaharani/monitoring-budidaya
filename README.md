# 🐟 Monitoring Unit Budidaya

Dashboard monitoring pelaporan dan produksi unit budidaya ikan nila dan lele di empat provinsi di Indonesia. Project ini dikembangkan untuk membantu memantau aktivitas pelaporan unit, mengukur progres pelaporan, memonitor produksi, serta mengidentifikasi data yang memerlukan tindak lanjut.

## 🌐 Live Dashboard

**[Buka Dashboard Monitoring Budidaya](https://monitoring-budidaya-cepk2nbnx5dtncoixs8bvu.streamlit.app/)**

## 📌 Tentang Project

Monitoring Unit Budidaya merupakan aplikasi berbasis web yang dibangun menggunakan Python dan Streamlit. Aplikasi ini mengolah data pelaporan dan produksi budidaya ikan menjadi informasi yang lebih terstruktur melalui visualisasi data interaktif.

Project ini menggunakan data simulasi untuk menggambarkan proses monitoring unit budidaya ikan nila dan lele di empat provinsi, yaitu:

- Jawa Barat
- Jawa Tengah
- Jawa Timur
- Sulawesi Selatan

## 🎯 Tujuan Project

- Memantau jumlah lokasi atau unit budidaya yang terdaftar.
- Mengetahui persentase unit yang telah melakukan pelaporan.
- Memonitor perkembangan produksi budidaya ikan.
- Mengidentifikasi data bermasalah.
- Menampilkan lokasi yang belum melakukan pelaporan dalam periode tertentu.
- Menyajikan informasi melalui dashboard interaktif untuk mendukung proses monitoring dan evaluasi.

## ✨ Fitur Dashboard

### 1. Ringkasan Monitoring
Menampilkan informasi utama dalam bentuk kartu indikator (KPI), meliputi:
- Jumlah lokasi terdaftar.
- Persentase lokasi yang sudah melapor.
- Total produksi bulan terakhir.
- Jumlah data bermasalah.

### 2. Progres Pelaporan per Provinsi
Visualisasi persentase lokasi yang melakukan pelaporan pada minggu terakhir berdasarkan provinsi.

### 3. Daftar Lokasi yang Perlu Ditindaklanjuti
Menampilkan unit yang belum melakukan pelaporan dalam dua minggu terakhir, dilengkapi informasi provinsi, kabupaten, tanggal laporan terakhir, dan filter provinsi.

### 4. Produksi Mingguan
Menampilkan perkembangan total produksi budidaya ikan dalam satuan kilogram.

### 5. Produksi per Komoditas
Menyajikan perbandingan produksi ikan nila dan lele dalam satuan ton.

## 🛠️ Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python | Bahasa pemrograman utama |
| Pandas | Pengolahan dan analisis data |
| OpenPyXL | Membaca dan mengolah file Excel |
| Streamlit | Pengembangan dashboard interaktif |
| Altair | Visualisasi data |
| SQLite | Penyimpanan data dalam database |
| Git & GitHub | Version control dan pengelolaan repository |
| Streamlit Community Cloud | Deployment aplikasi |

## 📂 Struktur Project

```text
monitoring-budidaya/
│
├── .streamlit/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── reference/
│   └── processed/
│
├── pipeline/
│   ├── generate_data.py
│   ├── clean_data.py
│   └── load_db.py
│
├── sql/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Instalasi dan Menjalankan Project

Ikuti langkah berikut untuk menjalankan aplikasi secara lokal.

### 1. Clone Repository

```bash
git clone https://github.com/USERNAME/monitoring-budidaya.git
```

Masuk ke folder project:

```bash
cd monitoring-budidaya
```

Ganti `USERNAME` dengan username GitHub pemilik repository.

### 2. Buat Virtual Environment

```bash
python -m venv .venv
```

Aktifkan virtual environment.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instal Dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan Dashboard

```bash
streamlit run dashboard/app.py
```

Aplikasi akan terbuka melalui browser menggunakan alamat lokal yang diberikan oleh Streamlit.

## 🔄 Alur Pengolahan Data

Project ini menggunakan pipeline pengolahan data yang terdiri dari beberapa tahapan:

1. **Generate Data:** Membuat data simulasi pelaporan dan produksi budidaya.
2. **Clean Data:** Menggabungkan sumber data, menyeragamkan format, melakukan normalisasi, dan validasi data.
3. **Load Database:** Memasukkan hasil pengolahan data ke dalam database SQLite.
4. **Dashboard:** Mengambil data dari database dan menyajikannya dalam bentuk indikator, tabel, dan grafik interaktif.

## 📊 Cakupan Data

| Informasi | Keterangan |
|---|---|
| Jumlah lokasi | 120 unit |
| Wilayah | 4 provinsi |
| Komoditas | Ikan nila dan lele |
| Jenis data | Data pelaporan dan produksi |
| Sumber data | Data simulasi |
| Format sumber | CSV dan Excel |

## 🚀 Deployment

Aplikasi ini di-deploy menggunakan **Streamlit Community Cloud** dan terhubung dengan repository GitHub.

Konfigurasi deployment:

- Repository: `USERNAME/monitoring-budidaya`
- Branch: `main`
- Main file path: `dashboard/app.py`
- Python version: 3.12

**Link aplikasi:**  
https://monitoring-budidaya-cepk2nbnx5dtncoixs8bvu.streamlit.app/

## 📝 Catatan

- Project ini menggunakan data simulasi, bukan data operasional atau data resmi.
- Angka dan hasil visualisasi dapat berubah sesuai dengan data simulasi yang dihasilkan.
- Folder environment, database hasil generate, dan data processed tidak disertakan dalam repository.
- Aplikasi menjalankan pipeline untuk menyiapkan data ketika database belum tersedia.

## 👩‍💻 Author

Adinda Clara Putri Maharani

Developed as a data processing and visualization project using Python, Pandas, SQLite, and Streamlit.

---

⭐ Jika project ini bermanfaat, jangan lupa berikan star pada repository ini!

-- name: ringkasan
WITH akhir AS (SELECT MAX(minggu) AS m FROM v_laporan),
lapor AS (SELECT COUNT(DISTINCT unit_id) AS n FROM v_laporan WHERE minggu = (SELECT m FROM akhir)),
total AS (SELECT COUNT(*) AS n FROM lokasi)
SELECT total.n AS lokasi_terdaftar,
       lapor.n AS sudah_lapor_minggu_terakhir,
       ROUND(100.0 * lapor.n / total.n, 1) AS persen_lapor,
       (SELECT ROUND(SUM(produksi_kg) / 1000.0, 2) FROM v_laporan
         WHERE strftime('%Y-%m', tanggal) = (SELECT strftime('%Y-%m', MAX(tanggal)) FROM laporan)) AS produksi_bulan_terakhir_ton,
       (SELECT COUNT(*) FROM masalah_data) AS baris_bermasalah
FROM total, lapor;
 
-- name: progres_per_provinsi
WITH akhir AS (SELECT MAX(minggu) AS m FROM v_laporan)
SELECT lk.provinsi,
       COUNT(DISTINCT lk.unit_id) AS terdaftar,
       COUNT(DISTINCT v.unit_id) AS sudah_lapor,
       ROUND(100.0 * COUNT(DISTINCT v.unit_id) / COUNT(DISTINCT lk.unit_id), 1) AS persen
FROM lokasi lk
LEFT JOIN v_laporan v ON v.unit_id = lk.unit_id AND v.minggu = (SELECT m FROM akhir)
GROUP BY lk.provinsi
ORDER BY persen DESC;
 
-- name: produksi_per_komoditas_bulan
SELECT strftime('%Y-%m', tanggal) AS bulan,
       komoditas,
       ROUND(SUM(produksi_kg) / 1000.0, 2) AS produksi_ton,
       COUNT(*) AS jumlah_laporan
FROM v_laporan
GROUP BY bulan, komoditas
ORDER BY bulan, komoditas;
 
-- name: belum_lapor_2_minggu
WITH akhir AS (SELECT MAX(minggu) AS m FROM v_laporan)
SELECT lk.unit_id, lk.provinsi, lk.kabupaten,
       MAX(v.tanggal) AS laporan_terakhir
FROM lokasi lk
LEFT JOIN v_laporan v ON v.unit_id = lk.unit_id
GROUP BY lk.unit_id
HAVING MAX(v.tanggal) IS NULL
    OR MAX(v.tanggal) < date((SELECT m FROM akhir), '-7 days')
ORDER BY laporan_terakhir, lk.unit_id;
 
-- name: tren_produksi_mingguan
SELECT minggu,
       COUNT(DISTINCT unit_id) AS unit_melapor,
       ROUND(SUM(produksi_kg), 1) AS produksi_kg
FROM v_laporan
GROUP BY minggu
ORDER BY minggu;
 
-- name: kualitas_data_per_sumber
SELECT sumber_file, alasan, COUNT(*) AS jumlah
FROM masalah_data
GROUP BY sumber_file, alasan
ORDER BY sumber_file, jumlah DESC;
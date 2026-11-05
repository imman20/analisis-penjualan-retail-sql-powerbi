# Kamus Data

## 1. Data mentah: `data/raw/online_retail_II.csv`

Sumber: Chen, D. (2019). *Online Retail II* [Dataset]. UCI Machine Learning
Repository. https://doi.org/10.24432/C5CG6D. Lisensi CC BY 4.0.
File ini (104 MB, 1.067.371 baris) tidak dikomit; sampel 5.000 baris pertama
tersedia di `data/raw/sample/online_retail_II_sample.csv`.

| Kolom (asli) | Kolom (proyek) | Tipe | Keterangan |
|---|---|---|---|
| Invoice | `invoice_no` | string | Nomor invoice 6 digit. Awalan `C` menandai pembatalan/retur. |
| StockCode | `stock_code` | string | Kode produk 5 digit, opsional huruf varian (`85123A`). Kode tanpa pola ini (`POST`, `M`, `D`, ...) adalah biaya administratif. |
| Description | `description` | string | Nama produk (huruf kapital). |
| Quantity | `quantity` | int | Jumlah unit; negatif untuk retur/penyesuaian. |
| InvoiceDate | `invoice_date` | datetime | Tanggal dan jam transaksi (menit). |
| Price | `unit_price` | float | Harga satuan dalam GBP. |
| Customer ID | `customer_id` | int (nullable) | ID pelanggan 5 digit; kosong pada 22,8% baris. |
| Country | `country` | string | Negara pelanggan (43 nilai unik). |
| - | `source_sheet` | string | Ditambahkan saat konversi: `Year 2009-2010` atau `Year 2010-2011`. |

## 2. Data bersih: `data/processed/retail_clean.parquet` dan `retail_returns.parquet`

Kolom mentah di atas (tanpa `source_sheet`) ditambah:

| Kolom | Tipe | Keterangan |
|---|---|---|
| `is_return` | bool | `False` di file penjualan, `True` di file retur. |
| `line_total` | float | `quantity * unit_price`, dibulatkan 2 desimal; negatif untuk retur. |
| `is_guest` | bool | `True` jika `customer_id` kosong. |
| `invoice_month` | string | Bulan invoice `YYYY-MM`. |

## 3. Warehouse: `data/processed/retail_dw.sqlite`

### `fact_sales` (1.021.128 baris)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `sales_key` | INTEGER PK | Surrogate key berurutan menurut waktu. |
| `invoice_no` | TEXT | Nomor invoice (degenerate dimension). |
| `invoice_datetime` | TEXT | `YYYY-MM-DD HH:MM:SS`. |
| `date_key` | INTEGER FK | Ke `dim_date`, format YYYYMMDD. |
| `product_key` | INTEGER FK | Ke `dim_product`. |
| `customer_key` | INTEGER FK | Ke `dim_customer`. |
| `store_key` | INTEGER FK | Ke `dim_store`. |
| `quantity` | INTEGER | Unit; negatif jika retur. |
| `unit_price` | REAL | Harga satuan GBP. |
| `line_total` | REAL | Nilai baris GBP; negatif jika retur. |
| `is_return` | INTEGER | 1 = retur, 0 = penjualan. |

### `dim_product` (4.721 baris)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `product_key` | INTEGER PK | |
| `stock_code` | TEXT UNIQUE | Kode stok. |
| `description` | TEXT | Deskripsi yang paling sering muncul untuk kode tersebut. |
| `category` | TEXT | Salah satu dari 9 kategori hasil pemetaan kata kunci (`src/data/categorize.py`): Home Decor, Kitchen & Dining, Bags & Accessories, Stationery & Gift Wrap, Candles & Lighting, Christmas & Seasonal, Garden & Outdoor, Toys & Kids, Other. |

### `dim_customer` (5.890 baris)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `customer_key` | INTEGER PK | |
| `customer_id` | INTEGER | ID asli; NULL untuk baris tamu. |
| `country` | TEXT | Negara yang paling sering dipakai pelanggan (13 pelanggan punya > 1 negara). |
| `region` | TEXT | `United Kingdom`, `Europe`, atau `Rest of World`. |
| `is_guest` | INTEGER | 1 = baris tamu (satu per negara). |
| `first_purchase_date` | TEXT | Tanggal invoice penjualan pertama; NULL untuk tamu. |

### `dim_date` (761 baris)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `date_key` | INTEGER PK | YYYYMMDD. |
| `full_date` | TEXT | `YYYY-MM-DD`. |
| `year`, `quarter`, `month`, `day` | INTEGER | Komponen tanggal. |
| `month_name` | TEXT | `Jan` ... `Dec`. |
| `year_month` | TEXT | `YYYY-MM`. |
| `week_of_year` | INTEGER | Minggu ISO. |
| `day_of_week` | INTEGER | 1 = Senin ... 7 = Minggu. |
| `day_name` | TEXT | `Mon` ... `Sun`. |
| `is_weekend` | INTEGER | 1 untuk Sabtu/Minggu. |

### `dim_store` (3 baris)

| Kolom | Tipe | Keterangan |
|---|---|---|
| `store_key` | INTEGER PK | 1, 2, 3. |
| `store_code` | TEXT | `ONL-UK`, `ONL-EU`, `ONL-ROW`. |
| `store_name` | TEXT | `Online Store - UK/Europe/Rest of World`. |
| `channel` | TEXT | Selalu `Online` pada dataset ini. |
| `region` | TEXT | Wilayah pasar, sama dengan `dim_customer.region`. |

## 4. Keluaran analisis

| File | Isi |
|---|---|
| `reports/sql_output/NN_*.csv` | Hasil tiap query `sql/NN_*.sql`. |
| `reports/sql_output/_indeks.md` | Ringkasan dan pratinjau semua hasil query. |
| `reports/rfm_segments.csv` | 5.852 pelanggan dengan nilai R/F/M, skor, segmen aturan, dan label klaster KMeans. |
| `reports/dashboard.html` | Dashboard statis (Plotly). |

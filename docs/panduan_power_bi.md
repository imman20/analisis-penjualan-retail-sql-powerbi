# Panduan Menghubungkan Warehouse ke Power BI dan Tableau

Repositori ini sengaja tidak menyertakan file `.pbix` atau `.twbx`: keduanya
berformat biner yang tidak bisa ditinjau di GitHub dan hanya bisa dibuat lewat
aplikasi desktop. Panduan ini menjelaskan cara saya membangun laporan di Power BI
secara manual dari warehouse yang dihasilkan pipeline, sehingga siapa pun bisa
mereproduksinya.

## 1. Sumber data yang bisa dipakai

| Sumber | Lokasi | Cocok untuk |
|---|---|---|
| SQLite star schema | `data/processed/retail_dw.sqlite` (hasil `make warehouse`) | Model relasional lengkap, ukuran DAX |
| CSV hasil query | `reports/sql_output/*.csv` | Visual cepat tanpa pemodelan |
| CSV segmen RFM | `reports/rfm_segments.csv` | Tabel/visual segmen pelanggan |

## 2. Power BI Desktop

### 2.1 Koneksi ke SQLite (lewat ODBC)

Power BI tidak punya konektor SQLite bawaan; cara paling stabil adalah ODBC.

1. Pasang **SQLite ODBC Driver** (http://www.ch-werner.de/sqliteodbc/, pilih
   versi 64-bit yang sesuai dengan Power BI).
2. Buka *ODBC Data Sources (64-bit)* di Windows, tab *System DSN*, klik *Add*,
   pilih *SQLite3 ODBC Driver*, beri nama `retail_dw`, dan arahkan *Database
   Name* ke path lengkap `data/processed/retail_dw.sqlite`.
3. Di Power BI Desktop: *Get Data* > *ODBC* > pilih DSN `retail_dw` > centang
   lima tabel (`fact_sales`, `dim_date`, `dim_product`, `dim_customer`,
   `dim_store`) > *Load*.

Alternatif tanpa ODBC: ekspor tiap tabel ke CSV dengan

```bash
python - <<'EOF'
import sqlite3, pandas as pd
conn = sqlite3.connect("data/processed/retail_dw.sqlite")
for t in ["fact_sales", "dim_date", "dim_product", "dim_customer", "dim_store"]:
    pd.read_sql(f"SELECT * FROM {t}", conn).to_csv(f"data/processed/{t}.csv", index=False)
EOF
```

lalu *Get Data* > *Text/CSV* untuk tiap file.

### 2.2 Model relasi yang disarankan

Di tampilan *Model*, buat relasi satu-ke-banyak (arah filter tunggal, dari
dimensi ke fakta):

| Dari (1) | Ke (banyak) | Kolom |
|---|---|---|
| `dim_date` | `fact_sales` | `date_key` |
| `dim_product` | `fact_sales` | `product_key` |
| `dim_customer` | `fact_sales` | `customer_key` |
| `dim_store` | `fact_sales` | `store_key` |

Tandai `dim_date` sebagai *date table* (*Table tools* > *Mark as date table*,
kolom `full_date` setelah diubah ke tipe Date) agar fungsi time intelligence
seperti `SAMEPERIODLASTYEAR` bekerja.

Sembunyikan kolom kunci (`*_key`) dari tampilan laporan supaya pengguna hanya
melihat atribut bisnis.

### 2.3 Ukuran DAX dasar

```dax
Total Sales =
CALCULATE ( SUM ( fact_sales[line_total] ), fact_sales[is_return] = 0 )

Returned Value =
CALCULATE ( -SUM ( fact_sales[line_total] ), fact_sales[is_return] = 1 )

Net Sales = [Total Sales] - [Returned Value]

Return Rate = DIVIDE ( [Returned Value], [Total Sales] )

Invoices =
CALCULATE ( DISTINCTCOUNT ( fact_sales[invoice_no] ), fact_sales[is_return] = 0 )

AOV = DIVIDE ( [Total Sales], [Invoices] )

Customers =
CALCULATE (
    DISTINCTCOUNT ( dim_customer[customer_id] ),
    dim_customer[is_guest] = 0,
    fact_sales[is_return] = 0
)

Units Sold =
CALCULATE ( SUM ( fact_sales[quantity] ), fact_sales[is_return] = 0 )

Sales LY =
CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( dim_date[full_date] ) )

YoY Growth = DIVIDE ( [Total Sales] - [Sales LY], [Sales LY] )

Sales MoM % =
VAR PrevMonth =
    CALCULATE ( [Total Sales], DATEADD ( dim_date[full_date], -1, MONTH ) )
RETURN
    DIVIDE ( [Total Sales] - PrevMonth, PrevMonth )

Sales YTD = TOTALYTD ( [Total Sales], dim_date[full_date] )

Sales Share % =
DIVIDE ( [Total Sales], CALCULATE ( [Total Sales], ALL ( dim_product ) ) )
```

Catatan: `YoY Growth` pada Desember 2011 akan menyesatkan karena bulan itu
hanya 9 hari; tambahkan kartu peringatan atau filter `dim_date[full_date] <=
DATE(2011,12,9)` pada visual perbandingan tahunan.

### 2.4 Halaman laporan yang disarankan

1. **Ringkasan** - kartu `Net Sales`, `Invoices`, `Customers`, `AOV`, `Return
   Rate`; grafik garis `Total Sales` per `year_month`; slicer periode, negara,
   kategori (meniru `app/dashboard.py`).
2. **Produk** - bar `Net Sales` per `description` (Top N = 10), bar pangsa per
   `category`, tabel ABC dari `reports/sql_output/12_pareto_produk.csv`.
3. **Pelanggan** - peta `Total Sales` per `country`, tabel segmen dari
   `reports/rfm_segments.csv` (gabungkan ke `dim_customer` lewat `customer_id`).
4. **Operasional** - matriks `Invoices` per `day_name` x jam
   (buat kolom `hour = HOUR(fact_sales[invoice_datetime])`), tabel tingkat
   retur per kategori.

## 3. Tableau Desktop / Tableau Public

1. *Connect* > *To a File* > *More...* > pilih `retail_dw.sqlite` memerlukan
   driver ODBC yang sama seperti di atas (*Other Databases (ODBC)*). Cara
   termudah untuk Tableau Public adalah memakai CSV hasil ekspor pada bagian
   2.1.
2. Seret `fact_sales` ke kanvas, lalu seret masing-masing dimensi dan
   hubungkan dengan *relationship* pada kolom kunci yang sama seperti tabel
   relasi Power BI.
3. Calculated fields padanan DAX:
   - `Total Sales`: `SUM(IF [is_return] = 0 THEN [line_total] END)`
   - `Returned Value`: `-SUM(IF [is_return] = 1 THEN [line_total] END)`
   - `Invoices`: `COUNTD(IF [is_return] = 0 THEN [invoice_no] END)`
   - `AOV`: `[Total Sales] / [Invoices]`
   - YoY: gunakan *Quick Table Calculation* > *Year over Year Growth* pada
     `Total Sales` dengan `full_date` di sumbu bulan.

## 4. Memperbarui data

Jalankan ulang `make data clean-data warehouse sql` lalu klik *Refresh* di Power
BI/Tableau. Karena surrogate key dibuat ulang secara deterministik dari data
yang sama, relasi tidak perlu diatur ulang.

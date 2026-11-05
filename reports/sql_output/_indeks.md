# Indeks hasil query SQL

Dibuat otomatis oleh `python -m src.run_sql`.

## 01_ringkasan_kpi

- File query: `sql/01_ringkasan_kpi.sql`
- Hasil: `reports/sql_output/01_ringkasan_kpi.csv` (1 baris, 1.43 detik)

| first_date   | last_date   |   gross_revenue |   returned_value |   net_revenue |   sales_invoices |   return_invoices |   registered_customers |   products_sold |   units_sold |   avg_order_value |
|:-------------|:------------|----------------:|-----------------:|--------------:|-----------------:|------------------:|-----------------------:|----------------:|-------------:|------------------:|
| 2009-12-01   | 2011-12-09  |     1.96427e+07 |          -716426 |   1.89263e+07 |            39516 |              7405 |                   5875 |            4721 |     11187774 |            497.08 |

## 02_penjualan_per_negara

- File query: `sql/02_penjualan_per_negara.sql`
- Hasil: `reports/sql_output/02_penjualan_per_negara.csv` (21 baris, 1.43 detik)

| country        | region         |   invoices |   customers |          revenue |   avg_order_value |   revenue_share_pct |
|:---------------|:---------------|-----------:|------------:|-----------------:|------------------:|--------------------:|
| United Kingdom | United Kingdom |      36184 |        5334 |      1.67998e+07 |            464.29 |               85.53 |
| EIRE           | Europe         |        581 |           3 | 623414           |           1073    |                3.17 |
| Netherlands    | Europe         |        216 |          22 | 549773           |           2545.25 |                2.8  |
| Germany        | Europe         |        752 |         106 | 383192           |            509.56 |                1.95 |
| France         | Europe         |        600 |          93 | 311373           |            518.95 |                1.59 |
| Australia      | Rest of World  |         87 |          14 | 168453           |           1936.24 |                0.86 |
| Spain          | Europe         |        137 |          35 |  96399.1         |            703.64 |                0.49 |
| Switzerland    | Europe         |         93 |          22 |  96166.9         |           1034.05 |                0.49 |

## 03_tren_bulanan

- File query: `sql/03_tren_bulanan.sql`
- Hasil: `reports/sql_output/03_tren_bulanan.csv` (25 baris, 1.17 detik)

| year_month   |   year | month_name   |   active_days |   invoices |   customers |   units |   revenue |   avg_order_value |   partial_month |
|:-------------|-------:|:-------------|--------------:|-----------:|------------:|--------:|----------:|------------------:|----------------:|
| 2009-12      |   2009 | Dec          |            21 |       1666 |         953 |  425189 |    797738 |            478.83 |               0 |
| 2010-01      |   2010 | Jan          |            24 |       1049 |         702 |  390408 |    612271 |            583.67 |               0 |
| 2010-02      |   2010 | Feb          |            24 |       1189 |         775 |  381619 |    537894 |            452.39 |               0 |
| 2010-03      |   2010 | Mar          |            27 |       1647 |        1055 |  525030 |    761666 |            462.46 |               0 |
| 2010-04      |   2010 | Apr          |            23 |       1435 |         943 |  366057 |    646233 |            450.34 |               0 |
| 2010-05      |   2010 | May          |            24 |       1484 |         968 |  395435 |    643474 |            433.61 |               0 |
| 2010-06      |   2010 | Jun          |            26 |       1612 |        1037 |  406197 |    696439 |            432.03 |               0 |
| 2010-07      |   2010 | Jul          |            26 |       1507 |         927 |  337548 |    632984 |            420.03 |               0 |

## 04_top_produk

- File query: `sql/04_top_produk.sql`
- Hasil: `reports/sql_output/04_top_produk.csv` (10 baris, 2.19 detik)

| stock_code   | description                        | category               |   units |   invoices |   avg_unit_price |   revenue |   revenue_share_pct |
|:-------------|:-----------------------------------|:-----------------------|--------:|-----------:|-----------------:|----------:|--------------------:|
| 22423        | REGENCY CAKESTAND 3 TIER           | Kitchen & Dining       |   26478 |       3918 |            14.19 |  330590   |                1.68 |
| 85123A       | WHITE HANGING HEART T-LIGHT HOLDER | Candles & Lighting     |   94719 |       5464 |             3.14 |  261169   |                1.33 |
| 85099B       | JUMBO BAG RED RETROSPOT            | Bags & Accessories     |   97176 |       4013 |             2.35 |  182681   |                0.93 |
| 23843        | PAPER CRAFT , LITTLE BIRDIE        | Stationery & Gift Wrap |   80995 |          1 |             2.08 |  168470   |                0.86 |
| 47566        | PARTY BUNTING                      | Home Decor             |   28200 |       2674 |             5.72 |  148318   |                0.76 |
| 84879        | ASSORTED COLOUR BIRD ORNAMENT      | Garden & Outdoor       |   80082 |       2807 |             1.86 |  129324   |                0.66 |
| 22086        | PAPER CHAIN KIT 50'S CHRISTMAS     | Christmas & Seasonal   |   35084 |       2018 |             3.37 |  117760   |                0.6  |
| 23166        | MEDIUM CERAMIC TOP STORAGE JAR     | Kitchen & Dining       |   78033 |        247 |             1.47 |   81700.9 |                0.42 |

## 05_kategori_per_tahun

- File query: `sql/05_kategori_per_tahun.sql`
- Hasil: `reports/sql_output/05_kategori_per_tahun.csv` (9 baris, 2.42 detik)

| category               |   products |     revenue_2010 |     revenue_2011 |   revenue_2010_to_dec9 |   growth_like_for_like_pct |   share_of_total_pct |
|:-----------------------|-----------:|-----------------:|-----------------:|-----------------------:|---------------------------:|---------------------:|
| Home Decor             |        901 |      2.36001e+06 |      2.41498e+06 |            2.26979e+06 |                       6.4  |                25.22 |
| Kitchen & Dining       |        823 |      2.23437e+06 |      2.30316e+06 |            2.11206e+06 |                       9.05 |                24.11 |
| Bags & Accessories     |        668 |      1.09748e+06 |      1.21323e+06 |            1.06445e+06 |                      13.98 |                12.24 |
| Other                  |        716 | 995910           | 920055           |       962057           |                      -4.37 |                10.2  |
| Stationery & Gift Wrap |        486 | 758867           | 848406           |       738082           |                      14.95 |                 8.47 |
| Candles & Lighting     |        465 | 781516           | 645871           |       750433           |                     -13.93 |                 7.74 |
| Christmas & Seasonal   |        279 | 427844           | 485210           |       409859           |                      18.38 |                 4.8  |
| Garden & Outdoor       |        250 | 473493           | 407288           |       463306           |                     -12.09 |                 4.74 |

## 06_pelanggan_di_atas_rata_rata

- File query: `sql/06_pelanggan_di_atas_rata_rata.sql`
- Hasil: `reports/sql_output/06_pelanggan_di_atas_rata_rata.csv` (1,162 baris, 1.44 detik)

|   customer_id | country        |   invoices |   total_spend |   avg_order_value |   times_average |
|--------------:|:---------------|-----------:|--------------:|------------------:|----------------:|
|         18102 | United Kingdom |        145 |        580987 |           4006.81 |          199.19 |
|         14646 | Netherlands    |        145 |        526752 |           3632.77 |          180.6  |
|         14156 | EIRE           |        144 |        303070 |           2104.65 |          103.91 |
|         14911 | EIRE           |        373 |        272253 |            729.9  |           93.34 |
|         17450 | United Kingdom |         51 |        244784 |           4799.69 |           83.92 |
|         13694 | United Kingdom |        143 |        195641 |           1368.12 |           67.08 |
|         17511 | United Kingdom |         60 |        172133 |           2868.88 |           59.02 |
|         16446 | United Kingdom |          2 |        168472 |          84236.2  |           57.76 |

## 07_cte_aov_per_wilayah

- File query: `sql/07_cte_aov_per_wilayah.sql`
- Hasil: `reports/sql_output/07_cte_aov_per_wilayah.csv` (3 baris, 0.85 detik)

| store_name                   | region         |   invoices |          revenue |   avg_order_value |   trimmed_aov_p99 |   avg_units_per_order |   avg_lines_per_order |
|:-----------------------------|:---------------|-----------:|-----------------:|------------------:|------------------:|----------------------:|----------------------:|
| Online Store - Rest of World | Rest of World  |        233 | 298463           |           1280.96 |           1030.78 |                 810.4 |                  25   |
| Online Store - Europe        | Europe         |       3099 |      2.54438e+06 |            821.03 |            688    |                 588.3 |                  23.9 |
| Online Store - UK            | United Kingdom |      36184 |      1.67998e+07 |            464.29 |            389.94 |                 253.6 |                  25.5 |

## 08_window_rank_produk_per_kategori

- File query: `sql/08_window_rank_produk_per_kategori.sql`
- Hasil: `reports/sql_output/08_window_rank_produk_per_kategori.csv` (27 baris, 1.90 detik)

| category             |   rank_in_category | stock_code   | description                         |   units |   revenue |   share_in_category_pct |
|:---------------------|-------------------:|:-------------|:------------------------------------|--------:|----------:|------------------------:|
| Bags & Accessories   |                  1 | 85099B       | JUMBO BAG RED RETROSPOT             |   97176 |  182681   |                    7.6  |
| Bags & Accessories   |                  2 | 22386        | JUMBO BAG PINK POLKADOT             |   39437 |   76324.6 |                    3.17 |
| Bags & Accessories   |                  3 | 20725        | LUNCH BAG RED RETROSPOT             |   40317 |   71106.3 |                    2.96 |
| Candles & Lighting   |                  1 | 85123A       | WHITE HANGING HEART T-LIGHT HOLDER  |   94719 |  261169   |                   17.18 |
| Candles & Lighting   |                  2 | 84347        | ROTATING SILVER ANGELS T-LIGHT HLDR |   31409 |   71300.4 |                    4.69 |
| Candles & Lighting   |                  3 | 23084        | RABBIT NIGHT LIGHT                  |   30739 |   66870   |                    4.4  |
| Christmas & Seasonal |                  1 | 22086        | PAPER CHAIN KIT 50'S CHRISTMAS      |   35084 |  117760   |                   12.48 |
| Christmas & Seasonal |                  2 | 22910        | PAPER CHAIN KIT VINTAGE CHRISTMAS   |   18634 |   58652.7 |                    6.22 |

## 09_window_growth_mom

- File query: `sql/09_window_growth_mom.sql`
- Hasil: `reports/sql_output/09_window_growth_mom.csv` (25 baris, 0.64 detik)

| year_month   |   revenue |   invoices |   revenue_prev_month |   mom_growth_pct |   revenue_same_month_last_year |   yoy_growth_pct |   partial_month |
|:-------------|----------:|-----------:|---------------------:|-----------------:|-------------------------------:|-----------------:|----------------:|
| 2009-12      |    797738 |       1666 |                  nan |           nan    |                            nan |              nan |               0 |
| 2010-01      |    612271 |       1049 |               797738 |           -23.25 |                            nan |              nan |               0 |
| 2010-02      |    537894 |       1189 |               612271 |           -12.15 |                            nan |              nan |               0 |
| 2010-03      |    761666 |       1647 |               537894 |            41.6  |                            nan |              nan |               0 |
| 2010-04      |    646233 |       1435 |               761666 |           -15.16 |                            nan |              nan |               0 |
| 2010-05      |    643474 |       1484 |               646233 |            -0.43 |                            nan |              nan |               0 |
| 2010-06      |    696439 |       1612 |               643474 |             8.23 |                            nan |              nan |               0 |
| 2010-07      |    632984 |       1507 |               696439 |            -9.11 |                            nan |              nan |               0 |

## 10_window_running_total

- File query: `sql/10_window_running_total.sql`
- Hasil: `reports/sql_output/10_window_running_total.csv` (25 baris, 0.76 detik)

|   year |   month | year_month   |   revenue |      ytd_revenue |   moving_avg_3m |   share_of_year_pct |
|-------:|--------:|:-------------|----------:|-----------------:|----------------:|--------------------:|
|   2009 |      12 | 2009-12      |    797738 | 797738           |          797738 |              100    |
|   2010 |       1 | 2010-01      |    612271 | 612271           |          705005 |                6.53 |
|   2010 |       2 | 2010-02      |    537894 |      1.15016e+06 |          649301 |                5.74 |
|   2010 |       3 | 2010-03      |    761666 |      1.91183e+06 |          637277 |                8.13 |
|   2010 |       4 | 2010-04      |    646233 |      2.55806e+06 |          648597 |                6.89 |
|   2010 |       5 | 2010-05      |    643474 |      3.20154e+06 |          683791 |                6.86 |
|   2010 |       6 | 2010-06      |    696439 |      3.89798e+06 |          662049 |                7.43 |
|   2010 |       7 | 2010-07      |    632984 |      4.53096e+06 |          657632 |                6.75 |

## 11_cohort_retensi

- File query: `sql/11_cohort_retensi.sql`
- Hasil: `reports/sql_output/11_cohort_retensi.csv` (169 baris, 0.75 detik)

| cohort_month   |   cohort_size |   month_number |   active_customers |   retention_pct |
|:---------------|--------------:|---------------:|-------------------:|----------------:|
| 2009-12        |           951 |              0 |                951 |           100   |
| 2009-12        |           951 |              1 |                333 |            35   |
| 2009-12        |           951 |              2 |                317 |            33.3 |
| 2009-12        |           951 |              3 |                404 |            42.5 |
| 2009-12        |           951 |              4 |                360 |            37.9 |
| 2009-12        |           951 |              5 |                342 |            36   |
| 2009-12        |           951 |              6 |                358 |            37.6 |
| 2009-12        |           951 |              7 |                327 |            34.4 |

## 12_pareto_produk

- File query: `sql/12_pareto_produk.sql`
- Hasil: `reports/sql_output/12_pareto_produk.csv` (3 baris, 1.94 detik)

| abc_class          |   products |   products_share_pct |          revenue |   revenue_share_pct |   first_rank |   last_rank |
|:-------------------|-----------:|---------------------:|-----------------:|--------------------:|-------------:|------------:|
| A (80% pendapatan) |       1029 |                21.86 |      1.5713e+07  |               79.99 |            1 |        1029 |
| B (80-95%)         |       1261 |                26.79 |      2.94642e+06 |               15    |         1030 |        2290 |
| C (5% terakhir)    |       2417 |                51.35 | 983253           |                5.01 |         2291 |        4707 |

## 13_rfm_sql

- File query: `sql/13_rfm_sql.sql`
- Hasil: `reports/sql_output/13_rfm_sql.csv` (8 baris, 1.00 detik)

| segment             |   customers |   customers_share_pct |   avg_recency_days |   avg_frequency |   avg_monetary |   total_monetary |   revenue_share_pct |
|:--------------------|------------:|----------------------:|-------------------:|----------------:|---------------:|-----------------:|--------------------:|
| Champions           |        1355 |                  23.2 |                 20 |            16.4 |        8849.27 |      1.19908e+07 |                70.3 |
| Loyal Customers     |         771 |                  13.2 |                 84 |             6.9 |        2755.29 |      2.12433e+06 |                12.4 |
| Need Attention      |         480 |                   8.2 |                298 |             5.6 |        2458.59 |      1.18012e+06 |                 6.9 |
| Potential Loyalists |        1176 |                  20.1 |                 68 |             2.4 |         591.98 | 696166           |                 4.1 |
| Hibernating         |        1176 |                  20.1 |                400 |             1.8 |         523.75 | 615926           |                 3.6 |
| At Risk             |          86 |                   1.5 |                494 |             7.2 |        3622.88 | 311568           |                 1.8 |
| Lost                |         600 |                  10.3 |                567 |             1.1 |         181.38 | 108831           |                 0.6 |
| New Customers       |         208 |                   3.6 |                 28 |             1.2 |         196.46 |  40863.8         |                 0.2 |

## 14_tingkat_retur

- File query: `sql/14_tingkat_retur.sql`
- Hasil: `reports/sql_output/14_tingkat_retur.csv` (9 baris, 3.13 detik)

| category               |   sales_invoices |   return_invoices |    gross_revenue |   returned_value |   return_rate_value_pct |   return_rate_units_pct |
|:-----------------------|-----------------:|------------------:|-----------------:|-----------------:|------------------------:|------------------------:|
| Stationery & Gift Wrap |            22707 |               629 |      1.66317e+06 |         195685   |                   11.77 |                    6.7  |
| Kitchen & Dining       |            30327 |              3401 |      4.73529e+06 |         218241   |                    4.61 |                    7.12 |
| Candles & Lighting     |            20211 |              1156 |      1.51983e+06 |          45685.9 |                    3.01 |                    4.03 |
| Home Decor             |            31237 |              2690 |      4.95386e+06 |         124782   |                    2.52 |                    2.56 |
| Toys & Kids            |            11999 |               327 | 488740           |          11908.1 |                    2.44 |                    1.72 |
| Other                  |            26541 |              1375 |      2.00356e+06 |          42260.4 |                    2.11 |                    2.16 |
| Garden & Outdoor       |            16659 |               566 | 930583           |          17579.8 |                    1.89 |                    1.95 |
| Bags & Accessories     |            22709 |              1078 |      2.40423e+06 |          44005.5 |                    1.83 |                    2.61 |

## 15_pola_hari_jam

- File query: `sql/15_pola_hari_jam.sql`
- Hasil: `reports/sql_output/15_pola_hari_jam.csv` (85 baris, 1.57 detik)

|   day_of_week | day_name   |   hour_of_day |   invoices |   revenue |   invoice_share_pct |
|--------------:|:-----------|--------------:|-----------:|----------:|--------------------:|
|             1 | Mon        |             7 |         14 |   15830.4 |                0.04 |
|             1 | Mon        |             8 |        169 |   90011.6 |                0.43 |
|             1 | Mon        |             9 |        498 |  301565   |                1.26 |
|             1 | Mon        |            10 |        727 |  403843   |                1.84 |
|             1 | Mon        |            11 |        721 |  372409   |                1.82 |
|             1 | Mon        |            12 |        994 |  424289   |                2.52 |
|             1 | Mon        |            13 |        931 |  467722   |                2.36 |
|             1 | Mon        |            14 |        803 |  373445   |                2.03 |

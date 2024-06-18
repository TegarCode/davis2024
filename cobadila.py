import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import squarify
from sqlalchemy import create_engine
from io import StringIO

# Fungsi untuk membuat koneksi ke database
def buat_koneksi():
    host = "kubela.id"
    port = 3306
    user = "davis2024irwan"
    password = "wh451n9m@ch1n3"
    database = "aw"
    
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        return connection
    except Exception as e:
        st.error(f"Error menghubungkan ke database: {e}")
        return None

# Fungsi untuk menjalankan query dan mendapatkan data
def ambil_data(query):
    connection = buat_koneksi()
    if connection is None:
        return None
    try:
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        st.error(f"Error menjalankan query: {e}")
        return None
    finally:
        connection.close()

st.write("Nama: Ardilla Firosya")
st.write("NPM: 21082010239")
st.write("Mata Kuliah : Data Visualisasi")

st.title("Dataset AdventureWorks")

st.header("Sales Amount by Product Sub Category")
st.write("Jumlah Penjualan Berdasarkan SubKategori Produk")
st.write("Comparison: Bar Chart Data Visualitation")

# Query untuk Sales Amount by Product Sub Category
query_sales_amount = """
SELECT 
    dpsc.EnglishProductSubCategoryName AS ProductSubCategory, 
    SUM(fis.SalesAmount) AS SalesAmount
FROM 
    factinternetsales fis
JOIN 
    dimproduct dp ON fis.ProductKey = dp.ProductKey
JOIN 
    dimproductsubcategory dpsc ON dp.ProductSubCategoryKey = dpsc.ProductSubCategoryKey
GROUP BY 
    dpsc.EnglishProductSubCategoryName
ORDER BY
    SalesAmount DESC
"""

df_sales_amount = ambil_data(query_sales_amount)
if df_sales_amount is not None:
    top_n = 7
    top_categories = df_sales_amount.nlargest(top_n, 'SalesAmount')
    others = pd.DataFrame({
        'ProductSubCategory': ['Others'],
        'SalesAmount': [df_sales_amount['SalesAmount'][~df_sales_amount['ProductSubCategory'].isin(top_categories['ProductSubCategory'])].sum()]
    })
    df_sales_combined = pd.concat([top_categories, others], ignore_index=True)
    
    plt.figure(figsize=(14, 7))
    sns.barplot(data=df_sales_combined, x='SalesAmount', y='ProductSubCategory', palette='viridis')
    plt.title('Sales Amount by Product Sub Category')
    plt.xlabel('Sales Amount')
    plt.ylabel('Product Sub Category')
    plt.tight_layout()
    st.pyplot(plt)

st.write("Deskripsi Data Visualisasi:")
st.write("Visualisasi data tersebut menggunakan Grafik Bar Chart dengan menampilkan Jumlah Penjualan berdasarkan Sub Category Product dari data AdventureWorks. Grafik tersebut terdiri antara sumbu x sebagai 'Sales Amount' (Jumlah Penjualan) dan sumbu y sebagai 'Product Sub Category'. Terdapat 8 subcategory dengan penjualan tertinggi dan kategori others (kategori produk lain) dimana jumlah penjualan digabungkan menjadi satu kategori yang memiliki jumlah penjualan paling sedikit. ")
st.write("- Road Bikes memiliki jumlah penjualan tertinggi yaitu sekitar 14 juta")
st.write("- Montain Bikes memiliki jumlah penjualan tertinggi ke dua sekitar 9 juta")
st.write("- Touring Bikes memiliki jumlah penjualan sekitar 5 juta")
st.write("- Tires dan Tubes memiliki jumlah penjualan sekitar 1 juta")
st.write("- Dan terakhir Kategori others memiliki jumlah penjualan lebih dari 100 ribu")

st.header("Total Revenue By Month")
st.write("Total Pendapatan dari Pelanggan tiap bulan")
st.write("Tren: Line Chart")

# Query untuk Total Revenue by Month
query_monthly_revenue = """
SELECT 
    DATE_FORMAT(di.DateFirstPurchase, '%Y-%m') AS MonthYear, 
    SUM(fis.SalesAmount) AS TotalRevenue
FROM 
    dimcustomer di
JOIN 
    factinternetsales fis ON di.CustomerKey = fis.CustomerKey
GROUP BY 
    DATE_FORMAT(di.DateFirstPurchase, '%Y-%m')
ORDER BY
    di.DateFirstPurchase
"""

df_monthly_revenue = ambil_data(query_monthly_revenue)
if df_monthly_revenue is not None:
    plt.figure(figsize=(10, 6))
    plt.plot(df_monthly_revenue['MonthYear'], df_monthly_revenue['TotalRevenue'], marker='o', color='r', linestyle='-')
    plt.title('Total Pendapatan dari Pelanggan per Bulan')
    plt.xlabel('Bulan')
    plt.ylabel('Total Pendapatan')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

st.write("Deskripsi Data Visualisasi:")
st.write("Visualisasi data tersebut menggunakan grafik Line Chart untuk menampilkan jumlah pendapatan dari pelanggan tiap bulan dengan rentang waktu 07-2001 hingga 04-2004. Terdapat komponen sumbu x menunjukkan rentang waktu bulan dan tahun pendapatan dan sumbu y menunjukkan total pendapatan. Berdasarkan gambar diketahui bahwa total pendapatan per bulan tertinggi terdapat pada bulan 12-2002 yaitu sebesar 1,2 juta (1,215,691). Kemudian total pendapatan tertinggi kedua terdapat pada bulan 04-2002 sebesar 1,1 juta (1,142,150).")

st.header("Total Sales Amount by Country")
st.write("Jumlah Penjualan Berdasarkan Negara")
st.write("Composition: Donut Chart")

# Query untuk Total Sales Amount by Country
query_sales_by_country = """
SELECT 
    dg.EnglishCountryRegionName AS Country,
    SUM(fis.SalesAmount) AS TotalSalesAmount
FROM 
    factinternetsales fis
JOIN 
    dimgeography dg ON fis.SalesTerritoryKey = dg.SalesTerritoryKey
GROUP BY 
    dg.EnglishCountryRegionName
"""

df_sales_by_country = ambil_data(query_sales_by_country)
if df_sales_by_country is not None:
    plt.figure(figsize=(10, 8))
    country_sales = df_sales_by_country['TotalSalesAmount']
    countries = df_sales_by_country['Country']
    plt.pie(country_sales, labels=countries, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title('Total Sales Amount by Country')
    plt.axis('equal')
    st.pyplot(plt)

st.write("Deskripsi Data Visualisasi:")
st.write("Visualisasi data diatas menggunakan grafik Donut Chart untuk menampilkan Jumlah Penjualan Berdasarkan Negara. Berikut penjelasan visualisasi tersebut: ")
st.write("- United State merupakan negara dengan jumlah penjulan tertinggi sekitar 50.7%. Hal ini menunjukkan bahwa lebih dari setengah total penjualan berasal dari US")
st.write("- Australia merupakan negara kedua dengan jumlah penjualan tertinggi sekitar 17.8%")
st.write("- Germany merupakan negara dengan jumlah penjualan sebesar 9.3%")
st.write("- United Kingdom merupakan negara dengan jumlah penjualan 8.8%")
st.write("- Canada merupakan negara dengan jumlah penjualan sebesar 7.1%")
st.write("- French merupakan negara dengan jumlah penjualan terendah sebesar 6.2%")

st.header("Relationship between Sales Amount and Order Quantity")
st.write("Relationship: Scatter Plot")

# Query untuk Relationship between Sales Amount and Order Quantity
query_sales_vs_order_qty = """
SELECT 
    SalesAmount,
    OrderQuantity
FROM 
    factinternetsales
"""

df_sales_vs_order_qty = ambil_data(query_sales_vs_order_qty)
if df_sales_vs_order_qty is not None:
    plt.figure(figsize=(10, 6))
    plt.scatter(df_sales_vs_order_qty['OrderQuantity'], df_sales_vs_order_qty['SalesAmount'], alpha=0.5)
    plt.xlabel('Order Quantity')
    plt.ylabel('Sales Amount')
    plt.title('Relationship between Sales Amount and Order Quantity')
    plt.grid(True)
    st.pyplot(plt)

# Load the CSV file
file_path = 'https://raw.githubusercontent.com/TegarCode/davis2024/main/imdb_combined_data2.csv'  # Sesuaikan path ini jika diperlukan
data = pd.read_csv(file_path)

# Menampilkan beberapa baris pertama DataFrame
st.write("Beberapa baris pertama dari DataFrame:")
st.write(data.head())

# Menampilkan informasi ringkasan tentang DataFrame
st.write("Informasi ringkasan tentang DataFrame:")
buffer = StringIO()
data.info(buf=buffer)
info_str = buffer.getvalue()
st.text(info_str)

# Menampilkan ringkasan statistik dari DataFrame
st.write("Ringkasan statistik dari DataFrame:")
st.write(data.describe())

# Grafik Perbandingan: Total Gross Worldwide per Tahun
st.write("Grafik Perbandingan: Total Gross Worldwide per Tahun")
fig, ax = plt.subplots(figsize=(10, 6))
data.groupby('Year')['Gross_World'].sum().plot(kind='bar', ax=ax)
ax.set_xlabel('Tahun')
ax.set_ylabel('Total Gross Worldwide')
ax.set_title('Total Gross Worldwide per Tahun')
st.pyplot(fig)

# Grafik Tren: Rating IMDb dari Waktu ke Waktu
st.write("Grafik Tren: Rating IMDb dari Waktu ke Waktu")
fig, ax = plt.subplots(figsize=(10, 6))
data.groupby('Year')['IMDB_Rating'].mean().plot(kind='line', marker='o', ax=ax)
ax.set_xlabel('Tahun')
ax.set_ylabel('Rata-rata Rating IMDb')
ax.set_title('Rata-rata Rating IMDb dari Waktu ke Waktu')
st.pyplot(fig)

# Grafik Komposisi: Distribusi Genre
st.write("Grafik Komposisi: Distribusi Genre")
fig, ax = plt.subplots(figsize=(10, 6))
data['Genre'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
ax.set_ylabel('')
ax.set_title('Distribusi Genre')
st.pyplot(fig)

# Grafik Hubungan: Rating IMDb vs Pendapatan
st.write("Grafik Hubungan: Rating IMDb vs Pendapatan")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(data['IMDB_Rating'], data['Gross_World'], alpha=0.5)
ax.set_xlabel('Rating IMDb')
ax.set_ylabel('Gross Worldwide')
ax.set_title('Rating IMDb vs Gross Worldwide')
st.pyplot(fig)

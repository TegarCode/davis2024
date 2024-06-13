import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import squarify
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

# Query untuk mendapatkan data penjualan per wilayah
query_penjualan_per_wilayah = """
SELECT st.SalesTerritoryRegion AS Region, SUM(fs.SalesAmount) AS TotalSales
FROM factinternetsales fs
JOIN dimsalesterritory st ON fs.SalesTerritoryKey = st.SalesTerritoryKey
GROUP BY st.SalesTerritoryRegion;
"""

# Query untuk mendapatkan distribusi usia pelanggan
query_distribusi_usia_pelanggan = """
SELECT YEAR(dc.DateFirstPurchase) - YEAR(dc.BirthDate) AS Age
FROM dimcustomer dc
WHERE dc.BirthDate IS NOT NULL;
"""

# Query untuk mendapatkan hubungan antara mountain bikes dan spareparts yang terjual
query_mountain_bike_spareparts = """
WITH MountainBikeSales AS (
    SELECT fs.SalesOrderNumber, fs.ProductKey AS BikeProductKey
    FROM factinternetsales fs
    JOIN dimproduct bikeProduct ON fs.ProductKey = bikeProduct.ProductKey
    JOIN dimproductsubcategory bikeSubcategory ON bikeProduct.ProductSubcategoryKey = bikeSubcategory.ProductSubcategoryKey
    JOIN dimproductcategory bikeCategory ON bikeSubcategory.ProductCategoryKey = bikeCategory.ProductCategoryKey
    WHERE bikeCategory.EnglishProductCategoryName = 'Bikes'
    AND bikeSubcategory.EnglishProductSubcategoryName = 'Mountain Bikes'
),
SparepartSales AS (
    SELECT fs.SalesOrderNumber, fs.ProductKey AS PartProductKey, partSubcategory.EnglishProductSubcategoryName AS SparepartType
    FROM factinternetsales fs
    JOIN dimproduct partProduct ON fs.ProductKey = partProduct.ProductKey
    JOIN dimproductsubcategory partSubcategory ON partProduct.ProductSubcategoryKey = partSubcategory.ProductSubcategoryKey
    JOIN dimproductcategory partCategory ON partSubcategory.ProductCategoryKey = partCategory.ProductCategoryKey
    WHERE partCategory.EnglishProductCategoryName IN ('Accessories', 'Components')
)
SELECT ss.SparepartType, COUNT(ss.SalesOrderNumber) AS TotalSales
FROM MountainBikeSales mb
JOIN SparepartSales ss ON mb.SalesOrderNumber = ss.SalesOrderNumber
GROUP BY ss.SparepartType
ORDER BY TotalSales DESC;
"""

st.title('Analisis Data dengan Streamlit dan MySQL')

# Bagian untuk visualisasi penjualan per wilayah
st.header('Distribusi Penjualan per Wilayah')
df_penjualan_per_wilayah = ambil_data(query_penjualan_per_wilayah)
if df_penjualan_per_wilayah is not None:
    st.bar_chart(df_penjualan_per_wilayah.set_index('Region'))

    # Membuat tree map chart
    st.write("Komposisi Penjualan per Wilayah")
    plt.figure(figsize=(12, 8))
    squarify.plot(sizes=df_penjualan_per_wilayah['TotalSales'], 
                  label=df_penjualan_per_wilayah['Region'], 
                  alpha=.8, 
                  color=plt.cm.Paired.colors)
    plt.title('Komposisi Penjualan per Wilayah')
    plt.axis('off')  # mematikan sumbu
    st.pyplot(plt)

# Bagian untuk distribusi usia pelanggan
st.header('Distribusi Usia Pelanggan')
df_distribusi_usia_pelanggan = ambil_data(query_distribusi_usia_pelanggan)
if df_distribusi_usia_pelanggan is not None:
    plt.figure(figsize=(10, 6))
    sns.histplot(df_distribusi_usia_pelanggan['Age'], bins=20, kde=True)
    plt.title('Distribusi Usia Pelanggan')
    plt.xlabel('Usia')
    plt.ylabel('Frekuensi')
    st.pyplot(plt)

# Bagian untuk hubungan antara mountain bikes dan spareparts
st.header('Penjualan Mountain Bike dan Spareparts')
df_mountain_bike_spareparts = ambil_data(query_mountain_bike_spareparts)
if df_mountain_bike_spareparts is not None:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_mountain_bike_spareparts, x='SparepartType', y='TotalSales')
    plt.title('Penjualan Mountain Bike dan Spareparts')
    plt.xlabel('Tipe Sparepart')
    plt.ylabel('Total Penjualan')
    plt.xticks(rotation=45)
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

# Grafik Distribusi: Distribusi Gross Worldwide
st.write("Grafik Distribusi: Distribusi Gross Worldwide")
fig, ax = plt.subplots(figsize=(10, 6))
data['Gross_World'].plot(kind='hist', bins=30, color='skyblue', ax=ax)
ax.set_xlabel('Gross Worldwide')
ax.set_ylabel('Frekuensi')
ax.set_title('Distribusi Gross Worldwide')
st.pyplot(fig)

# Grafik Komposisi: Komposisi Gross Worldwide berdasarkan Rating (Donut Chart)
st.write("Grafik Komposisi: Komposisi Gross Worldwide berdasarkan Rating")
gross_composition = data.groupby('Rating')['Gross_World'].sum()
fig, ax = plt.subplots(figsize=(10, 6))
wedges, texts, autotexts = ax.pie(gross_composition, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors, wedgeprops=dict(width=0.3))
ax.set_ylabel('')
ax.set_title('Komposisi Gross Worldwide berdasarkan Rating')
for text in texts + autotexts:
    text.set_color('black')
st.pyplot(fig)

# Grafik Hubungan: Budget vs. Gross Worldwide
st.write("Grafik Hubungan: Budget vs. Gross Worldwide")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(data['Budget'], data['Gross_World'], alpha=0.5)
ax.set_xlabel('Budget')
ax.set_ylabel('Gross Worldwide')
ax.set_title('Hubungan antara Budget dan Gross Worldwide')
st.pyplot(fig)

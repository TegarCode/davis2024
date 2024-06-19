import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import squarify
from io import StringIO
import os
from gtts import gTTS

# Fungsi untuk membuat koneksi ke database
def create_connection():
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
        st.error(f"Error connecting to database: {e}")
        return None

# Fungsi untuk menjalankan query dan mendapatkan data
def fetch_data(query):
    connection = create_connection()
    if connection is None:
        return None
    try:
        df = pd.read_sql_query(query, connection)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        connection.close()

# Fungsi untuk mengubah teks menjadi audio
def text_to_audio(text, filename):
    tts = gTTS(text, lang='id')
    tts.save(filename)

# Query untuk mendapatkan data penjualan per wilayah
query_sales_per_territory = """
SELECT st.SalesTerritoryRegion AS Region, SUM(fs.SalesAmount) AS TotalSales
FROM factinternetsales fs
JOIN dimsalesterritory st ON fs.SalesTerritoryKey = st.SalesTerritoryKey
GROUP BY st.SalesTerritoryRegion;
"""

# Query untuk mendapatkan distribusi usia pelanggan
query_customer_age_distribution = """
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

st.title('Data Analysis with Streamlit and MySQL')

# Bagian untuk visualisasi penjualan per wilayah
st.header('Distribusi Penjualan per Wilayah')
penjelasan_territory = """
Grafik batang ini menunjukkan distribusi penjualan di setiap wilayah. 
Setiap batang mewakili satu wilayah, dan tinggi batang menunjukkan jumlah total penjualan di wilayah tersebut. 
Ini membantu memahami bagaimana penjualan terdistribusi di berbagai wilayah geografis, yang dapat mempengaruhi pengambilan keputusan strategis.
"""
st.markdown(penjelasan_territory)
audio_territory = "audio_territory.mp3"
if not os.path.exists(audio_territory):
    text_to_audio(penjelasan_territory, audio_territory)
if st.button("Dengarkan Penjelasan Distribusi Penjualan per Wilayah"):
    audio_file = open(audio_territory, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

df_sales_per_territory = fetch_data(query_sales_per_territory)
if df_sales_per_territory is not None:
    st.bar_chart(df_sales_per_territory.set_index('Region'))

    # Membuat tree map chart
    st.write("Komposisi Penjualan per Wilayah")
    penjelasan_treemap = """
    Treemap ini menampilkan komposisi penjualan di setiap wilayah. 
    Luas setiap kotak sebanding dengan total penjualan di wilayah tersebut, sehingga memberikan visualisasi yang jelas mengenai proporsi penjualan antar wilayah. 
    Ini berguna untuk mengidentifikasi wilayah dengan performa penjualan tertinggi dan terendah.
    """
    st.markdown(penjelasan_treemap)
    audio_treemap = "audio_treemap.mp3"
    if not os.path.exists(audio_treemap):
        text_to_audio(penjelasan_treemap, audio_treemap)
    if st.button("Dengarkan Penjelasan Komposisi Penjualan per Wilayah"):
        audio_file = open(audio_treemap, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

    plt.figure(figsize=(12, 8))
    squarify.plot(sizes=df_sales_per_territory['TotalSales'], 
                  label=df_sales_per_territory['Region'], 
                  alpha=.8,
                  color=sns.color_palette("Spectral", len(df_sales_per_territory)),
                  ax=ax)
    ax.set_title('Komposisi Penjualan per Wilayah')
    ax.axis('off')  # turn off the axis
    st.pyplot(fig)

# Bagian untuk distribusi usia pelanggan
st.header('Distribusi Usia Pelanggan')
penjelasan_age_distribution = """
Histogram ini menampilkan distribusi usia pelanggan berdasarkan data tanggal lahir dan tanggal pembelian pertama mereka. 
Sumbu x mewakili usia pelanggan, sedangkan sumbu y menunjukkan frekuensi atau jumlah pelanggan pada rentang usia tertentu. 
Analisis ini penting untuk segmentasi pasar dan strategi pemasaran yang lebih efektif.
"""
st.markdown(penjelasan_age_distribution)
audio_age_distribution = "audio_age_distribution.mp3"
if not os.path.exists(audio_age_distribution):
    text_to_audio(penjelasan_age_distribution, audio_age_distribution)
if st.button("Dengarkan Penjelasan Distribusi Usia Pelanggan"):
    audio_file = open(audio_age_distribution, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

df_customer_age_distribution = fetch_data(query_customer_age_distribution)
if df_customer_age_distribution is not None:
    plt.figure(figsize=(10, 6))
    sns.histplot(df_customer_age_distribution['Age'], bins=20, kde=True)
    plt.title('Distribusi Usia Pelanggan')
    plt.xlabel('Usia')
    plt.ylabel('Frekuensi')
    st.pyplot(plt)

# Bagian untuk hubungan antara mountain bikes dan spareparts
st.header('Penjualan Mountain Bike dan Spareparts')
penjelasan_mountain_bike = """
Bubble plot ini menunjukkan hubungan antara penjualan mountain bike dan berbagai jenis spareparts yang terjual bersamaan. 
Setiap lingkaran mewakili satu jenis sparepart, dan ukurannya menunjukkan jumlah total penjualan sparepart tersebut yang terjadi bersamaan dengan penjualan mountain bike. 
Analisis ini memberikan wawasan tentang preferensi pelanggan dalam pembelian produk terkait, yang bisa digunakan untuk promosi bundling atau cross-selling.
"""
st.markdown(penjelasan_mountain_bike)
audio_mountain_bike = "audio_mountain_bike.mp3"
if not os.path.exists(audio_mountain_bike):
    text_to_audio(penjelasan_mountain_bike, audio_mountain_bike)
if st.button("Dengarkan Penjelasan Penjualan Mountain Bike dan Spareparts"):
    audio_file = open(audio_mountain_bike, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

df_mountain_bike_spareparts = fetch_data(query_mountain_bike_spareparts)
if df_mountain_bike_spareparts is not None:
    plt.figure(figsize=(10, 6))
    plt.scatter(data=df_mountain_bike_spareparts, x='SparepartType', y='TotalSales', s=df_mountain_bike_spareparts['TotalSales']*10, alpha=0.5)
    plt.title('Penjualan Mountain Bike dan Spareparts')
    plt.xlabel('Jenis Sparepart')
    plt.ylabel('Total Penjualan')
    plt.xticks(rotation=45)
    st.pyplot(plt)

# Bagian untuk analisis data IMDb
st.header('Analisis Data IMDb')
penjelasan_imdb = """
Analisis ini menggunakan data IMDb untuk memberikan wawasan tentang pendapatan kotor global dari film berdasarkan tahun, distribusi pendapatan, dan komposisi pendapatan berdasarkan rating.
Selain itu, juga menunjukkan hubungan antara anggaran produksi dan pendapatan kotor film.
"""
st.markdown(penjelasan_imdb)
audio_imdb = "audio_imdb.mp3"
if not os.path.exists(audio_imdb):
    text_to_audio(penjelasan_imdb, audio_imdb)
if st.button("Dengarkan Penjelasan Analisis Data IMDb"):
    audio_file = open(audio_imdb, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')


# Load the CSV file
file_path = 'https://raw.githubusercontent.com/TegarCode/davis2024/main/imdb_combined_data2.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the DataFrame
st.write("First few rows of the DataFrame:")
st.write(data.head())

# Display summary information about the DataFrame
st.write("Summary information about the DataFrame:")
buffer = StringIO()
data.info(buf=buffer)
info_str = buffer.getvalue()
st.text(info_str)

# Display statistical summary of the DataFrame
st.write("Statistical summary of the DataFrame:")
st.write(data.describe())

# Comparison Plot: Total Gross Worldwide per Year
st.write("Comparison Plot: Total Gross Worldwide per Year")
penjelasan_gross_per_year = """
Grafik batang ini menunjukkan total pendapatan kotor global dari film-film yang dirilis setiap tahun. 
Setiap batang mewakili satu tahun, dan tinggi batang menunjukkan jumlah total pendapatan kotor dari semua film yang dirilis pada tahun tersebut. 
Grafik ini membantu dalam mengidentifikasi tren pendapatan film dari waktu ke waktu.
"""
st.markdown(penjelasan_gross_per_year)
audio_gross_per_year = "audio_gross_per_year.mp3"
if not os.path.exists(audio_gross_per_year):
    text_to_audio(penjelasan_gross_per_year, audio_gross_per_year)
if st.button("Dengarkan Penjelasan Total Gross Worldwide per Year"):
    audio_file = open(audio_gross_per_year, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

fig, ax = plt.subplots(figsize=(10, 6))
data.groupby('Year')['Gross_World'].sum().plot(kind='bar', ax=ax)
ax.set_xlabel('Year')
ax.set_ylabel('Total Gross Worldwide')
ax.set_title('Total Gross Worldwide per Year')
st.pyplot(fig)

# Distribution Plot: Distribution of Gross Worldwide
st.write("Distribution Plot: Distribution of Gross Worldwide")
penjelasan_distribution_gross = """
Histogram ini menampilkan distribusi pendapatan kotor global dari film-film. 
Sumbu x mewakili pendapatan kotor, sementara sumbu y menunjukkan frekuensi atau jumlah film dalam rentang pendapatan tertentu. 
Grafik ini membantu memahami pola distribusi pendapatan film dan mengidentifikasi rentang pendapatan yang paling umum.
"""
st.markdown(penjelasan_distribution_gross)
audio_distribution_gross = "audio_distribution_gross.mp3"
if not os.path.exists(audio_distribution_gross):
    text_to_audio(penjelasan_distribution_gross, audio_distribution_gross)
if st.button("Dengarkan Penjelasan Distribusi Gross Worldwide"):
    audio_file = open(audio_distribution_gross, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

fig, ax = plt.subplots(figsize=(10, 6))
data['Gross_World'].plot(kind='hist', bins=30, color='skyblue', ax=ax)
ax.set_xlabel('Gross Worldwide')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Gross Worldwide')
st.pyplot(fig)

# Composition Plot: Gross Worldwide composition by Rating
st.write("Composition Plot: Gross Worldwide composition by Rating")
penjelasan_gross_composition = """
Donut chart ini menampilkan komposisi pendapatan kotor global dari film berdasarkan rating. 
Setiap bagian mewakili satu rating, dan ukuran bagian menunjukkan proporsi pendapatan kotor yang dihasilkan oleh film-film dengan rating tersebut. 
Grafik ini memberikan wawasan tentang kontribusi masing-masing rating terhadap total pendapatan kotor.
"""
st.markdown(penjelasan_gross_composition)
audio_gross_composition = "audio_gross_composition.mp3"
if not os.path.exists(audio_gross_composition):
    text_to_audio(penjelasan_gross_composition, audio_gross_composition)
if st.button("Dengarkan Penjelasan Komposisi Gross Worldwide berdasarkan Rating"):
    audio_file = open(audio_gross_composition, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

gross_composition = data.groupby('Rating')['Gross_World'].sum()
fig, ax = plt.subplots(figsize=(10, 6))
ax.pie(gross_composition, labels=gross_composition.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors, wedgeprops=dict(width=0.3))
ax.set_title('Komposisi Gross Worldwide berdasarkan Rating')
st.pyplot(fig)

# Relationship Plot: Budget vs. Gross Worldwide
st.write("Plot Hubungan: Budget vs. Gross Worldwide")
penjelasan_budget_vs_gross = """
Scatter plot ini menunjukkan hubungan antara anggaran produksi film dan pendapatan kotor di seluruh dunia. 
Setiap titik mewakili satu film, dengan sumbu x menunjukkan anggaran produksi dan sumbu y menunjukkan pendapatan kotor. 
Grafik ini membantu dalam mengidentifikasi korelasi antara anggaran dan pendapatan, serta mengidentifikasi film-film yang berhasil menghasilkan pendapatan tinggi dengan anggaran rendah atau sebaliknya.
"""
st.markdown(penjelasan_budget_vs_gross)
audio_budget_vs_gross = "audio_budget_vs_gross.mp3"
if not os.path.exists(audio_budget_vs_gross):
    text_to_audio(penjelasan_budget_vs_gross, audio_budget_vs_gross)
if st.button("Dengarkan Penjelasan Hubungan antara Budget dan Gross Worldwide"):
    audio_file = open(audio_budget_vs_gross, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(data['Budget'], data['Gross_World'], alpha=0.5)
ax.set_xlabel('Budget')
ax.set_ylabel('Gross Worldwide')
ax.set_title('Hubungan antara Budget dan Gross Worldwide')
st.pyplot(fig)

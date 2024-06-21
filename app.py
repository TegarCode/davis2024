import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import plotly.express as px
from io import StringIO
import os
from gtts import gTTS



st.sidebar.title("Menu Navigasi")
page = st.sidebar.selectbox("Pilih Halaman", ["Analisis Data Database", "Analisis Data IMDb"])


if page == "Analisis Data Database":
    st.title('Final Project Data Analysis with Streamlit and MySQL')
    st.title('Tegar Oktavianto Simbolon')
    st.title('21082010140')

    st.title('Analisis Data dari Database')
    # Fungsi untuk membuat koneksi ke database

    # Fungsi untuk membuat koneksi ke database menggunakan Streamlit secrets
    def create_connection():
        try:
            connection = pymysql.connect(
                host=st.secrets["connections_mydb"]["host"],
                port=st.secrets["connections_mydb"]["port"],
                user=st.secrets["connections_mydb"]["user"],
                password=st.secrets["connections_mydb"]["password"],
                database=st.secrets["connections_mydb"]["database"]
            )
            return connection
        except Exception as e:
            st.error(f"Error connecting to database: {e}")
            return None

# Contoh penggunaan koneksi
connection = create_connection()
if connection:
    st.success("Koneksi berhasil!")


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


    # Bagian untuk visualisasi penjualan per wilayah
    st.header('Perbandingan Penjualan per Wilayah')

    df_sales_per_territory = fetch_data(query_sales_per_territory)
    if df_sales_per_territory is not None:
        # Menggunakan plotly untuk grafik bar interaktif
        fig_bar = px.bar(df_sales_per_territory, x='Region', y='TotalSales',
                        color='TotalSales', color_continuous_scale='Viridis',
                        labels={'TotalSales': 'Total Penjualan', 'Region': 'Wilayah'},
                        title='Distribusi Penjualan per Wilayah')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Penjelasan dan audio
        penjelasan_territory = """
        Grafik batang ini menunjukkan perbandingan penjualan di setiap wilayah. 
        Setiap batang mewakili satu wilayah, dan tinggi batang menunjukkan jumlah total penjualan di wilayah tersebut. 
        Ini membantu memahami bagaimana penjualan terdistribusi di berbagai wilayah geografis, yang dapat mempengaruhi pengambilan keputusan strategis. Visualisasi ini penting untuk melihat
        dan menyampaikan sebaran penjualan dari toko di setiap wilayah terutama negara, hal ini dapat membantu kita sebagai
        audience memahami tingkat popularitas toko tersebut disuatu negara terutama bila dinegara sendiri
        """
        st.markdown(penjelasan_territory)
        audio_territory = "audio_territory.mp3"
        if not os.path.exists(audio_territory):
            text_to_audio(penjelasan_territory, audio_territory)
        if st.button("Dengarkan Penjelasan Distribusi Penjualan per Wilayah"):
            audio_file = open(audio_territory, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')

        # Membuat tree map chart
        st.write("Komposisi Penjualan per Wilayah")
        fig_treemap = px.treemap(df_sales_per_territory, path=['Region'], values='TotalSales',
                                color='TotalSales', color_continuous_scale='RdBu',
                                title='Komposisi Penjualan per Wilayah')
        st.plotly_chart(fig_treemap, use_container_width=True)

        # Penjelasan dan audio
        penjelasan_treemap = """
        Treemap ini menampilkan komposisi penjualan di setiap wilayah. 
        Luas setiap kotak sebanding dengan total penjualan di wilayah tersebut, sehingga memberikan visualisasi yang jelas mengenai proporsi penjualan antar wilayah. 
        Ini berguna untuk mengidentifikasi wilayah dengan performa penjualan tertinggi dan terendah. Dari sini kita dapat mengetahui bahwa
        Australia memiliki performa penjualan yang baik mungkin karena Australia memiliki wilayah yang luas tetapi wilayah yang dapat dihuni
        tidak sampai 1/4nya kota kota di Australia sangat jauh akan tetapi setiap kotanya merupakan kota metropolitan karna itu penjualan disana untuk produk 
        speda dll sangat diminati
        """
        st.markdown(penjelasan_treemap)
        audio_treemap = "audio_treemap.mp3"
        if not os.path.exists(audio_treemap):
            text_to_audio(penjelasan_treemap, audio_treemap)
        if st.button("Dengarkan Penjelasan Komposisi Penjualan per Wilayah"):
            audio_file = open(audio_treemap, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')

    # Bagian untuk distribusi usia pelanggan
    st.header('Distribusi Usia Pelanggan')

    df_customer_age_distribution = fetch_data(query_customer_age_distribution)
    if df_customer_age_distribution is not None:
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.histplot(df_customer_age_distribution['Age'], bins=20, kde=True, ax=ax)
        ax.set_title('Distribusi Usia Pelanggan', fontsize=16)
        ax.set_xlabel('Usia', fontsize=14)
        ax.set_ylabel('Frekuensi', fontsize=14)
        st.pyplot(fig)

        # Penjelasan dan audio
        penjelasan_age_distribution = """
        Histogram ini menampilkan distribusi usia pelanggan berdasarkan data tanggal lahir dan tanggal pembelian pertama mereka. 
        Sumbu x mewakili usia pelanggan, sedangkan sumbu y menunjukkan frekuensi atau jumlah pelanggan pada rentang usia tertentu. 
        Analisis ini penting untuk segmentasi pasar dan strategi pemasaran yang lebih efektif. Dilihat dari grafiknya usia paling banyak 
        mengkonsumsi produk ini berasal dari orang dewasa diatas 40. Data diambil dari tanggal lahir pelanggan dan data terakhir penjualan tercatat.
        karena tidak terdapat keterangan apakah pembeli masih aktif membeli atau tidak jadi terdapat data yang sedikit aneh dmna usia tertinggi
        pelanggan mencapai 120 tahun jadi butuh evaluasi tenatng sistem pencatan pembelian agar data umur dapat terpresentasi dengan baik
        """
        st.markdown(penjelasan_age_distribution)
        audio_age_distribution = "audio_age_distribution.mp3"
        if not os.path.exists(audio_age_distribution):
            text_to_audio(penjelasan_age_distribution, audio_age_distribution)
        if st.button("Dengarkan Penjelasan Distribusi Usia Pelanggan"):
            audio_file = open(audio_age_distribution, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')

    # Bagian untuk hubungan antara mountain bikes dan spareparts
    st.header('Penjualan Mountain Bike dan Spareparts')

    df_mountain_bike_spareparts = fetch_data(query_mountain_bike_spareparts)
    if df_mountain_bike_spareparts is not None:
        fig_bubble = px.scatter(df_mountain_bike_spareparts, x='SparepartType', y='TotalSales',
                                size='TotalSales', color='SparepartType',
                                labels={'TotalSales': 'Total Penjualan', 'SparepartType': 'Jenis Sparepart'},
                                title='Penjualan Mountain Bike dan Spareparts')
        fig_bubble.update_layout(xaxis_title='Jenis Sparepart', yaxis_title='Total Penjualan')
        st.plotly_chart(fig_bubble, use_container_width=True)

        # Penjelasan dan audio
        penjelasan_mountain_bike = """
        Bubble plot ini menunjukkan hubungan antara penjualan mountain bike dan berbagai jenis spareparts yang terjual bersamaan. 
        Setiap lingkaran mewakili satu jenis sparepart, dan ukurannya menunjukkan jumlah total penjualan sparepart tersebut yang terjadi bersamaan dengan penjualan mountain bike. 
        Analisis ini memberikan wawasan tentang preferensi pelanggan dalam pembelian produk terkait, yang bisa digunakan untuk promosi bundling atau cross-selling. Jika teliti 
        data tersebut menunjukkan produk sparepart yang paling banyak dikonsumsi oleh pengguna sepeda gunung kita bisa mengesampingkan Bottle and Cages dan juga Tires karena sparepart
        tersebut memang memiliki masa pakai yang relatif singkat. Disini Helmet dan Fenders menjadi acuan kita karena helmet dibutuhkan untuk safety ketika offroad menggunakan speda gunung,
        Sementara Fenders sering kali rusak karena pengguna sepeda gunung kerap kali jatuh saat melakukan offroad
        """
        st.markdown(penjelasan_mountain_bike)
        audio_mountain_bike = "audio_mountain_bike.mp3"
        if not os.path.exists(audio_mountain_bike):
            text_to_audio(penjelasan_mountain_bike, audio_mountain_bike)
        if st.button("Dengarkan Penjelasan Penjualan Mountain Bike dan Spareparts"):
            audio_file = open(audio_mountain_bike, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mp3')




elif page == "Analisis Data IMDb":
    st.title('Final Project Data Analysis with Streamlit and MySQL')
    st.title('Tegar Oktavianto Simbolon')
    st.title('21082010140')

    st.title('Data Analysis with Streamlit and IMDb Data')

    # Bagian untuk analisis data IMDb
    st.header('Analisis Data IMDb')

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
    gross_per_year = data.groupby('Year')['Gross_World'].sum().reset_index()
    fig_bar = px.bar(gross_per_year, x='Year', y='Gross_World', 
                    labels={'Gross_World': 'Total Gross Worldwide', 'Year': 'Year'}, 
                    title='Total Gross Worldwide per Year',
                    color='Gross_World', color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, use_container_width=True)

    penjelasan_gross_per_year = """
    Grafik batang ini menunjukkan total pendapatan kotor global dari film-film yang dirilis setiap tahun. 
    Setiap batang mewakili satu tahun, dan tinggi batang menunjukkan jumlah total pendapatan kotor dari semua film yang dirilis pada tahun tersebut. 
    Grafik ini membantu dalam mengidentifikasi tren pendapatan film dari waktu ke waktu. Kita bisa melihat pendapata kotor yang paling banyak didapat dan 
    dikonsumsi dari film terlaris itu berasal dari tahun berapa.
    """
    st.markdown(penjelasan_gross_per_year)
    audio_gross_per_year = "audio_gross_per_year.mp3"
    if not os.path.exists(audio_gross_per_year):
        text_to_audio(penjelasan_gross_per_year, audio_gross_per_year)
    if st.button("Dengarkan Penjelasan Total Gross Worldwide per Year"):
        audio_file = open(audio_gross_per_year, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

    # Distribution Plot: Distribution of Gross Worldwide
    st.write("Distribution Plot: Distribution of Gross Worldwide")
    fig_hist = px.histogram(data, x='Gross_World', nbins=30, 
                            labels={'Gross_World': 'Gross Worldwide'}, 
                            title='Distribution of Gross Worldwide',
                            color_discrete_sequence=['skyblue'])
    st.plotly_chart(fig_hist, use_container_width=True)

    penjelasan_distribution_gross = """
    Histogram ini menampilkan distribusi pendapatan kotor global dari film-film. 
    Sumbu x mewakili pendapatan kotor, sementara sumbu y menunjukkan frekuensi atau jumlah film dalam rentang pendapatan tertentu. 
    Grafik ini membantu memahami pola distribusi pendapatan film dan mengidentifikasi rentang pendapatan yang paling umum. Kita dapat melihat
    pendapatan kotor dalam rentang pendapatan tertentu dari film-film terlaris yang tercatat di IMDB ada berapa banyak misal pada rentang 1.1-1.150 B 
    hanya terrcatat 1 film yang berhasil mencapainya
    """
    st.markdown(penjelasan_distribution_gross)
    audio_distribution_gross = "audio_distribution_gross.mp3"
    if not os.path.exists(audio_distribution_gross):
        text_to_audio(penjelasan_distribution_gross, audio_distribution_gross)
    if st.button("Dengarkan Penjelasan Distribusi Gross Worldwide"):
        audio_file = open(audio_distribution_gross, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

    # Composition Plot: Gross Worldwide composition by Rating
    st.write("Composition Plot: Gross Worldwide composition by Rating")
    gross_composition = data.groupby('Rating')['Gross_World'].sum().reset_index()
    fig_pie = px.pie(gross_composition, names='Rating', values='Gross_World', 
                    title='Komposisi Gross Worldwide berdasarkan Rating',
                    color_discrete_sequence=px.colors.qualitative.Set3, hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

    penjelasan_gross_composition = """
    Donut chart ini menampilkan komposisi pendapatan kotor global dari film berdasarkan rating. 
    Setiap bagian mewakili satu rating, dan ukuran bagian menunjukkan proporsi pendapatan kotor yang dihasilkan oleh film-film dengan rating tersebut. 
    Grafik ini memberikan wawasan tentang kontribusi masing-masing rating terhadap total pendapatan kotor. Kita lihat rata-rata penghimpun
    pendapatan kotor itu berasal dari film dengan Rating R dimana rating R merupakan Dibatasi, Anak-Anak di Bawah 17 Tahun Wajib didampingi Orang Tua atau Wali Dewasa. 
    Rating ini berarti film tersebut mengandung materi dewasa seperti aktivitas dewasa, bahasa kasar, kekerasan grafis yang intens, penyalahgunaan narkoba.
    """
    st.markdown(penjelasan_gross_composition)
    audio_gross_composition = "audio_gross_composition.mp3"
    if not os.path.exists(audio_gross_composition):
        text_to_audio(penjelasan_gross_composition, audio_gross_composition)
    if st.button("Dengarkan Penjelasan Komposisi Gross Worldwide berdasarkan Rating"):
        audio_file = open(audio_gross_composition, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')

    # Relationship Plot: Budget vs. Gross Worldwide
    st.write("Plot Hubungan: Budget vs. Gross Worldwide")
    fig_scatter = px.scatter(data, x='Budget', y='Gross_World', 
                            labels={'Budget': 'Budget', 'Gross_World': 'Gross Worldwide'}, 
                            title='Hubungan antara Budget dan Gross Worldwide',
                            color='Gross_World', color_continuous_scale='Viridis', size='Gross_World')
    st.plotly_chart(fig_scatter, use_container_width=True)

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

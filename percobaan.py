import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sqlalchemy import create_engine
import pymysql
import random
import squarify
from io import StringIO
import os
from gtts import gTTS


# Fungsi untuk mengambil data dari dataset IMDB Movies
def load_data_imdb(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        st.error(f"Error loading IMDB Movies dataset: {e}")
        return None

# Main function to set up the Streamlit app
def main():
    
    # Sidebar untuk memilih dataset
    dataset_choice = st.sidebar.radio("Pilih Dataset", ("Adventure Works", "IMDb top Movies"))
    

    if dataset_choice == "Adventure Works":
        st.markdown("<h1 style='text-align: center;'>Dashboard Adventure Works📝</h1>", unsafe_allow_html=True)
        
        # Visualisasi untuk AdventureWorks
        st.header("Sales Amount by Product Sub Category")
        st.write("Jumlah Penjualan Berdasarkan SubKategori Produk")
        st.write("Comparison: Bar Chart")
        
        # SQLAlchemy connection and query for bar chart
        try:
            dialect = st.secrets['connections.mydb.dialect']
            driver = st.secrets['connections.mydb.driver']
            host = st.secrets['connections.mydb.host']
            port = st.secrets['connections.mydb.port']
            user = st.secrets['connections.mydb.user']
            password = st.secrets['connections.mydb.password']
            database = st.secrets['connections.mydb.database']    
            # Buat URL koneksi untuk SQLAlchemy
            engine = f"{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}"
                
            # SQL query to fetch the required data for bar chart
            bar_chart_query = """
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
            
            # Fetch the data into a pandas DataFrame
            df_viz = pd.read_sql(bar_chart_query, engine)
    
            # Determine the top 7 categories and group the rest into 'Others'
            top_n = 7
            top_categories = df_viz.nlargest(top_n, 'SalesAmount')
            others = pd.DataFrame({
                'ProductSubCategory': ['Others'],
                'SalesAmount': [df_viz['SalesAmount'][~df_viz['ProductSubCategory'].isin(top_categories['ProductSubCategory'])].sum()]
            })
        
            # Combine the top categories with the 'Others' category
            df_viz_combined = pd.concat([top_categories, others], ignore_index=True)
            
            # Plotting the bar chart using seaborn
            plt.figure(figsize=(14, 7))
            sns.barplot(data=df_viz_combined, x='SalesAmount', y='ProductSubCategory', palette='viridis')
            plt.title('Sales Amount by Product Sub Category')
            plt.xlabel('Sales Amount')
            plt.ylabel('Product Sub Category')
            plt.tight_layout()
    
            # Display the plot in Streamlit
            st.pyplot(plt)
            
            st.markdown("""
            <div style='text-align: justify;'>
            <b>Deskripsi Data Visualisasi:</b> <br>
            Visualisasi data tersebut menggunakan Grafik Bar Chart dengan menampilkan jumlah penjualan berdasarkan sub category product dari data AdventureWorks. Grafik tersebut terdiri antara sumbu x sebagai 'Sales Amount' (jumlah penjualan) dan sumbu y sebagai 'Product Sub Category'. Terdapat 8 subcategory dengan penjualan tertinggi dan kategori others (kategori produk lain) dimana jumlah penjualan digabungkan menjadi satu kategori yang memiliki jumlah penjualan paling sedikit.
            </div>
            """, unsafe_allow_html=True)
    
            st.markdown("""
            <div style='text-align: justify;'>
            <ul>
            <li>Road Bikes memiliki jumlah penjualan tertinggi yaitu sekitar 14 juta</li>
            <li>Montain Bikes memiliki jumlah penjualan tertinggi ke dua sekitar 9 juta</li>
            <li>Touring Bikes memiliki jumlah penjualan sekitar 5 juta</li>
            <li>Tires dan Tubes memiliki jumlah penjualan sekitar 1 juta</li>
            <li>Dan terakhir Kategori others memiliki jumlah penjualan lebih dari 100 ribu</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")

        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal
        
        st.header("Total Sales Amount by Country")
        st.write("Jumlah Penjualan Berdasarkan Negara")
        st.write("Composition: Donut Chart")
        
        # SQLAlchemy connection and query for donut chart
        try:
            # SQL query to fetch the required data for donut chart
            donut_chart_query = """
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
        
            # Fetch the data into a pandas DataFrame
            df_country = pd.read_sql(donut_chart_query, engine)
            
            # Plotting the donut chart using matplotlib
            plt.figure(figsize=(10, 8))
            country_sales = df_country['TotalSalesAmount']
            countries = df_country['Country']
            plt.pie(country_sales, labels=countries, autopct='%1.1f%%', startangle=90)
            # Draw a circle at the center of pie to make it a donut
            centre_circle = plt.Circle((0, 0), 0.70, fc='white')
            fig = plt.gcf()
            fig.gca().add_artist(centre_circle)
            plt.title('Total Sales Amount by Country')
            plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            
            # Display the plot in Streamlit
            st.pyplot(plt)

            st.markdown("""
            <div style='text-align: justify;'>
            <b>Deskripsi Data Visualisasi:</b> <br>
            Visualisasi data diatas menggunakan grafik Donut Chart untuk menampilkan Jumlah Penjualan Berdasarkan Negara. Berikut penjelasan visualisasi tersebut: 
            <ul>
            <li>United State merupakan negara dengan jumlah penjulan tertinggi sekitar 50.7%. Hal ini menunjukkan bahwa lebih dari setengah total penjualan berasal dari US</li>
            <li>Australia merupakan negara kedua dengan jumlah penjualan tertinggi sekitar 17.8%</li>
            <li>Germany merupakan negara dengan jumlah penjualan sebesar 9.3%</li>
            <li>United Kingdom merupakan negara dengan jumlah penjualan 8.8%</li>
            <li>Canada merupakan negara dengan jumlah penjualan sebesar 7.1%</li>
            <li>French merupakan negara dengan jumlah penjualan terendah sebesar 6.2%</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
        except Exception as e:
            st.error(f"Error: {e}")

        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal
        
        st.header("Relationship between Sales Amount and Order Quantity")
        st.write("Relationship: Scatter Plot")
        
        # SQLAlchemy connection and query for scatter plot
        try:
            # SQL query to fetch the required data for scatter plot
            scatter_plot_query = """
            SELECT 
                SUM(SalesAmount) AS TotalSalesAmount,
                SUM(OrderQuantity) AS TotalOrderQuantity
            FROM 
                factinternetsales
            GROUP BY 
                ProductKey
            """
            
            # Fetch the data into a pandas DataFrame
            df_scatter = pd.read_sql(scatter_plot_query, engine)
            
            # Plotting the scatter plot using seaborn
            plt.figure(figsize=(12, 8))
            sns.scatterplot(data=df_scatter, x='TotalOrderQuantity', y='TotalSalesAmount')
            plt.title('Relationship between Sales Amount and Order Quantity')
            plt.xlabel('Total Order Quantity')
            plt.ylabel('Total Sales Amount')
            plt.tight_layout()
            
            # Display the plot in Streamlit
            st.pyplot(plt)
            
        except Exception as e:
            st.error(f"Error: {e}")

        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deskripsi Data Visualisasi:</b> <br>
        Visualisasi data diatas menggunakan scatter plot untuk menampilkan hubungan antara Order Quantity dan Total Sales Amount. Hal ini digunakan untuk melihat hubungan antara Total Sales Amount (Jumlah Total Penjualan) dan Total Order Quantity (Jumlah Total Pesanan). Berdasarkan gambar, terdapat titik pada koordinat (336, 1.2 juta), ini berarti produk tersebut memiliki 336 pesanan dengan total penjualan sebesar kurang lebih 1.2 (1,202,208) juta.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal

        st.header("Monthly Sales Amount Distribution")
        st.write("Distribusi Jumlah Total Penjualan Per Bulan")
        st.write("Distribution: Histogram Column")
        
        # SQLAlchemy connection and query for histogram
        try:
            # SQL query to fetch the required data for histogram
            histogram_query = """
            SELECT 
                MONTH(OrderDateKey) AS Month,
                SUM(SalesAmount) AS TotalSalesAmount
            FROM 
                factinternetsales
            GROUP BY 
                MONTH(OrderDateKey)
            """
            
            # Fetch the data into a pandas DataFrame
            df_histogram = pd.read_sql(histogram_query, engine)
            
            # Plotting the column histogram using matplotlib
            plt.figure(figsize=(10, 6))
            plt.bar(df_histogram['Month'], df_histogram['TotalSalesAmount'], color='skyblue')
            plt.title('Monthly Sales Amount Distribution')
            plt.xlabel('Month')
            plt.ylabel('Total Sales Amount')
            plt.xticks(range(1, 13))  # Set x-axis ticks from 1 to 12 (months)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Display the plot in Streamlit
            st.pyplot(plt)
            
        except Exception as e:
            st.error(f"Error: {e}")

        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deskripsi Data Visualisasi:</b><br>
        Data Visualisasi tersebut menggunakan Histogram Column Chart untuk menampilkan distribusi jumlah penjualan tiap bulan. Komponen grafik ini terdiri dari label sumbu x yaitu Month (Bulan) dan label sumbu y yaitu Total Sales Amount (Jumlah penjualan). Berdasarkan hasil tersebut, diketahui bahwa jumlah penjualan perbulan tertinggi terletak pada bulan ke-10 (Oktober) sekitar 1,640,296.00 dan jumlah penjualan terendah terletak pada bulan ke-11 (November) sekitar 45,642.00.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal
        
    elif dataset_choice == "IMDb top Movies":
        st.markdown("<h1 style='text-align: center;'>Dasboard IMDb top Movies🎬</h1>", unsafe_allow_html=True)
        
        # Load data IMDB Movies
        file_path = 'imdb_combined.csv'  # Sesuaikan dengan path file CSV IMDB Movies Anda
        data = load_data_imdb(file_path)
        if data is not None:
            st.write(data)
            
            # Visualisasi untuk IMDB Movies
            st.header("Top 10 Highest Rated Movies")
            st.write("10 Film berdasarkan Rate Tertinggi")
            st.write("Comparison: Line Chart")
            
            # Convert the 'Rate' column to numeric
            data['Rate'] = pd.to_numeric(data['Rate'], errors='coerce')
        
            # Sort data by rating and select top 10 highest rated movies
            top_10_movies = data.nlargest(10, 'Rate')[['Name', 'Rate']]
        
            # Plot line chart for top 10 highest rated movies
            plt.figure(figsize=(14, 8))
            plt.plot(top_10_movies['Name'], top_10_movies['Rate'], marker='o', linestyle='-', color='b', label='Rating')
            plt.title('Top 10 Highest Rated Movies')
            plt.xlabel('Movie Title')
            plt.ylabel('Rating')
            plt.xticks(rotation=45)
            plt.legend()
            plt.grid(True)
        
            # Display the plot in Streamlit
            st.pyplot(plt)
            
            st.markdown("""
            <div style='text-align: justify;'>
            <b>Deskripsi Data Visualisasi:</b><br>
            Data Visualisasi tersebut menggunakan Line Chart untuk menampilkan 10 film tertinggi berdasarkan rate film. Pada sumbu x menunjukkan judul film dan sumbu y menunjukkan rate film. Berdasarkan gambar, diketahui bahwa The Shawshank Redemption mendapatkan rate tertinggi sebesar 9.3 dan The Godfather mendapatkan rate tertinggi kedua sebesar 9.2. Selain itu, terdapat 5 film yang mendapatkan rate 9.2 yaitu The Dark Knight, The Godfather Part II, 12 Angry Men, Schindler's List, dan The Lord of the Rings: The Return of the King. Kemudian, Pulp Fiction dan The Lord of the Rings: The Fellowship of the Ring mendapatkan rate sebesar 8.9. Terakhir, rate terendah 8.8 terdapat pada judul film The Good, the Bad and the Ugly.
            </div>
            """, unsafe_allow_html=True)
        
            st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal

            st.header("Total Movies by Release Year")
            st.write("Jumlah Film berdasarkan Tahun Rilis")
            st.write("Comparison: Bar Chart")
        
            # Plot the total movies by release year
        try:
            # Count total movies by release year
            movies_per_year = data['Year'].value_counts().sort_index()
    
            # Create a list of random colors for each bar
            colors = ['#%06X' % random.randint(0, 0xFFFFFF) for i in range(len(movies_per_year))]
    
            # Plotting the bar chart
            plt.figure(figsize=(10, 6))
            movies_per_year.plot(kind='bar', color=colors)  # Set bar colors to be colorful
            plt.title('Total Movies by Release Year')
            plt.xlabel('Release Year')
            plt.ylabel('Total Movies')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
    
            # Display the plot in Streamlit
            st.pyplot(plt)
            
        except Exception as e:
            st.error(f"Error: {e}")
    
        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deskripsi Data Visualisasi:</b><br>
        Data Visualisasi tersebut menggunakan Bar Chart untuk mengetahui Jumlah Film Berdasarkan Tahun Rilis. Setiap batang mewakili tahun rilis film, dengan tinggi batang menunjukkan jumlah film yang dirilis pada tahun tersebut. Berdasarkan gambar, tahun 1994 merilis film paling banyak sejumlah 5 film. Pada tahun 1999 dan 2000 merilis film terbanyak kedua sejumlah 3 film. Untuk tahun lainnya, merilis film dengan jumlah yang sama sekitar 1 film.
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal

        # Second visualization: Donut Chart (Composition)
        st.header("Distribution of Movies by Rating")
        st.write("Distribusi Film Berdasarkan Rating (Persen)")
        st.write("Composition: Donut Chart")
    
        data['Rating'] = data['Rating'].astype(str)
        rating_counts = data['Rating'].value_counts()
    
        # Plot donut chart
        plt.figure(figsize=(8, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(rating_counts)))  # Generate colors
        wedges, texts, autotexts = plt.pie(rating_counts, labels=rating_counts.index, autopct='%1.1f%%', startangle=140, wedgeprops=dict(width=0.3), colors=colors, textprops=dict(color="black"))
    
        # Add a white circle at the center to make it a donut chart
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
    
        # Improve label visibility
        for text in texts + autotexts:
            text.set_fontsize(10)
    
        # Set title and legend
        plt.title('Distribution of Movies by Rating')
        plt.legend(wedges, rating_counts.index, title='Rating', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        st.pyplot(plt)
        plt.clf()
    
        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deksripsi Data Visualisasi:</b><br>
        Data visualisasi tersebut menggunakan Donut Chart untuk menampilkan distribusi film berdasarkan rating. Gambar tersebut menunjukkan distribusi rating film, sedangkan label dan persentase yang diberikan menunjukkan proporsi masing-masing rating. Terdapat 6 kategori rating yaitu kategori rating R mendapatkan nilai proporsi tertinggi sebesar 52%, Rating PG-13 mendapatkan nilai proporsi sebesar 20%, Rating PG mendapatkan nilai proporsi sebesar 16%, Rating Not Rate mendapatkan nilai proporsi sebesar 6%, Rating G mendapatkan nilai proporsi sebesar 2%. sedangkan nilai terendah sebesar 2% terdapat pada kategori rating Approved.
        </div>
        """, unsafe_allow_html=True)
    
        
        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal
    
        # Third visualization: Histogram (Distribution)
        st.header("Distribusi Gross US ")
        st.write("Distribusi Pendapatan Kotor pada Data IMDB")
        st.write("Distribution : Histogram Column")
    
        data['Gross_Us'] = pd.to_numeric(data['Gross_Us'], errors='coerce').fillna(0)
    
        # Plot histograms
        plt.figure(figsize=(14, 6))
    
        # Histogram untuk Gross US
        plt.subplot(1, 2, 1)
        plt.hist(data['Gross_Us'], bins=50, color='blue', edgecolor='black', alpha=0.7)
        plt.title('Distribusi Gross US')
        plt.xlabel('Gross US (dalam dolar)')
        plt.ylabel('Frekuensi')
        plt.grid(True)
    
        plt.tight_layout()
        st.pyplot(plt)
        plt.clf()
    
        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deksripsi Data Visualisasi:</b><br>
        Data Visualisasi tersebut menggunakan Histogram Column untuk menunjukkan jumlah film yang memiliki pendapatan kotor (dalam dolar) dalam rentang tertentu. Sumbu x menunjukkan jumlah pendapatan kotor berkisar dari 0 hingga lebih dari 5e8 (500 juta dolar) dan sumbu y menunjukkan frekuensi atau jumlah film yang jatuh dalam rentang pendapatan kotor tertentu. Terdapat beberapa film yang memiliki pendapatan kotor antara 1e8 (100 juta dolar) hingga 5e8 (500 juta dolar), tetapi frekuensi film tersebut rendah hanya sekitar 1 hingga 2 film per rentang.
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal
    
        # Fourth visualization: Scatter Plot (Relationship)
        st.header("Relationship between Year and Movie Rating")
        st.write("Hubungan antara Tahun dan Rate Film")
        st.write("Relationship : Scatter Plot")
    
        data['Year'] = pd.to_numeric(data['Year'], errors='coerce')
        data['Rate'] = pd.to_numeric(data['Rate'], errors='coerce').fillna(0)
    
        # Remove rows with missing years or rates
        data = data.dropna(subset=['Year', 'Rate'])
    
        # Plot scatter plot
        plt.figure(figsize=(12, 6))
        plt.scatter(data['Year'], data['Rate'], alpha=0.5, c='orange')
        plt.title('Year vs Rate')
        plt.xlabel('Year')
        plt.ylabel('Rate')
        plt.grid(True)
        plt.tight_layout()
        st.pyplot(plt)
        plt.clf()
    
        st.markdown("""
        <div style='text-align: justify;'>
        <b>Deskripsi Data Visualisasi:</b><br>
        Data Visualisasi tersebut menggunakan Scatter Plot untuk menampilkan hubungan antara Year (tahun) dan Rate. Terdapat dua komponen, yaitu sumbu x menunjukkan tahun (Year) dan sumbu y menunjukkan rating film (Rate). Sebagian besar titik tersebar secara acak di seluruh rentang tahun. Salah satu hasil visualisasi tersebut terdapat pada koordinat titik (1980, 8.7), yang berarti pada tahun 1980, film yang terdapat pada data IMDb memiliki rating sebesar 8.7. Selain itu, ditemukan bahwa rentang tahun 1980-2000 memiliki rating film tertinggi sebesar 9.3.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)  # Garis horizontal

# Entry point untuk aplikasi Streamlit
if __name__ == "__main__":
    main()

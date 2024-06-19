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

# Main function to set up the Streamlit app
def main():
    st.write("Nama: Ardilla Firosya")
    st.write("NPM: 21082010239")
    st.write("Mata Kuliah : Data Visualisasi")

    st.title("Dataset AdventureWorks")
    
    st.header("Sales Amount by Product Sub Category")
    st.write("Jumlah Penjualan Berdasarkan SubKategori Produk")
    st.write("Comparison: Bar Chart Data Visualitation")
    
    # SQLAlchemy connection and query for bar chart
    try:
        # Establish the database connection using SQLAlchemy
        engine = create_engine("mysql+mysqlconnector://davis2024irwan:wh451n9m@ch1n3@kubela.id:3306/aw")

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
        
    except Exception as e:
        st.error(f"Error: {e}")

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
    
    # SQLAlchemy connection and query for monthly profit trend
    try:
        # SQL query to fetch the required data for line chart
        monthly_profit_query = """
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

        # Fetch the data into a pandas DataFrame
        df_monthly_profit = pd.read_sql(monthly_profit_query, engine)
        
        # Plotting the line chart
        plt.figure(figsize=(10, 6))
        plt.plot(df_monthly_profit['MonthYear'], df_monthly_profit['TotalRevenue'], marker='o', color='r', linestyle='-')
        plt.title( 'Total Pendapatan dari Pelanggan per Bulan')
        plt.xlabel('Bulan')
        plt.ylabel('Total Pendapatan')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)
        
    except Exception as e:
        st.error(f"Error: {e}")

    st.write("Deskripsi Data Visualisasi:")
    st.write("Visualisasi data tersebut menggunakan grafik Line Chart untuk menampilkan jumlah pendapatan dari pelanggan tiap bulan dengan rentang waktu 07-2001 hingga 04-2004. Terdapat komponen sumbu x menunjukkan rentang waktu bulan dan tahun pendapatan dan sumbu y menunjukkan total pendapatan. Berdasarkan gambar diketahui bahwa total pendapatan per bulan tertinggi terdapat pada bulan 12-2002 yaitu sebesar 1,2 juta (1,215,691). Kemudian total pendapatan tertinggi kedua terdapat pada bulan 04-2002 sebesar 1,1 juta (1,142,150).")
    
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

    except Exception as e:
        st.error(f"Error: {e}")

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

    st.write("Deskripsi Data Visualisasi:")
    st.write("Visualisasi data diatas menggunakan scatter plot untuk menampilkan hubungan antara Order Quantity dan Total Sales Amount. Hal ini diguakan untuk melihat hubungan antara Total Sales Amount (Jumlah Total Penjualan) dan Total Order Quantity (Jumlah Total Pesanan). Berdasarkan gambar, terdapat titik pada koordinat (336, 1.2 juta), ini berarti produk tersebut memiliki 336 pesanan dengan total penjualan sebesar kurang lebih 1.2 (1,202,208) juta.")
    st.write("")
    

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

    st.write("Deskripsi Data Visualisasi:")
    st.write(" Data Visualisasi tersebut menggunakan Histogram Column Chart untuk menampilkan distribusi Jumlah Penjualan tiap bulan. Komponen grafik ini terdiri dari label sumbu x yaitu Month (Bulan) dan label sumbu y yaitu Total Sales Amout (Jumlah penjualan). Berdasarkan hasil tersebut, diketahui bahwa jumlah penjualan perbulan tertinggi terletak pada bulan ke-10 (Oktober) sekitar 1,6 juta (1640296.00) dan jumlah penjulan terendah terletak pada bulan ke-11 (November) yaitu sekitar 45642.00")
    
    st.title("Dataset IMDB Movies")
    
    st.header("Top 10 Highest Rated Movies")
    st.write("10 Film berdasarkan Rate Tertinggi")
    st.write("Comparison: Line Chart ")
    
    # Load data
    file_path = 'imdb_combined.csv'  # ganti dengan jalur file CSV yang sesuai
    data = pd.read_csv(file_path)

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
    st.write("Deskripsi Data Visualisasi:")
    st.write("Data Visualisasi tersebut menggunakan Line Chart untuk menampilkan 10 film tertinggi berdasarkan rate film. Pada sumbu x menunjukkan judul film dan sumbu y menunjukkan rate film. Berdasarkan gambar, diketahui bahwa The Shawsank Redemtion mendapatkan rate tertinggi sebesar 9.3 dan The Gold Father mendapatkan rate tertinggi kedua sebesar 9.2. Selain itu terdaoat 5 film yang mendapatkan rate 9.2 diantaranya The Dark Knight, The GOld Father Part Dua, Angry Men, Schindler'r list, dan The Lord of The Ring: The Return of The King. Kemudian Pulp Fiction dan The Lord of The Ring: The Fellowship of The King mendapatkan rate sebesar 8.9. Terakhir, rate terendah 8.8 ada pada judul film The God The Bad and The Ugly.")
    

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

    st.write("Deskripsi Data Visualisasi:")
    st.write("Data Visualisasi tersebut menggunakan Bar Chart untuk mengetahui Jumlah Film Berdarkan Tahun Rilis. Setiap batang mewakili tahun rilis film, dengan tinggi batang menunjukkan jumlah film yang dirilis pada tahun tersebut. Berdasarkan gambar, tahun 1994 merilis film paling banyak sejumlah 5 film. Pada tahun 1999 dan 2000 memrilis film terbanyak kedua sejumlah 3 film. Untuk tahun lainnya, merilis film dengan jumlah yang sama sekitar 1 film.")

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

    st.write("Deksripsi Data Visualisasi:")
    st.write("Data visualisasi tersebut menggunakan Donut Chart untuk menampilkan distribusi film berdasarkan rating. Gambar tersebut menunjukkan distribusi rating film, sedangkan label dan persentase yang diberikan menunjukkan proporsi masing-masing rating. Terdapat 6 kategori rating dimana Kategori rating R mendapatkan nilai proporsi tertinggi sebesar 52% dan nilai terendah sebesar 2% terdapat pada kategori rating Approved.")

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

    st.write("Deksripsi Data Visualisasi :")
    st.write("Data Visualisasi tersebut menggunakan Histogram Column untuk menunjukkan jumlah film yang memiliki pendapatan kotor (dalam dolar) dalam rentang tertentu. Sumbu x menunjukkan  jumlah pendapatan kotor berkisar dari 0 hingga lebih dari 5e8 (500 juta dolar) dan sumbu y menunjukkan frekuensi atau jumlah film yang jatuh dalam rentang pendapatan kotor tertentu. Terdapat beberapa film yang memiliki pendapatan kotor antara 1e8 (100 juta dolar) hingga 5e8 (500 juta dolar), tetapi frekuensi film tersebut rendah hanya sekitar 1 hingga 2 film per rentang.")


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

    st.write("Deksripsi Data Visualisasi :")
    st.write("Data Visualisasi tersebut menggunakan Scatter Plot untuk menampilkan hubungan antara Year (tahun) dan rate. Terdapat dua kompenen yaitu sumbu x menunjukkan year (tahun) dan sumbu y menunjukkan rate film. Sebagian besar titik tersebar secara acak di seluruh rentang tahun. Salah satu hasil visualisasi tersebut terdapat pada koordinat titik (1980,8.7) artinya pada tahun 1980, film yang terdapat pada data imdb tersebut memiliki rate sebesar 8.7. Selain itu ditemukan dari rentang tahun 1980-2000 memiliki rate film tertinggi sebesar 9.3.")


# Entry point for the Streamlit app
if __name__ == "__main__":
    main()


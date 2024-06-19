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
    df_viz = fetch_data(bar_chart_query)

    if df_viz is not None:
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
    else:
        st.error("Failed to load data for bar chart.")
    
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
    df_monthly_profit = fetch_data(monthly_profit_query)
    
    if df_monthly_profit is not None:
        # Plotting the line chart
        plt.figure(figsize=(10, 6))
        plt.plot(df_monthly_profit['MonthYear'], df_monthly_profit['TotalRevenue'], marker='o', color='r', linestyle='-')
        plt.title('Total Pendapatan dari Pelanggan per Bulan')
        plt.xlabel('Bulan')
        plt.ylabel('Total Pendapatan')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)
    else:
        st.error("Failed to load data for line chart.")
    
    st.write("Deskripsi Data Visualisasi:")
    st.write("Visualisasi data tersebut menggunakan grafik Line Chart untuk menampilkan jumlah pendapatan dari pelanggan tiap bulan dengan rentang waktu 07-2001 hingga 04-2004. Terdapat komponen sumbu x menunjukkan rentang waktu bulan dan tahun pendapatan dan sumbu y menunjukkan total pendapatan. Berdasarkan gambar diketahui bahwa total pendapatan per bulan tertinggi terdapat pada bulan 12-2002 yaitu sebesar 1,2 juta (1,215,691). Kemudian total pendapatan tertinggi kedua terdapat pada bulan 04-2002 sebesar 1,1 juta (1,142,150).")
    
    st.header("Total Sales Amount by Country")
    st.write("Jumlah Penjualan Berdasarkan Negara")
    st.write("Composition: Donut Chart")
    
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
    df_country = fetch_data(donut_chart_query)
    
    if df_country is not None:
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
    else:
        st.error("Failed to load data for donut chart.")
    
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
    df_scatter = fetch_data(scatter_plot_query)
    
    if df_scatter is not None:
        # Plotting the scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df_scatter['TotalOrderQuantity'], df_scatter['TotalSalesAmount'], alpha=0.6)
        plt.title('Relationship between Sales Amount and Order Quantity')
        plt.xlabel('Total Order Quantity')
        plt.ylabel('Total Sales Amount')
        plt.grid(True)
        plt.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(plt)
    else:
        st.error("Failed to load data for scatter plot.")
    
    st.write("Deskripsi Data Visualisasi:")
    st.write("Visualisasi data tersebut menggunakan grafik Scatter Plot untuk menampilkan hubungan antara Jumlah Penjualan (Sales Amount) dengan Jumlah Pemesanan (Order Quantity). Berikut penjelasan visualisasi tersebut: ")
    st.write("Berdasarkan grafik tersebut diketahui bahwa terdapat hubungan linier antara jumlah pemesanan dengan jumlah penjualan. Artinya, semakin tinggi jumlah pemesanan maka semakin tinggi pula jumlah penjualannya. Dari grafik tersebut terlihat bahwa ada kecenderungan data yang berkelompok di bagian awal grafik, yang menunjukkan jumlah pemesanan dan jumlah penjualan yang rendah. Namun, terdapat juga beberapa data yang tersebar di bagian kanan atas grafik yang menunjukkan jumlah pemesanan dan penjualan yang tinggi.")
    
    st.header("Yearly Sales Performance")
    st.write("Kinerja Penjualan Tahunan")
    st.write("Tree Map Data Visualisation")
    
    # SQL query to fetch the required data for treemap
    treemap_query = """
    SELECT 
        dp.EnglishProductCategoryName AS ProductCategory, 
        DATE_FORMAT(fis.OrderDate, '%Y') AS OrderYear, 
        SUM(fis.SalesAmount) AS TotalSalesAmount
    FROM 
        factinternetsales fis
    JOIN 
        dimproduct dp ON fis.ProductKey = dp.ProductKey
    GROUP BY 
        dp.EnglishProductCategoryName, 
        DATE_FORMAT(fis.OrderDate, '%Y')
    """
    
    # Fetch the data into a pandas DataFrame
    df_tree = fetch_data(treemap_query)
    
    if df_tree is not None:
        # Data preparation for treemap
        df_tree['ProductCategory_Year'] = df_tree['ProductCategory'] + " " + df_tree['OrderYear'].astype(str)
        sizes = df_tree['TotalSalesAmount']
        labels = df_tree['ProductCategory_Year']
        
        # Plotting the treemap using squarify
        plt.figure(figsize=(12, 8))
        squarify.plot(sizes=sizes, label=labels, alpha=0.8)
        plt.title('Yearly Sales Performance by Product Category')
        plt.axis('off')
        
        # Display the plot in Streamlit
        st.pyplot(plt)
    else:
        st.error("Failed to load data for treemap.")
    
    st.write("Deskripsi Data Visualisasi:")
    st.write("Visualisasi data tersebut menggunakan Tree Map untuk menampilkan Kinerja Penjualan Tahunan berdasarkan Kategori Produk. Berikut penjelasan visualisasi tersebut: ")
    st.write("- Berdasarkan gambar diketahui bahwa penjualan tahunan terbesar adalah Product Category Bikes pada tahun 2002")
    st.write("- Kemudian Product Category Clothing pada tahun 2002 juga memiliki penjualan yang cukup besar")
    st.write("- Terakhir Product Category Acessories pada tahun 2001 juga memiliki penjualan yang besar")
    

# Running the main function
if __name__ == '__main__':
    main()

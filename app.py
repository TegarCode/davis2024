import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pymysql
import squarify
from io import StringIO


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
st.header('Sales Distribution per Territory')
df_sales_per_territory = fetch_data(query_sales_per_territory)
if df_sales_per_territory is not None:
    st.bar_chart(df_sales_per_territory.set_index('Region'))

    # Membuat tree map chart
    st.write("Komposisi Penjualan per Wilayah")
    plt.figure(figsize=(12, 8))
    squarify.plot(sizes=df_sales_per_territory['TotalSales'], 
                  label=df_sales_per_territory['Region'], 
                  alpha=.8)
    plt.title('Komposisi Penjualan per Wilayah')
    plt.axis('off')  # turn off the axis
    st.pyplot(plt)

# Bagian untuk distribusi usia pelanggan
st.header('Customer Age Distribution')
df_customer_age_distribution = fetch_data(query_customer_age_distribution)
if df_customer_age_distribution is not None:
    plt.figure(figsize=(10, 6))
    sns.histplot(df_customer_age_distribution['Age'], bins=20, kde=True)
    plt.title('Age Distribution of Customers')
    plt.xlabel('Age')
    plt.ylabel('Frequency')
    st.pyplot(plt)

# Bagian untuk hubungan antara mountain bikes dan spareparts
st.header('Mountain Bike and Spareparts Sales')
df_mountain_bike_spareparts = fetch_data(query_mountain_bike_spareparts)
if df_mountain_bike_spareparts is not None:
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_mountain_bike_spareparts, x='SparepartType', y='TotalSales')
    plt.title('Mountain Bike and Spareparts Sales')
    plt.xlabel('Sparepart Type')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    st.pyplot(plt)






# Load the CSV file
file_path = 'imdb_combined_data2.csv'  # Adjust this path if needed
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
fig, ax = plt.subplots(figsize=(10, 6))
data.groupby('Year')['Gross_World'].sum().plot(kind='bar', ax=ax)
ax.set_xlabel('Year')
ax.set_ylabel('Total Gross Worldwide')
ax.set_title('Total Gross Worldwide per Year')
st.pyplot(fig)

# Distribution Plot: Distribution of Gross Worldwide
st.write("Distribution Plot: Distribution of Gross Worldwide")
fig, ax = plt.subplots(figsize=(10, 6))
data['Gross_World'].plot(kind='hist', bins=30, color='skyblue', ax=ax)
ax.set_xlabel('Gross Worldwide')
ax.set_ylabel('Frequency')
ax.set_title('Distribution of Gross Worldwide')
st.pyplot(fig)

# Composition Plot: Gross Worldwide composition by Rating
st.write("Composition Plot: Gross Worldwide composition by Rating")
gross_composition = data.groupby('Rating')['Gross_World'].sum()
fig, ax = plt.subplots(figsize=(10, 6))
gross_composition.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors, ax=ax)
ax.set_ylabel('')
ax.set_title('Gross Worldwide Composition by Rating')
st.pyplot(fig)

# Relationship Plot: Budget vs. Gross Worldwide
st.write("Relationship Plot: Budget vs. Gross Worldwide")
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(data['Budget'], data['Gross_World'], alpha=0.5)
ax.set_xlabel('Budget')
ax.set_ylabel('Gross Worldwide')
ax.set_title('Relationship between Budget and Gross Worldwide')
st.pyplot(fig)
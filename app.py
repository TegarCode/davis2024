import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pyttsx3

# Function untuk mengucapkan teks dalam bahasa Inggris

# Menampilkan teks 
st.subheader("VISUALISASI DATA KU")
st.write("Tegar Oktavianto Simbolon (21082010140)")

st.subheader("")
st.subheader("Scatter Plot")
# 1
# reading the database
data = pd.read_csv("https://raw.githubusercontent.com/TegarCode/davis2024/main/tips.csv")

# Scatter plot with day against tip
fig, ax = plt.subplots()
scatter = ax.scatter(data['day'], data['tip'])

# Setting the X and Y labels
plt.xlabel('Day')
plt.ylabel('Tip')

# showing the plot
st.pyplot(fig)

st.subheader("")
st.subheader("Line Plot")
# 2
# draw lineplot
fig, ax = plt.subplots() 
sns.lineplot(x="sex", y="total_bill", data=data, ax=ax)

# showing the plot
st.pyplot(fig)

st.subheader("")
st.subheader("Line Chart")
# 3
# plotting the scatter chart
fig = px.line(data, y='tip', color='sex')

# showing the plot
st.plotly_chart(fig)

# Bar plot
fig = plt.figure(figsize=(10, 6))
sns.barplot(x='day', y='tip', data=data, hue='sex')
plt.xlabel('Day')
plt.ylabel('Tip')
plt.title('Bar Plot')
plt.legend(title='Sex')
st.pyplot(fig)


    text_to_speech_indonesian(additional_text)

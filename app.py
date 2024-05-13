import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import pyttsx3

# Function untuk mengucapkan teks dalam bahasa Inggris
def text_to_speech_english(text):
    engine = pyttsx3.init(driverName='sapi5')  # Menggunakan mode offline
    engine.setProperty('rate', 150)
    engine.setProperty('voice', 'english')
    engine.say(text)
    engine.runAndWait()

# Function untuk mengucapkan teks dalam bahasa Indonesia
def text_to_speech_indonesian(text):
    engine = pyttsx3.init(driverName='sapi5')  # Menggunakan mode offline
    engine.setProperty('rate', 150)
    engine.setProperty('voice', 'indonesian')
    engine.say(text)
    engine.runAndWait()

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

# Teks tambahan
additional_text = "Project ini dibuat oleh Tegar Oktavianto Simbolon dengan NPM mahasiswa 21082010140"

# Pilihan bahasa
language = st.selectbox("Pilih Bahasa", ["English", "Indonesian"])

if language == "English":
    text_to_speech_english(additional_text)
else:
    text_to_speech_indonesian(additional_text)

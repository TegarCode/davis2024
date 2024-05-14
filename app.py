import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from gtts import gTTS
import io
import base64
import os

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.bar_chart(chart_data)



# Initialize connection.
# conn = st.connection('mysql', type='sql', username=st.secrets["DB_USER"], password=st.secrets["DB_PASS"], host=st.secrets["HOST"], database=st.secrets["DB"])
# conn = st.connection(**st.secrets.db_credentials)
conn = st.connection("mydb", type="sql", autocommit=True)

# Perform query.
df = conn.query('SELECT EnglishPromotionName, StartDate, EndDate, MaxQty from dimpromotion limit 10;', ttl=600)

st.table(df)
# Print results.
# for row in df.itertuples():
#     st.write(f"{row.EnglishPromotionName} , {row.MaxQty} ")

# Function to convert text to speech and generate audio file
def text_to_speech(text, filename="audio.mp3"):
    tts = gTTS(text=text, lang='id')  # Using Indonesian language
    tts.save(filename)
    return filename

# Function to play audio in streamlit using HTML
def play_audio(audio_file):
    with open(audio_file, "rb") as file:
        audio_bytes = file.read()
        audio_placeholder = st.empty()
        audio_placeholder.markdown(f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)

# Menampilkan teks 
st.subheader("Visualisasi dari Data tips.csv")

# Text-to-speech untuk subheader
audio_file = text_to_speech("Ini hasil deploynya")
play_audio(audio_file)

st.write("Dhavina Ocxa Dwiyantie")
st.write("21082010136")

# 1
# reading the database
data = pd.read_csv("https://raw.githubusercontent.com/dhavinaocxa/davis-2024/main/tips.csv")

st.subheader("")
st.subheader("Scatter Plot")
# Scatter plot with day against tip
fig, ax = plt.subplots()
scatter = ax.scatter(data['day'], data['tip'], c=data['size'], s=data['total_bill'])

# Adding Title to the Plot
plt.title("Scatter Plot")

# Setting the X and Y labels
plt.xlabel('Day')
plt.ylabel('Tip')

plt.colorbar(scatter)

st.pyplot(fig)

st.subheader("")
st.subheader("Line Chart")
# 3
# plotting the scatter chart
fig = px.line(data, y='tip', color='sex')

# showing the plot
st.plotly_chart(fig)

st.subheader("")
st.subheader("Line Plot")
# 2
# draw lineplot
fig, ax = plt.subplots() 
sns.lineplot(x="sex", y="total_bill", data=data, ax=ax)

# showing the plot
st.pyplot(fig)

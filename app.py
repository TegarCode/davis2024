import streamlit as st
import pyttsx3
from gtts import gTTS
import translators as ts
import pygame
import io

def text_to_speech(text, language='en'):
    # Inisialisasi pyttsx3
    engine = pyttsx3.init()

    # Mengucapkan teks
    engine.say(text)
    engine.runAndWait()

def translate_text(text, to_language='id'):
    # Melakukan terjemahan
    hasil = ts.translate_text(text, to_language=to_language, translator='google')
    return hasil

def text_to_speech_gTTS(text, language='en'):
    # Membuat objek gTTS dari teks
    tts = gTTS(text=text, lang=language)

    # Save the audio as bytes
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)

    return audio_bytes

def play_audio(audio_bytes):
    # Inisialisasi mixer untuk Pygame
    pygame.mixer.init()

    # Load the audio into Pygame mixer
    audio_bytes.seek(0)
    pygame.mixer.music.load(audio_bytes)

    # Play the audio
    pygame.mixer.music.play()

# Menampilkan input teks
input_text = st.text_area("Masukkan teks yang ingin diterjemahkan dan didengar:", "")

# Memilih bahasa tujuan
to_language = st.selectbox("Pilih bahasa tujuan:", ["Indonesia", "English"])
to_language_code = 'id' if to_language == "Indonesia" else 'en'

# Terjemahkan teks jika ada input
if input_text:
    translated_text = translate_text(input_text, to_language=to_language_code)
    st.write("Teks Terjemahan:", translated_text)

    # Pilihan untuk menggunakan pyttsx3 atau gTTS
    audio_engine = st.radio("Pilih engine untuk membaca teks:", ("pyttsx3", "gTTS"))

    if st.button("Dengarkan"):
        if audio_engine == "pyttsx3":
            text_to_speech(translated_text, language=to_language_code)
        else:
            audio_bytes = text_to_speech_gTTS(translated_text, language=to_language_code)
            play_audio(audio_bytes)

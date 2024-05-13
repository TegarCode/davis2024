import pyttsx3
from gtts import gTTS
import translators as ts
import os
import pygame
import io

# Inisialisasi pyttsx3
engine = pyttsx3.init()

# Teks yang ingin diterjemahkan
text = "This company was founded in 2010 by the infamous movie star, \
          Graeme Alexander. Currently, the company worths USD 1 billion \
          according to Forbes report in 2023. What an achievement in just \
          13 years."

# Mengucapkan teks dalam bahasa Inggris
engine.say(text)
engine.runAndWait()

# Inisialisasi mixer untuk Pygame
pygame.mixer.init()

# Melakukan terjemahan ke bahasa Indonesia
hasil = ts.translate_text(text, to_language="id", translator='google')

# Membuat objek gTTS dari teks terjemahan
tts = gTTS(text=hasil, lang='id')

print(hasil)

# Save the audio as bytes
audio_bytes = io.BytesIO()
tts.write_to_fp(audio_bytes)

# Load the audio into Pygame mixer
audio_bytes.seek(0)
pygame.mixer.music.load(audio_bytes)

# Play the audio
pygame.mixer.music.play()

import streamlit as st
import pytesseract
from PIL import Image
from googlesearch import search
import os
import datetime

st.set_page_config(page_title="Cat CPT", layout="centered")

# Konuları saklamak için session state
if "conversations" not in st.session_state:
    st.session_state.conversations = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "Genel Konuşma"

# Yeni konu başlat butonu
if st.button("➕ Yeni Konu"):
    st.session_state.current_topic = f"Konu ({datetime.datetime.now().strftime('%H:%M:%S')})"
    st.session_state.conversations.append((st.session_state.current_topic, []))

# Konu seçimi veya oluşturulmamışsa ilk konu
if len(st.session_state.conversations) == 0:
    st.session_state.conversations.append((st.session_state.current_topic, []))

# Mevcut konu verisine referans
topic_index = next(i for i, (t, _) in enumerate(st.session_state.conversations) if t == st.session_state.current_topic)
messages = st.session_state.conversations[topic_index][1]

# Konu başlığı
st.markdown(f"## 🧠 {st.session_state.current_topic}")

# Geçmiş konuşmaları göster
for i, (sender, msg) in enumerate(messages):
    with st.chat_message(sender):
        st.markdown(msg)

# Giriş kutusu ve dosya yükleme
with st.container():
    user_input = st.chat_input("Mesajınızı yazın...")
    uploaded_file = st.file_uploader("📎 Dosya/Fotograf", type=["png", "jpg", "jpeg", "txt", "pdf"], label_visibility="collapsed")

# Mesaj gönderildiyse
if user_input or uploaded_file:
    if user_input:
        messages.append(("user", user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        if any(user_input.lower().startswith(q) for q in ["nedir", "kim", "nasıl", "ne", "kaç"]):
            query = user_input.strip()
            result_links = list(search(query, num_results=2))
            answer = "\n\n".join([f"🔗 [{link}]({link})" for link in result_links])
            messages.append(("assistant", f"İşte bulduklarım:\n{answer}"))
            with st.chat_message("assistant"):
                st.markdown(f"İşte bulduklarım:\n{answer}")
        elif any(x in user_input.lower() for x in ["yorumla", "analiz et"]):
            answer = f"Bu konuda şöyle düşünüyorum: {user_input} oldukça ilginç bir konu. İçeriğini değerlendirirken hem bağlam hem de niyet göz önüne alınmalı."
            messages.append(("assistant", answer))
            with st.chat_message("assistant"):
                st.markdown(answer)
        else:
            answer = f"Söylediğini anladım: '{user_input}'. Sana nasıl yardımcı olabilirim?"
            messages.append(("assistant", answer))
            with st.chat_message("assistant"):
                st.markdown(answer)

    if uploaded_file:
        filetype = uploaded_file.type
        messages.append(("user", f"📎 Dosya yüklendi: {uploaded_file.name}"))
        with st.chat_message("user"):
            st.markdown(f"📎 Dosya yüklendi: {uploaded_file.name}")

        if filetype.startswith("image"):
            image = Image.open(uploaded_file)
            text = pytesseract.image_to_string(image)
            messages.append(("assistant", f"📖 Görselden okunan metin:\n{text}"))
            with st.chat_message("assistant"):
                st.markdown(f"📖 Görselden okunan metin:\n{text}")
        else:
            messages.append(("assistant", "🔍 Bu dosya türü şu anda desteklenmiyor."))
            with st.chat_message("assistant"):
                st.markdown("🔍 Bu dosya türü şu anda desteklenmiyor.")

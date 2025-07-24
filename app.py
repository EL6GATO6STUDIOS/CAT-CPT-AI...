import streamlit as st import pytesseract from PIL import Image from googlesearch import search import requests from bs4 import BeautifulSoup import os import datetime

st.set_page_config(page_title="Cat CPT", layout="centered")

Konuları saklamak için session state

if "conversations" not in st.session_state: st.session_state.conversations = [] if "current_topic" not in st.session_state: st.session_state.current_topic = "Genel Konuşma"

Yeni konu başlat butonu

if st.button("➕ Yeni Konu"): st.session_state.current_topic = f"Konu ({datetime.datetime.now().strftime('%H:%M:%S')})" st.session_state.conversations.append((st.session_state.current_topic, []))

Konu seçimi veya oluşturulmamışsa ilk konu

if len(st.session_state.conversations) == 0: st.session_state.conversations.append((st.session_state.current_topic, []))

Mevcut konu verisine referans

topic_index = next(i for i, (t, _) in enumerate(st.session_state.conversations) if t == st.session_state.current_topic) messages = st.session_state.conversations[topic_index][1]

Konu başlığı

st.markdown(f"## 🧠 {st.session_state.current_topic}")

Geçmiş konuşmaları göster

for i, (sender, msg) in enumerate(messages): with st.chat_message(sender): st.markdown(msg)

Mesaj yazma kutusu en alta sabit ve tam genişlikte olacak şekilde

with st.container(): col1, col2 = st.columns([8, 2]) with col1: user_input = st.text_input("", placeholder="Mesajınızı yazın...", key="input_field") with col2: send_clicked = st.button("Gönder") uploaded_file = st.file_uploader("📎 Dosya/Fotograf", type=["png", "jpg", "jpeg", "txt", "pdf"], label_visibility="collapsed")

Mesaj gönderildiyse

if user_input or uploaded_file or send_clicked: if user_input and send_clicked: messages.append(("user", user_input)) with st.chat_message("user"): st.markdown(user_input)

# Soru mu, analiz mi, gündelik mi kontrol et
    if any(user_input.lower().startswith(q) for q in ["nedir", "kim", "nasıl", "ne", "kaç"]):
        query = user_input.strip()
        result_links = list(search(query, num_results=1))
        summary = f"İnsanlar genellikle şöyle der: '{query}' hakkında bazı bilgiler buldum."
        if result_links:
            summary += f" Bunlardan biri: [Kaynak]({result_links[0]})"
        else:
            summary += " Ancak kaynak bulunamadı."
        messages.append(("assistant", summary))
        with st.chat_message("assistant"):
            st.markdown(summary)
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
        result = f"📖 Görselden okunan metin: {text}"
        messages.append(("assistant", result))
        with st.chat_message("assistant"):
            st.markdown(result)
    else:
        messages.append(("assistant", "🔍 Bu dosya türü şu anda desteklenmiyor."))
        with st.chat_message("assistant"):
            st.markdown("🔍 Bu dosya türü şu anda desteklenmiyor.")


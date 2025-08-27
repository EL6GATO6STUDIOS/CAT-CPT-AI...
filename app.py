import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import random

# Sayfa ayarları
st.set_page_config(page_title="Cat CPT 😺", layout="wide")
st.title("Cat CPT 😺")

# Sohbet geçmişi
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Kullanıcıdan giriş al
user_input = st.text_input("Sorunuzu yazın:")

# Yorumlama (analiz) cevabı üreten fonksiyon
def generate_opinion_response(user_input):
    fikir_sablonlari = [
        "Bence bu oldukça düşündürücü. '{}' konusu insanların bakış açısına göre farklı yorumlanabilir.",
        "'{}' hakkında düşündüğümde, bağlam çok şey değiştiriyor. Genel olarak bu konu üzerinde dikkatle durulmalı.",
        "Açıkçası '{}' konusuna pek sıcak bakmıyorum. Ama farklı fikirlerin değerli olduğunu düşünüyorum.",
        "'{}' bana kalırsa günümüzde tartışılması gereken bir mesele. Önemli olan yaklaşım tarzıdır.",
        "'{}' konusunu düşündüğümde aklıma gelen ilk şey: insanlara saygı duyarak değerlendirilmesi gerektiğidir.",
        "Kendi bakış açıma göre '{}' bazen abartılıyor olabilir. Ama yine de önemli bir noktaya işaret ediyor.",
        "'{}' ile ilgili fikrim: tamamen bağlama göre değişir ama çoğu durumda dikkate alınması gereken bir durum.",
    ]
    return random.choice(fikir_sablonlari).format(user_input)

# Kullanıcıdan metin geldiyse işleme
if user_input:
    original_text = user_input
    lower_text = user_input.lower()

    if any(keyword in lower_text for keyword in ["sence", "yorumla", "analiz", "ne düşünüyorsun", "karakter", "tartış", "duygusal", "kişilik"]):
        response = generate_opinion_response(original_text)

    else:
        try:
            response = "Araştırılıyor..."
            results = list(search(original_text, num=1, stop=1, pause=2))
            if results:
                url = results[0]
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                paragraphs = soup.find_all("p")
                found = False
                for p in paragraphs:
                    if len(p.text.strip()) > 50:
                        bilgi = p.text.strip()
                        response = f"Sorduğun şeyle ilgili şunu öğrendim: {bilgi}"
                        found = True
                        break
                if not found:
                    response = "Uygun bir bilgi bulunamadı."
            else:
                response = "Sonuç bulunamadı."
        except Exception as e:
            response = f"Araştırma sırasında bir hata oluştu: {str(e)}"

    st.session_state.chat_history.append((original_text, response))

# Sohbet geçmişini göster
if st.session_state.chat_history:
    st.subheader("🧠 Sohbet Geçmişi")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**{i}. Soru:** {q}")
        st.markdown(f"**{i}. Cevap:** {a}")
# Sohbet geçmişini göster
if st.session_state.chat_history:
    st.subheader("🧠 Sohbet Geçmişi")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**{i}. Soru:** {q}")
        st.markdown(f"**{i}. Cevap:** {a}")

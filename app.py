import streamlit as st
from googlesearch import search
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Cat CPT 😺", layout="wide")
st.title("Cat CPT 😺")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

text = st.text_input("Sorunuzu yazın:")

def generate_response(query):
    try:
        # Google'da arama yap
        urls = []
        for url in search(query, num=3, stop=3, pause=2):  # ✅ num_results yerine num & stop
            urls.append(url)

        if not urls:
            return "🔍 Arama sonucu bulunamadı."

        # İlk linkten içerik çek
        res = requests.get(urls[0], timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")

        for p in paragraphs:
            if len(p.text.strip()) > 80:
                return f"Sorduğun konu hakkında şunu buldum: {p.text.strip()} Kaynak: {urls[0]}"

        return f"Bilgi bulunamadı ama istersen şuraya bakabilirsin: {urls[0]}"

    except Exception as e:
        return f"❌ Araştırma sırasında hata oluştu: {str(e)}"


if text:
    response = generate_response(text)
    st.session_state.chat_history.append((text, response))

if st.session_state.chat_history:
    st.subheader("🧠 Sohbet Geçmişi")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**{i}. Soru:** {q}")
        st.markdown(f"**{i}. Cevap:** {a}")

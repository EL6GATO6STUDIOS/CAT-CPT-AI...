import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import random
import json

# ---- TDK sözlükten anlam bulma ----
def tdk_lookup(word):
    url = f"https://sozluk.gov.tr/gts?ara={word}"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]["anlamlarListe"][0]["anlam"]
        return None
    except:
        return None

# ---- Rastgele analiz cümlesi üretme ----
def generate_opinion_response(user_input):
    fikir_sablonlari = [
        "Bence {} konusu oldukça düşündürücü. İnsanların karakterine ve bakış açısına göre farklılık gösterebilir.",
        "{} hakkında kendi fikrimi söylemem gerekirse: bu konuda birçok açıdan değerlendirme yapılabilir.",
        "Açıkçası ben {} konusuna farklı bir gözle bakıyorum. Ama herkesin fikrine saygı duyarım.",
        "{} bana kalırsa günümüzde çokça tartışılan bir mesele. Önemli olan kişinin yaklaşımıdır.",
        "{} konusunu düşündüğümde, insanların bunu farklı yorumlayabileceğini görüyorum.",
        "Kendi bakış açıma göre, {} biraz abartılıyor olabilir. Ama yine de farklı görüşler değerlidir.",
        "{} ile ilgili fikrim şu: bu tamamen bağlama göre değişir, ama genel olarak önemli bir konudur.",
    ]
    sablon = random.choice(fikir_sablonlari)
    return sablon.format(user_input.capitalize())

# ---- Sayfa ayarları ----
st.set_page_config(page_title="Cat CPT 😺 (v1.05)", layout="wide")
st.title("Cat CPT 😺 (v1.05)")

# ---- Sohbet geçmişi ----
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---- Kullanıcı giriş alanı ----
text = st.text_input("Sorunuzu yazın:")

# ---- Dosya yükleme alanı ----
uploaded_file = st.file_uploader("Bir dosya yükleyin (.pdf, .txt, .jpg, .png)",
                                 type=["pdf", "txt", "jpg", "jpeg", "png"])

# ---- Dosya gösterimi ----
if uploaded_file is not None:
    file_type = uploaded_file.type
    st.subheader("Yüklenen Dosya:")

    if "pdf" in file_type:
        reader = PdfReader(uploaded_file)
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text()
        st.text_area("PDF İçeriği", all_text)

    elif "text" in file_type:
        content = uploaded_file.read().decode("utf-8")
        st.text_area("Metin Dosyası İçeriği", content)

    elif "image" in file_type:
        img = Image.open(uploaded_file)
        st.image(img, caption="Yüklenen Görsel", use_column_width=True)

# ---- Kullanıcı metni işleme ----
if text:
    original_text = text
    lower_text = text.lower()

    # Sözlük araması isteyen sorular
    if any(keyword in lower_text for keyword in ["ne demek", "anlamı", "nedir", "kelime"]):
        kelimeler = original_text.split()
        cevaplar = []
        for kelime in kelimeler:
            meaning = tdk_lookup(kelime)
            if meaning:
                cevaplar.append(f"**{kelime}**: {meaning}")
        if cevaplar:
            response = "📖 TDK Sözlüğüne göre:\n" + "\n".join(cevaplar)
        else:
            response = "Aradığınız kelimelerin anlamını bulamadım."

    # Analiz (yorumlama) isteyen ifadeler
    elif any(keyword in lower_text for keyword in ["sence", "yorumla", "analiz", "ne düşünüyorsun", "karakter", "tartış", "duygusal", "kişilik"]):
        response = generate_opinion_response(original_text)

    # Diğer tüm sorular için Google araştırması
    else:
        response = "Araştırılıyor..."
        try:
            results = list(search(original_text, num_results=1))
            if results:
                url = results[0]
                res = requests.get(url, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")
                paragraphs = soup.find_all("p")
                found = False
                for p in paragraphs:
                    if len(p.text.strip()) > 50:
                        response = f"Sorduğun şeyle ilgili şöyle bir bilgi buldum: {p.text.strip()}"
                        found = True
                        break
                if not found:
                    response = "Uygun bir bilgi bulunamadı."
            else:
                response = "Sonuç bulunamadı."
        except Exception as e:
            response = f"Araştırma sırasında bir hata oluştu: {str(e)}"

    # ---- Sohbet geçmişine ekle ----
    st.session_state.chat_history.append((original_text, response))

# ---- Geçmişi sırayla göster ----
if st.session_state.chat_history:
    st.subheader("🧠 Sohbet Geçmişi")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**{i}. Soru:** {q}")
        st.markdown(f"**{i}. Cevap:** {a}")

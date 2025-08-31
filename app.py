import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, parse_qs
import random

# Sayfa başlığı ve ayarları
st.set_page_config(page_title="Cat CPT 😺", layout="wide")
st.title("Cat CPT 😺")

# Sohbet geçmişi
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Kullanıcıdan giriş al
text = st.text_input("Sorunuzu yazın:")

# --- Yardımcılar ---

def extract_real_url(href: str) -> str:
    """
    DuckDuckGo bazı sonuçları /l/?uddg=... şeklinde yönlendirir.
    Bu fonksiyon gerçek hedef URL'yi çıkarır.
    """
    try:
        parts = urlsplit(href)
        if parts.path.startswith("/l/"):
            qs = parse_qs(parts.query)
            if "uddg" in qs and qs["uddg"]:
                return qs["uddg"][0]
        return href
    except Exception:
        return href

def ddg_search(query: str, k: int = 3):
    """
    DuckDuckGo HTML endpoint ile basit arama.
    API anahtarı gerekmez.
    """
    url = "https://duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }
    try:
        resp = requests.get(url, params={"q": query}, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.select("a.result__a"):
            href = a.get("href", "").strip()
            if not href:
                continue
            real = extract_real_url(href)
            if real.startswith("http"):
                links.append(real)
            if len(links) >= k:
                break
        return links
    except Exception:
        return []

def fetch_first_paragraph(src_url: str) -> str | None:
    """
    Verilen sayfadan anlamlı (>= 80 karakter) ilk paragrafı çeker.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    }
    try:
        r = requests.get(src_url, headers=headers, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for p in soup.find_all("p"):
            txt = (p.get_text() or "").strip()
            if len(txt) >= 80:
                return txt
        return None
    except Exception:
        return None

def generate_opinion_response(user_input: str) -> str:
    """
    Analiz/yorum cümleleri (şablonsuz, daha doğal ton; yine de çeşit için küçük bir havuz).
    """
    fikirler = [
        f"'{user_input}' konusunu değerlendirirken bağlam, amaç ve etkiler birlikte düşünülmeli. "
        f"Bence sağlıklı çıkarım, varsayımları açık etmek ve karşıt görüşleri de tartmakla mümkün olur.",

        f"Sorduğun '{user_input}' meselesi, tek bir doğru yanıtı olmayan, zemini bağlama göre değişen bir konu. "
        f"Ben, ölçülü bir yaklaşımın uzun vadede daha tutarlı sonuç verdiğini düşünüyorum.",

        f"'{user_input}' hakkında net bir sonuca varmadan önce, hem verileri hem de olası önyargıları kontrol etmek gerekir. "
        f"Bana göre iyi bir değerlendirme; kanıt, tutarlılık ve açıklık üretir."
    ]
    return random.choice(fikirler)

# --- Ana akış ---

if text:
    original_text = text
    lower_text = text.lower()

    # Analiz/yorum (gündelik kalıpları kaldırıldı; kendi cevabını üretiyor)
    if any(k in lower_text for k in ["sence", "yorumla", "analiz", "ne düşünüyorsun", "fikir", "görüş"]):
        response = generate_opinion_response(original_text)

    else:
        # Web araması (DuckDuckGo) + sayfadan anlamlı paragraf çekme
        response = "Araştırılıyor..."
        links = ddg_search(original_text, k=3)

        if not links:
            response = "🔍 Uygun bir sonuç bulamadım. Sorguyu biraz daha açıklayabilir veya farklı bir ifade deneyebilirsin."
        else:
            paragraph = None
            used_url = None
            for u in links:
                para = fetch_first_paragraph(u)
                if para:
                    paragraph = para
                    used_url = u
                    break
            if paragraph:
                # Bulduğu bilgiyi cümle içinde kullan
                response = (
                    f"Sorduğun konuyu taradığımda öne çıkan temel bilgi şu şekilde anlatılıyor: {paragraph} "
                    f"(Kaynak: {used_url})"
                )
            else:
                response = f"Doğrudan alıntılanabilir bir açıklama bulamadım; yine de şu kaynaklara göz atabilirsin: " + \
                           " • ".join(links)

    # Sohbet geçmişine ekle ve göster
    st.session_state.chat_history.append((original_text, response))

# Sohbet geçmişini sırayla göster
if st.session_state.chat_history:
    st.subheader("🧠 Sohbet Geçmişi")
    for i, (q, a) in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**{i}. Soru:** {q}")
        st.markdown(f"**{i}. Cevap:** {a}")

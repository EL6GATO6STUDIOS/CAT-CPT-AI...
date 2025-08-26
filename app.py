    import streamlit as st
import requests
import json

st.set_page_config(page_title="Cat CPT 😺", layout="wide")
st.title("Cat CPT 😺")

API_URL = "http://localhost:8000/v1/chat/completions"  # API adresi
API_KEY = "public-key-123"  # ortak key

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Kullanıcıdan giriş al
user_input = st.chat_input("Mesajınızı yazın...")

if user_input:
    # Kullanıcı mesajını göster
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    headers = {"x-api-key": API_KEY}
    payload = {
        "messages": [{"role": "user", "content": user_input}]
    }

    # Asistan cevabını yazdır
    with st.chat_message("assistant"):
        response_box = st.empty()
        full_response = ""

        try:
            with requests.post(API_URL, json=payload, headers=headers, stream=True, timeout=60) as r:
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8")
                        if decoded.startswith("data: "):
                            data = decoded[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                content = json.loads(data)["choices"][0]["delta"].get("content", "")
                                full_response += content
                                response_box.markdown(full_response)
                            except Exception:
                                continue
        except Exception as e:
            full_response = f"⚠️ Sunucuya bağlanırken hata oluştu: {e}"
            response_box.markdown(full_response)

    st.session_state.chat_history.append(("assistant", full_response))

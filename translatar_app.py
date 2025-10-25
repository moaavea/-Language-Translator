import streamlit as st
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import PyPDF2
import os
from io import BytesIO

# ---------- CONFIG ----------
st.set_page_config(page_title="🌍 Smart Translator", page_icon="🈯", layout="wide")

# ---------- INITIAL SETUP ----------
if "history" not in st.session_state:
    st.session_state["history"] = []

translator = Translator()

# ---------- SIDEBAR ----------
st.sidebar.title("⚙️ Settings")

# 🎨 Color theme selection
color_themes = {
    "Classic White": {"bg": "#F5F6FA", "text": "#000000"},
    "Ocean Blue": {"bg": "#E3F2FD41", "text": "#0D47A1"},
    "Mint Green": {"bg": "#E8F5F0", "text": "#1B5E20"},
    "Sunset Orange": {"bg": "#FFF3E0AA", "text": "#E65100"},
    "Midnight Black": {"bg": "#212121", "text": "#FAFAFA"}
}

selected_theme = st.sidebar.selectbox("🎨 Choose Color Theme", list(color_themes.keys()))

bg_color = color_themes[selected_theme]["bg"]
text_color = color_themes[selected_theme]["text"]

# Apply color theme with HTML + CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Language selection
src_lang = st.sidebar.selectbox("Source Language", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index('english'))
tgt_lang = st.sidebar.selectbox("Target Language", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index('urdu'))

# File upload
uploaded_file = st.sidebar.file_uploader("📂 Upload File (PDF or TXT)", type=["pdf", "txt"])

# Buttons
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state["history"].clear()
    st.rerun()

# ---------- MAIN INTERFACE ----------
st.title("🌍 Smart Language Translator")
st.markdown("Translate text or documents instantly — with chat history, speech, and color themes!")

# Text input
text_input = st.text_area("✏️ Enter text to translate:", height=150)

# Read file content if uploaded
file_text = ""
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            file_text += page.extract_text()
    elif uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")

if file_text:
    st.info("📄 Extracted Text from File:")
    st.text_area("File Content", file_text, height=150)

# ---------- TRANSLATION ----------
if st.button("🔄 Translate"):
    text_to_translate = text_input.strip() or file_text.strip()

    if not text_to_translate:
        st.warning("⚠️ Please enter text or upload a file first!")
    else:
        src_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(src_lang)]
        tgt_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(tgt_lang)]

        try:
            translated = translator.translate(text_to_translate, src=src_code, dest=tgt_code)
            st.success("✅ Translation Successful!")

            # Show translation
            st.text_area("Translated Text", translated.text, height=150)

            # Save to chat history
            st.session_state["history"].append({
                "source": text_to_translate,
                "translated": translated.text,
                "from": src_lang,
                "to": tgt_lang
            })

            # 🎧 Text-to-speech
            if st.button("🔊 Listen to Translation"):
                tts = gTTS(translated.text, lang=tgt_code)
                audio_file = "translated_audio.mp3"
                tts.save(audio_file)
                st.audio(audio_file)

        except Exception as e:
            st.error(f"❌ Translation error: {str(e)}")

# ---------- CHAT HISTORY ----------
if st.session_state["history"]:
    st.subheader("💬 Translation History")

    for i, item in enumerate(reversed(st.session_state["history"]), 1):
        st.markdown(f"**{i}. From {item['from'].capitalize()} → {item['to'].capitalize()}**")
        st.write(f"📝 **Original:** {item['source']}")
        st.write(f"🌐 **Translated:** {item['translated']}")
        st.divider()

    # Download full history
    all_text = "\n\n".join(
        [f"From {h['from']} → {h['to']}\nOriginal: {h['source']}\nTranslated: {h['translated']}" for h in st.session_state["history"]]
    )
    buffer = BytesIO(all_text.encode("utf-8"))
    st.download_button("💾 Download Full Chat History", buffer, file_name="translation_history.txt")


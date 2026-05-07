import streamlit as st
import easyocr
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import cv2

st.set_page_config(page_title="SafeFood AI Expert", page_icon="🥗", layout="wide")

st.sidebar.header("🎨 Настройки")
theme_choice = st.sidebar.select_slider("Тема:", options=["Тъмна", "Светла"])

if theme_choice == "Тъмна":
    st.markdown("<style>.main { background-color: #1a1a1a; color: white; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.main { background-color: white; color: black; }</style>", unsafe_allow_html=True)

DANGER_LEVELS = {
    "🚨 КРИТИЧНО": {
        "E102": "Тартразин - Риск от хиперактивност.",
        "E129": "Алура червено - Канцерогенен риск.",
        "E211": "Натриев бензоат - Консервант, риск при смесване с Вит. С.",
        "E250": "Натриев нитрит - Опасен консервант в месата.",
        "E621": "Глутамат - Мощен овкусител, главоболие.",
        "E951": "Аспартам - Изкуствен подсладител.",
        "PALM": "Палмово масло - Наситени мазнини.",
        "SUGAR": "Захар - Високо съдържание."
    }
}

def fix_image(image):
    img = np.array(image.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Увеличаване на мащаба за по-добро четене на малък шрифт
    height, width = img.shape[:2]
    img = cv2.resize(img, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
    
    # Адаптивен праг за изчистване на шума (прави текста отчетлив)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return img

@st.cache_resource
def load_model():
    # Зареждаме английски, защото Е-номерата са с латински букви
    return easyocr.Reader(['en', 'bg'], gpu=False)

st.title("🥗 SafeFood AI")
st.write("Ако не разчита текста, опитайте да снимате на по-силна светлина.")

source = st.radio("Източник:", ["📸 Камера", "📁 Файл"], horizontal=True)
img_file = st.camera_input("Снимай") if source == "📸 Камера" else st.file_uploader("Качи", type=['jpg','png','jpeg'])

if img_file:
    original = Image.open(img_file)
    
    with st.spinner('Анализиране...'):
        processed = fix_image(original)
        reader = load_model()
        result = reader.readtext(processed, detail=0)
        full_text = " ".join(result).upper()
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, use_container_width=True)
        
        with col2:
            st.subheader("Резултат:")
            found = False
            for cat, items in DANGER_LEVELS.items():
                for code, desc in items.items():
                    if code in full_text:
                        st.error(f"{cat}: {desc}")
                        found = True
            
            if not found:
                st.success("Не са открити опасни Е-номера.")
            
            with st.expander("Разчетен текст:"):
                st.write(full_text if full_text else "ИИ не откри текст. Пробвайте по-близо.")

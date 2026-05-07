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
        "E102": "Тартразин", "E129": "Алура червено", "E211": "Натриев бензоат",
        "E250": "Натриев нитрит", "E621": "Глутамат", "E951": "Аспартам",
        "ПАЛМОВО": "Палмово масло", "ХИДРОГЕНИРАНИ": "Трансмазнини"
    },
    "⚠️ ВНИМАНИЕ": {
        "E202": "Калиев сорбат", "ЗАХАР": "Захар", "ГЛЮКОЗО": "Сироп"
    }
}

def ultra_fix_image(image):
    # Превръщане в OpenCV формат
    img = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 1. Изравняване на светлината (премахва отблясъци)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # 2. Шум и размазване (Denoising)
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # 3. Увеличаване за ситен шрифт
    resized = cv2.resize(denoised, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    return resized

@st.cache_resource
def load_model():
    # Добавяме 'en' като приоритет за Е-номерата
    return easyocr.Reader(['en', 'bg'], gpu=False)

st.title("🥗 SafeFood AI")
st.info("💡 СЪВЕТ: Ако има отблясък от лампата върху етикета, променете ъгъла на снимане!")

source = st.radio("Източник:", ["📸 Камера", "📁 Файл"], horizontal=True)
img_file = st.camera_input("Снимай") if source == "📸 Камера" else st.file_uploader("Качи", type=['jpg','png','jpeg'])

if img_file:
    original = Image.open(img_file)
    
    with st.spinner('🔬 ИИ "изчиства" изображението и чете...'):
        processed = ultra_fix_image(original)
        reader = load_model()
        
        # Оптимизирани настройки на детектора
        result = reader.readtext(processed, detail=0, contrast_ths=0.1, adjust_contrast=0.7)
        full_text = " ".join(result).upper()
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, use_container_width=True, caption="Оригинал")
            with st.expander("Виж как ИИ вижда снимката след обработка:"):
                st.image(processed, use_container_width=True)
        
        with col2:
            st.subheader("Резултат:")
            found_any = False
            for cat, items in DANGER_LEVELS.items():
                for code, name in items.items():
                    if code in full_text:
                        st.error(f"{cat}: {name} ({code})")
                        found_any = True
            
            if not found_any and len(full_text) > 5:
                st.success("Не са открити опасни добавки.")
            elif len(full_text) <= 5:
                st.warning("⚠️ Текстът е твърде неясен. Моля, снимайте по-отблизо и без отблясъци.")
            
            with st.expander("Разчетен текст:"):
                st.write(full_text)

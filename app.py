import streamlit as st
import easyocr
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

st.set_page_config(page_title="HealthyFood AI Expert", page_icon="🥗", layout="wide")

st.sidebar.header("🎨 Настройки на изгледа")
theme_choice = st.sidebar.select_slider(
    "Изберете тема:",
    options=["Тъмна", "Светла"]
)

if theme_choice == "Тъмна":
    st.markdown("""
        <style>
        .main { background-color: #1a1a1a; color: #ffffff; }
        .stMarkdown { color: #ffffff; }
        .stButton>button { background-color: #4f4f4f; color: white; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .main { background-color: #ffffff; color: #000000; }
        .stButton>button { border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

DANGER_LEVELS = {
    "🚨 КРИТИЧНО": {
        "E102": "Тартразин - Риск от хиперактивност и тежки алергии.",
        "E129": "Алура червено - Потенциално канцерогенен оцветител.",
        "E250": "Натриев нитрит - Използва се в колбаси, риск от образуване на нитрозамини.",
        "E951": "Аспартам - Изкуствен подсладител, може да влияе на нервната система.",
        "ХИДРОГЕНИРАНИ": "Трансмазнини - Основна причина за сърдечни заболявания.",
    },
    "⚠️ ВНИМАНИЕ": {
        "E211": "Натриев бензоат - В комбинация с витамин С може да бъде вреден.",
        "E621": "Глутамат - Предизвиква изкуствен апетит и главоболие.",
        "ПАЛМОВО МАСЛО": "Нискокачествена мазнина, богата на наситени киселини.",
        "ЗАХАР": "Прекомерното количество води до възпалителни процеси.",
        "ГЛЮКОЗО": "Глюкозо-фруктозен сироп - Натоварва черния дроб."
    }
}

def optimize_image(image):
    img = ImageOps.grayscale(image)
    img = ImageEnhance.Contrast(img).enhance(2.5)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    return img

st.title("🥗 HealthyFood AI: Твоят личен лаборант")
st.write("Провери какво реално съдържа храната ти само със снимка.")
st.divider()

source = st.radio("Източник на изображение:", ["📸 Камера", "📁 Качи файл"], horizontal=True)

img_file = st.camera_input("Сканирай етикета") if source == "📸 Камера" else st.file_uploader("Избери снимка", type=['jpg', 'png', 'jpeg'])

@st.cache_resource
def get_ocr_reader():
    return easyocr.Reader(['bg', 'en'])

if img_file:
    original_img = Image.open(img_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(original_img, caption="Оригинален етикет", use_container_width=True)
    
    with st.spinner('🔬 Извличане на съставките...'):
        processed_img = optimize_image(original_img)
        reader = get_ocr_reader()
        result = reader.readtext(np.array(processed_img), detail=0)
        full_text = " ".join(result).upper()
        
        found_critical = [v for k, v in DANGER_LEVELS["🚨 КРИТИЧНО"].items() if k in full_text]
        found_warning = [v for k, v in DANGER_LEVELS["⚠️ ВНИМАНИЕ"].items() if k in full_text]
        
    with col2:
        st.subheader("📊 Резултати от анализа")
        
        if not found_critical and not found_warning:
            st.success("🥦 Не са открити опасни добавки. Изглежда чисто!")
        else:
            if found_critical:
                for item in found_critical:
                    st.error(item)
            
            if found_warning:
                for item in found_warning:
                    st.warning(item)

        with st.expander("👁️ Виж разчетения текст"):
            st.text_area("Разпознати думи:", full_text, height=150)

st.sidebar.markdown("---")
st.sidebar.info("""
**SafeFood AI**
Приложение за разпознаване на съставки чрез изкуствен интелект.
""")

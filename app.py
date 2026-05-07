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
        "E211": "Натриев бензоат - Риск при смесване с Вит. С.",
        "E250": "Натриев нитрит - Опасен консервант в месата.",
        "E621": "Глутамат - Мощен овкусител, главоболие.",
        "E951": "Аспартам - Изкуствен подсладител.",
        "ПАЛМОВО": "Палмово масло - Вредни наситени мазнини.",
        "ХИДРОГЕНИРАНИ": "Трансмазнини - Риск за сърцето."
    },
    "⚠️ ВНИМАНИЕ": {
        "E171": "Титанов диоксид - Вече забранен в ЕС като оцветител.",
        "E202": "Калиев сорбат - Консервант, може да дразни кожата.",
        "ЗАХАР": "Високо съдържание на захар.",
        "ГЛЮКОЗО": "Глюкозо-фруктозен сироп."
    }
}

def fix_image(image):
    img = np.array(image.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Увеличаваме контраста драстично
    alpha = 2.0 
    beta = 0    
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    # Филтър за премахване на леко размазване (Sharpening)
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    img = cv2.filter2D(img, -1, kernel)
    
    return img

@st.cache_resource
def load_model():
    return easyocr.Reader(['bg', 'en'], gpu=False)

st.title("🥗 SafeFood AI")
st.write("Снимайте етикета отблизо и на фокус за най-добър резултат.")

source = st.radio("Източник:", ["📸 Камера", "📁 Файл"], horizontal=True)
img_file = st.camera_input("Снимай") if source == "📸 Камера" else st.file_uploader("Качи", type=['jpg','png','jpeg'])

if img_file:
    original = Image.open(img_file)
    
    with st.spinner('Анализиране на съставките...'):
        processed = fix_image(original)
        reader = load_model()
        result = reader.readtext(processed, detail=0, paragraph=True)
        full_text = " ".join(result).upper()
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(original, use_container_width=True)
        
        with col2:
            st.subheader("Резултат:")
            found = []
            
            for cat, items in DANGER_LEVELS.items():
                for code, desc in items.items():
                    if code in full_text:
                        found.append(f"{cat}: {desc}")
            
            if found:
                for item in found:
                    st.error(item)
            else:
                st.success("Не са открити критични съставки от базата ни данни.")
            
            with st.expander("Виж какво разчете ИИ:"):
                if full_text.strip():
                    st.write(full_text)
                else:
                    st.write("Текстът е твърде размазан. Опитай отново с по-стабилна ръка.")

import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="AI 도서 비서 - 최종 검증판", page_icon="💡")
st.title("💡 도서 비서 (자동 모델 탐지 버전)")

# 1. API 키 설정
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API 키를 Secrets에 입력해주세요!")
    st.stop()

genai.configure(api_key=api_key)

# 2. [핵심] 사용 가능한 모델 자동으로 찾기
@st.cache_resource
def find_available_model():
    try:
        # 내 API 키가 쓸 수 있는 모델 목록을 가져옵니다.
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 그 중 1.5-flash가 들어간 최신 모델을 먼저 찾습니다.
        for m_name in models:
            if '1.5-flash' in m_name:
                return genai.GenerativeModel(m_name)
        # 없으면 목록 중 첫 번째 모델이라도 가져옵니다.
        return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"모델 목록을 가져오지 못했습니다: {e}")
        return None

model = find_available_model()

# 3. 사진 분석 로직
img_file = st.camera_input("책을 찍어주세요")
if img_file:
    img = Image.open(img_file)
    st.image(img, caption="촬영된 사진", use_container_width=True)
    
    if st.button("AI에게 물어보기"):
        if model is None:
            st.error("사용 가능한 AI 모델이 없습니다.")
        else:
            with st.spinner(f"AI({model.model_name})가 분석 중..."):
                try:
                    prompt = "이 사진 속의 책 내용을 한국어로 아주 쉽게 설명해줘."
                    response = model.generate_content([prompt, img])
                    st.success("✅ 분석 완료!")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"분석 중 에러 발생: {e}")

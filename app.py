import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 설정: 화면을 넓게(wide) 쓰고 제목을 설정합니다.
st.set_page_config(
    page_title="Book Holder - AI 도서 비서",
    page_icon="📖",
    layout="wide" # 화면을 꽉 차게 만들어 카메라 크기를 키웁니다.
)

# 2. 카메라 화면을 더 크게 만들기 위한 커스텀 디자인(CSS)
st.markdown("""
    <style>
    /* 카메라 입력창의 너비를 100%로 강제 확대 */
    div[data-testid="stCameraInput"] {
        width: 100% !important;
        max-width: 1000px !important; 
        margin: 0 auto;
    }
    /* 버튼 디자인 강조 */
    .stButton>button {
        width: 100%;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        font-size: 1.2em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📖 Book Holder: 고화질 도서 분석 비서")

# 3. 사용자 안내 (화질 및 손떨림 문제 해결 가이드)
st.warning("💡 **고화질/손떨림 방지가 필요할 때:** 폰의 '기본 카메라 앱'으로 찍은 뒤 **[📁 파일 업로드]** 탭을 이용하세요! 브라우저 카메라는 화질 제한이 있습니다.")

# 4. API 키 설정
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API 키가 설정되지 않았습니다. Secrets 설정을 확인해주세요.")
    st.stop()

genai.configure(api_key=api_key)

# 5. 자동 모델 탐지 로직 (성공했던 코드 유지)
@st.cache_resource
def find_available_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m_name in models:
            if '1.5-flash' in m_name:
                return genai.GenerativeModel(m_name)
        return genai.GenerativeModel(models[0])
    except Exception as e:
        st.error(f"모델 탐지 실패: {e}")
        return None

model = find_available_model()

# 6. 메인 기능 구현 (탭 구성)
tab1, tab2 = st.tabs(["📷 크게 찍기 (퀵 스캔)", "📁 고화질 파일 올리기 (추천)"])

def run_analysis(image):
    if image:
        img = Image.open(image)
        # 화면에 찍은 사진 표시
        st.image(img, caption="분석할 이미지", use_container_width=True)
        
        if st.button("🚀 AI에게 분석 요청하기"):
            with st.spinner("Gemini가 정밀 분석 중입니다..."):
                try:
                    prompt = "이 사진 속 책 내용을 한국어로 아주 상세하게 설명해줘. 전문적인 내용이라면 쉽게 풀어서 설명해줘."
                    response = model.generate_content([prompt, img])
                    st.success("✅ 분석 완료!")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")

with tab1:
    st.subheader("카메라로 바로 찍기")
    camera_img = st.camera_input("카메라를 허용하고 사진을 찍어주세요")
    run_analysis(camera_img)

with tab2:
    st.subheader("폰 카메라 앱으로 찍은 고화질 사진 올리기")
    st.info("가장 추천하는 방법입니다. 폰 카메라의 '손떨림 보정'과 '고화질'을 그대로 쓸 수 있습니다.")
    upload_img = st.file_uploader("사진 파일을 선택하세요", type=['jpg', 'jpeg', 'png', 'webp'])
    run_analysis(upload_img)

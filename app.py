import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 기본 설정
st.set_page_config(page_title="나만의 도서 해설 비서", page_icon="📖")

st.title("📖 나만의 도서 해설 비서 (최종본)")
st.write("책 사진을 찍거나 업로드하면 Gemini AI가 내용을 설명해줍니다.")

# 2. API 키 설정 (Streamlit Secrets 사용)
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ API 키가 설정되지 않았습니다. Streamlit Settings > Secrets에 키를 입력해주세요.")
    st.stop()

# 구글 AI 설정
genai.configure(api_key=api_key)

# 3. 모델 설정 (가장 안정적인 호출 방식)
# 최신 모델인 gemini-1.5-flash를 사용합니다.
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. 화면 구성 (탭 사용)
tab1, tab2 = st.tabs(["📷 카메라로 찍기", "📁 파일 업로드"])

def process_image(img_file):
    """이미지를 분석하고 결과를 화면에 출력하는 함수"""
    if img_file is not None:
        image = Image.open(img_file)
        st.image(image, caption="선택된 이미지", use_container_width=True)
        
        if st.button("AI에게 분석 요청하기"):
            with st.spinner("Gemini AI가 책을 읽고 있습니다... 🔍"):
                try:
                    # AI에게 던지는 질문(프롬프트)
                    prompt = "이 사진은 책의 표지이거나 본문입니다. 내용을 한국어로 친절하고 자세하게 설명해주세요."
                    response = model.generate_content([prompt, image])
                    
                    st.success("✅ 분석 완료!")
                    st.markdown("### 🤖 AI의 설명")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"❌ 에러가 발생했습니다: {e}")
                    st.info("Tip: API 키가 유효한지, 혹은 잠시 후 다시 시도해보세요.")

with tab1:
    camera_img = st.camera_input("책을 카메라에 비춰주세요")
    process_image(camera_img)

with tab2:
    upload_img = st.file_uploader("이미지 파일을 선택하세요", type=['jpg', 'jpeg', 'png'])
    process_image(upload_img)

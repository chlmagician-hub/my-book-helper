import io
from typing import Optional

import streamlit as st
from PIL import Image
import google.generativeai as genai


def init_page() -> None:
    """기본 페이지 설정."""
    st.set_page_config(
        page_title="Gemini 책 사진 설명 앱",
        page_icon="📚",
        layout="centered",
    )

    st.title("📚 Gemini 책 사진 설명 앱")
    st.write(
        "책 **표지**나 **페이지** 사진을 올리면, "
        "Google **Gemini**가 한국어로 쉽게 설명해주는 간단한 웹 앱입니다."
    )


@st.cache_resource
def get_model() -> genai.GenerativeModel:
    """Gemini 모델 초기화 (캐시)."""
    api_key: Optional[str] = None

    # 1순위: Streamlit secrets
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")  # type: ignore[attr-defined]
    except Exception:
        api_key = None

    # 2순위: 환경 변수 (옵션)
    if not api_key:
        import os

        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "❗ Gemini API 키가 설정되지 않았어요.\n\n"
            "아래 README의 안내대로 `.streamlit/secrets.toml` 이나 "
            "환경 변수 `GEMINI_API_KEY`를 설정해 주세요."
        )
        st.stop()

    genai.configure(api_key=api_key)
    return genai.GenerativeModel("models/gemini-1.5-flash-latest")


def extract_image_bytes(uploaded_file) -> tuple[bytes, str]:
    """Streamlit UploadedFile에서 바이너리와 MIME 타입을 추출."""
    mime_type = getattr(uploaded_file, "type", "image/jpeg")
    data: bytes = uploaded_file.getvalue()
    return data, mime_type


def describe_book_image(image_bytes: bytes, mime_type: str) -> str:
    """Gemini에게 책 사진을 설명해 달라고 요청."""
    model = get_model()

    prompt = (
        "이 이미지는 책의 표지이거나 책 속 페이지(본문)입니다.\n"
        "다음 내용을 한국어로 자세하고 이해하기 쉽게 설명해 주세요.\n\n"
        "1. 책의 제목, 저자, 출판사 등 겉표지에서 보이는 정보\n"
        "2. (가능하다면) 책의 대략적인 주제나 분위기\n"
        "3. 본문 페이지라면, 글과 그림의 내용을 요약\n"
        "4. 일반 독자가 이해하기 쉬운 말로 친절하게 설명\n"
    )

    image_part = {
        "mime_type": mime_type,
        "data": image_bytes,
    }

    response = model.generate_content([prompt, image_part])
    return response.text or "설명을 가져오지 못했어요. 다시 시도해 주세요."


def main() -> None:
    init_page()

    with st.sidebar:
        st.header("⚙️ 사용 방법")
        st.markdown(
            "- **1단계**: 아래에서 사진을 찍거나 업로드합니다.\n"
            "- **2단계**: `이 사진 분석하기` 버튼을 누릅니다.\n"
            "- **3단계**: 잠시 기다리면 Gemini가 한국어로 설명을 보여줍니다.\n"
        )

    tab_camera, tab_upload = st.tabs(["📷 카메라로 찍기", "📁 파일 업로드"])

    with tab_camera:
        st.subheader("카메라로 책 사진 찍기")
        camera_image = st.camera_input("웹캠으로 책 사진을 찍어 주세요.")

        if camera_image and st.button("이 사진 분석하기", key="analyze_camera"):
            with st.spinner("Gemini가 책 사진을 읽는 중입니다... 📖"):
                image_bytes, mime_type = extract_image_bytes(camera_image)
                try:
                    description = describe_book_image(image_bytes, mime_type)
                except Exception as e:  # noqa: BLE001
                    st.error(f"에러가 발생했어요: {e}")
                else:
                    st.subheader("🧠 Gemini의 설명")
                    st.write(description)

    with tab_upload:
        st.subheader("파일로 책 사진 업로드")
        uploaded_file = st.file_uploader(
            "책 표지나 페이지 사진을 업로드해 주세요.",
            type=["jpg", "jpeg", "png", "webp"],
        )

        if uploaded_file and st.button("이 사진 분석하기", key="analyze_upload"):
            with st.spinner("Gemini가 책 사진을 읽는 중입니다... 📖"):
                image_bytes, mime_type = extract_image_bytes(uploaded_file)
                try:
                    description = describe_book_image(image_bytes, mime_type)
                except Exception as e:  # noqa: BLE001
                    st.error(f"에러가 발생했어요: {e}")
                else:
                    st.subheader("🧠 Gemini의 설명")
                    st.write(description)


if __name__ == "__main__":
    main()




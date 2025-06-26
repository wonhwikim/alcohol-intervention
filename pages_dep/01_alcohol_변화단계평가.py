import json
import os

import streamlit as st

from alcohol_TTM import TTMChatbot

# Initialize session states
if "messages_TTM" not in st.session_state:
    st.session_state.messages_TTM = []

if "therapist_TTM" not in st.session_state:
    st.session_state.therapist_TTM = None

if "current_version_TTM" not in st.session_state:
    st.session_state.current_version_TTM = 2  # Default to version 2


def initialize_therapist(version):
    """Initialize the MI therapist_TTM with OpenAI API key and version"""
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    st.session_state.therapist_TTM = TTMChatbot(
        openai_api_key=openai_api_key, version=version
    )
    # Add initial message from therapist_TTM
    if not st.session_state.messages_TTM:
        initial_message = "안녕하세요. 오늘 음주 행동 변화에 대해 이야기를 나눠보려고 합니다. 현재 음주가 걱정되거나 변화가 필요하다고 생각하시나요?"
        st.session_state.messages_TTM.append(
            {"role": "assistant", "content": initial_message}
        )


def parse_stage(response: str) -> str:
    """변화단계 평가 결과를 파싱"""
    try:
        if "STAGE_RESULT:" in response:
            # STAGE_RESULT: 다음에 나오는 단계명 추출
            stage = response.split("STAGE_RESULT:")[1].strip()
            return stage
    except:
        return "평가 불가"
    return "평가 불가"


def main():
    # Add version selector in sidebar
    st.sidebar.title("버전 선택")
    version_descriptions_TTM = {1: "V1", 2: "V2(최신버전)"}
    selected_version_TTM = st.sidebar.radio(
        "테스트할 버전을 선택하세요:",
        options=list(version_descriptions_TTM.keys()),
        format_func=lambda x: version_descriptions_TTM[x],
    )

    # Reset conversation if version changes
    if selected_version_TTM != st.session_state.current_version_TTM:
        st.session_state.messages_TTM = []
        st.session_state.therapist_TTM = None
        st.session_state.current_version_TTM = selected_version_TTM

    st.title("🤝 변화단계평가 챗봇")
    st.write(
        "이 챗봇은 범이론적 모형 (Transtheoretical model)에 기반한 변화단계평가를 수행합니다."
    )

    # Version info
    st.info(f"현재 버전 (TTM): {version_descriptions_TTM[selected_version_TTM]}")

    # Initialize therapist_TTM if not already initialized
    if st.session_state.therapist_TTM is None:
        initialize_therapist(selected_version_TTM)

    # Display chat messages_TTM
    for message in st.session_state.messages_TTM:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # Add user message to chat history
        st.session_state.messages_TTM.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            response = st.session_state.therapist_TTM.get_response(prompt)
            st.markdown(response)
            st.session_state.messages_TTM.append(
                {"role": "assistant", "content": response}
            )

            # 마지막 메시지에서 변화단계 파싱
            stage = parse_stage(response)
            if stage != "평가 불가":
                st.success(f"📊 평가된 변화단계: {stage}")

    # Add a reset button
    if st.button("대화 초기화"):
        st.session_state.messages_TTM = []
        if st.session_state.therapist_TTM:
            st.session_state.therapist_TTM.clear_memory()
        initialize_therapist(selected_version_TTM)
        st.rerun()


if __name__ == "__main__":
    main()

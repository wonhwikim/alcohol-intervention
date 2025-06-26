import streamlit as st

from src.chatbots import TTMChatbot

# st.set_page_config(
#     page_title="TTM Chatbot",
#     page_icon="⛰️",
#     initial_sidebar_state="expanded",
# )

# Initialize session states
if "messages_TTM" not in st.session_state:
    st.session_state.messages_TTM = []

if "TTM_chatbot" not in st.session_state:
    st.session_state.TTM_chatbot = None

if "current_version_TTM" not in st.session_state:
    st.session_state.current_version_TTM = 0  # Default to version 0 (V3)

if "session_started_TTM" not in st.session_state:
    st.session_state.session_started_TTM = False

TTM_VERSION_DICT = {0: "V3 + Guardrail"}


def initialize_TTM_chatbot(prompt_version: int) -> None:
    """Initialize the TTM therapist with OpenAI API key and version"""
    openai_api_key = st.secrets["OPENAI_API_KEY"]

    # Add initial message from TTM_chatbot if not present
    if not st.session_state.messages_TTM:
        initial_message = "안녕하세요, 저는 오늘 당신의 음주 습관에 대해 이야기해보고자 합니다. 현재의 음주 습관이 걱정되거나, 변화가 필요하다고 생각하시나요?"
        st.session_state.messages_TTM.append(
            {"role": "assistant", "content": initial_message}
        )

    # Initialize the TTM chatbot with initial message
    st.session_state.TTM_chatbot = TTMChatbot(
        openai_api_key=openai_api_key,
        version=prompt_version,
        history=st.session_state.messages_TTM,
    )

    return


def parse_stage(response: str) -> str:
    """Parse the stage from the response"""
    try:
        if "STAGE_RESULT:" in response:
            # Extract the stage name after STAGE_RESULT:
            stage = response.split("STAGE_RESULT:")[1].strip()
            return stage

    except:
        return "평가 불가"

    return "평가 불가"


def main():
    # Add version selector in sidebar
    if not st.session_state.session_started_TTM:
        # Prompt version selection
        st.sidebar.title("TTM 프롬프트 버전 선택")

        # Prompt version selector
        selected_version_TTM = st.sidebar.radio(
            "테스트할 프롬프트 버전을 선택하세요:",
            options=list(TTM_VERSION_DICT.keys()),
            format_func=lambda x: TTM_VERSION_DICT[x],
            key="version_select_TTM",
            index=st.session_state.current_version_TTM,  # Default to current version
        )

        # Reset conversation if version changes
        if selected_version_TTM != st.session_state.current_version_TTM:
            st.session_state.current_version_TTM = selected_version_TTM
            st.session_state.messages_TTM = []
            st.session_state.TTM_chatbot = None

        # Start session button
        if st.sidebar.button("대화 시작"):
            st.session_state.session_started_TTM = True
            initialize_TTM_chatbot(prompt_version=st.session_state.current_version_TTM)

            st.rerun()
    else:  # If session has started
        st.sidebar.title("현재 대화 설정")
        st.sidebar.text(
            f"현재 프롬프트 버전: {TTM_VERSION_DICT[st.session_state.current_version_TTM]}"
        )

    # Main area
    st.title("⛰️ 변화단계평가 챗봇")
    st.markdown(
        "> 이 챗봇은 범이론적 모형 (Transtheoretical Model)에 기반한 변화단계평가를 수행합니다."
    )

    # Initialize TTM chatbot if needed
    if st.session_state.TTM_chatbot is None and st.session_state.session_started_TTM:
        initialize_TTM_chatbot(prompt_version=st.session_state.current_version_TTM)

    # Display chat messages_TTM
    for message in st.session_state.messages_TTM:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # chat_input 비활성화 제어
    prompt = st.chat_input(
        "메시지를 입력하세요...", disabled=not st.session_state.session_started_TTM
    )

    if prompt:
        # Add user message to chat history
        st.session_state.messages_TTM.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            response = st.session_state.TTM_chatbot.get_response(prompt)
            st.markdown(response)
            st.session_state.messages_TTM.append(
                {"role": "assistant", "content": response}
            )

            # Parse and display stage if available
            stage = parse_stage(response)
            if stage != "평가 불가":
                st.success(f"📊 평가된 변화단계: {stage}")

    # Reset button
    if st.button("대화 초기화"):
        st.session_state.messages_TTM = []
        st.session_state.session_started_TTM = False

        if st.session_state.TTM_chatbot:
            st.session_state.TTM_chatbot.clear_memory()
        st.rerun()


if __name__ == "__main__":
    main()

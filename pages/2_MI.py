import datetime

import streamlit as st

from src.chatbots import MIChatbot

st.set_page_config(
    page_title="MI Chatbot",
    page_icon="🤝",
    initial_sidebar_state="expanded",
)

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "therapist" not in st.session_state:
    st.session_state.therapist = None

if "current_version" not in st.session_state:
    st.session_state.current_version = 0  # Default to version 0 (V5 + guardrail)

# Add to session state initialization section:
if "stage" not in st.session_state:
    st.session_state.stage = 1  # Default to stage 1

if "session_started" not in st.session_state:
    st.session_state.session_started = False

if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.datetime.now()

STAGE_DICT = {
    1: "고려전 (Precontemplation)",
    2: "고려 (Contemplation)",
    3: "준비 (Preparation)",
    4: "실천 (Action)",
    5: "유지 (Maintenance)",
    6: "종결 (Termination)",
}

VERSION_DICT = {0: "V5 + Guardrail"}


def initialize_MI_chatbot(prompt_version: int) -> None:
    """Initialize the MI chatbot with OpenAI API key and version"""
    openai_api_key = st.secrets["OPENAI_API_KEY"]

    st.session_state.therapist = MIChatbot(
        openai_api_key=openai_api_key, version=prompt_version
    )

    # Add initial message from therapist
    if not st.session_state.messages:
        initial_message = (
            "안녕하세요, 저는 당신의 동기부여 상담사입니다. 오늘 상담을 시작해볼까요?"
        )

        st.session_state.messages.append(
            {"role": "assistant", "content": initial_message}
        )

    # Initialize MI chatbot with initial message
    st.session_state.therapist = MIChatbot(
        openai_api_key=openai_api_key,
        version=prompt_version,
        history=st.session_state.messages,
    )

    return


def main():
    # Before session starts, allow prompt version & stage of change selection
    if not st.session_state.session_started:
        # Prompt version selection area
        st.sidebar.title("프롬프트 버전 선택")

        # Prompt version selector
        selected_version = st.sidebar.radio(
            "테스트할 프롬프트 버전을 선택하세요:",
            options=list(VERSION_DICT.keys()),
            format_func=lambda x: VERSION_DICT[x],
            key="version_select",
            index=st.session_state.current_version,  # Default to current version
        )

        # Re-initialize therapist if version changes
        if selected_version != st.session_state.current_version:
            st.session_state.current_version = selected_version
            st.session_state.messages = []
            st.session_state.therapist = None

        # Stage of change selection area
        st.sidebar.title("변화단계 선택")

        # Stage of change selection radio button
        selected_stage = st.sidebar.radio(
            "환자(본인)의 변화단계를 선택하세요:",
            options=list(STAGE_DICT.keys()),
            format_func=lambda x: STAGE_DICT[x],
            key="stage_select",
            index=st.session_state.stage - 1,  # Default to current stage
        )

        # Start session button
        if st.sidebar.button("대화 시작"):
            st.session_state.session_started = True
            st.session_state.stage = selected_stage
            initialize_MI_chatbot(prompt_version=st.session_state.current_version)
            st.session_state.start_time = datetime.datetime.now()

            st.rerun()

    else:  # After session has started
        st.sidebar.title("현재 대화 설정")
        st.sidebar.text(f"버전: {VERSION_DICT[st.session_state.current_version]}")
        st.sidebar.text(f"변화단계: {STAGE_DICT[st.session_state.stage]}")
        st.sidebar.text(
            f"시작 시간: {st.session_state.start_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # Main area
    st.title("🤝 알코올 중독 동기부여 상담 챗봇")
    st.markdown(
        "> 이 챗봇은 동기부여면담(Motivational Interviewing) 기법을 사용하여 당신의 변화를 돕습니다."
    )

    # Initialize therapist if needed
    if st.session_state.therapist is None and st.session_state.session_started:
        initialize_MI_chatbot(prompt_version=st.session_state.current_version)

    # Display chat messages with timestamps for user messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "user" and "timestamp" in message:
                elapsed_time = message["timestamp"] - st.session_state.start_time
                elapsed_minutes = int(elapsed_time.total_seconds() / 60)
                elapsed_seconds = int(elapsed_time.total_seconds() % 60)
                timestamp_str = message["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(
                    f"<p style='font-size: 12px; text-align: right; color: gray;'>{timestamp_str} ({elapsed_minutes:02d}:{elapsed_seconds:02d} 경과)</p>",
                    unsafe_allow_html=True,
                )
    if prompt := st.chat_input("메시지를 입력하세요..."):
        timestamp = datetime.datetime.now()
        elapsed_time = timestamp - st.session_state.start_time
        elapsed_minutes = int(elapsed_time.total_seconds() / 60)
        elapsed_seconds = int(elapsed_time.total_seconds() % 60)
        elapsed_time_message = f"\n[Total elapsed time: {elapsed_minutes} minutes.]"

        st.session_state.messages.append(
            {"role": "user", "content": prompt, "timestamp": timestamp}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(
                f"<p style='font-size: 12px; text-align: right; color: gray;'>{timestamp_str} ({elapsed_minutes:02d}:{elapsed_seconds:02d} 경과)</p>",
                unsafe_allow_html=True,
            )

        with st.chat_message("assistant"):
            response = st.session_state.therapist.get_response(
                prompt + elapsed_time_message, st.session_state.stage
            )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Reset button
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.session_started = False

        if st.session_state.therapist:
            st.session_state.therapist.clear_memory()
        st.rerun()


if __name__ == "__main__":
    main()

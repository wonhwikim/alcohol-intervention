import datetime
import json

import streamlit as st

from src.chatbots import MIChatbot

st.set_page_config(
    #     page_title="MI Chatbot",
    #     page_icon="🤝",
    initial_sidebar_state="expanded",
)

# Define dictionaries for stages, versions, and initial prompts
STAGE_DICT = {
    1: "고려전 (Precontemplation)",
    2: "고려 (Contemplation)",
    3: "준비 (Preparation)",
    4: "실천 (Action)",
    5: "유지 (Maintenance)",
    6: "종결 (Termination)",
}


VERSION_DICT = {0: "V5 (V4 수정 + Guardrail)", 1: "V6 (4판 기반 + Guardrail)"}

INITIAL_PROMPT_DICT = {
    0: "안녕하세요, 반갑습니다. 오늘 상담을 시작해볼까요? 오늘 내담자님께서 경험하신 일이나, 들었던 생각 또는 감정에 대해 이야기해볼까요?",
    1: "안녕하세요, 저는 당신의 동기부여 상담사입니다. 오늘 상담을 시작해볼까요?",
}

# Load data from json files - onboarding data, self-reports, and session notes
with open("json/example_onboarding.json", "rt", encoding="utf-8") as f:
    onboarding_data = json.load(f)
onboarding_data_s = json.dumps(onboarding_data, indent=2, ensure_ascii=False)

with open("json/example_daily.json", "rt", encoding="utf-8") as f:
    self_reports = json.load(f)
self_reports_s = json.dumps(self_reports, indent=2, ensure_ascii=False)


with open("json/example_notes.json", "rt", encoding="utf-8") as f:
    session_notes = json.load(f)
session_number = len(session_notes) + 1

notes_s = ""
for note in session_notes:
    notes_s += f"""Session {note["sessionNumber"]} ({note["sessionDateTime"][:10]}): {note["sessionNotes"]}\n"""

# Initialize session states
if "MI_chatbot" not in st.session_state:
    st.session_state.MI_chatbot = None

if "messages_MI" not in st.session_state:
    st.session_state.messages_MI = []

if "system_prompt_ver_MI" not in st.session_state:
    st.session_state.system_prompt_ver_MI = 0

if "initial_prompt_ver_MI" not in st.session_state:
    st.session_state.initial_prompt_ver_MI = 0

if "stage" not in st.session_state:
    st.session_state.stage = 1

if "session_started_MI" not in st.session_state:
    st.session_state.session_started_MI = False

if "start_time_MI" not in st.session_state:
    st.session_state.start_time_MI = datetime.datetime.now()


def initialize_MI_chatbot(prompt_version: int) -> None:
    """Initialize the MI chatbot with OpenAI API key and version"""
    openai_api_key = st.secrets["OPENAI_API_KEY"]  # type: ignore

    # Add initial message from MI_chatbot if not present
    if not st.session_state.messages_MI:
        initial_message = INITIAL_PROMPT_DICT[st.session_state.initial_prompt_ver_MI]
        st.session_state.messages_MI.append(
            {"role": "assistant", "content": initial_message}
        )

    # Initialize MI_chatbot with initial message
    st.session_state.MI_chatbot = MIChatbot(
        openai_api_key=openai_api_key,
        version=prompt_version,
        history=st.session_state.messages_MI,
    )

    return


def parse_end_of_session(response: str):
    """Parse the end-of-session indicator from the response"""
    if "[END-OF-SESSION]" in response:
        # Extract the summary after the end-of-session indicator
        summary = response.split("[END-OF-SESSION]")[1].strip()
        return summary
    return False


def main():
    # Main area
    st.title("🤝 음주 문제 동기부여 상담 챗봇")
    st.markdown(
        "> 이 챗봇은 동기부여면담(Motivational Interviewing) 기법을 사용하여 당신의 변화를 돕습니다."
    )

    # Sidebar area
    st.sidebar.title("동기부여면담 챗봇 설정")

    if not st.session_state.session_started_MI:
        # Prompt version selection
        st.sidebar.markdown("## MI 프롬프트 버전 선택")

        selected_system_prompt = st.sidebar.radio(
            "테스트할 프롬프트 버전을 선택하세요:",
            options=list(VERSION_DICT.keys()),
            format_func=lambda x: VERSION_DICT[x],
            key="version_select",
            index=st.session_state.system_prompt_ver_MI,
        )

        # Re-initialize therapist if version changes
        if selected_system_prompt != st.session_state.system_prompt_ver_MI:
            st.session_state.system_prompt_ver_MI = selected_system_prompt
            st.session_state.messages_MI = []
            st.session_state.MI_chatbot = None

        # Stage of change selection area
        st.sidebar.markdown("## 변화단계 선택")

        selected_stage = st.sidebar.radio(
            "환자(본인)의 변화단계를 선택하세요:",
            options=list(STAGE_DICT.keys()),
            format_func=lambda x: STAGE_DICT[x],
            key="stage_select",
            index=st.session_state.stage - 1,  # Default to current stage
        )

        if selected_stage != st.session_state.stage:
            st.session_state.stage = selected_stage
            st.session_state.messages_MI = []
            st.session_state.MI_chatbot = None

        # Initial prompt selection area
        st.sidebar.markdown("## 챗봇 첫 메시지 선택")

        selected_initial_prompt = st.sidebar.radio(
            "챗봇의 첫 메시지를 선택하세요:",
            options=list(INITIAL_PROMPT_DICT.keys()),
            format_func=lambda x: INITIAL_PROMPT_DICT[x],
            key="initial_prompt_select",
            index=st.session_state.initial_prompt_ver_MI,
        )

        if selected_initial_prompt != st.session_state.initial_prompt_ver_MI:
            st.session_state.initial_prompt_ver_MI = selected_initial_prompt
            st.session_state.messages_MI = []
            st.session_state.MI_chatbot = None

        # Start session button
        if st.sidebar.button("대화 시작"):
            st.session_state.session_started_MI = True
            st.session_state.stage = selected_stage
            initialize_MI_chatbot(prompt_version=st.session_state.system_prompt_ver_MI)
            st.session_state.start_time_MI = datetime.datetime.now()

            st.rerun()

    else:  # After session has started
        st.sidebar.markdown("## 현재 대화 설정")
        st.sidebar.text(f"버전: {VERSION_DICT[st.session_state.system_prompt_ver_MI]}")
        st.sidebar.text(f"변화단계: {STAGE_DICT[st.session_state.stage]}")
        st.sidebar.text(
            f"시작 시간: {st.session_state.start_time_MI.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    # Initialize therapist if needed
    if st.session_state.MI_chatbot is None and st.session_state.session_started_MI:
        initialize_MI_chatbot(prompt_version=st.session_state.system_prompt_ver_MI)

    # Display chat messages with timestamps for user messages
    for message in st.session_state.messages_MI:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "user" and "timestamp" in message:
                elapsed_time = message["timestamp"] - st.session_state.start_time_MI
                elapsed_minutes = int(elapsed_time.total_seconds() / 60)
                elapsed_seconds = int(elapsed_time.total_seconds() % 60)
                timestamp_str = message["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                st.markdown(
                    f"<p style='font-size: 12px; text-align: right; color: gray;'>{timestamp_str} ({elapsed_minutes:02d}:{elapsed_seconds:02d} 경과)</p>",
                    unsafe_allow_html=True,
                )
            if message["role"] == "assistant" and parse_end_of_session(
                message["content"]
            ):
                st.success("📜 세션이 종료되었습니다.")

    # Chat input area - disabled if session not started
    prompt = st.chat_input(
        "메시지를 입력하세요...", disabled=not st.session_state.session_started_MI
    )

    if not st.session_state.session_started_MI:
        st.info(
            "💡 메시지를 입력하기 전에 👈 사이드바에서 프롬프트 버전과 변화단계를 선택하세요."
        )

    if prompt:
        timestamp = datetime.datetime.now()
        elapsed_time = timestamp - st.session_state.start_time_MI
        elapsed_minutes = int(elapsed_time.total_seconds() / 60)
        elapsed_seconds = int(elapsed_time.total_seconds() % 60)
        elapsed_time_message = f"\n[Total elapsed time: {elapsed_minutes} minutes.]"

        st.session_state.messages_MI.append(
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

            payload = {
                "STAGE": STAGE_DICT.get(st.session_state.stage, "UNKNOWN"),
                "ONBOARDING-DATA": onboarding_data_s,
                "SELF-REPORTS": self_reports_s,
                "SESSION-NUMBER": session_number,
                "SESSION-NOTES": notes_s,
                "SESSION-DATE": st.session_state.start_time_MI.strftime("%Y-%m-%d"),
            }

            # print(payload)

            response = st.session_state.MI_chatbot.get_response(
                prompt + elapsed_time_message, payload
            )
            st.markdown(response)
            st.session_state.messages_MI.append(
                {"role": "assistant", "content": response}
            )

            # Parse end-of-session
            if summary := parse_end_of_session(response):
                print(summary)
                st.success("📜 세션이 종료되었습니다.")
                st.session_state.session_started_MI = False
                st.rerun()

    # Reset button
    if st.button("대화 초기화"):
        st.session_state.messages_MI = []
        st.session_state.session_started_MI = False

        if st.session_state.MI_chatbot:
            st.session_state.MI_chatbot.clear_memory()
        st.rerun()


if __name__ == "__main__":
    main()

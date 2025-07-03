import datetime
import json
import time

import streamlit as st

from src.chatbots import MIChatbot

st.set_page_config(
    #     page_title="MI Chatbot",
    #     page_icon="🤝",
    initial_sidebar_state="expanded",
)


def initialize_session_states():
    """Initialize session states for MI chatbot"""
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

    if "selected_onboarding_MI" not in st.session_state:
        st.session_state.selected_onboarding_MI = 0
    if "selected_selfreport_MI" not in st.session_state:
        st.session_state.selected_selfreport_MI = 0
    if "selected_session_notes" not in st.session_state:
        st.session_state.selected_session_notes = 0

    if "onboardings" not in st.session_state:
        with open("json/example_onboarding.json", "r", encoding="utf-8") as f:
            data = json.load(f)

            st.session_state.onboardings = {i: data[i] for i in range(len(data))}

    if "self_reports" not in st.session_state:
        with open("json/example_selfreports.json", "rt", encoding="utf-8") as f:
            data = json.load(f)

            st.session_state.self_reports = {i: data[i] for i in range(len(data))}

    if "session_series" not in st.session_state:
        with open("json/example_notes.json", "rt", encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.session_series = {i: data[i] for i in range(len(data))}

    if "session_notes" not in st.session_state:
        if st.session_state.session_series != {}:
            st.session_state.session_notes = st.session_state.session_series[0]["data"]
        else:
            st.session_state.session_notes = []

    if "session_number" not in st.session_state:
        # Initialize session number based on the length of session notes
        st.session_state.session_number = len(st.session_state.session_notes) + 1

    return


# Load data from json files - onboarding data, self-reports, and session notes
# Each json file is structured as a list of dictionaries
# Convert each list to dictionary for easier access


# Define dictionaries for stages, versions, and initial prompts
STAGE_DICT = {
    1: "고려전 (Precontemplation)",
    2: "고려 (Contemplation)",
    3: "준비 (Preparation)",
    4: "실천 (Action)",
    5: "유지 (Maintenance)",
    6: "종결 (Termination)",
}

VERSION_DICT = {
    0: "V5 (V4 수정 + Guardrail)",
    1: "V6 (4판 기반 + 내담자 데이터 + Guardrail)",
}

INITIAL_PROMPT_DICT = {
    0: "안녕하세요, 반갑습니다. 오늘 상담을 시작하겠습니다. 오늘 내담자님께서 경험하신 일이나, 들었던 생각 또는 감정에 대해 이야기해볼까요?",
    1: f"안녕하세요, 시작해볼까요?",
}

ONBOARDING_EMPTY = {
    "label": "",
    "data": {
        "birthday": "",
        "gender": "",
        "occupation": "",
        "education": "",
        "maritalStatus": "",
        "smoking": "",
        "psychiatricHistory": "",
    },
}

SELF_REPORT_EMPTY = {
    "label": "",
    "data": {
        "mood": "",
        "interest": "",
        "meal": {
            "breakfast": "",
            "lunch": "",
            "dinner": "",
            "midnightSnack": "",
        },
        "drinking": {
            "drinkedToday": "",
            "details": {
                "timeOfDay": "",
                "type": "",
                "amount": "",
                "withWho": "",
                "forHowLong": "",
                "where": "",
                "reason": [],
                "blackout": "",
            },
        },
        "sleep": {
            "timeSlept": "",
            "timeWokeUp": "",
            "satisfaction": "",
            "fatigue": "",
        },
    },
}


@st.dialog("💾 데이터 보기", width="large")
def display_data(data: str):
    """Display the selected onboarding data in a modal dialog"""
    st.markdown("# 데이터 보기")
    st.json(data, expanded=True)


@st.dialog("➕ 데이터 추가", width="large")
def add_custom_data(category: str):
    if category == "onboarding":
        st.markdown("# 온보딩 데이터 추가")
        input = st.text_area(
            "온보딩 데이터를 입력하세요 (JSON 형식)",
            value=json.dumps(ONBOARDING_EMPTY, ensure_ascii=False, indent=2),
            key="custom_onboarding_data",
            height=300,
        )
        if st.button("온보딩 데이터 추가"):
            try:
                custom_data = json.loads(input)
                if isinstance(custom_data, dict) and "data" in custom_data:
                    new_key = len(st.session_state.onboardings)
                    st.session_state.onboardings[new_key] = {
                        "label": custom_data["label"],
                        "data": custom_data["data"],
                    }
                    st.success("온보딩 데이터가 추가되었습니다.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("잘못된 온보딩 데이터 형식입니다.")
            except json.JSONDecodeError:
                st.error("유효하지 않은 JSON 형식입니다.")
    elif category == "selfreport":
        st.markdown("# 자기보고 데이터 추가")
        input = st.text_area(
            "자기보고 데이터를 입력하세요 (JSON 형식)",
            value=json.dumps(SELF_REPORT_EMPTY, ensure_ascii=False, indent=2),
            key="custom_selfreport_data",
            height=600,
        )
        if st.button("자기보고 데이터 추가"):
            try:
                custom_data = json.loads(input)
                if isinstance(custom_data, dict) and "data" in custom_data:
                    new_key = len(st.session_state.self_reports)
                    st.session_state.self_reports[new_key] = {
                        "label": custom_data["label"],
                        "data": custom_data["data"],
                    }
                    st.success("자기보고 데이터가 추가되었습니다.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("잘못된 자기보고 데이터 형식입니다.")
            except json.JSONDecodeError:
                st.error("유효하지 않은 JSON 형식입니다.")
    else:
        raise ValueError("Invalid category. Choose 'onboarding' or 'selfreport'.")


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
    initialize_session_states()

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

        st.sidebar.markdown("## 내담자 데이터 선택 (V6 전용)")
        if st.session_state.system_prompt_ver_MI == 1:
            # Client data selection area
            # Client onboarding data
            st.sidebar.markdown("### 온보딩 데이터")
            selected_onboarding = st.sidebar.selectbox(
                "내담자의 온보딩 데이터를 선택하세요:",
                options=list(st.session_state.onboardings.keys()),
                format_func=lambda x: st.session_state.onboardings[int(x)]["label"],
                key="onboarding_select",
                index=st.session_state.selected_onboarding_MI,
            )
            if selected_onboarding != st.session_state.selected_onboarding_MI:
                st.session_state.selected_onboarding_MI = selected_onboarding
                onboarding_data_s = st.session_state.onboardings[selected_onboarding][
                    "data"
                ]
                st.session_state.messages_MI = []
                st.session_state.MI_chatbot = None

            # Button to view selected onboarding data - display data in a modal
            if st.sidebar.button("선택한 온보딩 데이터 보기"):
                display_data(
                    json.dumps(
                        st.session_state.onboardings[
                            st.session_state.selected_onboarding_MI
                        ],
                        ensure_ascii=False,
                    )
                )

            # Button to add custom onboarding data
            if st.sidebar.button("온보딩 데이터 추가"):
                add_custom_data(category="onboarding")

            # Client self-reports data
            st.sidebar.markdown("### 자기보고 데이터 선택")
            selected_selfreport = st.sidebar.selectbox(
                "내담자의 자기보고 데이터를 선택하세요:",
                options=list(st.session_state.self_reports.keys()),
                format_func=lambda x: st.session_state.self_reports[int(x)]["label"],
                key="selfreport_select",
                index=st.session_state.selected_selfreport_MI,
            )

            if selected_selfreport != st.session_state.selected_selfreport_MI:
                st.session_state.selected_selfreport_MI = selected_selfreport
                self_reports_s = st.session_state.self_reports[selected_selfreport]
                st.session_state.messages_MI = []
                st.session_state.MI_chatbot = None

            if st.sidebar.button("선택한 자기보고 데이터 보기"):
                display_data(
                    json.dumps(
                        st.session_state.self_reports[
                            st.session_state.selected_selfreport_MI
                        ],
                        ensure_ascii=False,
                    )
                )

            # Button to add custom self-report data
            if st.sidebar.button("자기보고 데이터 추가"):
                add_custom_data(category="selfreport")

            # Session notes (only viewing for now)
            st.sidebar.markdown("### 지난 회기 기록 선택")
            selected_session_series = st.sidebar.selectbox(
                "지난 회기 기록을 선택하세요:",
                options=list(st.session_state.session_series.keys()),
                format_func=lambda x: st.session_state.session_series[int(x)]["label"],
                key="session_notes_select",
                index=st.session_state.selected_session_notes,
            )

            if selected_session_series != st.session_state.selected_session_notes:
                st.session_state.selected_session_notes = selected_session_series
                st.session_state.session_notes = st.session_state.session_series[
                    selected_session_series
                ]["data"]
                st.session_state.session_number = (
                    len(st.session_state.session_notes) + 1
                )
                st.session_state.messages_MI = []
                st.session_state.MI_chatbot = None

            st.sidebar.button(
                "지난 회기 기록 보기",
                on_click=display_data,
                args=(json.dumps(st.session_state.session_notes, ensure_ascii=False),),
            )
        else:
            st.sidebar.markdown("(비활성)")

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
        st.sidebar.markdown(f"### 프롬프트 버전")
        st.sidebar.markdown(f"{VERSION_DICT[st.session_state.system_prompt_ver_MI]}")

        st.sidebar.markdown("### 변화단계")
        st.sidebar.markdown(f"{STAGE_DICT[st.session_state.stage]}")

        if st.session_state.system_prompt_ver_MI == 1:
            st.sidebar.markdown("### 온보딩 데이터")
            st.sidebar.markdown(
                f"{st.session_state.onboardings[st.session_state.selected_onboarding_MI]['label']}"
            )
            st.sidebar.button(
                "온보딩 데이터 보기",
                on_click=display_data,
                args=(
                    json.dumps(
                        st.session_state.onboardings[
                            st.session_state.selected_onboarding_MI
                        ],
                        ensure_ascii=False,
                    ),
                ),
            )

            st.sidebar.markdown("### 자기보고 데이터")
            st.sidebar.markdown(
                f"{st.session_state.self_reports[st.session_state.selected_selfreport_MI]['label']}"
            )

            st.sidebar.button(
                "자기보고 데이터 보기",
                on_click=display_data,
                args=(
                    json.dumps(
                        st.session_state.self_reports[
                            st.session_state.selected_selfreport_MI
                        ],
                        ensure_ascii=False,
                    ),
                ),
            )

        st.sidebar.markdown("### 시작 시간")
        st.sidebar.markdown(
            f"{st.session_state.start_time_MI.strftime('%Y-%m-%d %H:%M:%S')}"
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
                st.success("⚠️ 세션이 종료되었습니다.")

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
        elapsed_minutes = int(elapsed_time.total_seconds() // 60)
        elapsed_seconds = int(elapsed_time.total_seconds() % 60)
        elapsed_time_message = (
            f"\n[Total elapsed time: {elapsed_minutes} minutes.]"
            if elapsed_minutes >= 14
            else ""
        )

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

            onboarding_data_s = json.dumps(
                st.session_state.onboardings[st.session_state.selected_onboarding_MI][
                    "data"
                ]
            )
            self_reports_s = json.dumps(
                st.session_state.self_reports[st.session_state.selected_selfreport_MI]
            )

            payload = {
                "STAGE": STAGE_DICT.get(st.session_state.stage, "UNKNOWN"),
                "ONBOARDING-DATA": onboarding_data_s,
                "SELF-REPORTS": self_reports_s,
                "SESSION-NUMBER": st.session_state.session_number,
                "SESSION-NOTES": st.session_state.session_notes,
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

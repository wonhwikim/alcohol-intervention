import streamlit as st

st.set_page_config(
    page_title="Alcohol Intervention",
    page_icon="🤖",
)

# st.title("🤖 Alcohol Intervention")
# st.markdown("왼쪽 사이드바에서 원하는 페이지를 선택하세요.")

pages = [
    st.Page("src/1_TTM.py", title="변화단계평가 (TTM)", icon="⛰️"),
    st.Page("src/2_MI.py", title="동기부여면담 (MI)", icon="🤝"),
]

current_page = st.navigation(pages, position="top", expanded=True)
current_page.run()

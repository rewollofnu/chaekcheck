# main.py
import streamlit as st
from streamlit_option_menu import option_menu

# from ocrMain import get_titles
import my_book
import enroll_book
import pic_upload
import recommend_book

st.set_page_config(page_title="My Book")

# session state 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'my_book'

# 페이지 선택을 위한 사이드바 메뉴
with st.sidebar:
    st.session_state.page = option_menu(
        menu_title="My Book",  # 메뉴 제목
        options=["my_book", "pic_upload", "enroll_book", "recommend_book"],  # 메뉴 옵션
        icons=["book", "image", "pencil", "star"],  # 아이콘 (선택 사항)
        menu_icon="cast",  # 메뉴 아이콘 (선택 사항)
        default_index=["my_book", "pic_upload", "enroll_book", "recommend_book"].index(st.session_state.page),  # 기본 선택 인덱스
    )

# 선택한 페이지 호출
if st.session_state.page == "my_book":
    my_book.app()
elif st.session_state.page == "enroll_book":
    enroll_book.app()
elif st.session_state.page == "pic_upload":
    pic_upload.app()
elif st.session_state.page == "recommend_book":
    recommend_book.app()

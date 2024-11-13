from ocrMain import get_titles

import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
import pymysql
import datetime
from PIL import Image

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

def get_db_connection():
    return pymysql.connect(
        host=os.environ["a_host"],
        port=int(os.environ["a_port"]),
        database=os.environ["a_database"],
        user=os.environ["a_user"],
        password=os.environ["a_password"],
        charset=os.environ['charset']
    )

conn = get_db_connection()
cursor = conn.cursor()

def app():
    st.header("📕 책 등록하기", divider="rainbow")
    st.caption("인식된 책 제목이 맞는지 확인해주세요.")

    if 'uploaded_pic' not in st.session_state:
        st.warning("책 정보가 없습니다. 먼저 책 사진을 업로드하세요.")
        return

    # 이전 페이지에서 가져온 책 정보
    if st.session_state.need_detect:
        st.session_state.detected_books = get_titles(Image.open(st.session_state.uploaded_pic))
        st.session_state.need_detect = False

    edited_books = []
    st.subheader("인식된 책 정보")
    for idx, book in enumerate(st.session_state.detected_books):
        with st.expander(f"책 {idx + 1}: {book}"):
            new_title = st.text_input(f"책 제목 {idx + 1}", value=book)
            edited_books.append({"title": new_title})

    if st.button('책 등록하기', type="primary", use_container_width=True):
        st.session_state.edited_books = edited_books
        add_books_to_shelf(edited_books)

    if st.button('나의 서재 확인하기', use_container_width=True):
        st.session_state.page = 'my_book'


def generate_unique_url(counter):
    # 현재 날짜와 시간을 "YYYYMMDDHHMMSS" 형식으로 포맷합니다.
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 카운터와 조합하여 URL을 생성합니다.
    return f"user1_unfinedbook_{current_time}_{counter:04d}"


# 콜백 함수 정의
def on_yes():
    # 예 선택 시 책을 DB에 추가하는 로직
    with conn.cursor() as cursor:
        for idx, title in enumerate(st.session_state.missing_books):
            url = generate_unique_url(idx)
            cursor.execute(
                "INSERT INTO tb_book (title, categories, url) VALUES (%s, %s, %s)",
                (title, "temp", url)
            )
            book_id = cursor.lastrowid
            cursor.execute("INSERT INTO tb_user_books (book_id) VALUES (%s)", (book_id,))
        conn.commit()
    st.session_state.message = "책 등록이 완료되었습니다. chaek chek~!"


def on_no():
    # 아니오 선택 시 표시할 메시지
    st.session_state.message = "책 등록이 취소되었습니다."


# 세션 상태에 'message' 키가 없으면 초기화
if 'message' not in st.session_state:
    st.session_state.message = ''


def add_books_to_shelf(books):
    missing_books = []  # 없는 책을 모으는 리스트
    existing_books = []  # 이미 있는 책을 모으는 리스트

    with conn.cursor() as cursor:
        for book in books:
            title = book["title"]

            # DB에서 책이 있는지 확인
            cursor.execute("SELECT id FROM tb_book WHERE title = %s", (title,))
            result = cursor.fetchone()

            if result:
                book_id = result[0]
                cursor.execute("SELECT * FROM tb_user_books WHERE book_id = %s", (book_id,))
                if cursor.fetchone() is None:
                    cursor.execute("INSERT INTO tb_user_books (book_id) VALUES (%s)", (book_id,))
                else:
                    existing_books.append(title)  # 이미 있는 책은 리스트에 추가
            else:
                missing_books.append(title)  # 없는 책은 리스트에 추가

    # 이미 있는 책들에 대해 알림 메시지
    if existing_books:
        existing_books_str = ', '.join(existing_books)
        st.info(f"'{existing_books_str}'은(는) 이미 내 책장에 있어요. :)")

    # 없는 책들에 대해 추가 여부 묻기
    if missing_books:
        missing_books_str = ', '.join(missing_books)
        
        # missing_books 리스트를 세션 상태로 저장
        st.session_state.missing_books = missing_books

        # selectbox를 통해 사용자에게 선택지 제공
        choice = st.selectbox(
            f"""{missing_books_str}을(를) 찾을 수 없습니다.\n나만의 책장에 추가하시겠어요?""",
            ("예", "아니오"),
            key='choice'  # 세션 상태에서 값을 참조할 수 있도록 키 설정
        )

        # 버튼 클릭 시 콜백 함수 실행
        if choice == "예":
            st.button("확인", on_click=on_yes)
        else:
            st.button("확인", on_click=on_no)


# 버튼 클릭 후 메시지 표시
if st.session_state.message:
    st.success(st.session_state.message)


# Streamlit 앱 실행
if __name__ == "__main__":
    app()

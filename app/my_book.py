import streamlit as st
import pandas as pd
import pymysql
import os
from dotenv import load_dotenv, find_dotenv

def app():
    st.header("📚책쳌(Chaek Check)", divider="rainbow")
    st.markdown("# 🚀나의 서재")

    dotenv_file = find_dotenv()
    load_dotenv(dotenv_file)

    # 데이터베이스 연결 함수
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

    # 책 목록 쿼리 실행

    with conn.cursor() as cursor:
        query = "SELECT b.title AS 책제목, b.author AS 저자 FROM tb_user_books ub JOIN tb_book b ON ub.book_id = b.id"
        cursor.execute(query)
        rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=['Title', 'Author'])

    # 체크박스 상태를 저장할 세션 스테이트 초기화
    if 'selected_books' not in st.session_state:
        st.session_state.selected_books = []

    # 체크박스와 책 목록을 표시
    st.caption("선택한 도서를 기반으로 책을 추천해드려요.")
    for index, row in df.iterrows():
        # 각 책에 대해 체크박스 생성
        if st.checkbox(f"{row['Title']} | {row['Author']}", key=f"book_{index}"):
            if row['Title'] not in st.session_state.selected_books:
                st.session_state.selected_books.append(row['Title'])
        else:
            if row['Title'] in st.session_state.selected_books:
                st.session_state.selected_books.remove(row['Title'])

    # 책 등록하기 버튼
    if st.button('책 등록하기', use_container_width=True):
        st.session_state.page = 'pic_upload'
        st.rerun()  # 페이지 이동

    # 삭제하기 버튼을 눌렀을 때 선택된 책을 삭제
    if st.button('삭제하기',type="primary", use_container_width=True):
        if st.session_state.selected_books:
            # 데이터베이스 연결
            with conn.cursor() as cursor:
                for title in st.session_state.selected_books:
                    # 책 제목을 이용해 book_id 조회
                    cursor.execute("SELECT id FROM tb_book WHERE title = %s", (title,))
                    result = cursor.fetchone()
                    
                    if result:  # book_id가 존재할 경우
                        book_id = result[0]
                        # tb_user_books에서 삭제
                        cursor.execute("DELETE FROM tb_user_books WHERE book_id = %s", (book_id,))
                
                conn.commit()
            
            st.success("선택한 책들이 삭제되었습니다.")
            st.session_state.selected_books = []  # 선택된 책 목록 초기화
            st.rerun()
        else:
            st.warning("삭제할 책을 선택해주세요.")
    
    st.write(" ")
    st.write(" ")
    st.write(" ")

    # MMR 파라미터
    st.subheader("얼마나 새로운 책을 만나고 싶으세요?")
    mmr_alpha = st.slider("숫자가 클수록 다양한 종류의 책을 만날 수 있어요.", min_value=0, max_value=10, value=5, step=1)
    st.session_state.mmr_alpha = 1-(mmr_alpha/20)

    # 추천받기 버튼 클릭 시 recommend_book 페이지로 이동
    if st.button('추천받기', use_container_width=True):
        if st.session_state.selected_books:
            st.session_state.page = 'recommend_book'
            st.rerun()  # 페이지 이동
        else:
            st.warning("추천을 받기 위해서는 책을 하나 이상 선택해주세요.")


# Streamlit app execution
if __name__ == '__main__':
    app()

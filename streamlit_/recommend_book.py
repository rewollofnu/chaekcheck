from recsys import Recsys

import streamlit as st
import pymysql
import pandas as pd

import os
from dotenv import load_dotenv, find_dotenv

def app():
    # 데이터베이스 연결
    def get_db_connection():
        return pymysql.connect(
            host=os.environ["a_host"],
            port=int(os.environ["a_port"]),
            database=os.environ["a_database"],
            user=os.environ["a_user"],
            password=os.environ["a_password"],
            charset=os.environ['charset']
        )
    

    # 페이지 상태가 'my_book'이 아닌 경우에만 추천 로직 실행
    if st.session_state.get('page', '') != 'my_book':
        conn = get_db_connection()

        st.header("📖 추천 도서", divider="rainbow")
        st.caption("선택하신 책을 기반으로 추천해드려요.")
        
        selected_books = st.session_state.get('selected_books', [])

        if selected_books:
            st.subheader('🌈추천 책 목록')

            # DB에서 데이터 가져오기
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tb_book;")
                result = cursor.fetchall()  # 모든 결과 가져오기
                columns = [desc[0] for desc in cursor.description]  # 컬럼명 가져오기

                df = pd.DataFrame(result, columns=columns)

            tfidf_matrix_path = r"tfidf_matrix.npz"
            recsys = Recsys(df, tfidf_matrix_path)
            results = recsys.recommend_books(selected_books, alpha=st.session_state.mmr_alpha)

            st.dataframe(results)

            # 선택한 책들 표시
            book_list = ", ".join(selected_books)  # 선택된 책 리스트를 콤마로 구분된 문자열로 변환
            st.info(f"선택한 책: {book_list}")

            st.session_state.selected_books = []
            st.write("")
        else:
            st.write("선택한 책이 없습니다.")

    # 메인 페이지로 돌아가기 버튼 클릭 시 페이지 이동
    if st.button('메인 페이지로 돌아가기', type="primary"):
        st.session_state.page = 'my_book'
        st.rerun()  # 페이지 상태를 변경하고 즉시 다시 렌더링

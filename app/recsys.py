from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import load_npz

import pandas as pd
import numpy as np
import math
import pymysql

import os
from dotenv import load_dotenv, find_dotenv


class Recsys:
    def __init__(self, df_path, tfidf_matrix_path, replace_books_path=r'replace_books.csv') -> None:

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

        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_book;")
            result = cursor.fetchall()  # 모든 결과 가져오기
            columns = [desc[0] for desc in cursor.description]  # 컬럼명 가져오기

        # 결과를 DataFrame으로 변환
        self.df = pd.DataFrame(result, columns=columns)
        self.df.set_index('id', inplace=True)
        self.tfidf_matrix = load_npz(tfidf_matrix_path)
        self.df_replace_books = pd.read_csv(replace_books_path, index_col=0)
        

    def get_related_books(self, q_book, k1=2000, k2=10, alpha=0.5):

        q_book_row = self.df[self.df['title'] == q_book]
        # print(q_book_row.columns)
        if q_book_row.iloc[0].categories == 'temp':
            return self.df_replace_books
        
        q_idx = q_book_row.index[0]
        cosine_sim_1 = cosine_similarity(self.tfidf_matrix[q_idx], self.tfidf_matrix).flatten()

        # 유사도 top_k1 인덱스들
        # similar_book_idxes = cosine_sim_1.argsort()[-(k1+1):][::-1]
        similar_k1_idxes = cosine_sim_1.argpartition(-(k1+1))[-(k1+1):]
        df_top_k1 = self.df.loc[similar_k1_idxes]
        # df_top_k1['similarity'] = cosine_sim_1[similar_book_idxes]
        tfidf_top_k1 = self.tfidf_matrix[similar_k1_idxes, :].toarray()

        # MMR
        cosine_sim_2 = cosine_similarity(tfidf_top_k1, tfidf_top_k1)

        # 쿼리 책 & 유사도
        np_idx = np.argwhere(similar_k1_idxes==q_idx).flatten()[0]
        sim_scores = cosine_sim_2[np_idx]

        # MMR을 위한 초기 후보 목록 생성
        recommended_indexes = []
        ranked_indices = np.argsort(sim_scores)[::-1]  # 내림차순 정렬

        # MMR Search
        for i in ranked_indices[1:]:
            if len(recommended_indexes) >= k2:
                break
            
            if i not in recommended_indexes:
                # MMR 계산
                relevance_score = sim_scores[i]
                diversity_score = sum(cosine_sim_2[i][j] for j in recommended_indexes) if recommended_indexes else 0
                mmr_score = alpha * relevance_score - (1 - alpha) * diversity_score

                # print(i, mmr_score, relevance_score, diversity_score)
                # MMR 점수가 높은 항목 선택
                if mmr_score > 0:
                    # print(i, df_top_k1.iloc[i, 0])
                    recommended_indexes.append(i)
        
        # 추천 결과 반환
        recommended_books = df_top_k1.iloc[recommended_indexes].copy()
        recommended_books['similarity'] = [sim_scores[i] for i in recommended_indexes]
        return recommended_books[['title', 'author']]
    
    def recommend_books(self, q_book_list, k1=2000, k2=10, alpha=0.7):
        n = len(q_book_list)
        bpk = math.ceil(k2/n)

        results = []
        for q_book in q_book_list:
            print(f"'{q_book}'과 유사한 책 찾는 중")
            result = self.get_related_books(q_book, k1=k1, k2=k2, alpha=alpha)[:bpk]
            results.append(result)
        # print(results)
        rc_df = pd.concat(results).iloc[:k2, :].reset_index(drop=True)
        rc_df.index = rc_df.index + 1
        return rc_df


if __name__=='__main__':
    df_path = r'D:\python_project\chaekchecklab\data\emb_value.csv'
    tfidf_matrix_path = r'D:\python_project\chaekchecklab\data\tfidf_matrix.npz'

    recsys = Recsys(df_path, tfidf_matrix_path)

    # q_book = "회계 천재가 된 홍대리"
    q_book_list = ['돈의 물리학', '회계 천재가 된 홍대리', '트렌드 코리아 2025']

    res = recsys.recommend_books(q_book_list)

    print(res)
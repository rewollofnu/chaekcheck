import pymysql
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv

dotenv_file = find_dotenv()
load_dotenv(dotenv_file)

class DataBase:
    def __init__(self) -> None:
        self.conn = pymysql.connect(
            host=os.environ["a_host"],
            port = int(os.environ["a_port"]),
            database =os.environ["a_database"],
            user=os.environ["a_user"],
            password=os.environ["a_password"],
            charset=os.environ['charset']
        )

    def check_databases(self):
        with self.conn.cursor() as cursor: 
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
        return databases

    def show_tables(self) :
        with self.conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;") #SHOW TABLE STATUS : 자세히 보기
            tables = cursor.fetchall()
        return tables
    
    def show_books(self, query) :
        with self.conn.cursor() as cursor:
            cursor.execute(query) #SHOW TABLE STATUS : 자세히 보기
            books = cursor.fetchall()  # 모든 결과를 가져옴
        return books

    
    def make_table(self, query):

        with self.conn.cursor() as cursor :
            cursor.execute(query)
            self.conn.commit()
        return


if __name__=="__main__":
    db = DataBase()

    # 데이터베이스 확인
    databases = db.check_databases()
    print(databases)

    # 테이블 확인
    tables = db.show_tables()
    print(tables)

    # 결과 확인
    book_datas = db.show_books()
    print(book_datas)

    # tb_book 생성
    query_make_table = '''
    CREATE TABLE IF NOT EXISTS tb_book (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    title VARCHAR(500) NOT NULL,
    full_title VARCHAR(500) NULL,
    author VARCHAR(500) NULL,
    translator VARCHAR(500) NULL,
    etc_author VARCHAR(500) NULL,
    author_list VARCHAR(500) NULL,
    publish_date DATE NULL,
    publisher VARCHAR(50) NULL,
    introduction TEXT NULL,
    isbn VARCHAR(20) NULL,
    page VARCHAR(10) NULL,
    categories VARCHAR(500) NOT NULL,
    url VARCHAR(100) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY unique_name (url)
    )
    '''

    # tb_user_books 생성
    query_make_user_table = '''
    CREATE TABLE IF NOT EXISTS tb_user_books (
    id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    book_id INTEGER UNSIGNED NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (book_id) REFERENCES tb_book(id)
    )
    '''

    # tb_category_table 생성
    query_make_category = '''
    CREATE TABLE IF NOT EXISTS tb_category (
    id BIGINT NOT NULL,
    depth_1 VARCHAR(30) NOT NULL,
    depth_2 VARCHAR(30) NULL,
    depth_3 VARCHAR(30) NULL,
    depth_4 VARCHAR(30) NULL,
    depth_5 VARCHAR(100) NULL
    )
    '''

    # db.make_table(query_make_table)
    # db.make_table(query_make_user_table)
    # db.make_table(query_make_category)

    # tb_book 확인
    query_check_all_book = "SELECT * FROM tb_book;"
    
    # 이용자 책장 목록 확인
    query_check_user_books = """
                  SELECT b.title AS 책제목, b.author AS 저자
                  FROM tb_user_books ub
                  JOIN tb_book b ON ub.book_id = b.id;"""
    result = db.show_books(query_check_user_books)
    print(result)



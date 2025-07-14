import os
import sys
import logging
import azure.sql.connector
from pathlib import Path

# 상위 디렉토리를 sys.path에 추가
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from config import SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD

def create_tables():
    """SQL 테이블을 생성합니다."""
    logging.info("SQL 테이블 생성 시작...")
    
    # SQL 스키마 파일 읽기
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # SQL 명령어로 분리
    sql_commands = schema_sql.split(';')
    
    # SQL Database 연결
    try:
        conn = azure.sql.connector.connect(
            server=SQL_SERVER,
            database=SQL_DATABASE,
            user=SQL_USERNAME,
            password=SQL_PASSWORD
        )
        
        cursor = conn.cursor()
        
        # 각 SQL 명령어 실행
        for command in sql_commands:
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    conn.commit()
                    logging.info(f"SQL 명령어 실행 성공: {command[:50]}...")
                except Exception as e:
                    logging.error(f"SQL 명령어 실행 실패: {str(e)}")
                    logging.error(f"실패한 명령어: {command}")
        
        logging.info("SQL 테이블 생성 완료!")
        
    except Exception as e:
        logging.error(f"SQL Database 연결 실패: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    create_tables() 
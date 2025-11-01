import os, pymysql, time

db_host = os.getenv("DB_HOST", "localhost")
db_user = os.getenv("MYSQL_USER")
db_password = os.getenv("MYSQL_PASSWORD")
db_name = os.getenv("MYSQL_DATABASE")
db_port = int(os.getenv("DB_PORT", 3306))

def get_conn():
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db(retries=5, delay=3):
    for i in range(retries):
        try:
            conn = get_conn()
            with conn.cursor() as cursor:
                # todosテーブルにdescriptionとdue_dateを追加
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task VARCHAR(255) NOT NULL,
                    description TEXT,
                    due_date DATE,
                    done BOOLEAN DEFAULT FALSE
                )
                """)
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL
                )
                """)
            conn.commit()
            conn.close()
            print("DB initialized successfully")
            return
        except pymysql.err.OperationalError:
            print(f"DB not ready, retrying in {delay}s... ({i+1}/{retries})")
            time.sleep(delay)
    print("DB Init failed after retries")

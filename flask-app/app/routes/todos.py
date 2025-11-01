from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import pymysql, os, time

todos_bp = Blueprint("todos", __name__)

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
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task VARCHAR(255) NOT NULL,
                    done BOOLEAN DEFAULT FALSE
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

init_db()

# ------- ページ表示 -------
@todos_bp.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("index.html")

# ------- API -------
def check_login():
    if "user" not in session:
        return False, {"error": "ログインしてください"}, 401
    return True, None, None

@todos_bp.route("/todos", methods=["GET"])
def get_todos():
    ok, resp, status = check_login()
    if not ok: return resp, status
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM todos")
            todos = cursor.fetchall()
        conn.close()
        return jsonify(todos)
    except Exception as e:
        return {"error": str(e)}, 500

@todos_bp.route("/todos", methods=["POST"])
def create_todo():
    ok, resp, status = check_login()
    if not ok: return resp, status

    data = request.json
    task = data.get("task")
    if not task:
        return {"error": "task is required"}, 400
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
        conn.commit()
        conn.close()
        return {"message": "Todo created"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@todos_bp.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    ok, resp, status = check_login()
    if not ok: return resp, status

    data = request.json
    done = data.get("done")
    if done is None:
        return {"error": "done is required"}, 400
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE todos SET done=%s WHERE id=%s", (done, todo_id))
        conn.commit()
        conn.close()
        return {"message": "Todo updated"}
    except Exception as e:
        return {"error": str(e)}, 500

@todos_bp.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    ok, resp, status = check_login()
    if not ok: return resp, status

    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM todos WHERE id=%s", (todo_id,))
        conn.commit()
        conn.close()
        return {"message": "Todo deleted"}
    except Exception as e:
        return {"error": str(e)}, 500

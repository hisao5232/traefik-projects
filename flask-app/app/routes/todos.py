from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
import pymysql, os, time, traceback

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
                    description TEXT,
                    due_date DATE,
                    done BOOLEAN DEFAULT FALSE
                )
                """)
            conn.commit()
            conn.close()
            print("DB initialized successfully", flush=True)
            return
        except pymysql.err.OperationalError:
            print(f"DB not ready, retrying in {delay}s... ({i+1}/{retries})", flush=True)
            time.sleep(delay)
    print("DB Init failed after retries", flush=True)

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
            cursor.execute("SELECT * FROM todos ORDER BY id DESC")
            todos = cursor.fetchall()
        conn.close()
        return jsonify(todos)
    except Exception as e:
        print("GET TODOS ERROR:", e, flush=True)
        traceback.print_exc()
        return {"error": str(e)}, 500

@todos_bp.route("/todos", methods=["POST"])
def create_todo():
    ok, resp, status = check_login()
    if not ok: 
        print("Not logged in", flush=True)
        return resp, status

    try:
        data = request.get_json(force=True)  # 強制的に JSON として取得
        print("POST data:", data, flush=True)
    except Exception as e:
        print("Error parsing JSON:", e, flush=True)
        traceback.print_exc()
        return {"error": "Invalid JSON"}, 400

    task = data.get("task")
    description = data.get("description")
    due_date = data.get("due_date") or None

    if not task:
        print("Task is missing", flush=True)
        return {"error": "task is required"}, 400

    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            print("Executing INSERT...", flush=True)
            cursor.execute(
                "INSERT INTO todos (task, description, due_date) VALUES (%s, %s, %s)",
                (task, description, due_date)
            )
        conn.commit()
        conn.close()
        print("Todo created successfully", flush=True)
        return {"message": "Todo created"}, 201
    except Exception as e:
        print("CREATE TODO ERROR:", e, flush=True)
        traceback.print_exc()
        return {"error": str(e)}, 500

@todos_bp.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    ok, resp, status = check_login()
    if not ok: return resp, status

    try:
        data = request.get_json(force=True)
        print(f"PUT data for id={todo_id}:", data, flush=True)
    except Exception as e:
        print("Error parsing JSON:", e, flush=True)
        traceback.print_exc()
        return {"error": "Invalid JSON"}, 400

    task = data.get("task")
    description = data.get("description")
    due_date = data.get("due_date") or None
    done = data.get("done")

    if task is None or done is None:
        return {"error": "taskとdoneは必須です"}, 400

    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE todos SET task=%s, description=%s, due_date=%s, done=%s WHERE id=%s",
                (task, description, due_date, done, todo_id)
            )
        conn.commit()
        conn.close()
        return {"message": "Todo updated"}
    except Exception as e:
        print("UPDATE TODO ERROR:", e, flush=True)
        traceback.print_exc()
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
        print("DELETE TODO ERROR:", e, flush=True)
        traceback.print_exc()
        return {"error": str(e)}, 500

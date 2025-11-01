from flask import Blueprint, render_template, request, session, redirect, url_for
import os

auth_bp = Blueprint("auth", __name__)

USER_ID = os.getenv("USER_ID")
USER_PASSWORD = os.getenv("USER_PASSWORD")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        if user_id == USER_ID and password == USER_PASSWORD:
            session["user"] = user_id
            return redirect(url_for("todos.index"))
        else:
            return render_template("login.html", error="IDまたはパスワードが違います")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))

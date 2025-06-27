from app import app, mysql
from flask import render_template, request, redirect, url_for, session

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department FROM members ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    members = [
        {"id": row[0], "name": row[1], "department": row[2]}
        for row in rows
    ]
    return render_template("members.html", members=members)

@app.route("/member/add", methods=["GET", "POST"])
def add_member():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]
        if not name or not department:
            error = "全ての項目を入力してください"
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO members (name, department) VALUES (%s, %s)", (name, department))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("index"))
    return render_template("member_add.html", error=error)

@app.route("/member/<int:member_id>")
def member_detail(member_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department FROM members WHERE id=%s", (member_id,))
    member = cur.fetchone()
    cur.close()
    if not member:
        return "メンバーが見つかりません", 404
    member_dict = {"id": member[0], "name": member[1], "department": member[2]}
    return render_template("member_detail.html", member=member_dict)

@app.route("/member/<int:member_id>/edit", methods=["GET", "POST"])
def member_edit(member_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, department FROM members WHERE id=%s", (member_id,))
    member = cur.fetchone()
    if not member:
        cur.close()
        return "メンバーが見つかりません", 404
    error = None
    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]
        if not name or not department:
            error = "全ての項目を入力してください"
        else:
            cur.execute("UPDATE members SET name=%s, department=%s WHERE id=%s", (name, department, member_id))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("member_detail", member_id=member_id))
    cur.close()
    member_dict = {"id": member[0], "name": member[1], "department": member[2]}
    return render_template("member_edit.html", member=member_dict, error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("index"))
        else:
            error = "IDまたはパスワードが違います"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/member/<int:member_id>/delete", methods=["POST"])
def member_delete(member_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM members WHERE id=%s", (member_id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index")) 
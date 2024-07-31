from flask import Flask, session, render_template, request, redirect
from supabase import create_client

url, key = "https://qcxjdptketsmrmfuever.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFjeGpkcHRrZXRzbXJtZnVldmVyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjI0MTQ2MzgsImV4cCI6MjAzNzk5MDYzOH0.75JlMm9vQmUbevDb9VdJIEvhDbT6pUfPAwejSyMFxYA" #입력 필요
database = create_client(url, key)

pos_list = ['자습실', '1학년 공강실', '2학년 공강실', '3학년 공강실']

app = Flask(__name__)
app.secret_key = 'secret'

WEB_FULL_URL = "127.0.0.1:5000"

@app.route("/")
def main_page():
    if 'uid' in session:
        return render_template('main_logged_in.html', name=session['name'], title="이석 신청")
    else:
        return render_template('main_not_logged_in.html', title="이석 신청")

@app.route("/login")
def login():
    return render_template("login.html", title="이석 신청:로그인")

@app.route("/register")
def register():
    return render_template("register.html", title="이석 신청:회원가입")

@app.route("/api/login", methods=['POST'])
def login_api():
    uid = database.table("logins").select("uid, name").eq("uid", request.form["id"]).eq("upw", request.form["password"]).execute()
    if len(uid.data) >= 1:
        session["uid"] = uid.data[0]["uid"]
        session["name"] = uid.data[0]["name"]
    return redirect("/")

@app.route("/api/register", methods=['POST'])
def register_api():
    uid = database.table("logins").select("uid").eq("uid", request.form["id"]).execute()
    if len(uid.data) == 0:
        _ = (database.table("logins")
               .insert({"uid": request.form["id"],
                        "upw": request.form["password"],
                        "number": request.form["number"],
                        "name": request.form["name"]})
               .execute())
        _ = (database.table("iseok")
               .insert({"uid": request.form["id"],
                        "current": 0})
               .execute())
        session["uid"] = request.form["id"]
        session["name"] = request.form["name"]
    return redirect("/")

@app.route("/api/logout")
def logout_api():
    session.pop('uid')
    session.pop('name')
    return redirect("/")

@app.route("/view")
def view():
    from_login = {item["uid"]:(item["number"], item["name"]) for item in database.table("logins").select("uid, number, name").execute().data}
    from_iseok = {item["uid"]:item["current"] for item in database.table("iseok").select("uid, current").execute().data}
    data = []
    for item in from_login:
        data.append((*from_login[item], pos_list[from_iseok[item]]))
    return render_template("view.html", data=data, title="이석 현황")


@app.route("/api/dev/reset") #테스트용
def reset():
    database.table("iseok").delete().neq("current", -1).execute()
    database.table("logins").delete().neq("number", 0).execute()
    return redirect("/")

@app.route("/reset") #테스트용
def reset_datas():
    database.table("iseok").delete().neq("current", -1).execute()
    for item in database.table("logins").select("uid").execute().data:
        _ = (database.table("iseok")
               .insert({"uid": item["uid"],
                        "current": 0})
               .execute())
    return redirect("/")

@app.route("/iseok")
def iseok():
    return render_template("iseok.html", title="이석 신청:이석 신청")

@app.route("/api/iseok", methods=['POST'])
def iseok_api():
    _ = (database.table("iseok")
         .update({"current": request.form["pos"]})
         .eq("uid", session["uid"])
         .execute())
    return redirect("/")


app.run()
from flask import Flask, render_template, request, redirect, session, jsonify
from supabase import create_client
import os, bcrypt, requests

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"

SUPABASE_URL = os.environ.get("https://apldxuzvruozepekurxq.supabase.co")
SUPABASE_KEY = os.environ.get("sb_publishable_HdYqujiRN84RoCMQXJuFBA_5A8oJvmv")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

EMOTE_API = "https://bdapi-subo.onrender.com/join"

# ---------------- AUTH PAGE ----------------

@app.route("/auth", methods=["GET","POST"])
def auth():
    if request.method == "POST":

        action = request.form.get("action")
        username = request.form.get("username")
        password = request.form.get("password")

        if action == "register":
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            try:
                supabase.table("users").insert({
                    "username": username,
                    "password": hashed
                }).execute()
                return "Registered Successfully"
            except:
                return "Username Already Exists"

        elif action == "login":
            user = supabase.table("users").select("*").eq("username", username).execute()

            if user.data:
                stored_password = user.data[0]["password"]
                if bcrypt.checkpw(password.encode(), stored_password.encode()):
                    session["user"] = username
                    return redirect("/")
            return "Invalid Credentials"

    return render_template("auth.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/auth")

# ---------------- USER PANEL ----------------

@app.route("/")
def home():
    if not session.get("user"):
        return redirect("/auth")

    emotes = supabase.table("emotes").select("*").execute().data
    return render_template("index.html", emotes=emotes, user=session["user"])

@app.route("/send_emote", methods=["POST"])
def send_emote():
    if not session.get("user"):
        return jsonify({"error":"Login required"})

    team_code = request.form.get("team_code")
    uid = request.form.get("uid")
    emote_id = request.form.get("emote_id")

    requests.get(f"{EMOTE_API}?tc={team_code}&uid1={uid}&emote_id={emote_id}")
    requests.get(f"{EMOTE_API}?tc=1694161&uid1={uid}&emote_id={emote_id}")
    requests.get(f"{EMOTE_API}?tc=3859281&uid1={uid}&emote_id={emote_id}")

    return jsonify({"status":"success"})

if __name__ == "__main__":
    app.run()
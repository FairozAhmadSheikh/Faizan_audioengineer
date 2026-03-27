import os
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

ADMIN_KEY = os.environ.get("ADMIN_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)



load_dotenv()

# Fetch the URI
MONGO_URI = os.getenv("MONGO_URI")

# Safety Check: If MONGO_URI is missing, the app will explain why in the logs
if not MONGO_URI:
    print("CRITICAL: MONGO_URI environment variable is not set!")
    # You can set a dummy string to prevent the immediate InvalidURI crash 
    # during build, but the app will still fail on data fetch.
    MONGO_URI = "mongodb://localhost:27017" 

client = MongoClient(MONGO_URI)
db = client.music_portfolio
app.secret_key = os.environ.get("SECRET_KEY", "secret")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["music_portfolio"]
projects = db["projects"]


@app.route("/")
def home():
    data = list(projects.find().sort("_id", -1))
    return render_template("index.html", projects=data)


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":
        key = request.form.get("key")

        if key == ADMIN_KEY:
            session["admin"] = True
            return redirect("/dashboard")

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/admin")

    data = list(projects.find().sort("_id", -1))
    return render_template("admin_dashboard.html", projects=data)


@app.route("/add", methods=["POST"])
def add():

    if not session.get("admin"):
        return "Unauthorized"

    title = request.form.get("title")
    description = request.form.get("description")
    link = request.form.get("link")

    projects.insert_one({
        "title": title,
        "description": description,
        "link": link
    })

    return redirect("/dashboard")


@app.route("/delete/<id>")
def delete(id):

    if not session.get("admin"):
        return "Unauthorized"

    projects.delete_one({"_id": ObjectId(id)})
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
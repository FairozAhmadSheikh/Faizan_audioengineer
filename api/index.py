import os
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
load_dotenv()

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = os.getenv("SECRET_KEY", "supersecret")

ADMIN_KEY = os.getenv("ADMIN_KEY")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client.music_portfolio
projects = db.projects


@app.route("/")
def home():

    data = list(projects.find().sort("_id",-1))

    return render_template(
        "index.html",
        projects=data
    )


@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        key = request.form.get("key")

        if key == ADMIN_KEY:
            session["admin"] = True
            return redirect("/dashboard")

        return "Invalid Key"

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():

    if not session.get("admin"):
        return redirect("/admin")

    data = list(projects.find().sort("_id",-1))

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


def handler(request):
    return app(request.environ, lambda status, headers: None)


if __name__ == "__main__":
    app.run(debug=True)
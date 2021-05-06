#Importing the needed modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string, random

#Declaring the Flask app and SQLAlchemy database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///urls.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#Assigning the database to the db variable
db = SQLAlchemy(app)

#Defining the database model
class URLs(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key = True)
    long = db.Column("long", db.String())
    short = db.Column("short", db.String(3))
    
    def __init__(self, long, short):
        self.long = long
        self.short = short

#Building the database before the page loads
@app.before_first_request
def create_tables():
    db.create_all()

#The function for shortening the URL, creates a random sequence of 3 letters and checks that it isn't already used in the database
def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters = random.choices(letters, k = 3)
        rand_letters = "".join(rand_letters)
        short_url = URLs.query.filter_by(short = rand_letters).first()
        if not short_url:
            return rand_letters

#Creates the home page and defines what happens if a new URL is entered into the input field for shortening
@app.route('/', methods = ["POST", "GET"])
def home():
    if request.method == "POST":
        url_received = request.form["nm"]
        found_url = URLs.query.filter_by(long = url_received).first()
        if found_url:
            return redirect(url_for("display_short_url", url = found_url.short))
        else:
            short_url = shorten_url()
            new_url = URLs(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url = short_url))
    else:
        return render_template("home.html")

#Creates the page to display the shortened URL
@app.route("/display/<url>")
def display_short_url(url):
    return render_template("shorturl.html", short_url_display = url)

#Defines how the webpage will redirect to the associated url when the shortened URL is entered
@app.route("/<short_url>")
def redirection(short_url):
    long_url = URLs.query.filter_by(short = short_url).first()
    if long_url:
        return redirect(long_url.long)
    else:
        return f"<h1>URL does not exist</h1>"

#Running the application
if __name__ == '__main__':
    app.run(port=5000, debug=True)
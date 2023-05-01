from db import db, User, Post
from flask import Flask, request
import json
import os

app = Flask(__name__)
db_filename = "savvy.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(msg, code=404):
    return json.dumps({"error": msg}), code

@app.route("/")
def welcome():
    """
    This route is a test
    """
    return "Welcome to Savvy!"


### User Routes ###

@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    """
    This route gets a user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    This route creates a new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    netid = body.get("netid")
    class_year = body.get("class_year", "")

    if not name or not netid:
        return failure_response("Missing name or NetID")
    
    user = User(name=name, netid=netid, class_year=class_year)
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route("/api/users/saved_posts/")
def get_saved_posts(user_id):
    """
    This route gets all saved posts by user id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    
    saved_posts = user.saved_posts()
    return success_response({"saved_posts": saved_posts})


### Post Routes ###

# - save/bookmark post
# - unsave/unbookmark post
# - apply with link? frontend?
# - filter by field
# - filter by location
# - filter by payment
# - filter by qualifications




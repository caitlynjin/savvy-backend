from db import db, User, Post, Asset
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

@app.route("/api/users/<int:user_id>/")
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


### Post Routes ###

@app.route("/api/users/<int:user_id>/saved_posts/")
def get_saved_posts(user_id):
    """
    This route gets all saved posts by user id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    
    saved_posts = user.serialize_saved_posts()
    return success_response(saved_posts)

@app.route("/api/posts/<int:post_id>/")
def get_post_by_id(post_id):
    """
    Endpoint for displaying the page for a single post given its id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    return success_response(post.serialize())

@app.route("/api/posts/<int:user_id>/unsave/<int:post_id>/", methods=["POST"])
def unsave_post(user_id, post_id):
    """
    Endpoint for unsaving a post/removing it from a user's bookmarks
    Takes in user id and post id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    user.remove_post(post)
    db.session.commit()
    return success_response(user.serialize_saved_posts(), 201)

### Asset Routes ###

@app.route("/api/upload/", methods=["POST"])
def upload():
    """
    Endpoint for uploading an image to AWS given its base64 form,
    then storing/returning the URL of that image
    """
    body = json.loads(request.data)
    image_data = body.get("image_data")
    if image_data is None:
        return failure_response("No Base64 URL")
    
    #create new Asset object
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()

    return success_response(asset.serialize(), 201)

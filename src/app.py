from db import db, User, Post, Tag
from flask import Flask, request
import json
import os
from data import add_data

app = Flask(__name__)
FILE_NAME = "data.json"
db_filename = "savvy.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False

db.init_app(app)
with app.app_context():
    db.create_all()
    if len(Post.query.all()) == 0:
        add_data(FILE_NAME)


def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(msg, code=404):
    return json.dumps({"Error": msg}), code

@app.route("/")
def welcome():
    """
    This route is a test
    """
    return "Welcome to Savvy!"


### User Routes ###

@app.route("/api/users/<int:user_id>/")
def get_user_by_id(user_id):
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

    if not name:
        return failure_response("Missing name")
    if not netid:
        return failure_response("Missing NetID")
    
    user = User(name=name, netid=netid, class_year=class_year)
    db.session.add(user)
    db.session.commit()
    return success_response(user.serialize(), 201)

@app.route("/api/users/<int:user_id>/posts_saved/")
def get_saved_posts(user_id):
    """
    This route gets all saved posts by user id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    saved_posts = user.serialize_saved_posts()
    return success_response(saved_posts)

@app.route("/api/users/<int:user_id>/posts_applied/")
def get_applied_posts(user_id):
    """
    This route gets all applied posts by user id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    applied_posts = user.serialize_applied_posts()
    return success_response(applied_posts)

@app.route("/api/users/<int:user_id>/save_post/<int:post_id>/", methods=["POST"])
def save_post(user_id, post_id):
    """
    This route adds post to bookmarked posts for this user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    user.add_posts_saved(post)
    db.session.commit()
    return success_response(user.serialize_saved_posts(), 201)
    
@app.route("/api/users/<int:user_id>/unsave_post/<int:post_id>/", methods=["POST"])
def unsave_post(user_id, post_id):
    """
    This route removes post from bookmarked posts for this user
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    user.remove_posts_saved(post)
    db.session.commit()
    return success_response(user.serialize_saved_posts(), 201)

@app.route("/api/users/<int:user_id>/apply_post/<int:post_id>/", methods=["POST"])
def apply_post(user_id, post_id):
    """
    This route adds post to list of applied posts for this user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    user.add_posts_applied(post)
    db.session.commit()
    return success_response(user.serialize_applied_posts(), 201)
    
@app.route("/api/users/<int:user_id>/unapply_post/<int:post_id>/", methods=["POST"])
def unapply_post(user_id, post_id):
    """
    This route removes post from list of applied posts for this user
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    user.remove_posts_applied(post)
    db.session.commit()
    return success_response(user.serialize_applied_posts(), 201)

@app.route("/api/users/<int:user_id>/add_tag/<int:tag_id>/", methods=["POST"])
def add_tag(user_id, tag_id):
    """
    This route adds this tag to saved tags for this user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag is None:
        return failure_response("Tag not found")
    user.add_tag(tag)
    db.session.commit()
    return success_response(user.serialize_saved_tags(), 201)

@app.route("/api/users/<int:user_id>/remove_tag/<int:tag_id>/", methods=["POST"])
def remove_tag(user_id, tag_id):
    """
    This route removes this tag from saved tags for this user
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag is None:
        return failure_response("Tag not found")
    user.remove_tag(tag)
    db.session.commit()
    return success_response(user.serialize_saved_tags(), 201)


### Post Routes ###

@app.route("/api/posts/")
def get_all_posts():
    """
    This route gets all posts
    """
    posts = [post.serialize() for post in Post.query.all()]
    return success_response({"posts": posts})

@app.route("/api/posts/<int:post_id>/")
def get_post_by_id(post_id):
    """
    Endpoint for displaying the page for a single post given its id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    return success_response(post.serialize())

@app.route("/api/posts/filter/", methods=["POST"])
def filter_posts_by_tag():
    """
    This route filters all posts by tag
    Request body: { "tags": [{"id": , "type":, "name": }, ...]}
    """
    body = json.loads(request.data)
    tags = body.get("tags")
    posts = []
    for t in tags:
        tag = Tag.query.filter_by(id=t.get("id")).first()
        if tag is None:
            return failure_response("Tag not found")
        for p in tag.get_posts():
            if not p in posts:
                posts.append(p)
    return success_response({"posts": posts})


### Tag Routes ###

@app.route("/api/tags/")

def get_all_tags():
    """
    This route gets all tags
    """
    tags = [tag.serialize() for tag in Tag.query.all()]
    return success_response({"tags": tags})

@app.route("/api/tags/<int:tag_id>/")
def get_tag_by_id(tag_id):
    """
    This route gets tag by id
    """
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag is None:
        return failure_response("Tag not found")
    return success_response(tag.serialize())


### Asset Routes ###

@app.route("/upload/", methods=["POST"])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

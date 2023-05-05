from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

user_post_association_table = db.Table(
    "association",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"))
)

user_tag_association_table = db.Table(
    "user_tag_association",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
)

post_tag_association_table = db.Table(
    "post_tag_association",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id")),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"))
)


class User(db.Model):
    """
    Model class for a User
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    class_year = db.Column(db.String, nullable=True)
    # asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False)
    posts_saved = db.relationship("Post", secondary=user_post_association_table,
                                  back_populates="users_saved")
    posts_applied = db.relationship("Post", secondary=user_post_association_table,
                                    back_populates="users_applied")
    tags_saved = db.relationship("Tag", secondary=user_tag_association_table,
                                 back_populates="users")

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")
        self.password = kwargs.get("password", "")
        self.class_year = kwargs.get("class_year", "")
        # self.asset_id = kwargs.get("asset_id", None)
    
    def serialize(self):
        """
        Serialize a User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "password": self.password,
            "class_year": self.class_year,
            # "img_url": self.get_img_url_by_asset_id(self.asset_id),
            "posts_saved": [post.serialize() for post in self.posts_saved],
            "posts_applied": [post.serialize() for post in self.posts_applied],
            "tags": [tag.serialize() for tag in self.tags_saved]
        }
    
    # def get_img_url_by_asset_id(self, asset_id):
    #     """
    #     Return user's image url by Asset object id
    #     """
    #     asset = Asset.query.filter_by(id=asset_id).first()
    #     if asset is None:
    #         return ""
    #     return self.get_asset_by_id(self.asset_id).get_url()
    
    def serialize_saved_posts(self):
        """
        Serialize list of saved posts
        """
        return {
            "posts_saved": [post.serialize() for post in self.posts_saved]
        }
    
    def serialize_applied_posts(self):
        """
        Serialize list of applied posts
        """
        return {
            "posts_applied": [post.serialize() for post in self.posts_applied]
        }
    
    def serialize_saved_tags(self):
        """
        Serialize list of saved tags
        """
        return {
            "tags_saved": [tag.serialize() for tag in self.tags_saved]
        }
    
    def add_posts_saved(self, post):
        """
        Add post to the user's saved posts
        """
        self.posts_saved.append(post)

    def remove_posts_saved(self, post):
        """
        Remove post from user's saved posts
        """
        self.posts_saved.remove(post)

    def add_posts_applied(self, post):
        """
        Add post to the user's applied posts
        """
        self.posts_applied.append(post)

    def remove_posts_applied(self, post):
        """
        Remove post from user's applied posts
        """
        self.posts_applied.remove(post)

    def add_tag(self, tag):
        """
        Add tag to user's saved tags
        """
        self.tags.append(tag)

    def remove_tag(self, tag):
        """
        Remove tag from user's saved tags
        """
        self.tags.remove(tag)
    

class Post(db.Model):
    """
    Model class for a Post
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.String, nullable=False)
    employer = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    qualifications = db.Column(db.String, nullable=False)
    wage = db.Column(db.String, nullable=False)
    how_to_apply = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    users_saved = db.relationship("User", secondary=user_post_association_table,
                                  back_populates="posts_saved")
    users_applied = db.relationship("User", secondary=user_post_association_table,
                                    back_populates="posts_applied")
    tags = db.relationship("Tag", secondary=post_tag_association_table,
                            back_populates="posts")

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.position = kwargs.get("position", "")
        self.employer = kwargs.get("employer", "")
        self.description = kwargs.get("description", "")
        self.qualifications = kwargs.get("qualifications", "")
        self.wage = kwargs.get("wage", "")
        self.how_to_apply = kwargs.get("how_to_apply", "")
        self.link = kwargs.get("link", "")

    def serialize(self):
        """
        Serialize a Post object
        """
        return {
            "id": self.id,
            "position": self.position,
            "employer": self.employer,
            "description": self.description,
            "qualifications": self.qualifications,
            "wage": self.wage,
            "how_to_apply": self.how_to_apply,
            "link": self.link,
            "tags": [tag.serialize() for tag in self.tags]
        }
    
    def serialize_link(self):
        """
        Returns this post's application link
        """
        return {
            "post_link": self.link
        }
    

class Tag(db.Model):
    """
    Model class for a Tag
    """
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    users = db.relationship("User", secondary=user_tag_association_table,
                                 back_populates="tags_saved")
    posts = db.relationship("Post", secondary=post_tag_association_table,
                            back_populates="tags")

    def __init__(self, **kwargs):
        """
        Initialize a Tag object
        """
        self.type = kwargs.get("type", "")
        self.name = kwargs.get("name", "")
    
    def serialize(self):
        """
        Serialize a Tag object
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name
        }
    
    def get_posts(self):
        """
        Return all posts for this tag
        """
        return [post.serialize() for post in self.posts]
    

# class Asset(db.Model):
#     """
#     Asset model
#     """
#     __tablename__ = "assets"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     base_url = db.Column(db.String, nullable=True)
#     salt = db.Column(db.String, nullable=True)
#     extension = db.Column(db.String, nullable=True)
#     width = db.Column(db.Integer, nullable=True)
#     height = db.Column(db.Integer, nullable=True)
#     created_at = db.Column(db.DateTime, nullable=False)

#     def __init__(self, **kwargs):
#         """
#         Initialize an Asset object
#         """
#         self.create(kwargs.get("image_data"))

#     def serialize(self):
#         """
#         Serialize an Asset object
#         """
#         return {
#             "url": f"{self.base_url}/{self.salt}.{self.extension}",
#             "created_at": str(self.created_at),
#         }
    
#     def get_url(self):
#         """
#         Return the image url
#         """
#         return f"{self.base_url}/{self.salt}.{self.extension}"

#     def create(self, image_data):
#         """
#         Given an image in base64 form, possible responses:
#             1. Rejects the image if it's not supported filetype
#             2. Generates a random string for the image filename
#             3. Decodes the image and attempts to upload it to AWS
#         """
#         try:
#             ext = guess_extension(guess_type(image_data)[0])[1:]

#             #only accept supported file extension
#             if ext not in EXTENSIONS:
#                 raise Exception(f"Extention {ext} not supported")
            
#             #securely generate a random string for image name
#             salt = "".join(
#                 random.SystemRandom().choice(
#                     string.ascii_uppercase + string.digits
#                 )
#                 for _ in range(16)
#             )

#             #remove base64 header
#             img_str = re.sub("^data:image/.+;base64,", "", image_data)
#             img_data = base64.b64decode(img_str)
#             img = Image.open(BytesIO(img_data))

#             self.base_url = S3_BASE_URL
#             self.salt = salt
#             self.extension = ext
#             self.width = img.width
#             self.height = img.height
#             self.created_at = datetime.datetime.now()

#             img_filename = f"{self.salt}.{self.extension}"
#             self.upload(img, img_filename)
#         except Exception as e:
#             print(f"Error while creating image: {e}")

#     def upload(self, img, img_filename):
#         """
#         Attempt to upload the image into S3 bucket
#         """
#         try:
#             #save image temporarily on the server
#             img_temploc = f"{BASE_DIR}/{img_filename}"
#             img.save(img_temploc)

#             #upload the image to S3
#             s3_client = boto3.client("s3")
#             s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

#             #make s3 image url public
#             s3_resource = boto3.resource("s3")
#             object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
#             object_acl.put(ACL="public-read")

#             #remove image from server
#             os.remove(img_temploc)

#         except Exception as e:
#             print(f"Error while uploading image: {e}")

    
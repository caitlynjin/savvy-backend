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

association_table = db.Table(
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
    class_year = db.Column(db.String, nullable=True)
    # asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False)
    posts = db.relationship("Post", secondary=association_table,
                                  back_populates="users")
    tags = db.relationship("Tag", secondary=user_tag_association_table,
                                 back_populates="users")

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")
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
            "class_year": self.class_year,
            # "img_url": self.get_img_url_by_asset_id(self.asset_id),
            "posts": [post.serialize() for post in self.posts],
            "tags": [tag.serialize() for tag in self.tags]
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
        Return list of saved posts
        """
        return {
            "saved_posts": [post.serialize() for post in self.posts]
        }
    
    def serialize_saved_tags(self):
        """
        Return list of saved tags
        """
        return {
            "saved_tags": [tag.serialize() for tag in self.tags]
        }
    
    def add_post(self, post):
        """
        Add this post to the given user
        """
        self.posts.append(post)

    def remove_post(self, post):
        """
        Remove post from user's list of saved posts
        """
        self.posts.remove(post)

    def add_tag(self, tag):
        """
        Add tag to user's list of saved tags
        """
        self.tags.append(tag)
    

class Post(db.Model):
    """
    Model class for a Post
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    ### Filters ###
    tags = db.relationship("Tag", secondary=post_tag_association_table,
                            back_populates="posts")
    ###
    wage = db.Column(db.String, nullable=False)
    how_to_apply = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)

    users = db.relationship("User", secondary=association_table,
                                  back_populates="posts")

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.position = kwargs.get("position", "")
        self.description = kwargs.get("description", "")
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
            "description": self.description,
            "tags": [tag.serialize() for tag in self.tags],
            "wage": self.wage,
            "how_to_apply": self.how_to_apply,
            "link": self.link
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
                                 back_populates="tags")
    posts = db.relationship("Post", secondary=post_tag_association_table,
                            back_populates="tags")

    def __init__(self, **kwargs):
        """
        Initialize a Filter object
        """
    
    def serialize(self):
        """
        Serialize a Filter object
        """
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name
        }
    
    def get_type(self):
        """
        Get tag type
        """
        return self.type
    

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

    
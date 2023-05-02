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


class User(db.Model):
    """
    Model class for a User
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    class_year = db.Column(db.Integer, nullable=True)
    saved_posts = db.relationship("Post", secondary=association_table)

    def __init__(self, **kwargs):
        """
        Initialize a User object
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")
        self.class_year = kwargs.get("class_year", "")
    
    def serialize(self):
        """
        Serialize a User object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "class_year": self.class_year,
            "saved_posts": [post.serialize() for post in self.posts]
        }
    
    def saved_posts(self):
        """
        Return list of saved posts
        """
        return [post.serialize() for post in self.posts]
    
    def add_post(self, post):
        """
        Add this post to the given user
        """
        self.saved_posts.append(post)
    
    def remove_post(self, post):
        """
        Remove post from user's list of saved posts
        """
        self.saved_posts.remove(post)
    

class Post(db.Model):
    """
    Model class for a Post
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    ### Filters ###
    field = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    payment = db.Column(db.String, nullable=False)
    qualifications = db.Column(db.String, nullable=False)
    ###
    wage = db.Column(db.String, nullable=False)
    how_to_apply = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.position = kwargs.get("position", "")
        self.description = kwargs.get("description", "")
        self.field = kwargs.get("field", "")
        self.location = kwargs.get("location", "")
        self.payment = kwargs.get("qualifications", "")
        self.qualifications = kwargs.get("qualifications", "")
        self.wage = kwargs.get("wage", "")
        self.how_to_apply = kwargs.get("how_to_apply", "")

    def serialize(self):
        """
        Serialize a Post object
        """
        return {
            "id": self.id,
            "position": self.position,
            "description": self.description,
            "field": self.field,
            "location": self.location,
            "payment": self.payment,
            "qualifications": self.qualifications,
            "wage": self.wage,
            "how_to_apply": self.how_to_apply
        }
    

class Asset(db.Model):
    """
    Asset model
    """
    __tablename__ = "assets"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=True)
    salt = db.Column(db.String, nullable=True)
    extension = db.Column(db.String, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize an Asset object
        """
        self.create(kwargs.get("image_data"))

    def serialize(self):
        """
        Serialize an Asset object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }

    def create(self, image_data):
        """
        Given an image in base64 form, possible responses:
            1. Rejects the image if it's not supported filetype
            2. Generates a random string for the image filename
            3. Decodes the image and attempts to upload it to AWS
        """
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]

            #only accept supported file extension
            if ext not in EXTENSIONS:
                raise Exception(f"Extention {ext} not supported")
            
            #securely generate a random string for image name
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            #remove base64 header
            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"
            self.upload(img, img_filename)
        except Exception as e:
            print(f"Error while creating image: {e}")

    def upload(self, img, img_filename):
        """
        Attempt to upload the image into S3 bucket
        """
        try:
            #save image temporarily on the server
            img_temploc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temploc)

            #upload the image to S3
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temploc, S3_BUCKET_NAME, img_filename)

            #make s3 image url public
            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object.acl.put(ACL="public-read")

            #remove image from server
            os.remove(img_temploc)

        except Exception as e:
            print(f"Error while uploading image: {e}")

    
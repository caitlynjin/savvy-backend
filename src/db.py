from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    
"""
Script to add data from data.json to database
"""
from db import Tag, db, Post
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

def create_tags():
    tag1 = Tag(type="Qualifications", name= "FWS")
    tag2 = Tag(type="Qualifications", name= "Non FWS")
    tag3 = Tag(type="Payment", name= "Paid")
    tag4 = Tag(type="Payment", name= "Unpaid")
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.add(tag3)
    db.session.add(tag4)
    db.session.commit()

def add_data(file):
    # Opening JSON file
    f = open(file)
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    
    # Iterating through the json
    for job in data["jobs"]:
        field = Tag.query.filter_by(name=job["field"], type="Field").first()
        if field is None:
             new_field = Tag(name=job["field"], type="Field")
             db.session.add(new_field)
             db.session.commit()
        location = Tag.query.filter_by(name=job["location"], type="Location").first()
        if location is None:
             new_location = Tag(name=job["location"], type="Location")
             db.session.add(new_location)
             db.session.commit()
        new_post = Post(position=job["position"], description=job["description"], wage=str(job["wage"]), how_to_apply=job["how_to_apply"], link=job["link"])
        db.session.add(new_post)
        db.session.commit()

        payment = Tag.query.filter_by(type="Payment", name="Paid").first()
        if not job["payment"]:
            payment = Tag.query.filter_by(type="Payment", name="Unpaid").first()
        qualifications = Tag.query.filter_by(name="Non FWS").first()
        if job["qualifications"] == "FWS":
            qualifications = Tag.query.filter_by(name="FWS").first()
        new_post.tags.append(payment)
        new_post.tags.append(qualifications)

        location = Tag.query.filter_by(name=job["location"], type="Location").first()
        field = Tag.query.filter_by(name=job["field"], type="Field").first() 
        new_post.tags.append(field)
        new_post.tags.append(location)
        db.session.commit()

    # Closing file
    f.close()
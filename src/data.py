"""
Script to add data from data.json to database
"""
from db import Tag, db, Post
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

# def create_tags():
    # tag1 = Tag(type="qualifications", name= "FWS")
    # tag2 = Tag(type="qualifications", name= "Non FWS")
    # tag3 = Tag(type="payment", name= "Paid")
    # tag4 = Tag(type="payment", name= "Unpaid")
    # db.session.add(tag1)
    # db.session.add(tag2)
    # db.session.add(tag3)
    # db.session.add(tag4)
    # db.session.commit()

def add_data(file):
    # Opening JSON file
    f = open(file)
    
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
    
    # Iterating through the json
    for job in data["jobs"]:
        field = Tag.query.filter_by(name=job["field"], type="field").first()
        if field is None:
            new_field = Tag(name=job["field"], type="field")
            db.session.add(new_field)
            db.session.commit()
        location = Tag.query.filter_by(name=job["location"], type="location").first()
        if location is None:
            new_location = Tag(name=job["location"], type="location")
            db.session.add(new_location)
            db.session.commit()
        payment = Tag.query.filter_by(name=job["payment"], type="payment").first()
        if payment is None:
            new_payment = Tag(name=job["payment"], type="payment")
            db.session.add(new_payment)
            db.session.commit()
        new_post = Post(position=job["position"], employer=job["employer"], description=job["description"], qualifications=job["qualifications"], wage=job["wage"], how_to_apply=job["how_to_apply"], link=job["link"])
        db.session.add(new_post)
        db.session.commit()

        location = Tag.query.filter_by(name=job["location"], type="location").first()
        field = Tag.query.filter_by(name=job["field"], type="field").first() 
        payment = Tag.query.filter_by(name=job["payment"], type="payment").first()
        new_post.tags.append(field)
        new_post.tags.append(location)
        new_post.tags.append(payment)
        db.session.commit()

    # Closing file
    f.close()
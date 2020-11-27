from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
    
db = SQLAlchemy()
migrate = Migrate()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    followers_count = db.Column(db.Integer)
    screenname =db.Column(db.String)
    def __repr__(self):
        return "< User {} {} {} {} >".format(self.id, self.username, self.followers_count,self.screenname)

def parse_records(db_data):
    parsed_list = []
    for record in db_data:
        parsed_record = record.__dict__
        del parsed_record["_sa_instance_state"]
        parsed_list.append(parsed_record)
    return parsed_list

class Tweet(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    text = db.Column(db.String)
    user_id = db.Column(db.BigInteger, db.ForeignKey("user.id"))
    embedding = db.Column(db.PickleType)
    user=db.relationship("User", backref=db.backref('tweets', lazy=True))

    def __repr__(self):
        return "< Tweet {} {} {} >".format(self.id,self.text,self.embedding)
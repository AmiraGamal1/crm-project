from db import db
from datetime import datetime
import pytz
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    user_phone = db.Column(db.String(15))
    password = db.Column(db.String(10), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))

    def __repr__(self):
        return '<Cuser name %r Email %r>' % self.user_name % self.user_email 
    

def get_user(search):
    search_pattern = f"%{search}"
    results = User.query.filter(
        (User.id.like(search_pattern)) | (User.user_name.like(search_pattern))
        | (User.user_email.like(search_pattern)) | (User.user_phone.like(search_pattern))
        | (User.type.like(search_pattern)) | (User.date.like(search_pattern))
    ).all()
    return results
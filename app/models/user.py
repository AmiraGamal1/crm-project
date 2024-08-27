from db import db
from datetime import datetime
import pytz
from flask_security import UserMixin, RoleMixin
import uuid
import secrets


fs_uniquifier_value = str(uuid.uuid4())

def generate_unique_value():
    return secrets.token_urlsafe(16)

                      
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False)
    user_email = db.Column(db.String(200), nullable=False)
    user_phone = db.Column(db.String(15))
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean(), default=True) 
    roles = db.relationship('Role', secondary='user_roles', backref='roled')
    date = db.Column(db.DateTime, default=datetime.now(pytz.UTC))
    fs_uniquifier = db.Column(db.String(90), nullable=False, unique=True,
                              default=generate_unique_value)

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))

def create_roles():
    admin = Role(name='admin')
    editor = Role(name='editor')
    supervisor = Role(name='supervisor')
    try:
        db.session.add(admin)
        db.session.add(editor)
        db.session.add(supervisor)
        db.session.commit()
    except:
        return "fail to add roles to database"

def get_user(search):
    search_pattern = f"%{search}"
    results = User.query.filter(
        (User.id.like(search_pattern)) | (User.user_name.like(search_pattern))
        | (User.user_email.like(search_pattern)) | (User.user_phone.like(search_pattern))
        | (User.type.like(search_pattern)) | (User.date.like(search_pattern))
    ).all()
    return results
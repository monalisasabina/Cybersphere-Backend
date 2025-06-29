from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User (db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable= False)
    email = db.Column(db.String, nullable= False)
    role=db.Column(db.String(50), nullable=False)
    _password_hash =  db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    

class Projects (db.Model, SerializerMixin):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable= False)
    description = db.Column(db.String, nullable= False)
    images = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Projects {self.title}>"
    

class Downloads (db.Model, SerializerMixin):
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable= False)
    description = db.Column(db.String, nullable= False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
      
    def __repr__(self):
        return f"<Downloads {self.name}>"
    


class Gallery (db.Model, SerializerMixin):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(100), nullable= False)
    url = db.Column(db.String, nullable= False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
      
    def __repr__(self):
        return f"<Downloads {self.username}>"
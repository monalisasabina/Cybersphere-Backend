from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable= False, unique=True)
    email = db.Column(db.String, nullable= False, unique=True)
    role=db.Column(db.String(50), nullable=False)
    _password_hash =  db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"
    
    @property
    def password(self):
        raise AttributeError("Password is write-only")
    
    @password.setter
    def password(self,password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)



class Project(db.Model, SerializerMixin):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable= False)
    description = db.Column(db.String, nullable= False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # One to many relationship
    images = db.relationship('Image', back_populates='project',cascade='all, delete-orphan')
    # want images to be deleted when a project is deleted, set cascade
    
    def __repr__(self):
        return f"<Projects {self.title}>"
    


class Image(db.Model, SerializerMixin):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(100), nullable= False)
    url = db.Column(db.String, nullable= False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # To control images to be used in the gallery
    is_in_gallery = db.Column(db.Boolean, default=False, nullable=False)

    # Foreign ID
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    #   nullable=True since not all the images will be used for the projects

    # Relationship
    project = db.relationship('Project', back_populates='images')  
    
    def __repr__(self):
        return f"<Image {self.caption}>"
    


class Downloads(db.Model, SerializerMixin):
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable= False)
    file_url =db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable= False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
      
    def __repr__(self):
        return f"<Downloads {self.filename}>"
    



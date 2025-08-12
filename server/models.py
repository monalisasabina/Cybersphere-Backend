from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    _password_hash = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)



class Project(db.Model, SerializerMixin):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.Column(db.JSON, nullable=False)  # Assuming images is a JSON field containing image URLs or objects
    # want images to be deleted when a project is deleted, set cascade

    def __repr__(self):
        return f"<Projects {self.title}>"
    
    def to_dict(self):
        return{
            "id":self.id,
            "title":self.title,
            "subtitle":self.subtitle,
            "description":self.description,
            "date_added":self.date_added.isoformat(),
            "images": self.images
        }
    
    # isoformat(): makes datetime JSON serializable


class Downloads(db.Model, SerializerMixin):
    __tablename__ = 'downloads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    file_url =db.Column(db.String(100), nullable=False)
    description = db.Column(db.String, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
      
    def __repr__(self):
        return f"<Downloads {self.filename}>"
    
     
    def to_dict(self):
        return {
            "id":self.id,
            "filename":self.filename,
            "file_url":self.file_url,
            "description":self.description,
            "uploaded_at":self.uploaded_at,
        }
    

class BlogPost(db.Model, SerializerMixin):
    __tablename__='blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    # A slug is a URL-friendly, human-readable string used to identify a resource (like a blog post) on a website.
    # example: https://example.com/blog/how-our-engineers-delivered-under-budget
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(300))
    category = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
 
    def __repr__(self):
        return f'<BlogPost {self.title}'
    
    
class RevokedToken(db.Model, SerializerMixin):
        id = db.Column(db.Integer, primary_key=True)
        jti = db.Column(db.String(120), nullable=False, unique=True)

        def __repr__(self):
            return f"<RevokedToken {self.jti}>"

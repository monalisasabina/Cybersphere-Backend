from flask import Flask,request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db,User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import random
import os

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# print("JWT_SECRET_KEY:", os.getenv("JWT_SECRET_KEY"))
# print("Type of JWT_SECRET_KEY:", type(os.getenv("JWT_SECRET_KEY")))

app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
CORS(app)
jwt= JWTManager(app)

# HOME PAGE
class Home(Resource):
    def get(self):
        return{
            "message":" Welcome to the CyberSphere Build Design API ",
            "Api_version":"v1",
            "available_endpoints":[
              
            ]
        },200
    
api.add_resource(Home,'/')

# _________________________________________________________
# Authentication

# Username Suggestions
class UsernameSuggestion(Resource):

    def post(self):
        data = request.get_json()

        firstname = data.get('firstname').strip().lower()
        lastname = data.get('lastname').strip().lower()

        if not firstname or not lastname:
            return{'error': 'Firstname and lastname are required'}, 400
        
        base_suggestions = [
            f'{firstname}{lastname}',
            f'{firstname}_{lastname}',
            f'{firstname}{random.randint(100,999)}',
            f"{lastname}_{random.randint(1, 100)}",
            f"{firstname[0]}{lastname}",
            f"{lastname}{random.randint(1, 1000)}",
        ]

        suggestions = []
        for suggestion in base_suggestions:

            # Checks if the username already exists in the database
            #  if None, its available
            if not User.query.filter_by(username=suggestion).first():
                suggestions.append(suggestion)

            if len(suggestions) == 3:
                break

        # Fallback Generator: if all suugestions are taken. Others are generated
        while len(suggestions) < 3:
            alt = f"{firstname}{random.randint(1000,9999)}"

            if not User.query.filter_by(username=alt).first():
                suggestions.append(alt)

        return{'suggestions':suggestions}, 200

api.add_resource(UsernameSuggestion,'/suggest-username', endpoint='suggest-username')

# Sign Up
class SignUp(Resource):
    def post(self):

        data = request.get_json()

        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')
        is_admin = data.get('is_admin', False)

        if not username or not password or not email or not role or not firstname or not lastname:
            return{'error':'Firstname, Lastname, Username, email, role and password required'}

        if is_admin and role != 'admin':
            return {'error':'Only users with an admin role can be set as an admin'}, 400
  
        if User.query.filter_by(username=username).first():
            return{'error':'Username already taken'},400
        
        if User.query.filter_by(email=email).first():
            return{'error':'Email already taken'},400
        
        new_user = User(
            firstname = firstname,
            lastname = lastname,
            username = username,
            email =  email,
            role=role,
            is_admin=is_admin
        )
        new_user.password = password

        db.session.add(new_user)
        db.session.commit()  

        return{
            'message': 'User created succesfully',
            'user': {
                'id':new_user.id,
                'firstname':new_user.firstname,
                'lastname':new_user.lastname,
                'email':new_user.email,
                'username':new_user.username,
                'is_admin':new_user.is_admin
            }
        },201
    
api.add_resource(SignUp,'/signup', endpoint='signup')

class Login(Resource):
    def post(self):
         data = request.get_json()

         if not data:
             return{'error':'Invalid JSON format'},400
         
         identifier = data.get('username') or data.get('email')
         password = data.get('password')

         if not identifier or not password:
             return{'error':'Username/email and password are required'},400
         
         user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

         if not user or not user.check_password(password):
             return{'error':'Invalid credentials'}, 401
        
         access_token = create_access_token(identity=str(user.id))

         print('\n')
         print(access_token)
         print('\n')
        
         return{
             'message':'Login successful',
             'access_token':access_token,
             'user':{
                 'id':user.id,
                 'username':user.username,
                 'email':user.email,
                 'is_admin':user.is_admin,
             }
         },200
         

api.add_resource(Login, '/login', endpoint='/login')        

class CheckSession(Resource):
    
    #decorator checks for a valid JWT TOKEN
    @jwt_required()

    def get(self):

        # Gives you whatever was set as identity(user ID)
        identity = get_jwt_identity()

        print(identity)

        user = db.session.get(User, identity)

        if not user:
            return {'error':'User not found'},404
        
        return{
            'message':'User is authenticated',
            'user':{
                'id':user.id,
                'username':user.username,
                'email':user.email,
                'is_admin':user.is_admin
            }
        },200
    
api.add_resource(CheckSession, '/check_session', endpoint='/check_session')




if __name__ == '__main__':
    app.run(port=5555, debug=True)
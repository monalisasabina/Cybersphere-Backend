from flask import Flask,request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db,User, RevokedToken
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from dotenv import load_dotenv
from datetime import timedelta
import random
import os

load_dotenv()

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback=secret-key')

# [LOGOUT] Blacklisting the token
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']

# [CHECKSESSION] Adding token expiration
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

app.json.compact = False

# Initialize extensions
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
CORS(app)
jwt= JWTManager(app)

# ─────────────────────────────────────────────────────────────
# JWT Revocation Check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return db.session.query(RevokedToken).filter_by(jti=jti).first() is not None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'message': 'Token expired, please log in again.'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(reason):
    return {'message': f'Invalid token: {reason}'}, 401

@jwt.unauthorized_loader
def missing_token_callback(reason):
    return {'message': f'Missing or invalid token: {reason}'}, 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return {'message': 'Token has been revoked. Please log in again.'}, 401


# ________________________________________________________
# HOME PAGE
class Home(Resource):
    def get(self):
        return{
            "message":" Welcome to the CyberSphere Build Design API ",
            "Api_version":"v1",
            "available_endpoints":[
                "/users"
              
            ]
        },200
    
api.add_resource(Home,'/')

# _________________________________________________________
# Authentication USERS

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

api.add_resource(UsernameSuggestion,'/suggest-username')

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
            return{'error':' All fields are required'},400

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
    
api.add_resource(SignUp,'/signup')


# Login
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

        #  print('\n')
        #  print(access_token)
        #  print('\n')
        
         return{
             'message':'Login successful',
             'access_token':access_token,
             'user':{
                 'id':user.id,
                 'username':user.username,
                 'email':user.email,
                 'is_admin':user.is_admin,
                 'role':user.role
             }
         },200
         

api.add_resource(Login, '/login')        


# Check session
class CheckSession(Resource):
    
    #decorator checks for a valid JWT TOKEN
    @jwt_required()

    def get(self):

        # Gives you whatever was set as identity(user ID)
        identity = get_jwt_identity()
        # print(identity)
        user = db.session.get(User, identity)

        if not user:
            return {'error':'User not found'},404
        
        # Checking if token was revoked
        jti =get_jwt()["jti"]
        if db.session.query(RevokedToken).filter_by(jti=jti).first():
            return {'error':"Session is invalid(logged out)"},401

        return{
            'message':'User is authenticated',
            'user':{
                'id':user.id,
                'username':user.username,
                'email':user.email,
                'is_admin':user.is_admin,
                'role':user.role
            }
        },200
    
api.add_resource(CheckSession, '/check_session')


# LOGOUT
class Logout(Resource):
    @jwt_required()

    def delete(self):
        jti = get_jwt()["jti"]
        revoked = RevokedToken(jti=jti)
        db.session.add(revoked)
        db.session.commit()
        return{'message':'Logged out successfully'},200
    
api.add_resource(Logout, '/logout')

# Dashboard
class Dashboard(Resource):
    @jwt_required()

    def get(self):
        return {'message':'Welcome to the protected route!'},200
    
api.add_resource(Dashboard, '/dashboard')    

# Change Password
class ChangePassword(Resource):

    @jwt_required()

    def patch(self):

        current_user_id = get_jwt_identity()

        user = User.query.get(current_user_id)

        if not user:
            return {"error":"User not found"},404
        
        data = request.get_json()

        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not user.check_password(old_password):
            return {"error":"Incorrect old password"},400
        
        if not new_password or  len(new_password) <8:
            return {"error":"Password must be at least 8 characters long"},400
        

        user.password = new_password

        db.session.commit()

        return {"message":"Password updated successfully"},200

api.add_resource(ChangePassword, '/changepassword')


# Fetching users
class Users(Resource):

    @jwt_required()
    
    def get(self):

        users_list=[]

        for user in User.query.all():

            user_dict = {
                "id":user.id,
                "firstname":user.firstname,
                "lastname":user.lastname,
                "username":user.username,
                "email":user.email,
                "role":user.role,
                "is_admin":user.is_admin,
            }

            users_list.append(user_dict)

        return make_response(jsonify(users_list),200)


api.add_resource(Users, '/users')      


# Users By ID
class User_by_ID(Resource):

    # Fetching User By ID
    @jwt_required()
    def get(self,id):

        user = User.query.filter(User.id==id).first()
        if not user:
            return {'error': 'User not found'}
        
        
        user_dict = {
                "id":user.id,
                "firstname":user.firstname,
                "lastname":user.lastname,
                "username":user.username,
                "email":user.email,
                "role":user.role,
                "is_admin":user.is_admin,
            }
        
        return make_response(jsonify(user_dict),200)
    
    # Updating User by ID
    @jwt_required()
    def patch(self,id):

        user = User.query.filter(User.id==id).first()

        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        # Only self or admin can update
        if current_user.id != user.id and not current_user.is_admin:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()

        if not user:
            return {"error":"User not found"}
        
        try:
            for attr in data:
                setattr(user, attr, data[attr])

            db.session.commit()

            user_dict = {
                "id":user.id,
                "firstname":user.firstname,
                "lastname":user.lastname,
                "username":user.username,
                "email":user.email,
                "role":user.role,
                "is_admin":user.is_admin,
            }

            return user_dict,200
        
        except Exception as e:
            return {"error": "Validation errors", "details": str(e)}, 400
        
    # Deleting a user
    @jwt_required()
    def delete(self,id):

        user = User.query.filter(User.id == id).first()

        if not user:
          return make_response(jsonify({"error":"User not found"}),404)
      
        current_user_id = int(get_jwt_identity())
        current_user = User.query.get(current_user_id)

        # Only self or admin can update
        if current_user.id != user.id and not current_user.is_admin:
            return {"error": "Unauthorized"}, 403
        
        
        db.session.delete(user)
        db.session.commit()

        response_dict = {"Message":"User successfully deleted"}

        return make_response(jsonify(response_dict),200)
  
api.add_resource(User_by_ID, '/users/<int:id>')    



if __name__ == '__main__':
    app.run(port=5555, debug=True)
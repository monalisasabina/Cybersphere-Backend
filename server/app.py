from flask import Flask,request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db,User
from flask_jwt_extended import JWTManager


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cybersphere.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False
ADMIN_CODE = 'admin1234'

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)
CORS(app)

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
                'username':new_user.username,
                'is_admin':new_user.is_admin
            }
        },201
    
api.add_resource(SignUp,'/signup', endpoint='signup')

        




if __name__ == '__main__':
    app.run(port=5555, debug=True)
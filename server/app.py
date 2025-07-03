from flask import Flask,request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db
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

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')
        code = data.get('code')

        if not username or not password or not email:
            return{'error':'Username, email, and password required'}

        if role == 'admin':
            if not ADMIN_CODE:
                return{'error':'Admin code not set'},500
            
            if code != ADMIN_CODE:
                return{'error':'Invalid admin code'},403


        




if __name__ == '__main__':
    app.run(port=5555, debug=True)
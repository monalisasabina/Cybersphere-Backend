from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS
from models import db


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cybersphere.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

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


if __name__ == '__main__':
    app.run(port=5555, debug=True)
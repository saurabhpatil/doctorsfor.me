from app import app, con, api

base_url = '/api'
parser = reqparse.RequestParser()
cursor = con.cursor()

class UserAPI(Resource):
    def get(self, id):
        return {'hello': 'world'}

    def put(self, id):
        pass

    def post(self, id):
        pass

class LoginAPI(Resource):
    def post(self):
        args = parser.parse_args()
        username = 
        sql_query = 'SELECT * FROM User WHERE '


class SignupAPI(Resource):
    def post(self):
        pass

api.add_resource(UserAPI, base_url + '/user/<int:id>', endpoint='user')
api.add_resource(LoginAPI, base_url + '/user/login', endpoint='login')
from flask import Flask, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

@auth.error_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized access'}), 401

@auth.get_password
def get_password(username):
    if username == 'admin':
        return 'password'
    return None

class TaskListAPI(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True,
            help = 'No task title provided', location = 'json')
        self.reqparse.add_argument('description', type = str, default = "", location = 'json')
        super(TaskListAPI, self).__init__()

    def get(self):
        return tasks

api.add_resource(TaskListAPI, '/tasks', endpoint = 'tasks')

class TaskAPI(Resource):
    decorators = [auth.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, location = 'json')
        self.reqparse.add_argument('description', type = str, location = 'json')
        self.reqparse.add_argument('done', type = bool, location = 'json')
        super(TaskAPI, self).__init__()

    def put(self, id):
        task = list(filter(lambda t: t['id'] == id, tasks))
        if len(task) == 0:
            abort(404)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v != None:
                task[0][k] = v
        return jsonify( { 'task': task[0] } )

api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint = 'task')

@app.route('/tasks/<int:task_id>', methods = ['GET'])
@auth.login_required
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify( { 'task': task[0] } )
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
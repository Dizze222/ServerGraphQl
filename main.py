from datetime import datetime
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from ariadne import load_schema_from_path, make_executable_schema, \
    graphql_sync, snake_case_fallback_resolvers, ObjectType
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from ariadne import convert_kwargs_to_snake_case


query = ObjectType("Query")


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getcwd()}/todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)

    def __repr__(self):
        return '<Article %r' % self.id

    def to_dict(self):
        return {
            "id": self.id,
            "completed": self.completed,
            "description": self.description,
            "due_date": str(self.due_date.strftime('%d-%m-%Y'))
        }

@convert_kwargs_to_snake_case
def resolve_todo(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }

    except AttributeError:  # todo not found
        payload = {
            "success": False,
            "errors": [f"Todo item matching id {todo_id} not found"]
        }

    return payload


@app.route('/')
def hello():
    todoo = Todo.query.order_by(Todo.due_date).all()
    count = 0
    if count != 1:
        print("dot")
        today = datetime.today().date()
        todo = Todo(description="Run a marathon", due_date=today, completed=False)
        todo.to_dict()
        db.session.add(todo)
        db.session.commit()
        count += 1
        for i in todoo:
            print(i.description)
    return 'Hello!'

def resolve_todos(obj, info):
    try:
        todos = [todo.to_dict() for todo in Todo.query.all()]
        payload = {
            "success": True,
            "todos": todos
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload

@convert_kwargs_to_snake_case
def resolve_todo(obj, info, todo_id):
    try:
        todo = Todo.query.get(todo_id)
        payload = {
            "success": True,
            "todo": todo.to_dict()
        }

    except AttributeError:
        payload = {
            "success": False,
            "errors": [f"Todo item matching id {todo_id} not found"]
        }

    return payload


query.set_field("todos", resolve_todos)
query.set_field("todos", resolve_todo)

type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(
    type_defs, query, snake_case_fallback_resolvers
)


@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200


@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )

    status_code = 200 if success else 400
    return jsonify(result), status_code


query.set_field("todo", resolve_todo)

if __name__ == '__main__':
    app.run()

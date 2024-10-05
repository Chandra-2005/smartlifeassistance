from flask import Blueprint

app1 = Blueprint('PythonProject', __name__)

@app1.route('/')
def index():
    return "Welcome to App 1!"

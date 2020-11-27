from flask import Blueprint,render_template, request,redirect
from tweety.models import User, parse_records

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/', methods=['GET', 'POST'])
def index(username=None):
    if request.method == 'POST':
        if request.form['username']!="" or request.form['username']!=None: 
            username=request.form['username']
        return render_template('index.html',username=username)
    elif request.method =='GET':
        return render_template('index.html',username=username)
    

@main_routes.route('/users.json')
def json_data():
    raw_data = User.query.all()
    parsed_data = parse_records(raw_data)
    
    return jsonify(parsed_data)

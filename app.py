import os
from flask import Flask, request, jsonify, render_template, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update, func

app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "user_preferences.db"))
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SECRET_KEY'] = 'app_test_af.guzman'
db = SQLAlchemy(app)

class user_entry(db.Model):
    __tablename__ = 'user_preferences'
    user_name = db.Column(db.String(255), primary_key = True)
    user_color = db.Column(db.String(255))
    user_pref = db.Column(db.String(255))

    def __init__(self, user_name, user_color, user_pref): 
        self.user_name = user_name
        self.user_color = user_color
        self.user_pref = user_pref
    
@app.route("/", methods = ['GET', 'POST'])
def register_user_pref():
    if request.method == 'POST': 
        user_name = request.form.get('user_name')
        user_color = request.form.get('user_color')
        user_pref = request.form.get('user_pref')
        existing_entry = user_entry.query.filter_by(user_name = user_name).first()
        if existing_entry is None: 
            new_entry = user_entry(user_name, user_color, user_pref)
            db.session.add(new_entry)
            db.session.commit()
            return user_name  + "'s preferences were saved."
        else: 
            return 'There is already a user with name: ' + user_name  + ' please try other name.'
    else: 
        return render_template('register_user_pref.html')

if __name__ == '__main__': 
    db.drop_all()
    db.create_all()
    app.run(host="0.0.0.0", port=80)
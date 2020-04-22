from flask import Flask
from flask import render_template, redirect, request, flash, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import pymysql
import secrets
#import os

#dbuser = os.environ.get('DBUSER')
#dbpass = os.environ.get('DBPASS')
#dbhost = os.environ.get('DBHOST')
#dbname = os.environ.get('DBNAME')

conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True, "pool_recycle": 300,}  # pymysql.err.Operational error warnings https://medium.com/@heyjcmc/controlling-the-flask-sqlalchemy-engine-a0f8fae15b47
app.config['DEBUG'] = True
db = SQLAlchemy(app)

# Prevent --> pymysql.err.OperationalError) (2006, "MySQL server has gone away (BrokenPipeError(32, 'Broken pipe')
class SQLAlchemy(SQLAlchemy):
     def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
# <-- MWC

class colbert_friends(db.Model):
    #__tablename__ = 'results'
    friendid = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
 
    def __repr__(self):
        return "id: {0} | first name: {1} | last name: {2}".format(self.friendid, self.first_name, self.last_name)

class FriendForm(FlaskForm):
    friendid = IntegerField('Friend ID:')
    first_name = StringField('First Name:', validators=[DataRequired()])
    last_name = StringField('Last Name:', validators=[DataRequired()])

    def __repr__(self):
        return "id: {0} | first name: {1} | last name: {2}".format(self.friendid, self.first_name, self.last_name)

@app.route('/')
def index():
    all_friends = colbert_friends.query.all()
    return render_template('index.html', friends=all_friends, pageTitle='Mike\'s Friends')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        form = request.form
        search_value = form['search_string']
        search = "%{0}%".format(search_value)
        results = colbert_friends.query.filter(or_(colbert_friends.first_name.like(search),
                                                    colbert_friends.last_name.like(search))).all()
        return render_template('index.html', friends=results, pageTitle='Mike\'s Friends', legend="Search Results")
    else:
        return redirect('/')


@app.route('/add_friend', methods=['GET', 'POST'])
def add_friend():
    form = FriendForm()
    if form.validate_on_submit():
        friend = colbert_friends(first_name=form.first_name.data, last_name=form.last_name.data)
        db.session.add(friend)
        db.session.commit()
        return redirect('/')

    return render_template('add_friend.html', form=form, pageTitle='Add A New Friend',
                            legend="Add A New Friend")


@app.route('/delete_friend/<int:friend_id>', methods=['GET', 'POST'])
def delete_friend(friend_id):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        friend = colbert_friends.query.get_or_404(friend_id)
        db.session.delete(friend)
        db.session.commit()
        flash("Friend deleted", "warning") #flash a message to the user
        return redirect("/")
    else: #if it's a GET request, send them to the home page
        return redirect("/")


@app.route('/friend/<int:friend_id>', methods=['GET','POST'])
def get_friend(friend_id):
    friend = colbert_friends.query.get_or_404(friend_id)
    form = FriendForm()

    form.friendid.data = friend.friendid
    form.first_name.data = friend.first_name
    form.last_name.data = friend.last_name
    return render_template('friend.html', form=form, pageTitle='Friend Details', legend="Friend Details")


@app.route('/friend/<int:friend_id>/update', methods=['GET','POST'])
def update_friend(friend_id):
    friend = colbert_friends.query.get_or_404(friend_id)
    form = FriendForm()

    if form.validate_on_submit():
        friend.first_name = form.first_name.data
        friend.last_name = form.last_name.data
        db.session.commit()
        flash("Friend updated", "success") 
        return redirect(url_for('get_friend', friend_id=friend.friendid))

    form.friendid.data = friend.friendid
    form.first_name.data = friend.first_name
    form.last_name.data = friend.last_name
    return render_template('update_friend.html', form=form, pageTitle='Update Friend', legend="Update A Friend")


if __name__ == '__main__':
    app.run(debug=True)

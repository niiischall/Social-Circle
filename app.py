from flask import Flask, request, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1371@localhost/flaskSocial'
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = '$2a$16$PnnIgfMwkOjGX4SkHqSOPO'
app.debug = True

db = SQLAlchemy(app)

#test route
@app.route('/')
@login_required
def index():
    return 'Welcome to the Flask Social'

#creating a homepage
@app.route('/home')
@login_required
def home():
    return render_template('home.html')


#creating a posting route for a user and also getting its credentials
@app.route('/posting')
@login_required
def posting():
    now_user = User.query.filter_by(email = current_user.email).first()
    return render_template('add_post.html', now_user = now_user)

#function to store the post in the Post data model and redirect to index page
@app.route('/addd_post', methods = ['POST'])
def add_post():
    post = Post(request.form['pcontent'],request.form['pemail'])
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))

#creating a route to display all the users
@app.route('/user_list')
@login_required
def get_user_list():
    users = User.query.filter_by(email = current_user.email)
    userDetails = UserDetails.query.all()
    return render_template('user_list.html',users = users, userDetails = userDetails)

#creating a feed showing all the posts made by the users
@app.route('/feed')
@login_required
def user_feed():
     feed_post = Post.query.all()
     return render_template('user_feed.html',feed_post = feed_post)
    
    
#creating a route to get user details
@app.route('/details')
@login_required
def user_details():
    present_user = User.query.filter_by(email = current_user.email).first()
    return render_template('user_details.html', present_user = present_user)


#route to add user details
@app.route('/add_details',methods =['POST'])
@login_required
def add_details():
    detail = UserDetails(request.form['pid'],request.form['username'], request.form['profile_pic'], request.form['user_location'])
    db.session.add(detail)
    db.session.commit()      
    return redirect(url_for('index'))


@app.route('/user_profile/<id>')
def user_profile(id):
    oneUser = UserDetails.query.filter_by(id = id).first()
    firstUser = User.query.filter_by(id = oneUser.user_id).first()
    singleUser = Post.query.filter_by(posted_by = firstUser.email).first()
    return render_template('user_profile.html',oneUser = oneUser, firstUser = firstUser, singleUser = singleUser)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_content = db.Column(db.String(200))
    posted_by = db.Column(db.String(100))

    def __init__(self,post_content, posted_by):
        self.post_content = post_content
        self.posted_by = posted_by
    
    def __repr__(self):
        return '<Post %r>' %self.post_content

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(100))
    profile_pic = db.Column(db.String(300))
    location = db.Column(db.String(100))

    def __init__(self, user_id, username, profile_pic, location):
        self.user_id = user_id
        self.username = username
        self.profile_pic = profile_pic
        self.location = location
        
    def __repr__(self):
        return '<UserDetails %r>' %self.username


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

if __name__ == "__main__":
    app.run()    
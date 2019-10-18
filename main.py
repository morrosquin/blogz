  
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:alita01@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP4B'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(5000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    whitelist = ['login', 'signup', 'home', 'allPosts', 'blog']
    if request.endpoint not in whitelist and 'username' not in session:
        return redirect('/login')

@app.route('/allPosts')
def allPosts ():
    blog = Blog.query.all()

    return render_template('allPosts.html', blog=blog)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        everyone = User.query.all()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            if username not in everyone:
                flash("You don't have an account yet. Sign up for one!", 'error')
            else:
                flash('Invalid password', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST','GET'])
def signup ():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifyPassword = request.form['verifyPassword']

        existing_user = User.query.filter_by(username=username).first()
        user = User.query.all()
        Error = False

        if username == '':
            Error = True
            flash("That's not a valid username","username_error")
        
        if existing_user: 
            Error = True   
            flash('A user with that username already exists',"existing_error")

        if password != verifyPassword or verifyPassword == '':
            Error = True
            flash("Passwords don't match","verify_error")

        if password == '':
            Error = True
            flash("That's not a valid password","password_error")

        if Error == False:
            user_account = User(username,password)

            db.session.add(user_account)
            db.session.commit()
            session['username'] = username

            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if title == '' or body == '':
            flash('we need both a title and a body!')
        else:
            owner = User.query.filter_by(username=session['username']).first()
            post = Blog(title,body,owner)
            db.session.add(post)
            db.session.commit()

            return redirect('/allPosts')

    return render_template('newpost.html')

@app.route('/blog', methods=['POST','GET'])
def blog():
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)

    return render_template('blog.html', blog=blog)

@app.route('/userBlog')
def userBlog():
    username = request.args.get('user')
    blogs = Blog.query.filter_by(owner_id=username).all()

    return render_template('userBlog.html', blogs=blogs)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/')
def home ():
    owner = User.query.all()
    return render_template('home.html', owner=owner)

if __name__ == '__main__':
    app.run()
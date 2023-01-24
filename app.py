from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import RegisterForm, LoginForm
from database import get_db, close_db
from forms import AddDish
from functools import wraps
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static\pictures"

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def login_required(view):
    """
    if login needed, auto login if possible
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user == None:
            return redirect(url_for("auto_login_check",next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.teardown_appcontext
def close_db_at_end_of_requests(e=None):
    close_db(e)

def login_required(view):
    """
    if login needed, auto login if possible
    """
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user == None:
            return redirect(url_for("auto_login_check",next=request.url))
        return view(**kwargs)
    return wrapped_view

@app.route("/", methods=["GET","POST"])
def index():
    """
    start route must be "/", directs straight to home page 
    """
    return redirect("home")

@app.route("/home", methods=["GET","POST"])
def home():     
    return render_template("home.html")

"""

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        surname = form.surname.data
        # if username in database
            form.username.errors.append("Username already taken")
        else:
            # add user to database

            response = make_response(redirect("auto_login_check"))
            response.set_cookie("username",username,max_age=(60*60*24))
            return response
    return render_template("register.html",form=form)


@app.route("/login", methods=["GET","POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db.execute("SELECT password FROM login WHERE username = ?",(username,)).fetchone()
        if user is not None:
            if not check_password_hash(user["password"],password ):
                form.password.errors.append("Incorrect password")
            else:
                session.clear()
                session["username"] = username
                next_page = request.args.get("next")
                if not next_page:
                    response = make_response( redirect( url_for('home')) )
                else:
                    response = make_response( redirect(next_page) )
                response.set_cookie("username",username,max_age=(60*60*24*7))
                return response
    return render_template("login.html",form=form)


@app.route("/auto_login_check", methods=["GET","POST"])
def auto_login_check():
    if request.cookies.get("username"):
        session.clear()
        session["username"] = request.cookies.get("username")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("home")
        else:
            return redirect( next_page )
    return redirect( "login" )


@app.route("/delete_cookie/<cookie>",methods=["GET","POST"])
def delete_cookie(cookie):
    response = redirect(url_for('home'))
    response.set_cookie(cookie, '', expires=0)
    return response

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"),404
"""

#initally i'm gonna just get all dishes to display but i do want to be able to separate it into like starter, main course etc
@app.route('/menu',methods=['GET'])
def menu():
    db = get_db()
    dishes =db.execute('''SELECT * FROM dish ORDERBY; ''').fetchall()
    return render_template('dishes.html', dishes=dishes)


#manager only
#form is not validating - no idea why
@app.route('/addDish', methods=['GET','POST'])
def addDish():
    form = AddDish()
    if form.validate_on_submit():
        db = get_db()
        name = form.name.data
        if db.execute('''SELECT * from dish WHERE name=?''',(name,)).fetchone() is not None:
            form.name.errors.append("This dish is already in the db")
        else:
            cost = form.cost.data
            cookTime = form.cookTime.data
            dishType = form.dishType.data
            dishDescription = form.dishDescription.data
            dishPic = form.dishPic.data
            filename = secure_filename(dishPic.filename)
            dishPic.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            if dishDescription is not None:
                db.execute("""INSERT INTO dish (name, cost, cook_time, dishType,description,dishPic) VALUES(?,?,?,?,?,?)""",(name,cost,cookTime,dishType,dishDescription,filename))
            else:
                db.execute("""INSERT INTO dish (name, cost, cook_time, dishType,dishPic) VALUES(?,?,?,?,?)""",(name,cost,cookTime,dishType,filename))
            db.commit()
            return redirect(url_for('menu'))
    return render_template('addDish.html', form=form)

#this was not working yesterday so I don't get why its working today
@app.route('/cart')
def cart():
    dish=''
    full = 0
    if 'cart' not in session:
        session['cart'] = {}
        print('create session')
    names = {}
    db = get_db()
    for dish_id in session['cart']:
        print(dish_id)
        name = db.execute('''SELECT * FROM dish WHERE dish_id=?;''',(dish_id,)).fetchone()['name']
        print(name)
        names[dish_id] = name
        dish = db.execute(''' SELECT * FROM dish WHERE dish_id=?; ''',(dish_id,)).fetchone()
        cost = db.execute(''' SELECT * FROM dish WHERE dish_id=?''',(dish_id,)).fetchone()['cost']
        quantity = session['cart'][dish_id]
        full+= (int(cost) *int(quantity))
    return render_template('cart.html', cart=session['cart'], names=names, dish=dish, full=full)

@app.route('/add_to_cart/<int:dish_id>')
#@login_required
def add_to_cart(dish_id):
    if 'cart' not in session:
        session['cart'] = {} 
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]= session['cart'][dish_id] + 1
    return redirect( url_for('cart') ) 

@app.route('/remove/<int:dish_id>')
#@login_required
def remove(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    for dishId in session['cart'].copy():
        if dish_id == int(dishId):
            session['cart'].pop(dishId)
    return redirect(url_for('cart'))

@app.route('/inc_quantity/<int:dish_id>')
#@login_required
def inc_quantity(dish_id):
    db = get_db()
    #stock_left = db.execute(''' SELECT * FROM inventory WHERE book_id=?; ''',(book_id,)).fetchone()['stock_left']
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    #if session['cart'][book_id] < stock_left:
    session['cart'][dish_id] = session['cart'][dish_id] +1
    return redirect(url_for('cart'))

@app.route('/dec_quantity/<int:dish_id>')
#@login_required
def dec_quantity(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    if session['cart'][dish_id] >1:
        session['cart'][dish_id] = session['cart'][dish_id] -1
    return redirect(url_for('cart'))

#to continue with functional cart i need to have customers up and running
#need to create stock levels 
#need to display menu better
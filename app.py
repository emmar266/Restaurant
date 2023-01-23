from flask import Flask, render_template, redirect, url_for, session, g, request, make_response
from flask_session import Session
from databaseTemporary import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import RegisterForm, LoginForm
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

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

#general prioirty queue for kitchen staff
#checks login details to see if your a kitchen staff or manager

@app.route('/kitchen', methods=['GET','POST'])
#@loginrequired
def kitchen():
    
    db=get_db()
    #if db.execute('''SELECT * FROM staff
                         #WHERE (role="chef" OR role="manager") AND staff_id=?''',(session['username'],)).fetchone() is None:
            #return redirect(url_for('error'))
    orderlist=db.execute('''SELECT d.name, o.time, d.cook_time, o.status, o.dish_id
                        FROM orders as o 
                        JOIN dish as d 
                        ON o.dish_id=d.dish_id
                        ORDER BY o.time*d.cook_time DESC;''').fetchall()
        
    return render_template('kitchen.html',orderlist=orderlist)

@app.route('/<int:dish_id>,<int:time>/kitchenUpdate', methods=['GET','POST'])
#@loginrequired
def kitchenUpdate(dish_id, time):
    
    db=get_db()
    #if db.execute('''SELECT * FROM staff
                         #WHERE (role="chef" OR role="manager") AND staff_id=?''',(session['username'],)).fetchone() is None:
            #return redirect(url_for('error'))

    db.execute('''UPDATE orders
                                SET status="ongoing" 
                                WHERE time==? and status=="unmade" 
                                and dish_id IN (
                                            SELECT dish_id
                                            FROM orders
            	                            WHERE dish_id==? AND 1 LIMIT 1);''',(time, dish_id))
    db.commit()

    return redirect(url_for('kitchen'))

@app.route('/<int:dish_id>,<int:time>/kitchenDelete', methods=['GET','POST'])
#@loginrequired
def kitchenDelete(dish_id, time):
    
    db=get_db()
    #if db.execute('''SELECT * FROM staff
                         #WHERE (role="chef" OR role="manager") AND staff_id=?''',(session['username'],)).fetchone() is None:
            #return redirect(url_for('error'))

    db.execute('''DELETE FROM orders
                                WHERE time==? and status=="ongoing" 
                                and dish_id IN (
                                            SELECT dish_id
                                            FROM orders
            	                            WHERE dish_id==? AND 1 LIMIT 1);''',(time, dish_id))
    db.commit()

    return redirect(url_for('kitchen'))

    
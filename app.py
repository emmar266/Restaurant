from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from werkzeug.utils import secure_filename
from forms import submitModifications,cardDetails, RegistrationForm ,LoginForm, ContactForm, ReplyForm, EmployeeForm, ResetPasswordForm, NewPasswordForm, CodeForm, AddDish, UserPic
from functools import wraps
from flask_mysqldb import MySQL 
from flask_mail import Mail, Message
from datetime import datetime
import random
from random import sample
import string


app = Flask(__name__)
UPLOAD_FOLDER = "static"
app.config["SECRET_KEY"] = "MY_SECRET_KEY"
app.config['UPLOAD_FOLDER']= UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# For the email function
mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'no.reply.please.and.thank.you@gmail.com'
app.config['MAIL_PASSWORD'] = 'plseiqkwvpwfxwwr'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail.init_app(app)

app.config['MYSQL_USER'] = 'er12' # someone's deets
app.config['MYSQL_PASSWORD'] = 'meiph' # someone's deets
app.config['MYSQL_HOST'] = 'cs1.ucc.ie'
app.config['MYSQL_DB'] = 'cs2208_er12' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

@app.before_request
def logged_in():
    g.user = session.get("username", None)
    g.access = session.get("access_level", None)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("customer_login")) #,next=request.url))
        return view(**kwargs)
    return wrapped_view

def staff_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "ordinary staff":
            return redirect(url_for("index")) #,next=request.url))
        return view(**kwargs)
    return wrapped_view

def manager_only(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.access != "managerial":
            return redirect(url_for("index"))
        return view(**kwargs)
    return wrapped_view


@app.route("/auto_login_check_customer", methods=["GET","POST"])
def auto_login_check_customer():
    if request.cookies.get("email"):
        session.clear()
        session["username"] = request.cookies.get("email")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("index")
        else:
            return redirect( next_page )
    return redirect( "customer_login" )

@app.route("/auto_login_check_staff", methods=["GET","POST"])
def auto_login_check_staff():
    if request.cookies.get("email"):
        session.clear()
        session["username"] = request.cookies.get("email")
        next_page = request.args.get("next")
        if not next_page:
            return redirect("index")
        else:
            return redirect( next_page )
    return redirect( "staff_login" )

@app.route("/delete_cookie/<cookie>",methods=["GET","POST"])
def delete_cookie(cookie):
    response = redirect(url_for('index'))
    response.set_cookie(cookie, '', expires=0)
    return response

@app.route("/logout", methods=["GET","POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.errorhandler(404)
def page_not_found(error):
    return render_template("error.html"),404

#initally i'm gonna just get all dishes to display but i do want to be able to separate it into like starter, main course etc
@app.route('/menu',methods=['GET'])
def menu():
    cur=mysql.connection.cursor()
    cur.execute('''SELECT * FROM dish ORDERBY; ''')
    dishes =cur.fetchall()
    #want to order this so that we display by dishtype
    cur.execute(" SELECT * FROM dish WHERE dishType='starter' ")
    starters =cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='main' ")
    mainCourse = cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='dessert' ")
    dessert= cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='drink'")
    drink= cur.fetchall()
    cur.execute(" SELECT * FROM dish WHERE dishType='side'")
    side = cur.fetchall()
    cur.close()#
    print(g.user)
    return render_template('dishes.html', dishes=dishes, starters=starters, mainCourse=mainCourse,dessert=dessert, drink=drink,side=side)




@app.route('/dish/<int:dish_id>', methods=['GET','POST'])
def dish(dish_id):
    if str(dish_id) not in session:
        session[str(dish_id)]={}
        print(session[str(dish_id)])
    session['CurrentDish'] = dish_id
    print(session[str(dish_id)])
    form = submitModifications()
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
    dish=cur.fetchone()
    dish_id=dish['dish_id']
    cur.execute("SELECT * FROM dish_ingredient JOIN ingredient ON dish_ingredient.ingredient_id = ingredient.ingredient_id  WHERE dish_ingredient.dish_id=%s",(dish_id,))
    result=cur.fetchall()
    print(result)
    for value in result:
        ingredient_id=value['ingredient_id']
        print('INGREDIENTID ', ingredient_id)
        if ingredient_id not in session[str(dish_id)]:
            session[str(dish_id)][ingredient_id] =0
            print('todo')
            print(session[str(dish_id)][ingredient_id])
    if form.validate_on_submit():
        changes = ''
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        for ingredient in ingredients:
            print(ingredient)
            ingredient_id = ingredient['ingredient_id']
            cur.execute("SELECT * FROM ingredient WHERE ingredient_id=%s",(ingredient_id,))
            ing_name=cur.fetchone()['name']
            #ingredient_name = ingredient['name']
            if ingredient_id not in session[str(dish_id)]:
                session[str(dish_id)][ingredient_id] =1
                print(session[dish_id])
            else:
                quantity=session[str(dish_id)][ingredient_id]
                changes+= str(ing_name) + str(quantity)
                print('changes1:',changes)
                session[str(dish_id)][ingredient_id] =1
        cur.execute("INSERT INTO modifications(dish_id,changes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
        mysql.connection.commit()
        session['CurrentDish'] = None
        return redirect(url_for('add_to_cart', dish_id=dish['dish_id']))
    return render_template('dish.html', dish=dish,result=result,form=form,quant=session[str(dish_id)])

#so by default all amounts of ingredients should be 1 - should have the option to increase by 1 and decrease by 1
#added that so that should work
# I'M PRETTY SURE THIS WORKS BESIDES THE REDIRECT  
@app.route('/inc_quantity_ingredient/<int:ingredient_id>')
@login_required
def inc_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor() 
    dish_id = session['CurrentDish']
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    #dish_id = result['dish_id']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] +1
    print(session[str(dish_id)][ingredient_id])
    return redirect(url_for('dish',dish_id=dish_id))

@app.route('/dec_quantity_ingredient/<int:ingredient_id>')
@login_required
def dec_quantity_ingredient(ingredient_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM dish_ingredient WHERE ingredient_id=%s",(ingredient_id,))
    result=cur.fetchone()
    dish_id = result['dish_id']
    if ingredient_id not in session[str(dish_id)]:
        session[str(dish_id)][ingredient_id] = 1
    if session[str(dish_id)][ingredient_id] !=0:
        session[str(dish_id)][ingredient_id] = session[str(dish_id)][ingredient_id] -1
    return redirect(url_for('dish',dish_id=dish_id))


#manager only
#should add instead of a text box for dishtype like a drop down with only a couple of options
#NEED TO ADD ABILITY TO LIST INGREDIENTS NECESSARY FOR EACH DISH.
@app.route('/addDish', methods=['GET','POST'])
def addDish():
    cur = mysql.connection.cursor()
    form = AddDish()
    if form.validate_on_submit():
        name = form.name.data
        cur.execute('SELECT * from dish WHERE name=%s',(name,))
        result = cur.fetchone()
        if result is not None:
            form.name.errors.append("This dish is already in the db")
        else:
            cost = form.cost.data
            cookTime = form.cookTime.data
            dishType = (form.dishType.data).lower()
            dishDescription = form.dishDescription.data
            dishPic = form.dishPic.data
            ingredients = form.ingredients.data
            allergins= form.allergins.data
            filename = secure_filename(dishPic.filename)
            #print(filename)
            dishPic.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            if dishDescription is not None and allergins is not None:
                cur.execute("INSERT INTO dish (name, cost, cook_time, dishType,description,dishPic,allergies) VALUES(%s,%s,%s,%s,%s,%s,%s)",(name,cost,cookTime,dishType,dishDescription,filename,allergins))
                mysql.connection.commit()
            elif dishDescription is not None:
                cur.execute("INSERT INTO dish (name, cost, cook_time, dishType,dishPic,description) VALUES(%s,%s,%s,%s,%s,%s)",(name,cost,cookTime,dishType,filename,dishDescription))
                mysql.connection.commit()
            elif allergins is not None:
                cur.execute("INSERT INTO dish (name, cost, cook_time, dishType,dishPic,allergies) VALUES(%s,%s,%s,%s,%s,%s)",(name,cost,cookTime,dishType,filename,allergins))
                mysql.connection.commit()
            else:
                cur.execute("INSERT INTO dish (name, cost, cook_time, dishType,dishPic) VALUES(%s,%s,%s,%s,%s)",(name,cost,cookTime,dishType,filename))
                mysql.connection.commit()
            print(ingredients)
            if ingredients is not None:
                ingredients=ingredients.split(',')
                for ingredient in ingredients:
                    print(ingredient)
                    cur.execute("SELECT * FROM ingredient WHERE name=%s",(ingredient,))
                    ingredient_id=cur.fetchone()
                    if ingredient_id is not None:
                        print('hellor', ingredient_id)
                        ingredient_id=ingredient_id['ingredient_id']
                        cur.execute('SELECT * FROM dish WHERE name=%s AND cost=%s AND cook_time=%s',(name, cost, cookTime))
                        dish_id=cur.fetchone()['dish_id']
                        cur.execute("INSERT INTO dish_ingredient(ingredient_id,dish_id) VALUES (%s,%s)",(ingredient_id,dish_id))
                        mysql.connection.commit()
                    else:
                        cur.execute('SELECT * FROM dish WHERE name=%s AND cost=%s AND cook_time=%s',(name, cost, cookTime))
                        dish_id=cur.fetchone()['dish_id']
                        cur.execute("INSERT INTO ingredient(name,quantity) VALUES (%s,%s)",(ingredient,0))
                        mysql.connection.commit()
                        cur.execute("SELECT * FROM ingredient WHERE name=%s",(ingredient,))
                        ingredient_id=cur.fetchone()['ingredient_id']
                        cur.execute("INSERT INTO dish_ingredient(ingredient_id,dish_id) VALUES (%s,%s)",(ingredient_id,dish_id))
                        mysql.connection.commit()
            cur.close()
            return redirect(url_for('menu'))
    return render_template('addDish.html', form=form)

#this was not working yesterday so I don't get why its working today

@app.route('/cart')
@login_required
def cart():
    #session['cart'].clear()
    cur = mysql.connection.cursor()
    dish=''
    full = 0
    if 'cart' not in session:
        session['cart'] = {}
        print('create session')
    names = {}
    print(session['cart'])
    for dish_id in session['cart']:
        print('heeloor',dish_id)
        cur.execute('SELECT * FROM dish WHERE dish_id=%s LIMIT 1;',(dish_id,))
        name = cur.fetchone()['name']
        print(name)
        names[dish_id] = name
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s; ',(dish_id,))
        dish = cur.fetchone()
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
        cost = cur.fetchone()['cost']
        quantity = session['cart'][dish_id]
        full+= (int(cost) *int(quantity))
        #cur.close()
    return render_template('cart.html', cart=session['cart'], names=names, dish=dish, full=full)

@app.route('/add_default_meal/<int:dish_id>')
@login_required
def add_default_meal(dish_id):
    cur = mysql.connection.cursor()
    if 'cart' not in session:
        session['cart'] = {}
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]=session['cart'][dish_id]+1
    changes=""
    cur.execute("INSERT INTO modifications(dish_id,changes,user) VALUES(%s,%s,%s)",(dish_id,changes,g.user))
    mysql.connection.commit()

    return redirect(url_for('cart'))


#There's an issue here 
@app.route('/add_to_cart/<int:dish_id>')
@login_required
def add_to_cart(dish_id):
    #session['cart'].clear()
    cur = mysql.connection.cursor()
    if 'cart' not in session:
        session['cart'] = {} 
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    session['cart'][dish_id]= session['cart'][dish_id] + 1
    return redirect( url_for('cart') ) 

@app.route('/remove/<int:dish_id>')
@login_required
def remove(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id] = 0
    for dishId in session['cart'].copy():
        if dish_id == int(dishId):
            session['cart'].pop(dishId)
    return redirect(url_for('cart'))

@app.route('/inc_quantity/<int:dish_id>')
@login_required
def inc_quantity(dish_id):
    cur = mysql.connection.cursor()
    #stock_left = db.execute(''' SELECT * FROM inventory WHERE book_id=?; ''',(book_id,)).fetchone()['stock_left']
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    #if session['cart'][book_id] < stock_left:
    session['cart'][dish_id] = session['cart'][dish_id] +1
    return redirect(url_for('cart'))

@app.route('/dec_quantity/<int:dish_id>')
@login_required
def dec_quantity(dish_id):
    if dish_id not in session['cart']:
        session['cart'][dish_id]=0
    if session['cart'][dish_id] >1:
        session['cart'][dish_id] = session['cart'][dish_id] -1
    return redirect(url_for('cart'))


#question does this need to be specific to user?? or is it already
@app.route('/checkout', methods=['GET','POST'])
def checkout():

    full =0
    form = cardDetails()
    names = {}
    username = g.user
    cur = mysql.connection.cursor()
    for dish_id in session['cart']:
        cur.execute('SELECT * FROM dish WHERE dish_id=%s;',(dish_id,))
        name = cur.fetchone()['name']
        names[dish_id] = name
        cur.execute("SELECT * FROM dish WHERE dish_id=%s",(dish_id,))
        cost = cur.fetchone()['cost']
        cur.execute(' SELECT * FROM dish WHERE dish_id=%s;',(dish_id,))
        dish = cur.fetchone()
        quantity = session['cart'][dish_id]
        full += (cost *quantity)
        cur.execute('SELECT * FROM dish_ingredient WHERE dish_id=%s',(dish_id,))
        ingredients=cur.fetchall()
        changes=''
        print('session',session['cart'])
    if form.validate_on_submit():
        cardNum=form.cardNum.data
        cardHolder = form.cardHolder.data
        cvv = form.cvv.data
        date = datetime.now().strftime(' %d-%m-%y')
        now = datetime.now()
        for dish_id in session['cart']:
            cur.execute('SELECT * FROM modifications WHERE dish_id=%s AND user=%s',(dish_id,g.user))
            result = cur.fetchall()
            print('Result:',result)
            for values in result:
                print('myval',values)
                cur.execute('SELECT * FROM dish WHERE dish_id=%s',(dish_id,))
                currentDish=cur.fetchone()
                print('cd',currentDish)
                cost=currentDish['cost']
                changes=values['changes']
                cur.execute('INSERT INTO transactions(username, dish_id,cost,quantity,date) VALUES(%s,%s,%s,%s,%s) ',(username, dish_id,cost,1,date))
                mysql.connection.commit()
                cur.execute("INSERT INTO orders(time,dish_id,changes) VALUES(%s,%s,%s)",(now,dish_id,changes))
                mysql.connection.commit()
            #cur.execute('DELETE FROM modifications WHERE user=%s',(g.user,))
        cur.execute('DELETE FROM modifications WHERE user=%s',(g.user,))
        mysql.connection.commit()    
        session['cart'].clear()
        cur.close()
        return render_template('cart.html')
    return render_template('checkout.html', cart=session['cart'],form=form,full=full,names=names,dish=dish)

    #need table number to be inputed here 


@app.route('/customer_profile')
@login_required
def customer_profile():
    username = session['username']
    cur = mysql.connection.cursor()
    message = ''
    transactionHistory=''
    image = None
    cur.execute(" SELECT * FROM customer WHERE email=%s",(username,))
    check= cur.fetchone()['profile_pic']
    print(check)
    if check is None:
        error = 'No profile picture yet'
        print('why')
    else:  
        image=check
        print(image)
    cur.execute("SELECT * FROM transactions WHERE username=%s;",(username,))
    check2 = cur.fetchall()
    if check2 is not None:
        message = "You've made no transactions yet"
    else:
        cur.execute(" SELECT * FROM dishes;")
        dish = cur.fetchall()
        cur.execute(" SELECT * FROM transactions WHERE username=%s ",(username,))
        transactionHistory = cur.fetchall()
    cur.close()
    #return render_template("customer/profile.html", title="My Profile")
    return render_template('customer/customer_profile.html',image=image, transactionHistory=transactionHistory)


@app.route('/user_pic', methods=['GET','POST'])
@login_required
def user_pic():
    username = session['username']
    cur = mysql.connection.cursor()
    form = UserPic()
    if form.validate_on_submit():
        profile_pic = form.profile_pic.data
        filename = secure_filename(profile_pic.filename)
        profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cur.execute(' UPDATE customer SET profile_pic=%s WHERE email=%s; ' ,(filename,username))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('customer_profile'))
    return render_template('profile_pic.html', form=form)

#to continue with functional cart i need to have customers up and running
#need to create stock levels 
#need to display menu better

@app.route("/", methods=["GET","POST"])
def index():
    return render_template("home.html", title = "Home")
    
# Register for an account
@app.route("/registration", methods=["GET", "POST"])
def registration():
    cur = mysql.connection.cursor()
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        code = "None" # this is for my 'forgot password' idea that I'd upload later

        '''
            Assuming that only customers can create new accounts
            New staff accounts will be created by the manager and then credentials will
            be provided to the staff member
        '''

        cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
        r1 = cur.fetchone()

        if r1 is not None:
            form.email.errors.append("Sorry, the email you entered already exists, please use another email.")
        elif password.isupper() or password.isdigit() or password.islower() or password.isalpha():
            form.password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            cur.execute("""INSERT INTO customer ( email, first_name, last_name, password, code)
                        VALUES (%s,%s,%s,%s,%s);""", (email, first_name, last_name, generate_password_hash(password), code))
            mysql.connection.commit()
            flash("Successful Registration! Please login now")
            return redirect( url_for("customer_login"))

            #response = make_response(redirect("auto_login_check"))
            #response.set_cookie("email",email,max_age=(60*60*24))
            #return response
    return render_template("customer/registration.html", form=form, title="Registration")

# Login to customer account
@app.route("/customer_login", methods=["GET", "POST"])
def customer_login():
    cur = mysql.connection.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        
        cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
        customer = cur.fetchone()

        if 'counter' not in session:
            session['counter'] = 0

        if customer is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(customer["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Sucks to be you'))
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            return redirect(url_for("customer_profile"))
            '''next_page = request.args.get("next")
            if not next_page:
                response = make_response( redirect( url_for('index')) )
            else:
                response = make_response( redirect(next_page) )
            response.set_cookie("username",username,max_age=(60*60*24*7))
            return response'''
    return render_template("customer/customer_login.html", form=form, title="Login")

# Login to staff account
@app.route("/staff_login", methods=["GET", "POST"])
def staff_login():
    cur = mysql.connection.cursor()
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data

        cur.execute("SELECT * FROM staff WHERE email = %s", (email,))
        staff = cur.fetchone()

        if 'counter' not in session:
            session['counter'] = 0

        if staff is None:
            form.email.errors.append("Email doesn't exist, please check your spelling")
        elif not check_password_hash(staff["password"], password):
            form.password.errors.append("Incorrect password")
            session['counter'] = session.get('counter') + 1
            if session.get('counter')==3:
                flash(Markup('Oh no, are you having trouble logging in? Sucks to be you'))
                session.pop('counter', None)
        else:
            session.clear()
            session["username"] = email
            if staff["access_level"] == "managerial":
                return redirect(url_for("manager"))
            elif staff["access_level"] == "ordinary staff":
                return redirect(url_for("staff_profile"))
                '''next_page = request.args.get("next")
                if not next_page:
                    response = make_response( redirect( url_for('index')) )
                else:
                    response = make_response( redirect(next_page) )
                response.set_cookie("username",username,max_age=(60*60*24*7))
                return response'''
    return render_template("staff/staff_login.html", form=form, title="Login")


# Staff profile
@app.route("/staff_profile")
@staff_only
def staff_profile():
    return render_template("staff/staff_profile.html", title="My Profile")


# Contact form so that customers can send enquiries
@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    cur = mysql.connection.cursor()
    form = ContactForm()
    if form.validate_on_submit() == False:
      flash('All fields are required.')
    else:
        name = form.name.data
        email = form.email.data.lower().strip()
        subject = form.subject.data
        message = form.message.data
        date = datetime.now().date()

        cur.execute("""INSERT INTO user_queries (name, email, subject, message, date)
                        VALUES (%s,%s,%s,%s,%s);""", (name, email, subject, message, date))
        mysql.connection.commit()

        msg = Message(subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=['no.reply.please.and.thank.you@gmail.com'])   
        msg.body = f"""
        From: {name} <{email}>
        {message}
        """
        mail.send(msg)
        flash("Message sent. We will reply to you in 2-3 business days.")
    return render_template("customer/enquiry_form.html",form=form, title="Contact Us")

# Change password
@app.route("/change_password/<table>", methods=["GET", "POST"])
#@login_required
def change_password(table):
    cur = mysql.connection.cursor()
    form = NewPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data

        if new_password.isupper() or new_password.islower() or new_password.isdigit():
            form.new_password.errors.append("Create a STRONG password with one uppercase character, one lowercase character and one number")
        else:
            if table == 'staff':
                cur.execute("""UPDATE staff SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            else:
                cur.execute("""UPDATE customer SET password=%s WHERE email=%s;""", (generate_password_hash(new_password),g.user))
            mysql.connection.commit()
            session.clear()
            flash("Successfully changed password! Please login now.")
            if table == 'staff':
                return redirect(url_for("staff_login"))
            else:
                return redirect(url_for("customer_login"))
    return render_template("password_management/change_password.html", title ="Change password", form=form)

# Reset password feature
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    cur = mysql.connection.cursor()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        table = form.role.data

        pin = sample(range(10000, 99999), 1)

        random_code = ""
        for i in pin:
            random_code += str(i)

        if table == 'staff':
            cur.execute("SELECT * FROM staff WHERE email = %s", (email,))
            user = cur.fetchone()
        else:
            cur.execute("SELECT * FROM customer WHERE email = %s", (email,))
            user = cur.fetchone()

        if user is None:
            form.email.errors.append("There is no account associated with this email, please check your spelling")
        else:
            msg = ""
            cur.execute("""UPDATE staff SET code=%s WHERE email=%s""", (random_code,email))
            mysql.connection.commit()
            msg = Message(f"Hello, {user['first_name']}", sender='no.reply.please.and.thank.you@gmail.com', recipients=[user["email"]])
            msg.body = f"""
            Hello,
            To reset your password, enter this code: 
            {random_code}"""
            mail.send(msg)
            flash("Great news! An email containing a 5 digit code has been sent to your email account. Enter the code below!")
            return redirect(url_for("confirm_code", email=email, random_code=random_code, table=table))
    return render_template("password_management/forgot_password.html", form=form, title= "Forgot Password")

# Checks whether the code the user received corresponds to the one in the database
@app.route("/confirm_code/<email>/<random_code>/<table>", methods=["GET", "POST"])
def confirm_code(email,random_code,table):
    form = CodeForm()
    if form.validate_on_submit():
        code = form.code.data.strip()

        if code != random_code:
            form.code.errors.append("Oh no, that's not the code in your email!")
        else:
            flash("Code correct! Now you can reset your password :)")
            session["username"] = email
            return redirect(url_for("change_password", table=table))
    return render_template("password_management/confirm_code.html", form=form, title= "Confirm code")

##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
'''
            ALL FEATURES BELOW ARE RELATED TO THE MANAGER
'''
##############################################################################################################################################
##############################################################################################################################################
##############################################################################################################################################
def get_random_password():
    random_char = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase) 
    password += random.choice(string.ascii_lowercase) + random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase) + random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(2):
        password += random.choice(random_char)

    password_list = list(password)
    # shuffle all characters to make it even more random
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return password

# Manager account
@manager_only
@app.route("/manager")
def manager():
    return render_template("manager/dashboard.html")

# View and manage all employees
#@manager_only
@app.route("/view_all_employees")
def view_all_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM staff")
    employees = cur.fetchall()
    return render_template("manager/employees.html", employees=employees, title="Employee Data")

# Add new employee
@app.route("/add_new_employee", methods=["GET", "POST"])
#@manager_only
def add_new_employee():
    cur = mysql.connection.cursor()
    form = EmployeeForm()
    if form.validate_on_submit():
        role = form.role.data
        email = form.email.data
        access_level = form.access_level.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        password = get_random_password()
        
        cur.execute("""INSERT INTO staff (email, role, access_level, first_name, last_name, password)
                            VALUES (%s,%s,%s,%s,%s,%s);""", (email, role, access_level, first_name, last_name, generate_password_hash(password)))
        mysql.connection.commit()
        
        # Notify employee's email about their new account
        message = "Please sign into your account with your email and password:" + password
        msg = Message("Welcome on board! We're happy you joined us.", sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        
        flash ("New employee successfully added!")
        return redirect(url_for("view_all_employees"))
    return render_template("manager/new_staff_form.html", form=form, title="Add New Employee")   

# View queries from users
#@manager_only
@app.route("/view_query")
def view_query():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_queries")
    queries = cur.fetchall()
    return render_template("manager/queries.html", queries=queries)

# Delete queries from users
#@manager_only
@app.route("/delete_query/<int:id>")
def delete_query(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user_queries WHERE query_id=%s", (id,))
    cur.fetchone()
    mysql.connection.commit()
    flash ("Deleted!")
    return redirect(url_for("view_query"))

# Manager can reply to user queries
#@manager_only
@app.route("/reply_email/<id>", methods=["GET", "POST"])
def reply_email(id):
    cur = mysql.connection.cursor()
    form = ReplyForm()
    cur.execute("SELECT * FROM user_queries WHERE query_id=%s", (id,))
    query = cur.fetchone()

    if form.validate_on_submit() == False:
        flash('All fields are required.')
    else:
        email = form.email.data
        subject = form.subject.data
        message = form.message.data

        msg = Message("Replying to your query: "+subject, sender='no.reply.please.and.thank.you@gmail.com', recipients=[email])   
        msg.body = f"""{message}"""
        mail.send(msg)
        flash("Message sent successfully.")
    return render_template("manager/reply_email.html",form=form, title="Reply", query=query)








if __name__ == '__main__':
    app.run(debug=True)

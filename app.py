from flask import Flask, render_template, redirect, url_for, session, g, request, make_response, flash
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
#from forms import RegisterForm, LoginForm
from functools import wraps
from flask_mysqldb import MySQL 

app = Flask(__name__)

app.config["SECRET_KEY"] = "MY_SECRET_KEY"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['MYSQL_USER'] = 'root' # someone's deets
app.config['MYSQL_PASSWORD'] = '8800' # someone's deets
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'world' # someone's deets
app.config['MYSQL_CURSORCLASS']= 'DictCursor'

mysql = MySQL(app)

#general priority queue for kitchen staff
#checks login details to see if your a kitchen staff or manager

@app.route('/kitchen', methods=['GET','POST'])
def kitchen():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT d.name, o.time, d.cook_time, o.tableNo, o.notes, o.status, o.dish_id
                    FROM orders as o 
                    JOIN dish as d 
                    ON o.dish_id=d.dish_id
                    ORDER BY o.notes='priority' DESC,
                            o.time,
                            o.time*d.cook_time DESC,
                            o.tableNo,  
                            d.cook_time DESC,
                            d.category='starter',
                            d.category='main',
                            d.category='side',
                            d.category='dessert';''')
    orderlist=cur.fetchall()
        
    return render_template('kitchen.html',orderlist=orderlist)

@app.route('/<int:dish_id>,<int:time>/kitchenUpdate', methods=['GET','POST'])

def kitchenUpdate(dish_id, time):
    cur = mysql.connection.cursor()
    cur.execute('''UPDATE orders
                                SET status="ongoing" 
                                WHERE time=%s and status="unmade" 
                                and dish_id=%s 
                                LIMIT 1;''',(time, dish_id))
    mysql.connection.commit()

    return redirect(url_for('kitchen'))

@app.route('/<int:dish_id>,<int:time>/kitchenDelete', methods=['GET','POST'])
def kitchenSentOut(dish_id, time):
    
    cur = mysql.connection.cursor()

    cur.execute('''UPDATE orders
                                SET status="sent out"
                                WHERE time=%s and status="ongoing" 
                                and dish_id =%s
                                LIMIT 1;''',(time, dish_id))
    mysql.connection.commit()

    return redirect(url_for('kitchen'))

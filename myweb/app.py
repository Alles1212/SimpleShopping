from flask import Flask, render_template, request, jsonify, flash, session, redirect, url_for
from flask_mysqldb import MySQL#default為MySQLdb pip install wheel, pip install mysqlclient
from application import create_app


app = create_app()
app.config["SECRET_KEY"] = '57e3b0516c0bbf2a20b555579980b875'#secrets.token_hex(16)
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Flask                    2.3.2(改到3.0.0 solved)

mysql = MySQL(app)

# Check MySQL connection
with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT 1')
    result = cursor.fetchone()

    if result:
        print('Connected to MySQL')
    else:
        print('Failed to connect to MySQL')

    # Close the cursor
    cursor.close()

#pos 商家:1 使用者:0
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        pos = request.form['pos']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, password, pos) VALUES (%s, %s, %s)",(name, password, pos))
        mysql.connection.commit()

        cur.close()

        flash("Register success","success")

    return render_template('login_regi.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE name = %s AND password = %s", (name, password))
        user = cur.fetchone()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            if user['pos'] == 0:# 0:客戶
                flash('customerUser Login successful.', 'success')            
                return render_template('browse_client.html')
            else:# 1:商家
                flash('shopUser Login successful.', 'success')
                return render_template('browse.html') 
        else:
            flash('Login failed. Please check your username and password.', 'danger')

        cur.close()

    return render_template('login_regi.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login_regi'))

@app.route('/cartList')#列出購物車
def cartlist():
    cur = mysql.connection.cursor()

    cartItem = cur.execute("SELECT * FROM customer_cart")

    # columns = [column[0] for column in cur.description]

    if cartItem > 0:
        print("items")
        
        cartLists = cur.fetchall()
        # cartLists_dict = [dict(zip(columns, row)) for row in cartLists]
        items_num = len(cartLists)

        cur.close()
        return render_template('cart.html', cartLists = cartLists, items_num = items_num)
    
    else:
        print("no item")
        items_num = 0

        cur.close()
        return render_template('cart.html', cartLists = cartLists, items_num = items_num)
    
    
@app.route('/add_cart/<int:id>')
def add_cart(id,amount):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id = %s", (id,))

    item_add = cur.fetchone()
    if item_add:
        product = item_add['name']
        price = item_add['price']
        if (amount>item_add['stock']):
             flash('產品庫存不足', 'danger')
        else:
            amount=amount
        sumPrice = price * amount
        
        cur.execute("INSERT INTO customer_cart (product, price, amount, sumPrice) VALUES (%s, %s, %s, %s)",(product, price, amount, sumPrice))
        mysql.connection.commit()
        cur.close()
        flash('成功加入購物車', 'success')
        return redirect(url_for('cartlist'))
    else:
        cur.close()
        flash('產品不存在', 'danger')
        return redirect(url_for('cartlist'))
    
@app.route('/del_cart/<int:id>')
def del_cart(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM customer_cart WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    flash('已移出購物車', 'danger')
    return index()




@app.route('/shop')
def index():
    # product data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from product")


    # Get column names to use as keys in the dictionaries
    # columns = [column[0] for column in cur.description]

    # Fetch all rows as a list of dictionaries
    products = cur.fetchall() #更動
    # products = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('browse.html', products = products)

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        # Create MySQL cursor
        cur = mysql.connection.cursor()

        try:
            # Insert data into the database
            cur.execute("INSERT INTO product (name, price, stock) VALUES (%s, %s, %s)", (name, price, stock))

            # Commit changes and close the cursor
            mysql.connection.commit()

            # Return a JSON response
            return jsonify({'success': True, 'message': 'Data inserted successfully'})

        except Exception as e:
            # Rollback changes in case of an error
            mysql.connection.rollback()

            # Return a JSON response in case of an error
            return jsonify({'success': False, 'message': str(e)})

        finally:
            # Close the cursor
            cur.close()

    return render_template('index.html')
@app.route('/delete_product/<int:id>')
def delete_product(id):

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()

    return index()
@app.route('/change_product/<int:id>')
def change_product(id):
   # product data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from product WHERE id = %s", (id,))
     # Get column names to use as keys in the dictionaries
    columns = [column[0] for column in cur.description]

    # Fetch all rows as a list of dictionaries
    products = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('change_product.html', products=products)
@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        id = request.form['id']

        # Create MySQL cursor
        cur = mysql.connection.cursor()

        try:
            # Update data in the database
            cur.execute("UPDATE product SET name=%s, price=%s, stock=%s WHERE id=%s", (name, price, stock, id))

            # Commit changes and close the cursor
            mysql.connection.commit()

            # Return a JSON response
            return jsonify({'success': True, 'message': 'Data updated successfully'})

        except Exception as e:
            # Rollback changes in case of an error
            mysql.connection.rollback()

            # Return a JSON response in case of an error
            return jsonify({'success': False, 'message': str(e)})

        finally:
            # Close the cursor
            cur.close()

    return index()
if __name__ == "__main__":
    app.run(debug=True, port=8000)
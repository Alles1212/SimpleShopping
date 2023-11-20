from flask import Flask, render_template, request, jsonify, flash, session, redirect, url_for
from flask_mysqldb import MySQL
# from flaskext.mysql import MySQL
# from flask_mysql_connector import MySQL
from application import create_app

app = create_app()
app.config["SECRET_KEY"] = '57e3b0516c0bbf2a20b555579980b875'#secrets.token_hex(16)
# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)
# mysql.init_app(app)
# mysql.init_app(app)

if mysql.connection:
    print("connected") 
else:
    print("retry")
    print(mysql.connection)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s)",(name, password))
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
            flash('Login successful.', 'success')
            return redirect(url_for('Home'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')

        cur.close()

    return render_template('login_regi.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login_regi'))

@app.route('/cartList')#test 還沒寫
def list():
    cur = mysql.connection.cursor()

    cartItem = cur.execute("SELECT * FROM cart")

    if cartItem > 0:
        cartLists = cur.fetchall()

        return render_template('cart.html', cartLists = cartLists)

@app.route('/shop')
def index():
    # product data
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * from product")
        # Get column names to use as keys in the dictionaries
        columns = [column[0] for column in cur.description]

        # Fetch all rows as a list of dictionaries
        products = [dict(zip(columns, row)) for row in cur.fetchall()]
        return render_template('index.html', products=products)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        # Close the cursor
        cur.close()

# @app.route('/add_cart/<int: id>')#test
# def add_cart(id):
#     cart = []
#     if mysql.connection:
#         cur = mysql.connection.cursor()
#         try:
#             cur.execute("SELECT * from product WHERE id = %s", (id,))



@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        # Check if MySQL connection is successful
        if mysql.connection:
            # Create MySQL cursor
            cur = mysql.connection.cursor()
            print("cur exists")

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
        else:
            return jsonify({'success': False, 'message': 'MySQL connection failed'})

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
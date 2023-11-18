from flask import Flask, render_template, request, jsonify
from flask_mysqldb import MySQL
from application import create_app

app = create_app()

# MySQL Configuration
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)
@app.route('/shop')
def index():
    # product data
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from product")
     # Get column names to use as keys in the dictionaries
    columns = [column[0] for column in cur.description]

    # Fetch all rows as a list of dictionaries
    products = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()
    return render_template('index.html', products=products)

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

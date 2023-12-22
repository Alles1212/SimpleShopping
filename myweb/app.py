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

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from product")
    products = cur.fetchall()
    cur.close()
    return render_template("index.html", products = products)

#pos 物流:2 商家:1 使用者:0 
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

        cur.execute("SELECT * FROM product")
        products = cur.fetchall()
        #選擇所有訂單
        cur.execute("SELECT * FROM product")
        transport=cur.fetchall()

        pos ={0:'客戶',1:'商家',2:'物流'}
        if user:
            session['user_id'] = user['id']
            print(user['id'])
            print (type(session['user_id']))
            session['user_name'] = user['name']
            session['user_pos'] = pos[user['pos']]

            if user['pos'] == 0:# 0:客戶
                flash('customerUser Login successful.', 'success')            
                return render_template('browse_client.html', products = products)
            elif user['pos'] == 1:# 1:商家
                flash('shopUser Login successful.', 'success')
                return render_template('browse.html', products = products) 
            else:# 2:物流
                flash('shipUser Login successful.', 'success')
                return render_template('transport.html', transport = transport ) 
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
    cartItem = cur.execute("SELECT * FROM customer_cart WHERE user_id = %s", (session['user_id'],))#對應到各自購物車
    # cartItem_personal = cur.fetchone()
    if cartItem > 0:
        # if session['user_id'] == cartItem['user_id']:    
        print("items")        
        cartLists = cur.fetchall()
        items_num = len(cartLists)

        cur.close()
        return render_template('cart.html', cartLists = cartLists, items_num = items_num)
    
    else:
        print("no item")
        items_num = 0

        cur.close()
        return render_template('cart.html', cartLists = [], items_num = items_num)
    
    
@app.route('/add_cart/<int:id>', methods=['POST'])
def add_cart(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM product WHERE id = %s", (id,))
    amount_str = request.form.get('amount')
    amount = int(amount_str)
    item_add = cur.fetchone()
    if item_add:
        product = item_add['name']
        price = item_add['price']
        description = item_add['description']
        shop_id = item_add['shop_id']
        user_id = session['user_id']

        if (amount>=item_add['stock']):
            flash('產品庫存不足', 'danger')
            return redirect(url_for('cartlist'))
        else:
            amount=amount
        sumPrice = price * amount
        
        cur.execute("INSERT INTO customer_cart (product, price, amount, sumPrice, description, user_id, shop_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",(product, price, amount, sumPrice, description, user_id, shop_id))
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
    return redirect(url_for('cartlist'))

@app.route('/reduce_cartNum/<int:id>', methods=['POST'])
def reduce(id):
    cur = mysql.connection.cursor()
    reduce_amount = request.form.get('amount')
    cur.execute("SELECT amount,price FROM customer_cart WHERE id = %s", (id,))
    result = cur.fetchone()
    print(result)
    print(result['amount'])
    print(result['price'])
    # print(result['price'])
    # print(result['sumPrice'])
    # if result:
    #     origin = result[3]
    # print(origin)
    reduce_amount = int(reduce_amount)
    sumPrice = result['price'] * (result['amount'] - reduce_amount)
    print(reduce_amount)
    if (reduce_amount > result['amount']):
        flash('不能刪減多於原數量', 'danger')
    else:
        cur.execute("UPDATE customer_cart SET amount=%s, sumPrice=%s WHERE id=%s ", (result['amount'] - reduce_amount, sumPrice, id))
        mysql.connection.commit()#才會commit
        cur.close()
        flash('商品數量已減少', 'success')
    return redirect(url_for('cartlist'))


# #商家頁面
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
        description = request.form['description']
        # Create MySQL cursor
        cur = mysql.connection.cursor()

        try:
            # Insert data into the database
            cur.execute("INSERT INTO product (name, price, stock,description) VALUES (%s, %s, %s,%s)", (name, price, stock,description))

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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from product WHERE id = %s", (id,))
    # Fetch all rows as a list of dictionaries
    products = cur.fetchall() #更動
    # products = [dict(zip(columns, row)) for row in cur.fetchall()]
    cur.close()   
    return render_template('change_product.html', products=products)

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        id = request.form['id']
        description = request.form['description']

        # Create MySQL cursor
        cur = mysql.connection.cursor()

        try:
            # Update data in the database
            cur.execute("UPDATE product SET name=%s, price=%s, stock=%s,description=%s  WHERE id=%s", (name, price, stock, description, id ))

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
#列出所有的訂單
@app.route('/transport', methods=['POST'])
def transport():
    cur = mysql.connection.cursor()
    # 從資料庫中擷取所有狀態
    cursor.execute("SELECT * FROM `order`")
    transports= cursor.fetchall()
    # 关闭数据库连接
    cur.close()
    # 渲染 HTML 模板并传递订单数据
    return render_template('transport.html', transports=transports)

@app.route('/change_status/<order_id>',methods=['POST'])
def change_status(order_id):
    cur = mysql.connection.cursor()
    # 從資料庫中擷取該訂單的狀態
    cursor.execute("SELECT `product_state` FROM `order` WHERE `order_id` = %s", (order_id,))
    # 获取订单状态
    order_status = cur.fetchone()
    # 如果订单的状态已经是 'Shipped'
    if order_status['product_state'] == 'Shipped':
        # 如果出貨了就改成已經送達了
        cur.execute("UPDATE `order` SET `product_state` = 'Delivered' WHERE `order_id` = %s", (order_id,))
    else:
        # 如果还没出货就改成已經出貨
       cur.execute("UPDATE `order` SET `product_state` = 'Shipped' WHERE `order_id` = %s", (order_id,))
    # 提交修改到数据库
    mysql.connection.commit()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
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
        pos ={0:'客戶',1:'商家',2:'物流'}
        if user:
            session['user_id'] = user['id']
            print(user['id'])
            print (type(session['user_id']))
            session['user_name'] = user['name']
            session['user_pos'] = pos[user['pos']]
            session['pos']=user['pos']

            if user['pos'] == 0:# 0:客戶
                flash('customerUser Login successful.', 'success')            
                return render_template('browse_client.html', products = products)
            elif user['pos'] == 1:# 1:商家
                flash('shopUser Login successful.', 'success')
                return index() 
            else:# 2:物流
                flash('shipUser Login successful.', 'success')
                return transport()
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

        if amount > item_add['stock']:
            flash('產品庫存不足', 'danger')
            return redirect(url_for('cartlist'))
        else:
            sumPrice = price * amount
            cur.execute("INSERT INTO customer_cart (product, price, amount, sumPrice, description, user_id, shop_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",(product, price, amount, sumPrice, description, user_id, shop_id))
            cur.execute("UPDATE product SET stock=stock-%s WHERE name=%s", (amount, product))
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
    elif(reduce_amount == result['amount']):
        cur.execute("UPDATE product SET stock=%s WHERE id=%s", (result['amount'], id))
        mysql.connection.commit()
        cur.execute("DELETE FROM customer_cart WHERE id=%s",(id,))
        mysql.connection.commit()
        cur.close()
        flash('商品已為0刪除', 'success')
    else:
        cur.execute("UPDATE customer_cart SET amount=%s, sumPrice=%s WHERE id=%s ", (result['amount'] - reduce_amount, sumPrice, id))
        mysql.connection.commit()#才會commit
        cur.close()
        flash('商品數量已減少', 'success')
    return redirect(url_for('cartlist'))

@app.route('/be_order')
def be_order():
    cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM customer_cart WHERE user_id = %s", (session['user_id'],))
    # cus_products = cur.fetchone()
    try:
        cur.execute("SELECT * FROM customer_cart WHERE user_id = %s", (session['user_id'],))#該使用者的購物車
        cus_products = cur.fetchall()
        print(cus_products)
        if cus_products:
            cur.execute("SELECT * FROM `order`")
            order_now = cur.fetchall()
            if order_now:
                # tmp = 0
                k = 0
                for i in range(len(order_now)):
                        # oId = k
                        # print(k)
                        if k != int(order_now[i]['oId']):
                            oId = k                            
                            # print(k)
                            continue
                        else:
                            k += 1
                            continue

            for i in range(len(cus_products)):
                oId = k#同筆訂單oId相同
                uId = session['user_id']
                pId = int(cus_products[i]['shop_id'])#哪個商家id
                product = cus_products[i]['product']
                sumPrice = cus_products[i]['sumPrice']
                amount = int(cus_products[i]['amount'])
                product_state = "unChecked"#訂單狀態
                review = 0#評價?

                cur.execute("INSERT INTO `order` (oId, uId, pId, product, sumPrice, amount, product_state, review) VALUES (%s, %s, %s,%s, %s, %s, %s, %s)", (oId, uId, pId,product, sumPrice, amount,product_state, review))
                mysql.connection.commit()
                cur.execute("TRUNCATE TABLE `customer_cart`")
                mysql.connection.commit()



            with mysql.connection.cursor() as cur2:
                orderItem = cur2.execute('SELECT * FROM `order` WHERE uId=%s', (uId,))
                if orderItem > 0:
                    order_products = cur2.fetchall()
                    items_num = len(order_products)
                else:
                    order_products = []
                    items_num = 0

            # return render_template('order.html', order_products = order_products, items_num = items_num)

    except Exception as e:
        # Rollback changes in case of an error
        mysql.connection.rollback()
        print("exception")
        # Return a JSON response in case of an error
        return jsonify({'success': False, 'message': str(e)})

    finally:
        # Close the cursor
        cur.close()

    # return jsonify({'success': False, 'message': 'No products found for the user'})

    return order()

# #商家頁面
@app.route('/shop')
def index():
    if session['pos']==1:
        
    
        # product data
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from product WHERE shop_id = %s", (session['user_id'],))
    

        # Get column names to use as keys in the dictionaries
        # columns = [column[0] for column in cur.description]

        # Fetch all rows as a list of dictionaries
        products = cur.fetchall() #更動
        # products = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return render_template('browse.html', products = products)
    else:
        return index()

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
            cur.execute("INSERT INTO product (name, price, stock,description,shop_id) VALUES (%s, %s, %s,%s,%s)", (name, price, stock,description,session['user_id']))

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
@app.route('/shop_order')
def shop_order():
    cur = mysql.connection.cursor()
    if session['pos']==1:
        # 使用反引號標記 SQL 保留字
        shop_order = cur.execute("SELECT * FROM `order` WHERE pId = %s", (session['user_id'],))
        
        if shop_order > 0:
            # 取得結果
            shop_order_result = cur.fetchall()
            items_num = len(shop_order_result)

            # 關閉 cursor
            cur.close()

            # 傳遞結果至模板
            return render_template('shop_order.html', shop_orders=shop_order_result, items_num=items_num)
        
        else:
            items_num = 0
            cur.close()
            return render_template('shop_order.html', shop_orders=[], items_num=items_num)
    else:
        return order()


@app.route('/order')
def order():
    cur = mysql.connection.cursor()

    # 使用反引號標記 SQL 保留字
    orderItem= cur.execute("SELECT * FROM `order` WHERE uID = %s", (session['user_id'],))
    
    if orderItem> 0:
        # 取得結果
        orderItem_result = cur.fetchall()
        items_num = len(orderItem_result)
        
        # 關閉 cursor
        cur.close()

        # 傳遞結果至模板
        return render_template('order.html', order_products=orderItem_result, items_num=items_num)
    
    else:
        items_num = 0
        cur.close()
        return render_template('order.html', order_products=[], items_num=items_num)


@app.route('/ok_order/<int:id>')
def ok_order(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE `order` SET `product_state` = %s WHERE `order_id` = %s", ("處理中訂單", id,))
    mysql.connection.commit()
    cur.close()

    return shop_order()

@app.route('/deliver_order/<int:id>')
def deliver_order(id):

    cur = mysql.connection.cursor()
    cur.execute("UPDATE `order` SET `product_state` = %s WHERE `order_id` = %s", ("delivering", id,))
    mysql.connection.commit()
    cur.close()

    return transport()

#列出所有的訂單
@app.route('/transport',methods=['POST'])
def transport():
    cur = mysql.connection.cursor()
    # 從資料庫中擷取所有狀態
    cur.execute("SELECT * FROM `order` ")
    transports= cur.fetchall()
    # 关闭数据库连接
    cur.close()
    # 渲染 HTML 模板并传递订单数据
    return render_template('transport.html', transports=transports)

#列出評價

@app.route('/write_review/<int:id>',methods=['POST','GET'])
def write_review(id):
    cur = mysql.connection.cursor()
    # 從資料庫中擷取所有狀態
    cur.execute("SELECT * FROM `order` WHERE `order_id` = %s", (id,))
    orderItem= cur.fetchone()
    # 关闭数据库连接
    cur.close()
    # 渲染 HTML 模板并传递订单数据
    return render_template('review.html', orderItem = orderItem)


@app.route('/setreview/<int:id>', methods=['POST'])
def set_review(id):
    try:
        # 从表单中获取评论
        review = request.form.get('review')

        # 更新数据库中的订单信息
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `order` SET `review` = %s WHERE `order_id` = %s", (review, id,))
        mysql.connection.commit()
        cur.close()

        # 重定向到订单页面或其他页面
        return redirect(url_for('order'))
    except Exception as e:
        # 处理错误
        return jsonify({'success': False, 'message': str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=8000)
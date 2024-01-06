# # 創建用戶表
# with app.app_context():
#     cur = mysql.connection.cursor()
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INT AUTO_INCREMENT PRIMARY KEY,
#             username VARCHAR(255) NOT NULL,
#             password VARCHAR(255) NOT NULL
#         )
#     """)
#     mysql.connection.commit()
#     cur.close()

# # 註冊路由
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # 檢查用戶是否已經存在
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE username = %s", (username,))
#         existing_user = cur.fetchone()

#         if existing_user:
#             flash('Username already exists. Please choose a different one.', 'danger')
#         else:
#             # 將用戶信息插入數據庫
#             cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
#             mysql.connection.commit()
#             flash('Registration successful. You can now log in.', 'success')
#             return redirect(url_for('login'))

#         cur.close()

#     return render_template('login.html')

# # 登入路由
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # 檢查用戶名和密碼是否匹配
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
#         user = cur.fetchone()

#         if user:
#             session['user_id'] = user['id']
#             flash('Login successful.', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Login failed. Please check your username and password.', 'danger')

#         cur.close()

#     return render_template('login.html')

# # 登出路由
# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     flash('You have been logged out.', 'success')
#     return redirect(url_for('login'))

# # 儀表板路由
# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' in session:
#         return render_template('dashboard.html')
#     else:
#         flash('You need to log in first.', 'warning')
#         return redirect(url_for('login'))
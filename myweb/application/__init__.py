from flask import Flask
from application.route import hello_world, Home ,add_shop

# app = Flask(__name__,template_folder='templates')#construct
# app.config["SECRET_KEY"] = '57e3b0516c0bbf2a20b555579980b875'#secrets.token_hex(16)


def create_app():
    app = Flask(__name__)
    app.add_url_rule('/', '/', hello_world)
    #app.add_url_rule('/shop', 'shop', Home)
    app.add_url_rule('/add_shop', 'add_shop', add_shop)
    return app
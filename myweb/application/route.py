from flask import render_template, redirect, url_for

def hello_world():
    return "Hello, MVC框架!"

def Home():
    return render_template("index.html") 
def add_shop():
    return render_template("add_shop.html")


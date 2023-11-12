from flask import Flask
from application import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8000)
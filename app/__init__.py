from flask import Flask
from os import getenv


app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
from . import routes, auth
from app.content import get_category_list


@app.context_processor
def inject_nav():
    category_list = get_category_list()
    return dict(category_list=category_list)
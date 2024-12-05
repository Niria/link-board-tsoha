from flask import Flask, session
from os import getenv

from app.utils import b64encode

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.jinja_env.filters['b64encode'] = b64encode
from app import routes, auth, admin
from app.content import get_category_list


@app.context_processor
def inject_nav():
    user_id = session.get("user_id")
    if user_id:
        category_list = get_category_list(user_id)
    else:
        category_list = get_category_list()
    return dict(category_list=category_list)
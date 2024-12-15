from os import getenv

from flask import Flask, session
from flask_wtf import CSRFProtect

from app.utils.thumbnail import b64encode

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
CSRFProtect(app)
app.jinja_env.filters["b64encode"] = b64encode
from app import routes
from app.services.categories import get_category_list


@app.context_processor
def inject_nav():
    user_id = session.get("user_id")
    if user_id:
        category_list = get_category_list(user_id)
    else:
        category_list = get_category_list()
    return dict(category_list=category_list)

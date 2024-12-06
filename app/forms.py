from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.fields.choices import RadioField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, URL, InputRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=24)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField("Login")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=24)])
    display_name = StringField("Display name", validators=[DataRequired(), Length(min=3, max=24)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=64), EqualTo("password2", message="Passwords must match")])
    password2 = PasswordField("Confirm password", validators=[DataRequired(), Length(min=8, max=64)])
    submit = SubmitField("Register")


class NewCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=32)])
    description = StringField("Description", validators=[Length(min=0, max=255)])
    is_public = BooleanField("Is public", validators=[DataRequired()])
    submit = SubmitField("Create")


class EditCategoryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=32)])
    description = StringField("Description", validators=[Length(min=0, max=255)])
    is_public = BooleanField("Is public", validators=[DataRequired()])
    submit = SubmitField("Update")

class ThreadForm(FlaskForm):
    url = StringField("URL", validators=[DataRequired(), Length(min=3, max=64), URL()])
    title = StringField("Title", validators=[DataRequired(), Length(min=3, max=64)])
    message = StringField("Message", validators=[Length(min=0, max=1000)])

class NewThreadForm(ThreadForm):
    fetch_image = BooleanField("Fetch image")
    submit = SubmitField("Create")

class EditThreadForm(ThreadForm):
    refresh_image = RadioField("Thumbnail", choices=[("refresh", "Refresh"), ("keep", "Keep"), ("delete", "Delete")])
    submit = SubmitField("Confirm")

class AdminEditThreadForm(EditThreadForm):
    visible = BooleanField("Visibility")

class ReplyForm(FlaskForm):
    message = TextAreaField("Message", validators=[Length(min=1, max=1000, message=f"Reply must be between %(min)d  and %(max)d characters")])

class NewReplyForm(ReplyForm):
    thread_id = HiddenField("thread_id")
    parent_id = HiddenField("parent_id")
    user_id = HiddenField("user_id")
    submit = SubmitField("Create")

class EditReplyForm(ReplyForm):
    submit = SubmitField("Confirm")

class AdminEditReplyForm(EditReplyForm):
    visible = BooleanField("Visible", validators=[InputRequired()])

class EditUserProfileForm(FlaskForm):
    display_name = StringField("Display name", validators=[InputRequired(), Length(min=3, max=24)])
    description = TextAreaField("Description", validators=[Length(min=0, max=1000)])
    is_public = BooleanField("Is public")
    submit = SubmitField("Update profile")

class AddPermissionsForm(FlaskForm):
    user_id = SelectField("Username", coerce=int, validators=[InputRequired()])
    submit = SubmitField("Add")

class RemovePermissionsForm(FlaskForm):
    user_id = HiddenField("user_id", validators=[InputRequired()])
    submit = SubmitField("Remove")
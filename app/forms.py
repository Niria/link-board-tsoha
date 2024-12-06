from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.fields.choices import RadioField, SelectField
from wtforms.validators import Length, EqualTo, URL, InputRequired, DataRequired


class StripFlaskForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            if my_strip_filter not in filters:
                filters.append(my_strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)

def my_strip_filter(value):
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value

class UserForm(StripFlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=3, max=24)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=64)])

class LoginForm(UserForm):
    submit = SubmitField("Login")

class RegistrationForm(UserForm):
    display_name = StringField("Display name", validators=[InputRequired(), Length(min=3, max=24)])
    confirm = PasswordField("Confirm password", validators=[InputRequired(), Length(min=8, max=64), EqualTo("password")])
    submit = SubmitField("Register")

class CategoryForm(StripFlaskForm):
    name = StringField("Name", validators=[InputRequired(), Length(min=2, max=32)])
    description = StringField("Description", validators=[Length(min=0, max=255)])
    is_public = BooleanField("Is public")

class NewCategoryForm(CategoryForm):
    submit = SubmitField("Create")

class EditCategoryForm(CategoryForm):
    submit = SubmitField("Update")

class ThreadForm(StripFlaskForm):
    url = StringField("URL", validators=[InputRequired(), Length(min=3, max=64), URL()])
    title = StringField("Title", validators=[InputRequired(), Length(min=3, max=64)])
    message = StringField("Message", validators=[Length(min=0, max=1000)])

class NewThreadForm(ThreadForm):
    fetch_image = BooleanField("Fetch image")
    submit = SubmitField("Create")

class EditThreadForm(ThreadForm):
    refresh_image = RadioField("Thumbnail", choices=[("refresh", "Refresh"), ("keep", "Keep"), ("delete", "Delete")])
    submit = SubmitField("Confirm")

class AdminEditThreadForm(EditThreadForm):
    visible = BooleanField("Visibility")

class ReplyForm(StripFlaskForm):
    message = TextAreaField("Message",
                            validators=[Length(min=1, max=1000,
                                               message=f"Reply must be between %(min)d  and %(max)d characters")])

class NewReplyForm(ReplyForm):
    parent_id = HiddenField("parent_id")
    submit = SubmitField("Create")

class EditReplyForm(ReplyForm):
    submit = SubmitField("Confirm")

class AdminEditReplyForm(EditReplyForm):
    visible = BooleanField("Visible", validators=[InputRequired()])

class EditUserProfileForm(StripFlaskForm):
    display_name = StringField("Display name", validators=[InputRequired(), Length(min=3, max=24)])
    description = TextAreaField("Description", validators=[Length(min=0, max=1000)])
    is_public = BooleanField("Is public")
    submit = SubmitField("Update profile")

class AddPermissionsForm(StripFlaskForm):
    user_id = SelectField("Username", coerce=int, validators=[InputRequired()])
    submit = SubmitField("Add")

class RemovePermissionsForm(StripFlaskForm):
    user_id = HiddenField("user_id", validators=[InputRequired()])
    submit = SubmitField("Remove")
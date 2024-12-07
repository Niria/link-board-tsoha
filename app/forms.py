from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, TextAreaField, URLField
from wtforms.fields.choices import RadioField, SelectField
from wtforms.validators import Length, EqualTo, URL, InputRequired


class StripFlaskForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = unbound_field.kwargs.get('filters', [])
            if strip_filter not in filters:
                filters.append(strip_filter)
            return unbound_field.bind(form=form, filters=filters, **options)

def strip_filter(value):
    if value is not None and hasattr(value, 'strip'):
        return value.strip()
    return value

class UserForm(StripFlaskForm):
    username = StringField("Username", validators=[InputRequired("Username is required"), Length(min=3, max=24, message="Username must be between %(min)d and %(max)d characters long")])
    password = PasswordField("Password", validators=[InputRequired("Password is required"), Length(min=8, max=64, message="Password must be between %(min)d and %(max)d characters long")])

class LoginForm(UserForm):
    submit = SubmitField("Login")

class RegistrationForm(UserForm):
    display_name = StringField("Display Name", validators=[InputRequired(message="Display name is required"), Length(min=3, max=24, message="Display name must be between %(min)d and %(max)d characters long")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired("Password confirmation is required"), Length(min=8, max=64, message="Password must be between %(min)d and %(max)d characters long"), EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Register")

class CategoryForm(StripFlaskForm):
    name = StringField("Name", validators=[InputRequired("Category name is required"), Length(min=2, max=32, message="Category name must be between %(min)d and %(max)d characters long")])
    description = TextAreaField("Description", validators=[Length(min=0, max=255, message="Category description can be up to %(max)d characters long")])
    is_public = BooleanField("Public Category")

class NewCategoryForm(CategoryForm):
    submit = SubmitField("Create")

class EditCategoryForm(CategoryForm):
    submit = SubmitField("Update")

class ThreadForm(StripFlaskForm):
    url = URLField("URL", validators=[InputRequired("Link URL is required"), Length(min=3, max=64, message="Link URL must be between %(min)d and %(max)d characters long"), URL()])
    title = StringField("Title", validators=[InputRequired("Link title is required"), Length(min=3, max=64, message="Link title must be between %(min)d and %(max)d characters long")])
    message = StringField("Message", validators=[Length(min=0, max=1000, message="Message must be between %(min)d and %(max)d characters long")])

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
                                               message="Reply must be between %(min)d and %(max)d characters long")])

class NewReplyForm(ReplyForm):
    parent_id = HiddenField("parent_id")
    submit = SubmitField("Create")

class EditReplyForm(ReplyForm):
    submit = SubmitField("Confirm")

class AdminEditReplyForm(EditReplyForm):
    visible = BooleanField("Visible", validators=[InputRequired("Visibility setting is required")])

class EditUserProfileForm(StripFlaskForm):
    display_name = StringField("Display Name",
                               validators=[InputRequired("Display name is required"),
                                           Length(min=3, max=24, message="Display name must be between %(min)d and %(max)d characters long")])
    description = TextAreaField("Description",
                                validators=[Length(min=0, max=1000, message="Profile description can be up to %(max)d characters long")])
    is_public = BooleanField("Public Profile")
    submit = SubmitField("Update profile")

class AddPermissionsForm(StripFlaskForm):
    user_id = SelectField("Username", coerce=int, validators=[InputRequired("User id is required")])
    submit = SubmitField("Add")

class RemovePermissionsForm(StripFlaskForm):
    user_id = HiddenField("user_id", validators=[InputRequired("User id is required")])
    username = HiddenField("username", validators=[InputRequired("Username is required")])
    submit = SubmitField("Remove")

class SearchForm(StripFlaskForm):
    search_type = SelectField("Search Type", validators=[InputRequired("Search type is required")])
    search_string = StringField("Search Keyword",
                                validators=[InputRequired("Search string is required"),
                                            Length(min=3, max=12, message="Search keyword must be between %(min)d and %(max)d characters long")])
    submit = SubmitField("Search")
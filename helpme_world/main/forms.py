from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    """
    Collects keyword for searching by post title
    """
    keyword = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')
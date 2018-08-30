from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search=StringField('Search for free gym passes at gyms near you!', validators=[DataRequired()])
    submit=SubmitField('Search')
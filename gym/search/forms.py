from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search=StringField('Search for free gym passes at gyms near you!', validators=[DataRequired()])
    range =IntegerField('Search distance in miles', render_kw={"placeholder": "Search distance in miles"})
    submit=SubmitField('Search')
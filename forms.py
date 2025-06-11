from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    input_city = StringField("City Name", validators=[DataRequired()], render_kw={"placeholder": "Enter city, state, region, or country"})
    submit = SubmitField("Search")
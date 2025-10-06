# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class MovementForm(FlaskForm):
    product_id = SelectField('Product', coerce=str, validators=[DataRequired()])
    from_location = SelectField('From Location (optional)', coerce=str, validators=[Optional()])
    to_location = SelectField('To Location (optional)', coerce=str, validators=[Optional()])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')

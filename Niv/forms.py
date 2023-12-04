from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ClienteForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    direccion = StringField('Dirección')
    telefono = StringField('Teléfono')
    correo = StringField('Correo', validators=[DataRequired(), Email()])
    submit = SubmitField('Guardar')
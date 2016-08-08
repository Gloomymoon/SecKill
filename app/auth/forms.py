# -*- coding: UTF-8 -*
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms_components import read_only
from wtforms import ValidationError
from ..models import User


class RegistrationForm(Form):
    ip = StringField('IP', validators=[Required(), Length(1, 64)])
    name = StringField(u'User Name', validators=[Required(), Length(1, 64)])
    submit = SubmitField(u'Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        read_only(self.ip)

    def validate_ip(self, filed):
        if User.query.filter_by(ip=filed.data).first():
            raise ValidationError('')


from datetime import datetime
from flask_wtf import Form
from flask_login import current_user
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms_components import read_only
from wtforms import ValidationError
from ..models import User, Coupon


class ReserveSecKillForm(Form):
    datemark = StringField('Coupon Date')
    coupon = SelectField('Coupon Type', coerce=int, validators=[Required()])
    submit = SubmitField('Choose this target')

    def __init__(self, *args, **kwargs):
        super(ReserveSecKillForm, self).__init__(*args, **kwargs)
        read_only(self.datemark)
        self.coupon.choices = [(c.id, c.name) for c in Coupon.query.filter(Coupon.limit > 0).order_by(Coupon.id).all()]


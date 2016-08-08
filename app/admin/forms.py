from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField
from wtforms_components import read_only
from wtforms.validators import Required, Length, NumberRange
from wtforms import ValidationError
from ..models import User, Role, Coupon, SecKill


class AdminEditUserForm(Form):
    staff_id = StringField('Staff ID')
    name = StringField('Name', validators=[Required(), Length(1, 64)])
    role = SelectField('Role', coerce=int)
    confirmed = BooleanField('Confirmed')
    password = StringField('New password')
    submit = SubmitField('Update')

    def __init__(self, user, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        read_only(self.staff_id)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user


class AdminEditSecKillForm(Form):
    id = StringField('SecKill ID')
    datemark = StringField('Datamark')
    user_name = StringField('User Name')
    coupon_name = StringField('Coupon Name')
    reserved = BooleanField('Reserved')
    kill_time = StringField('Kill Datatime')
    reset_kill_time = BooleanField('Reset Kill Datatime')
    win = BooleanField('Win')
    submit = SubmitField('Update')
    def __init__(self, user, *args, **kwargs):
        super(AdminEditSecKillForm, self).__init__(*args, **kwargs)
        read_only(self.id)
        read_only(self.datemark)
        read_only(self.user_name)
        read_only(self.coupon_name)
        read_only(self.reserved)
        read_only(self.kill_time)


class EditCouponLimitForm(Form):
    type = SelectField('Coupon name', coerce=int)
    limit = StringField('Limit', validators=[Required, NumberRange(0, 9), 'Limit must between 0 and 9'])
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super(EditCouponLimitForm, self).__init__(*args, **kwargs)
        self.type.choices=[(cp.id, cp.name) for cp in CouponType.query.order_by(CouponType.id).all()]

    def validate_type(self, field):
        pass

# -*- coding: UTF-8 -*
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import RegistrationForm

'''
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
'''

@auth.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr
    user = User.query.filter_by(ip=ip).first()
    if user is not None:
        login_user(user)
        return redirect(request.args.get('next') or url_for('main.index'))
    return redirect(url_for('auth.register'))


@auth.route('/logout')
def logout():
    pass


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    ip = request.remote_addr
    form.ip.data = ip
    if form.validate_on_submit() and ip == form.ip.data:
        user = User(ip=form.ip.data, name=form.name.data)
        db.session.add(user)
        db.session.commit()
        flash('User profile has been updated.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

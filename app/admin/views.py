from datetime import datetime
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from . import admin
from .forms import AdminEditUserForm, EditCouponLimitForm, AdminEditSecKillForm
from .. import db
from ..models import User, Permission, Role, Coupon, SecKill
from ..decorators import admin_required


@admin.route('/user')
@login_required
@admin_required
def user():
    page = request.args.get('page', 1, type=int)
    query = User.query
    pagination = query.order_by(User.id.asc()).paginate(
        page, per_page = 20, error_out=False)
    users = pagination.items
    return render_template('admin/user.html', users=users, pagination=pagination)


@admin.route('/user/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
	pass



@admin.route('/seckill/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def seckill_edit(id):
    seckill = SecKill.query.filter_by(id=id).first_or_404()
    form = AdminEditSecKillForm(user=user)
    if form.validate_on_submit():
        seckill.win = form.win.data
        if form.reset_kill_time.data:
        	seckill.kill_time = datetime.min
        	seckill.win = False
        db.session.add(seckill)
        db.session.commit()
        flash('The record has been updated.')
        return redirect(url_for('admin.seckill_edit', id=seckill.id))
    form.id.data = seckill.id
    form.datemark.data = seckill.datemark
    form.user_name.data = seckill.user.name
    form.coupon_name.data = seckill.coupon.name
    form.reserved.data = seckill.reserved
    form.kill_time.data = seckill.kill_time
    form.win.data = seckill.win
    return render_template('admin/seckill_edit.html', form=form)


@admin.route('/couponlimit/<int:coupontype_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_couponlimit(coupontype_id):
    cl = CouponLimit.query.filter_by(coupontyp_ide=coupontype_id, default=True).first()
    form = EditCouponLimitForm(couponlimit=cl)
    if form.validate_on_submit():
        cl.default = False
        cl2 = CouponLimit()
        cl2.type = type
        cl2.limit = form.limit.data
        cl2.default = True
        db.session.add(cl)
        db.session.add(cl2)
        db.session.commit()
        return render_template('admin/edit_couponlimit', coupontype_id = coupontype_id)

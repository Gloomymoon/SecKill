from datetime import datetime
import time
from flask import current_app, render_template, redirect, url_for, flash, request, make_response
import httplib, urllib
from flask_login import login_required, current_user
from flask_flatpages import FlatPages
from . import main
from .. import pages, db
from ..models import Permission, Role, User, Coupon, SecKill, Datemark
from ..decorators import admin_required, permission_required
from .forms import ReserveSecKillForm


@main.route('/')
@login_required
def index():
    datemark = datetime.now().strftime('%Y-%m-%d')
    kill_time = datetime.now()

    killhour = current_app.config['SECKILL_KILLHOUR']
    coupons = Coupon.query.filter(Coupon.limit > 0).all()
    seckill = current_user.reservation()
    deadline = datetime(kill_time.year, kill_time.month, kill_time.day, killhour, 0, 0)
    if deadline < datetime.now():
        timer = -1
    else:
        timer = (deadline - datetime.now()).seconds
    return render_template('index.html', coupons=coupons, seckill=seckill, killhour=killhour, timer=timer)


@main.route('/reserve', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.KILL)
def reserve():
    form = ReserveSecKillForm()
    seckill = current_user.reservation()
    if form.validate_on_submit():
        if seckill is None:
            seckill = SecKill(user=current_user._get_current_object(),
                              datemark=Datemark.today())
        seckill.coupon = Coupon.query.get(form.coupon.data)
        seckill.reserve_date = datetime.now()
        seckill.reserved = True
        db.session.add(seckill)
        db.session.commit()
        return redirect(url_for('.index'))
    form.datemark.data = Datemark.today()
    if seckill is not None:
        form.coupon.data = seckill.coupon_id
    return render_template('reserve.html', seckill=seckill, form=form)


@main.route('/unreserve')
@login_required
@permission_required(Permission.KILL)
def unreserve():
    seckill = current_user.reservation()
    if seckill is not None:
        seckill.reserved = False
        db.session.add(seckill)
        db.session.commit()
        # flash('Your ' + seckill.coupon.name + ' coupon reservation is canceled.')
    else:
        flash('You have no target coupon yet.')
    return redirect(url_for('.index'))


@main.route('/seckill')
@login_required
@permission_required(Permission.KILL)
def seckill():
    seckill = current_user.reservation()
    killhour = current_app.config['SECKILL_KILLHOUR']
    kill_time = datetime.now()
    deadline = datetime(kill_time.year, kill_time.month, kill_time.day, killhour, 0, 0)
    if kill_time < deadline:
        flash('Try not. Do or do not, there is no try.')
        return redirect(url_for('.index'))
    elif seckill is not None and seckill.reserved:
        seckill.kill_time = datetime.now()
        db.session.add(seckill)
        db.session.commit()
        time.sleep(3)
        seckill.reckon()
        return redirect(url_for('.index'))
    else:
        flash('You should choose a target coupon first.')
        return redirect(url_for('.reserve'))


@main.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    show_type = request.cookies.get('show_type', '')
    if show_type == 'all':
        query = SecKill.query.filter_by(win=True)
    elif show_type == 'today':
        query = SecKill.query.filter_by(reserved=True).filter_by(datemark=Datemark.today())
    else:
    	show_type = 'my'
        query = current_user.seckills
    pagination = query.order_by(SecKill.kill_time.desc()).paginate(
        page, per_page=20, error_out=False)
    seckills = pagination.items
    return render_template('history.html', seckills=seckills, show_type=show_type, pagination=pagination)


@main.route('/history/today')
@login_required
def history_today():
    resp = make_response(redirect(url_for('.history')))
    resp.set_cookie('show_type', 'today', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/history/all')
@login_required
def history_all():
    resp = make_response(redirect(url_for('.history')))
    resp.set_cookie('show_type', 'all', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/history/my')
@login_required
def history_my():
    resp = make_response(redirect(url_for('.history')))
    resp.set_cookie('show_type', 'my', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/comment/<int:id>')
@login_required
def comment(id):
    pass

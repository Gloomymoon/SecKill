from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from markdown import markdown
import bleach


class Datemark():
    @staticmethod
    def today():
        return datetime.now().strftime('%Y-%m-%d')


class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    limit = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime(), default=datetime.now)
    seckills = db.relationship('SecKill', backref='coupon', lazy='dynamic')

    @staticmethod
    def insert_coupons():
        types = {
            'Yellow': 0,
            'Red': 2
        }
        for t in types:
            c = Coupon.query.filter_by(name=t).first()
            if c is None:
                c = Coupon()
            c.name = t
            c.limit = types[t]
            db.session.add(c)
        db.session.commit()


class Permission:
    VIEW = 0x01
    KILL = 0x02
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.VIEW | Permission.KILL, True),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64), index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    member_since = db.Column(db.DateTime(), default=datetime.now)
    seckills = db.relationship('SecKill', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.name == 'admin':
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        
    def verify_user(self):
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def reservation(self):
        sk = self.seckills.filter_by(datemark=Datemark.today()).first()
        return sk

    def shot(self, datemark):
        sk = self.reservation(datemark)
        if sk is None:
            return False
        else:
            sk.kill_time = datetime.now
            db.session.add(sk)
            db.session.commit()
            return True


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SecKill(db.Model):
    __tablename__ = 'seckills'
    id = db.Column(db.Integer, primary_key=True)
    datemark = db.Column(db.String(10), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), index=True)
    reserve_date = db.Column(db.DateTime(), default=datetime.now)
    reserved = db.Column(db.Boolean, default=True, index=True)
    kill_time = db.Column(db.DateTime(), default=datetime.min, index=True)
    win = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='seckill', lazy='dynamic')

    def reckon(self):
        sql = 'select * from seckill_result'
        result = db.session.execute(sql).fetchall()
        flag = False
        for r in result:
            if r[0] == self.id:
                flag = True
        if flag:
            sk = SecKill.query.filter_by(id=self.id).first()
            sk.win = True
            db.session.add(sk)
            db.session.commit()
            return sk.win
        return False



class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seckill_id = db.Column(db.Integer, db.ForeignKey('seckills.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Comment.body, 'set', Comment.on_changed_body)



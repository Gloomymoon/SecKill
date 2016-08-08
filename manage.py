#!/usr/bin/env python
# -*- coding: UTF-8 -*
import os
from app import create_app, db
from app.models import User, Role, Permission, Coupon, SecKill, Datemark
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('ATH_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()


def init_app_data():
    db.drop_all()
    db.create_all()
    Coupon.insert_coupons()
    Role.insert_roles()
    u = User(ip="127.0.0.1", name="Administrator",
             role=Role.query.filter_by(permissions=0xff).first())
    db.session.add(u)
    db.session.commit()


def calculated():
	sk = SecKill.query.filter_by(win=False).filter_by(datemark=Datemark.today()).order_by(SecKill.kill_time).all()
	sk1 = sk[0]
	db.session.add(sk1)
	db.session.commit()
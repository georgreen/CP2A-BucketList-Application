#!/usr/bin/env python
"""Module containing app's entry point, testing and migration commands."""

import os
import unittest

from app.base import database, new_app
from app.models import bucketlist, profile, user
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, prompt_bool

app = new_app(enviroment=os.environ.get('APP_SETTINGS') or "default")
manager = Manager(app)
migrate = Migrate(app, database)


@manager.command
def drop_database():
    """Drop database tables."""
    if prompt_bool("Are you sure you want to lose all your data"):
        try:
            database.drop_all()
            print("Dropped all tables susscefully.")
        except Exception:
            print("Failed, make sure your database server is running!")


@manager.command
def create_database():
    """Create database tables from sqlalchemy models."""
    try:
        database.create_all()
        print("Created tables susscefully.")
    except Exception:
        print("Failed, make sure your database server is running!")


@manager.command
def test():
    """Run tests."""
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def shell_context():
    """Make a shell context available with defined Classess."""
    return dict(
        app=new_app,
        User=user.User,
        UserSchema=user.UserSchema,
        Item=bucketlist.Item,
        Bucket=bucketlist.Bucket,
        Profile=profile.Profile,
        database=database)


manager.add_command("shell", Shell(make_context=shell_context))
manager.add_command("database", MigrateCommand)

if __name__ == '__main__':
    manager.run()

#!/usr/bin/env python
import os
import unittest

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, prompt_bool

from app.api import endpoint
from app.authenticate import auth
from app.base import database, new_app
from app.models import bucketlist, user

app = new_app(enviroment=os.environ.get('APP_SETTINGS') or "default")
manager = Manager(app)
migrate = Migrate(app, database)


@manager.command
def drop_database():
    """Drop database tables."""
    if prompt_bool("Are you sure you want to lose all your data"):
        database.drop_all()


@manager.command
def create_database():
    """Create database tables from sqlalchemy models."""
    database.create_all()
    print("Created tables susscefully.")


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
        ItemSchema=bucketlist.BucketSchema,
        Bucket=bucketlist.Bucket,
        BucketSchema=bucketlist.BucketSchema,
        Profile=user.Profile,
        ProfileSchema=user.ProfileSchema,
        database=database)


manager.add_command("shell", Shell(make_context=shell_context))
manager.add_command("database", MigrateCommand)

if __name__ == '__main__':
    manager.run()

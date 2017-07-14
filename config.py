"""Module contains configuration classes for different enviroments."""
import os
from datetime import timedelta


class Config():
    """Model base config object that can inherited by other configs."""

    SECRET_KEY = os.environ.get('SECRET')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CSRF_ENABLED = True
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_JSONEDITOR = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=120)


class DevelopmentConfig(Config):
    """Model Development enviroment config object."""

    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE') or \
        'sqlite:///:memory:'


class TestingConfig(Config):
    """Model Testing enviroment config object."""

    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=1)
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE') or \
        'sqlite:///:memory:'


class ProductionConfig(Config):
    """Model Production enviroment config object."""

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class StagingConfig(Config):
    """Model Staging enviroment config object."""

    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config = {
    'default': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'stage': StagingConfig
}

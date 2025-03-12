import time
from datetime import datetime
from typing import Callable

from authlib.integrations.sqla_oauth2 import (
    OAuth2TokenMixin,
)
from cuid2 import cuid_wrapper
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

cuid_generator: Callable[[], str] = cuid_wrapper()


class User(db.Model, SerializerMixin):
    __tablename__ = 'User'

    id = db.Column(db.String, primary_key=True, default=cuid_generator)
    username = db.Column(db.String, nullable=False)
    health_data_list = relationship('HealthData', back_populates='author')

    def get_user_id(self):
        return self.id


class HealthData(db.Model, SerializerMixin):
    __tablename__ = 'HealthData'

    serialize_rules = ('-author',)

    id = Column(String, primary_key=True, default=cuid_generator)
    type = Column(String, nullable=False)  # PERSONAL_INFO
    data = Column(JSON, nullable=False)
    author_id = Column(String, ForeignKey('User.id'), nullable=True, name='authorId')
    meta_data = Column(JSON, nullable=True, name='metadata')
    file_path = Column(String, nullable=True, name='filePath')
    file_type = Column(String, nullable=True, name='fileType')  # image/jpeg, image/png, application/pdf
    status = Column(String, default='COMPLETED')  # PARSING, COMPLETED
    created_at = Column(DateTime, default=datetime.utcnow, name='createdAt')
    updated_at = Column(DateTime, onupdate=datetime.utcnow, name='updatedAt')

    author = relationship('User', back_populates='health_data_list')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'OAuth2Token'

    id = db.Column(db.String, primary_key=True, default=cuid_generator)
    user_id = db.Column(
        db.String, db.ForeignKey('User.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()

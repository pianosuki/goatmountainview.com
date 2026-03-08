"""
User Model

Represents admin users who can access the admin panel.
"""

from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """Admin user model for authentication."""
    
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

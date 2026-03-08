"""
Inquiry Model

Represents contact form submissions/inquiries.
"""

from datetime import datetime
from app import db


class Inquiry(db.Model):
    """Inquiry model for contact form submissions."""
    
    __tablename__ = "inquiries"
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Inquiry {self.email}>'

"""
Goat Model

Represents goats in the system (used by Doe, Foundation, Adoption).
"""

from app import db


class Goat(db.Model):
    """Goat model - base entity for all goat-related tables."""
    
    __tablename__ = "goats"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    images = db.relationship("Image", backref="goat", lazy="dynamic")
    
    def __repr__(self):
        return f'<Goat {self.name}>'

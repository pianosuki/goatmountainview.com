"""
Soap Model

Represents soap products for sale.
"""

from app import db


class Soap(db.Model):
    """Soap product model."""
    
    __tablename__ = "soaps"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    ingredients = db.Column(db.Text(), nullable=False)
    weight = db.Column(db.Float(), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=1)
    
    # Relationships
    image = db.relationship("Image", backref="soap", foreign_keys="Soap.image_id")
    
    def __repr__(self):
        return f'<Soap {self.name}>'

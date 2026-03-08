"""
Doe Model

Represents female goats (does) in the herd.
"""

from app import db


class Doe(db.Model):
    """Doe model for female goats."""
    
    __tablename__ = "does"
    
    id = db.Column(db.Integer, primary_key=True)
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.String(200))
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=2)
    
    # Relationships
    goat = db.relationship("Goat", backref="doe", foreign_keys="Doe.goat_id")
    image = db.relationship("Image", backref="doe", foreign_keys="Doe.image_id")
    
    def __repr__(self):
        return f'<Doe {self.goat.name if self.goat else "Unknown"}>'

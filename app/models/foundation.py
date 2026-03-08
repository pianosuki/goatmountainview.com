"""
Foundation Model

Represents foundation stock goats in the breeding program.
"""

from app import db


class Foundation(db.Model):
    """Foundation goat model for breeding program stock."""
    
    __tablename__ = "foundation"
    
    id = db.Column(db.Integer, primary_key=True)
    goat_id = db.Column(db.Integer, db.ForeignKey("goats.id"))
    description = db.Column(db.Text(), nullable=False)
    link = db.Column(db.String(200))
    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), default=2)
    
    # Relationships
    goat = db.relationship("Goat", backref="foundation", foreign_keys="Foundation.goat_id")
    image = db.relationship("Image", backref="foundation", foreign_keys="Foundation.image_id")
    
    def __repr__(self):
        return f'<Foundation {self.goat.name if self.goat else "Unknown"}>'

from database import db
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Text, SmallInteger, func, CheckConstraint
from sqlalchemy.orm import relationship

class review(db.Model):
    __tablename__ = "review"
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id", ondelete="CASCADE"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())  # Auto-update timestamp

    user = relationship("user", back_populates="reviews")
    dish = relationship("dish", back_populates="reviews")
    restaurant = relationship("restaurant", back_populates="reviews")

    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="valid_rating"),)
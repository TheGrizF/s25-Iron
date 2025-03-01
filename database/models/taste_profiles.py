from sqlalchemy import Column, Integer, Text, SmallInteger, TIMESTAMP, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from database import db

class tasteProfile(db.Model):
    __tablename__ = "taste_profile"
    taste_profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), unique=True, nullable=False)
    restrictions = Column(Text, nullable=True)
    sweet = Column(SmallInteger, nullable=True)
    savory = Column(SmallInteger, nullable=True)
    sour = Column(SmallInteger, nullable=True)
    bitter = Column(SmallInteger, nullable=True)
    spicy = Column(SmallInteger, nullable=True)
    umami = Column(SmallInteger, nullable=True)

    user = relationship("user", back_populates="taste_profile")

    __table_args__ = (
        CheckConstraint("sweet BETWEEN 1 AND 5", name="valid_sweet"),
        CheckConstraint("savory BETWEEN 1 AND 5", name="valid_savory"),
        CheckConstraint("sour BETWEEN 1 AND 5", name="valid_sour"),
        CheckConstraint("bitter BETWEEN 1 AND 5", name="valid_bitter"),
        CheckConstraint("spicy BETWEEN 1 AND 5", name="valid_spicy"),
        CheckConstraint("umami BETWEEN 1 AND 5", name="valid_umami"),
    )

class dishTasteProfile(db.Model):
    __tablename__ = "dish_taste_profile"
    dish_taste_profile_id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey("dish.dish_id"), unique=True, nullable=False)
    cuisine = Column(Text, nullable=True)
    restrictions = Column(Text, nullable=True)
    sweet = Column(SmallInteger, nullable=True)
    savory = Column(SmallInteger, nullable=True)
    sour = Column(SmallInteger, nullable=True)
    bitter = Column(SmallInteger, nullable=True)
    spicy = Column(SmallInteger, nullable=True)
    umami = Column(SmallInteger, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())  # Track creation time

    dish = relationship("dish", back_populates="taste_profiles")

    __table_args__ = (
        CheckConstraint("sweet BETWEEN 1 AND 5", name="valid_sweet"),
        CheckConstraint("savory BETWEEN 1 AND 5", name="valid_savory"),
        CheckConstraint("sour BETWEEN 1 AND 5", name="valid_sour"),
        CheckConstraint("bitter BETWEEN 1 AND 5", name="valid_bitter"),
        CheckConstraint("spicy BETWEEN 1 AND 5", name="valid_spicy"),
        CheckConstraint("umami BETWEEN 1 AND 5", name="valid_umami"),
    )

from database import db
from sqlalchemy import CheckConstraint, Column, Integer, Text, SmallInteger, ForeignKey, DECIMAL, TIMESTAMP, TIME, func, select, event
from sqlalchemy.orm import relationship

class restaurant(db.Model):
    __tablename__ = "restaurant"
    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_name = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    rating_average = Column(SmallInteger, nullable=True)
    phone_number = Column(Text, nullable=True) # could validate with a regular expression but sqlite does not support so validate before entry
    clean_average = Column(DECIMAL(5, 1), nullable=True)
    busy_average = Column(DECIMAL(5, 1), nullable=True)
    image_path = Column(Text, nullable=True, default="images/restaurant/default.jpg")
    description = Column(Text, nullable=True)
    cuisine = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    operating_hours = relationship("operatingHours", back_populates="restaurant", cascade="all, delete-orphan")
    reviews = relationship("review", back_populates="restaurant", cascade="all, delete-orphan")
    live_updates = relationship("liveUpdate", back_populates="restaurant", cascade="all, delete-orphan")
    menu = relationship("menu", back_populates="restaurant", cascade="all, delete-orphan")
    saved_restaurants = relationship("savedRestaurants", back_populates="restaurant", cascade="all, delete-orphan")

class operatingHours(db.Model):
    __tablename__ = "operating_hours"
    operating_hour_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"))
    days_of_week = Column(Text, nullable=False)
    open_time = Column(TIME, nullable=False)
    close_time = Column(TIME, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    restaurant = relationship("restaurant", back_populates="operating_hours")

class liveUpdate(db.Model):
    __tablename__ = "live_update"
    live_update_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    update_content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    restaurant = relationship("restaurant", back_populates="live_updates")
    user = relationship("user", back_populates="live_updates")


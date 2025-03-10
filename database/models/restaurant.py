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
    update_type = Column(Text, nullable=False)
    update_value = Column(SmallInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    restaurant = relationship("restaurant", back_populates="live_updates")

    __table_args__ = (
        CheckConstraint("update_type IN ('cleanliness', 'busy_level')", name='check_update_type'),
        CheckConstraint('update_value >= 1 AND update_value <= 5', name='check_update_value_range'),
    )

# function to update averages
def update_averages(mapper, connection, target):
    if target.update_type == 'cleanliness':
        avg_query = select([func.avg(liveUpdate.update_value)]).where(
            liveUpdate.restaurant_id == target.restaurant_id,
            liveUpdate.update_type == 'cleanliness'
        )
        avg_cleanliness = connection.execute(avg_query).scalar()
        connection.execute(
            restaurant.__table__.update().where(
                restaurant.restaurant_id == target.restaurant_id
            ).values(clean_average=avg_cleanliness)
        )
    elif target.update_type == 'busy_level':
        avg_query = select([func.avg(liveUpdate.update_value)]).where(
            liveUpdate.restaurant_id == target.restaurant_id,
            liveUpdate.update_type == 'busy_level'
        )
        avg_busy_level = connection.execute(avg_query).scalar()
        connection.execute(
            restaurant.__table__.update().where(
                restaurant.restaurant_id == target.restaurant_id
            ).values(busy_average=avg_busy_level)
        )

# attach the event listener to the liveUpdate model
event.listen(liveUpdate, 'after_insert', update_averages)
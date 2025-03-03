from sqlalchemy import Column, Integer, SmallInteger, Text, TIMESTAMP, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from database import db

class user(db.Model):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    user_role = Column(Text, nullable=False, default="user")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    cuisines = relationship("cuisineUserJunction", back_populates="user")
    taste_profile = relationship("tasteProfile", uselist=False, back_populates="user")
    reviews = relationship("review", back_populates="user")
    saved_dishes = relationship("savedDishes", back_populates="user")
    saved_restaurants = relationship("savedRestaurants", back_populates="user")

    friends = relationship("friends", foreign_keys="[friends.user_id]", back_populates="user")
    buddies = relationship("friends", foreign_keys="[friends.buddy_id]", back_populates="buddy")
    taste_comparisons = relationship("tasteComparisons", foreign_keys="[tasteComparisons.compare_from]", back_populates="user_from")
    compared_to = relationship("tasteComparisons", foreign_keys="[tasteComparisons.compare_to]", back_populates="user_to")

    __table_args__ = (
        CheckConstraint("user_role IN ('admin', 'user', 'moderator')", name="valid_user_role"),
    )

class tasteComparisons(db.Model):
    __tablename__ = "taste_comparisons"
    matches_id = Column(Integer, primary_key=True, autoincrement=True)
    compare_from = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    compare_to = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    comparison_num = Column(Integer, nullable=False)

    user_from = relationship("user", foreign_keys=[compare_from], back_populates="taste_comparisons")
    user_to = relationship("user", foreign_keys=[compare_to], back_populates="compared_to")

    __table_args__ = (
        CheckConstraint("compare_from != compare_to", name="prevent_self_comparison"),
        CheckConstraint("comparison_num BETWEEN 0 AND 50", name="valid_comparison_num"),
    )

class cuisine(db.Model):
    __tablename__ = "cuisine"
    cuisine_id = Column(Integer, primary_key=True, autoincrement=True)
    cuisine_name = Column(Text, nullable=False, unique=True)

    users = relationship("cuisineUserJunction", back_populates="cuisine")

class cuisineUserJunction(db.Model):
    __tablename__ = "cuisine_user_junction"
    cuisine_user_junction_id = Column(Integer, primary_key=True, autoincrement=True)
    cuisine_id = Column(Integer, ForeignKey("cuisine.cuisine_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    preference_level = Column(SmallInteger, nullable=True)

    cuisine = relationship("cuisine", back_populates="users")
    user = relationship("user", back_populates="cuisines")

    __table_args__ = (CheckConstraint("preference_level BETWEEN 1 AND 5", name="valid_preference_level"),)

class friends(db.Model):
    __tablename__ = "friends"
    friends_list_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    buddy_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    date_added = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())  # Auto timestamp
    status = Column(Text, nullable=False)

    user = relationship("user", foreign_keys=[user_id], back_populates="friends")
    buddy = relationship("user", foreign_keys=[buddy_id], back_populates="buddies")

    __table_args__ = (
        CheckConstraint("user_id != buddy_id", name="prevent_self_friendship"),
        CheckConstraint("status IN ('pending', 'accepted', 'blocked')", name="valid_friend_status"),
    )

class savedDishes(db.Model):
    __tablename__ = "saved_dishes"
    saved_dishes_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id"), nullable=False)
    date_saved = Column(TIMESTAMP, nullable=False, server_default=func.now())

    user = relationship("user", back_populates="saved_dishes")
    dish = relationship("dish", back_populates="saved_dishes")

class savedRestaurants(db.Model):
    __tablename__ = "saved_restaurants"
    saved_restaurants_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id"), nullable=False)
    date_saved = Column(TIMESTAMP, nullable=False, server_default=func.now())

    user = relationship("user", back_populates="saved_restaurants")
    restaurant = relationship("restaurant", back_populates="saved_restaurants")

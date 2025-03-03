from database import db
from sqlalchemy import CheckConstraint, Column, Enum, Integer, Text, SmallInteger, ForeignKey, Boolean, DECIMAL, TIMESTAMP, TIME, func
from sqlalchemy.orm import relationship

#
#
# This is the current models bundled into one in case I (Nate) break something
#
#

class dish(db.Model):
    __tablename__ = "dish"
    dish_id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    dish_name = Column(Text, nullable=False)
    featured = Column(Boolean, nullable=True, default=True)
    available = Column(Boolean, nullable=True, default=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    taste_profiles = relationship("dishTasteProfile", back_populates="dish")
    menu_dishes = relationship("menuDishJunction", back_populates="dish")
    reviews = relationship("review", back_populates="dish")
    saved_dishes = relationship("savedDishes", back_populates="dish")

class menu(db.Model):
    __tablename__ = "menu"
    menu_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id"), nullable=False)
    menu_name = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    menu_dishes = relationship("menuDishJunction", back_populates="menu")
    restaurant = relationship("restaurant", back_populates="menu")

class menuDishJunction(db.Model):
    __tablename__ = "menu_dish_junction"
    menu_dish_id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menu.menu_id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id"), nullable=False)

    menu = relationship("menu", back_populates="menu_dishes")
    dish = relationship("dish", back_populates="menu_dishes")

class restaurant(db.Model):
    __tablename__ = "restaurant"
    restaurant_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_name = Column(Text, nullable=False)
    restrictions = Column(Text, nullable=True)
    location = Column(Text, nullable=False)
    rating_average = Column(SmallInteger, nullable=True)
    phone_number = Column(Text, nullable=True) # could validate with a regular expression but sqlite does not support so validate before entry
    clean_average = Column(DECIMAL(5, 1), nullable=True)
    busy_average = Column(DECIMAL(5, 1), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    operating_hours = relationship("operatingHours", back_populates="restaurant")
    reviews = relationship("review", back_populates="restaurant")
    live_updates = relationship("liveUpdate", back_populates="restaurant")
    menu = relationship("menu", back_populates="restaurant")
    saved_restaurants = relationship("savedRestaurants", back_populates="restaurant")

class operatingHours(db.Model):
    __tablename__ = "operating_hours"
    operating_hour_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id"))
    days_of_week = Column(Text, nullable=False)
    open_time = Column(TIME, nullable=False)
    close_time = Column(TIME, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    restaurant = relationship("restaurant", back_populates="operating_hours")

class liveUpdate(db.Model):
    __tablename__ = "live_update"
    live_update_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id"))
    update_type = Column(Text, nullable=False)
    update_value = Column(SmallInteger, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    restaurant = relationship("restaurant", back_populates="live_updates")

class review(db.Model):
    __tablename__ = "review"
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())  # Auto-update timestamp

    user = relationship("user", back_populates="reviews")
    dish = relationship("dish", back_populates="reviews")
    restaurant = relationship("restaurant", back_populates="reviews")

    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="valid_rating"),)

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

class user(db.Model):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    user_role = Column(Text, nullable=False)
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

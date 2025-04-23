from sqlalchemy import Boolean, Column, Integer, SmallInteger, Text, TIMESTAMP, ForeignKey, func, CheckConstraint
from sqlalchemy.orm import relationship
from database import db, bcrypt

class user(db.Model):
    __tablename__ = "user"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    user_role = Column(Text, nullable=False, default="user")
    icon_path = Column(Text, nullable=True, default="images/profile_icons/default1.png")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    cuisines = relationship("cuisineUserJunction", back_populates="user", cascade="all, delete-orphan")
    taste_profile = relationship("tasteProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("review", back_populates="user", cascade="all, delete-orphan")
    saved_dishes = relationship("savedDishes", back_populates="user", cascade="all, delete-orphan")
    saved_restaurants = relationship("savedRestaurants", back_populates="user", cascade="all, delete-orphan")
    user_allergens = relationship("user_allergen", back_populates="user", cascade="all, delete-orphan")
    user_restrictions = relationship("user_restriction", back_populates="user", cascade="all, delete-orphan")
    live_updates = relationship("liveUpdate", back_populates="user", cascade="all, delete-orphan")

    friends = relationship("friends", foreign_keys="[friends.user_id]", back_populates="user", cascade="all, delete-orphan")
    buddies = relationship("friends", foreign_keys="[friends.buddy_id]", back_populates="buddy", cascade="all, delete-orphan")
    taste_comparisons = relationship("tasteComparisons", foreign_keys="[tasteComparisons.compare_from]", back_populates="user_from", cascade="all, delete-orphan")
    compared_to = relationship("tasteComparisons", foreign_keys="[tasteComparisons.compare_to]", back_populates="user_to", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("user_role IN ('admin', 'user', 'moderator')", name="valid_user_role"),
    )

    def __init__(self, first_name, last_name, email, password="tastebuddies", user_role="user", icon_path="images/profile_icons/default1.png"):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        self.user_role = user_role
        self.icon_path = icon_path

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class tasteComparisons(db.Model):
    __tablename__ = "taste_comparisons"
    matches_id = Column(Integer, primary_key=True, autoincrement=True)
    compare_from = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    compare_to = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
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

    users = relationship("cuisineUserJunction", back_populates="cuisine", cascade="all, delete-orphan")

class cuisineUserJunction(db.Model):
    __tablename__ = "cuisine_user_junction"
    cuisine_user_junction_id = Column(Integer, primary_key=True, autoincrement=True)
    cuisine_id = Column(Integer, ForeignKey("cuisine.cuisine_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    preference_level = Column(SmallInteger, nullable=True)

    cuisine = relationship("cuisine", back_populates="users")
    user = relationship("user", back_populates="cuisines")

    __table_args__ = (CheckConstraint("preference_level BETWEEN 1 AND 5", name="valid_preference_level"),)

class friends(db.Model):
    __tablename__ = "friends"
    friends_list_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    buddy_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    date_added = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())  # auto timestamp
    seen = Column(Boolean, default=False)  # 0 = not seen, 1 = seen

    user = relationship("user", foreign_keys=[user_id], back_populates="friends")
    buddy = relationship("user", foreign_keys=[buddy_id], back_populates="buddies")

    __table_args__ = (
        CheckConstraint("user_id != buddy_id", name="prevent_self_friendship"),
    )

class savedDishes(db.Model):
    __tablename__ = "saved_dishes"
    saved_dishes_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id", ondelete="CASCADE"), nullable=False)
    date_saved = Column(TIMESTAMP, nullable=False, server_default=func.now())

    user = relationship("user", back_populates="saved_dishes")
    dish = relationship("dish", back_populates="saved_dishes")

class savedRestaurants(db.Model):
    __tablename__ = "saved_restaurants"
    saved_restaurants_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"), nullable=False)
    date_saved = Column(TIMESTAMP, nullable=False, server_default=func.now())

    user = relationship("user", back_populates="saved_restaurants")
    restaurant = relationship("restaurant", back_populates="saved_restaurants")

class user_allergen(db.Model):
    __tablename__ = "user_allergen"
    allergen_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    allergen = Column(Text, nullable=False)

    user = relationship("user", back_populates="user_allergens")

class user_restriction(db.Model):
    __tablename__ = "user_restriction"
    restriction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    restriction = Column(Text, nullable=False)

    user = relationship("user", back_populates="user_restrictions")
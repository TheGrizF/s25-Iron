from database import db
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, TIMESTAMP, DECIMAL, func
from sqlalchemy.sql import expression
from sqlalchemy.orm import relationship

class dish(db.Model):
    __tablename__ = "dish"
    dish_id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    dish_name = Column(Text, nullable=False)
    featured = Column(Boolean, nullable=True, server_default=expression.false())
    available = Column(Boolean, nullable=True, server_default=expression.false())
    image_path = Column(Text, nullable=True, default="app/static/images/dishes/default.jpg")
    price = Column(DECIMAL(5,2), nullable=True, default=123.45)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    taste_profiles = relationship("dishTasteProfile", back_populates="dish", cascade="all, delete-orphan")
    menu_dishes = relationship("menuDishJunction", back_populates="dish", cascade="all, delete-orphan")
    reviews = relationship("review", back_populates="dish", cascade="all, delete-orphan")
    saved_dishes = relationship("savedDishes", back_populates="dish", cascade="all, delete-orphan")
    dish_allergens = relationship("dish_allergen", back_populates="dish", cascade="all, delete-orphan")
    dish_restrictions = relationship("dish_restriction", back_populates="dish", cascade="all, delete-orphan")

class menu(db.Model):
    __tablename__ = "menu"
    menu_id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.restaurant_id", ondelete="CASCADE"), nullable=False)
    menu_name = Column(Text, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    menu_dishes = relationship("menuDishJunction", back_populates="menu", cascade="all, delete-orphan")
    restaurant = relationship("restaurant", back_populates="menu")

class menuDishJunction(db.Model):
    __tablename__ = "menu_dish_junction"
    menu_dish_id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey("menu.menu_id", ondelete="CASCADE"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dish.dish_id", ondelete="CASCADE"), nullable=False)

    menu = relationship("menu", back_populates="menu_dishes")
    dish = relationship("dish", back_populates="menu_dishes")

class dish_allergen(db.Model):
    __tablename__ = "dish_allergen"
    allergen_id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey("dish.dish_id", ondelete="CASCADE"), nullable=False)
    allergen = Column(Text, nullable=False)

    dish = relationship("dish", back_populates="dish_allergens")

class dish_restriction(db.Model):
    __tablename__ = "dish_restriction"
    restriction_id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey("dish.dish_id", ondelete="CASCADE"), nullable=False)
    restriction = Column(Text, nullable=False)

    dish = relationship("dish", back_populates="dish_restrictions")
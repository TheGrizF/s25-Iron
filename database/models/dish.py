from database import db
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

class dish(db.Model):
    __tablename__ = "dish"
    dish_id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text, nullable=True)
    dish_name = Column(Text, nullable=False)
    featured = Column(Boolean, nullable=True, default=True)
    available = Column(Boolean, nullable=True, default=False)
    image_path = Column(Text, nullable=True, default="app/static/images/dishes/default.jpg")
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

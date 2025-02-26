from database import db
from sqlalchemy.dialects.postgresql import JSON

class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tasteBuddiesID = db.Column(db.Integer, db.ForeignKey('taste_buddies.userID'))
    savedRestaurantsID = db.Column(db.Integer, db.ForeignKey('saved_restaurants.userID'))
    tasteProfileID = db.Column(db.Integer, db.ForeignKey('taste_profile.tasteProfileID'))
    reviewID = db.Column(db.Integer, db.ForeignKey('review.reviewID'))
    savedDishesID = db.Column(db.Integer, db.ForeignKey('saved_dishes.userID'))
    userRole = db.Column(db.String(20))

    taste_profile = db.relationship('TasteProfile', back_populates='user', uselist=False, foreign_keys='TasteProfile.userID')

    def __repr__(self):
        return f'<User {self.firstName} {self.lastName} (email: {self.email})>'

class TasteProfile(db.Model):
    tasteProfileID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), unique=True, nullable=False)
    dietaryRestrictions = db.Column(db.Text)
    sweet = db.Column(db.SmallInteger)
    spicy = db.Column(db.SmallInteger)
    sour = db.Column(db.SmallInteger)
    bitter = db.Column(db.SmallInteger)
    umami = db.Column(db.SmallInteger)
    savory = db.Column(db.SmallInteger)
    cuisineID = db.Column(db.Integer, db.ForeignKey('cuisine.cuisineID'))

    user = db.relationship('User', back_populates='taste_profile', foreign_keys=[userID])

    def __repr__(self):    
        return (f"<TasteProfile ID={self.tasteProfileID}, Sweet={self.sweet}, "
                f"Spicy={self.spicy}, Sour={self.sour}, Bitter={self.bitter}, "
                f"Umami={self.umami}, Savory={self.savory}>")
    
class Cuisine(db.Model):
    cuisineID = db.Column(db.Integer, primary_key=True)
    cuisineName = db.Column(db.String(50), nullable=False)
    preferenceLevel = db.Column(db.SmallInteger)
    
class Review(db.Model):
    reviewID = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.SmallInteger)
    content = db.Column(db.Text)
    imagePath = db.Column(db.Text)
    dishID = db.Column(db.Integer, db.ForeignKey('dish.dishID'))
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.restaurantID'))

class SavedDishes(db.Model):
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    dishID = db.Column(db.Integer, db.ForeignKey('dish.dishID'), primary_key=True)
    dateSaved = db.Column(db.DateTime)

class SavedRestaurants(db.Model):
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    restaurantID = db.Column(db.Integer, db.ForeignKey('restaurant.restaurantID'), primary_key=True)
    dateSaved = db.Column(db.DateTime)

class TasteBuddies(db.Model):
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    buddyID = db.Column(db.Integer, db.ForeignKey('user.userID'), primary_key=True)
    dateAdded = db.Column(db.DateTime)
    
class Restaurant(db.Model):
    restaurantID = db.Column(db.Integer, primary_key=True)
    restaurantName = db.Column(db.String(100), nullable=False)
    operatingHoursID = db.Column(db.Integer, db.ForeignKey('operating_hours.operatingHoursID'))
    reviewID = db.Column(db.Integer, db.ForeignKey('review.reviewID'))
    dietaryRestrictions = db.Column(db.Text)
    location = db.Column(db.String(50))
    ratingAverage = db.Column(db.SmallInteger)
    phoneNumber = db.Column(db.String(14))
    menuID = db.Column(db.Integer, db.ForeignKey('menu.menuID'))
    cleanAverage = db.Column(db.SmallInteger)
    busyAverage = db.Column(db.SmallInteger)
    
    def __repr__(self):
        return f'<Restaurant {self.restaurantName}>'

class Menu(db.Model):
    menuID = db.Column(db.Integer, primary_key=True)
    menuName = db.Column(db.String(100))
    lastUpdated = db.Column(db.DateTime)

class Dish(db.Model):
    dishID = db.Column(db.Integer, primary_key=True)
    dishTasteProfileID = db.Column(db.Integer, db.ForeignKey('taste_profile.tasteProfileID'))
    dishName = db.Column(db.String(50), nullable=False)
    featured = db.Column(db.Boolean)
    available = db.Column(db.Boolean)

class OperatingHours(db.Model):
    operatingHoursID = db.Column(db.Integer, primary_key=True)
    daysOfWeek = db.Column(db.String(62))
    openTime = db.Column(db.Time)
    closeTime = db.Column(db.Time)


class TasteComparison(db.Model):
    matchesID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    compareFrom = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    compareTo = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    comparisonNum = db.Column(db.Integer, nullable=False)

    matches = db.relationship('User', foreign_keys=[compareTo], backref='reverse_match')
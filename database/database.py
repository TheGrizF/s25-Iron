import sqlite3
import os

# get the path to the database folder
database = os.path.join(os.path.dirname(__file__), "tastebuddies.db")

# connect to SQLite database (or create it if it doesn't exist) in the database folder
conn = sqlite3.connect(database)
cursor = conn.cursor()

# create tables
cursor.executescript("""
CREATE TABLE cuisine (
  cuisineID INTEGER PRIMARY KEY,
  cuisineName TEXT,
  preferenceLevel SMALLINT
);

CREATE TABLE restaurant (
  restaurantID INTEGER PRIMARY KEY,
  operatingHoursID INTEGER,
  reviewID INTEGER,
  dietaryRestrictions TEXT,
  location VARCHAR(50),
  ratingAverage SMALLINT,
  phoneNumber VARCHAR(14),
  menuID INTEGER,
  cleanAverage SMALLINT,
  busyAverage SMALLINT,
  FOREIGN KEY (menuID) REFERENCES menu(menuID),
  FOREIGN KEY (reviewID) REFERENCES review(reviewID),
  FOREIGN KEY (operatingHoursID) REFERENCES operatingHours(operatingHoursID)
);

CREATE TABLE menu (
  menuID INTEGER PRIMARY KEY,
  dishID INTEGER,
  menuName TEXT,
  lastUpdated TIMESTAMP,
  FOREIGN KEY (dishID) REFERENCES dish(dishID)
);

CREATE TABLE user (
  userID INTEGER PRIMARY KEY,
  firstName VARCHAR(20),
  lastName VARCHAR(20),
  email TEXT,
  tasteBuddiesID INTEGER,
  savedRestaurantsID INTEGER,
  tasteProfileID INTEGER,
  reviewID INTEGER,
  savedDishesID INTEGER,
  userRole VARCHAR(20),
  FOREIGN KEY (tasteBuddiesID) REFERENCES tasteBuddies(userID),
  FOREIGN KEY (savedRestaurantsID) REFERENCES savedRestaurants(userID),
  FOREIGN KEY (tasteProfileID) REFERENCES tasteProfile(tasteProfileID),
  FOREIGN KEY (reviewID) REFERENCES review(reviewID),
  FOREIGN KEY (savedDishesID) REFERENCES savedDishes(userID)
);

CREATE TABLE savedDishes (
  userID INTEGER,
  dishID INTEGER,
  dateSaved TIMESTAMP,
  PRIMARY KEY (userID, dishID),
  FOREIGN KEY (userID) REFERENCES user(userID),
  FOREIGN KEY (dishID) REFERENCES dish(dishID)
);

CREATE TABLE dish (
  dishID INTEGER PRIMARY KEY,
  dishTasteProfileID INTEGER,
  dishName VARCHAR(50),
  featured BOOLEAN,
  available BOOLEAN,
  FOREIGN KEY (dishTasteProfileID) REFERENCES tasteProfile(tasteProfileID)
);

CREATE TABLE tasteProfile (
  tasteProfileID INTEGER PRIMARY KEY,
  dietaryRestrictions TEXT,
  sweet SMALLINT,
  salty SMALLINT,
  sour SMALLINT,
  bitter SMALLINT,
  umami SMALLINT,
  cuisineID INTEGER,
  FOREIGN KEY (cuisineID) REFERENCES cuisine(cuisineID)
);

CREATE TABLE tasteBuddies (
  userID INTEGER,
  buddyID INTEGER,
  dateAdded TIMESTAMP,
  PRIMARY KEY (userID, buddyID),
  FOREIGN KEY (userID) REFERENCES user(userID),
  FOREIGN KEY (buddyID) REFERENCES user(userID)
);

CREATE TABLE operatingHours (
  operatingHoursID INTEGER PRIMARY KEY,
  daysOfWeek VARCHAR(62),
  openTime TIME,
  closeTime TIME
);

CREATE TABLE review (
  reviewID INTEGER PRIMARY KEY,
  rating SMALLINT,
  content TEXT,
  imagePath TEXT,
  dishID INTEGER,
  restaurantID INTEGER,
  FOREIGN KEY (dishID) REFERENCES dish(dishID),
  FOREIGN KEY (restaurantID) REFERENCES restaurant(restaurantID)
);

CREATE TABLE savedRestaurants (
  userID INTEGER,
  restaurantID INTEGER,
  dateSaved TIMESTAMP,
  PRIMARY KEY (userID, restaurantID),
  FOREIGN KEY (userID) REFERENCES user(userID),
  FOREIGN KEY (restaurantID) REFERENCES restaurant(restaurantID)
);
""")

# commit changes and close the connection
conn.commit()
conn.close()

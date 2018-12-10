from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Product, User

engine = create_engine('sqlite:///Amazonwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user1
User1 = User(name="Terry Rossi", email="rossiterry@yahoo.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Create dummy user
User2 = User(name="Terry Rossi", email="terryrossi1@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User2)
session.commit()

#Menu for Food
category1 = Category(user_id=2, name = "Food")

session.add(category1)
session.commit()

product1 = Product(user_id=2, name = "Veggie Burger", description = "Juicy grilled veggie patty with tomato mayo and lettuce", price = "$7.50", category = category1)

session.add(product1)
session.commit()

product2 = Product(user_id=2, name = "Chicken Burger", description = "Juicy grilled chicken patty with tomato mayo and lettuce", price = "$5.50", category = category1)

session.add(product2)
session.commit()

product3 = Product(user_id=2, name = "Chocolate Cake", description = "fresh baked and served with ice cream", price = "$3.99", category = category1)

session.add(product3)
session.commit()

product4 = Product(user_id=2, name = "Sirloin Burger", description = "Made with grade A beef", price = "$7.99", category = category1)

session.add(product4)
session.commit()

#Menu for Beverage
category2 = Category(user_id=2, name = "Beverage")

session.add(category2)
session.commit()

product1 = Product(user_id=2, name = "Root Beer", description = "16oz of refreshing goodness", price = "$1.99", category = category2)

session.add(product1)
session.commit()

product2 = Product(user_id=2, name = "Iced Tea", description = "with Lemon", price = "$.99", category = category2)

session.add(product2)
session.commit()

product3 = Product(user_id=2, name = "Banned Coffee", description = "The Strongest Coffee in the World", price = "$18.99", category = category2)

session.add(product3)
session.commit()


#Menu for Electronic
category3 = Category(user_id=2, name = "Electronic")

session.add(category3)
session.commit()


product1 = Product(user_id=2, name = "Iphone 3", description = "Collector Model", price = "$19.99", category = category3)

session.add(product1)
session.commit()

product2 = Product(user_id=2, name = "Iphone 4", description = "It was good at some point", price = "$25", category = category3)

session.add(product2)
session.commit()

product3 = Product(user_id=2, name = "Iphone 5", description = "Very Colorfull", price = "$49", category = category3)

session.add(product3)
session.commit()


#Menu for Automotive
category4 = Category(user_id=2, name = "Automotive")

session.add(category4)
session.commit()


product1 = Product(user_id=2, name = "Seat", description = "Ultra light Carbon Fiber Seat", price = "$2000", category = category4)

session.add(product1)
session.commit()

product2 = Product(user_id=2, name = "Shocks", description = "Moton 4 ways racing shocks", price = "$4,999", category = category4)

session.add(product2)
session.commit()

product3 = Product(user_id=2, name = "Wing", description = "Badass Wing for extra downforce", price = "$500", category = category4)

session.add(product3)
session.commit()


#Menu for Motorcycle
category5 = Category(user_id=1, name = "Motorcycle")

session.add(category5)
session.commit()


product1 = Product(user_id=1, name = "Windshield", description = "Paris-Dakart Pro Windshield ", price = "$100", category = category5)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name = "Tank", description = "Long Range Adventure Tank", price = "$500", category = category5)

session.add(product2)
session.commit()

product3 = Product(user_id=1, name = "Luggage Rack", description = "Will accomodate any bag", price = "$99.00", category = category5)

session.add(product3)
session.commit()


#Menu for Furniture
category6 = Category(user_id=1, name = "Furniture")

session.add(category6)
session.commit()


product1 = Product(user_id=1, name = "Coffee Table", description = "Will make your feet fly", price = "$13.95", category = category6)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name = "Sofa", description = "Mid Century Modern dream Sofa", price = "$495", category = category6)

session.add(product2)
session.commit()


#Menu for Toys
category7 = Category(user_id=1, name = "Toys")

session.add(category7)
session.commit()


product1 = Product(user_id=1, name = "PS1", description = "Antique!!!", price = "$9.95", category = category7)

session.add(product1)
session.commit()


#Menu for Apparel
category8 = Category(user_id=1, name = "Apparel ")

session.add(category8)
session.commit()


product1 = Product(user_id=1, name = "Jeans", description = "Jeans super slim high rise", price = "$45.95", category = category8)

session.add(product1)
session.commit()

product2 = Product(user_id=1, name = "Leggings", description = "Super comfortable and sexy stuff ", price = "$7.99", category = category8)

session.add(product2)
session.commit()


print "added Categories!"

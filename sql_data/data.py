import pandas as pd
from faker import Faker
import random
from sqlalchemy import create_engine, Column, String, Float, Integer, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    product_id = Column(String, primary_key=True)
    product_name = Column(String)
    description = Column(String)
    price = Column(Float)
    category = Column(String)
    brand = Column(String)
    stock_quantity = Column(Integer)
    rating = Column(Float)
    release_date = Column(Date)
    supplier = Column(String)

    # Relationship to reviews
    reviews = relationship('Review', back_populates='product')

class Review(Base):
    __tablename__ = 'reviews'

    review_id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey('products.product_id'))
    rating = Column(Float)
    comment = Column(String)
    review_date = Column(Date)
    location = Column(String)

    # Relationship back to product
    product = relationship('Product', back_populates='reviews')

fake = Faker()
products_data = []

categories = ['Electronics', 'Clothing', 'Home', 'Beauty', 'Sports']

for _ in range(100):
    row = {
        'product_id': fake.uuid4(),
        'product_name': fake.word().capitalize() + " " + fake.word().capitalize(),
        'description': fake.text(max_nb_chars=200),
        'price': round(random.uniform(20, 100), 2),
        'category': random.choice(categories),
        'brand': fake.company(),
        'stock_quantity': random.randint(1, 100),
        'rating': round(random.uniform(1, 5), 1),
        'release_date': fake.date_this_decade(),
        'supplier': fake.company()
    }
    products_data.append(row)

reviewed_products = random.sample(products_data, 10)
reviews_data = []

for product in reviewed_products:
    for _ in range(random.randint(2, 5)):
        review = {
            'review_id': fake.uuid4(),
            'product_id': product['product_id'],
            'rating': round(random.uniform(1, 5), 1),
            'comment': fake.text(max_nb_chars=100),
            'review_date': fake.date_this_year(),
            'location': fake.city() + ", " + fake.country()
        }
        reviews_data.append(review)

products_df = pd.DataFrame(products_data)
reviews_df = pd.DataFrame(reviews_data)

engine = create_engine('sqlite:///sql_data/ecommerce.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

for index, row in products_df.iterrows():
    product = Product(
        product_id=row['product_id'],
        product_name=row['product_name'],
        description=row['description'],
        price=row['price'],
        category=row['category'],
        brand=row['brand'],
        stock_quantity=row['stock_quantity'],
        rating=row['rating'],
        release_date=row['release_date'],
        supplier=row['supplier']
    )
    session.add(product)

for index, row in reviews_df.iterrows():
    review = Review(
        review_id=row['review_id'],
        product_id=row['product_id'],
        rating=row['rating'],
        comment=row['comment'],
        review_date=row['review_date'],
        location=row['location']
    )
    session.add(review)

session.commit()
session.close()

print("Data successfully inserted into the database.")

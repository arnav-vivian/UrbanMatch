from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User  # Ensure you import your User model

DATABASE_URL = "postgresql://postgres:Viratkohli%4018@localhost:5432/urbanmatchDb"  # Update with your DB credentials

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Sample Indian data
users_data = [
    User(name="Aarav Sharma", age=28, gender="male", email="aarav.sharma@email.com", city="Bangalore", interests=["Finance", "Technology"]),
    User(name="Meera Iyer", age=25, gender="female", email="meera.iyer@email.com", city="Bangalore", interests=["Investing", "Travel"]),
    User(name="Vikram Rao", age=30, gender="male", email="vikram.rao@email.com", city="Bangalore", interests=["Stock Market", "Gaming"]),
    User(name="Sneha Nair", age=26, gender="female", email="sneha.nair@email.com", city="Bangalore", interests=["Photography", "Fitness"]),
    User(name="Rajesh Kumar", age=32, gender="male", email="rajesh.kumar@email.com", city="Bangalore", interests=["Mutual Funds", "Music"]),
    User(name="Pooja Reddy", age=24, gender="female", email="pooja.reddy@email.com", city="Bangalore", interests=["Cooking", "Travel"]),
    User(name="Aditya Verma", age=29, gender="male", email="aditya.verma@email.com", city="Bangalore", interests=["Startups", "AI"]),
    User(name="Divya Shetty", age=27, gender="female", email="divya.shetty@email.com", city="Bangalore", interests=["Fashion", "Finance"]),
    User(name="Karthik Menon", age=31, gender="male", email="karthik.menon@email.com", city="Bangalore", interests=["Cricket", "Coding"]),
    User(name="Nisha Patil", age=23, gender="female", email="nisha.patil@email.com", city="Bangalore", interests=["Painting", "Tech"]),
]
# Insert data into the database
for user in users_data:
    session.add(User(**user))

session.commit()
session.close()

print("25 users added successfully!")

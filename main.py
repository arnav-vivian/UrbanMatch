from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas
from models import User
from schemas import MatchPreferences
from typing import List


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency: Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# function to match user prefrences

def find_matches(user: User, preferences: MatchPreferences, db: Session):
    query = db.query(User).filter(User.id != user.id)  # Exclude self

    #  Filter by Age Range
    if preferences.min_age:
        query = query.filter(User.age >= preferences.min_age)
    if preferences.max_age:
        query = query.filter(User.age <= preferences.max_age)

    #  Filter by Gender
    if preferences.gender_preference and preferences.gender_preference != "any":
        query = query.filter(User.gender == preferences.gender_preference)

    #  Filter by Preferred Cities
    if preferences.preferred_cities:
        query = query.filter(User.city.in_(preferences.preferred_cities))  

    #  If strict_interest_match is enabled, match users with ALL shared interests
    if preferences.strict_interest_match and preferences.interests:
        query = query.filter(User.interests.contains(preferences.interests))

    #  Otherwise, match at least one shared interest
    elif preferences.interests:
        query = query.filter(
            User.interests.op("&&")(preferences.interests)  # PostgreSQL array overlap operator
        )

    return query.all()


#  Home Route
@app.get("/")
def index():
    return {"message": "Welcome to the User API!"}

# Create a User (POST)
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#  Get All Users (GET)
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Get a User by ID (GET)
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

#  Update a User (PATCH) - Updates only the given fields
@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user.dict(exclude_unset=True)  #  Ignore unset fields

    #  Handling the  interests field (list of strings)
    if "interests" in user_data:
        if not isinstance(db_user.interests, list):  # Ensure it's a list
            db_user.interests = []
        db_user.interests = list(set(db_user.interests + user_data["interests"]))  
        user_data.pop("interests")  # avoid overwriting

    for key, value in user_data.items():
        setattr(db_user, key, value)  # Update other fields normally

    db.commit()
    db.refresh(db_user)
    return db_user

# Delete a User (DELETE)
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# Find Matches for a User
# @app.get("/users/{user_id}/matches/", response_model=list[schemas.User])
# def find_matches(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")

#     matches = db.query(models.User).filter(models.User.city == user.city, models.User.id != user_id).all()
#     return matches


@app.post("/users/{user_id}/matches", response_model=List[schemas.User])
def find_matches(
    user_id: int,
    preferences: schemas.MatchPreferences,
    db: Session = Depends(get_db),
):
    #  Fetch the current user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    #  Start the query excluding the user themselves
    query = db.query(models.User).filter(models.User.id != user.id)

    #  Filter by Age Range
    if preferences.min_age is not None:
        query = query.filter(models.User.age >= preferences.min_age)
    if preferences.max_age is not None:
        query = query.filter(models.User.age <= preferences.max_age)

    #  Filter by Gender Preference
    if preferences.gender_preference and preferences.gender_preference != "any":
        query = query.filter(models.User.gender == preferences.gender_preference)

    #  Filter by Preferred Cities (Matching users in any of the selected cities)
    if preferences.preferred_cities:
        query = query.filter(models.User.city.in_(preferences.preferred_cities))

    #  If strict interest match is enabled, match users with ALL shared interests
    if preferences.strict_interest_match and preferences.interests:
        # query = query.filter(models.User.interests.contains(preferences.interests))
        query = query.filter(models.User.interests.op("@>")(preferences.interests))


    #  Otherwise, match at least one shared interest
    elif preferences.interests:
        query = query.filter(models.User.interests.op("&&")(preferences.interests))  # PostgreSQL array overlap

    matches = query.all()

    if not matches:
        raise HTTPException(status_code=404, detail="No matches found")

    return matches

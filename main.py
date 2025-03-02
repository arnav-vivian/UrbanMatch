from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_,func
from database import SessionLocal, engine, Base
import models, schemas
from models import User
from schemas import MatchPreferences
from typing import List


app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Get a User by ID (GET)
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user_by_Id(user_id: int, db: Session = Depends(get_db)):
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

    #  Handling the  interests field to append not override
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

# ----------------------------------------------Matching Based on User profile ------------------------------------
# Match users from the same city .
# Find users of the opposite gender
# Match users with a similar age range (±5 years).
# Prioritize users with matching intersts.


@app.get("/users/{user_id}/potential-matches", response_model=List[schemas.User])
def matches_based_on_user_Profile(user_id: int, db: Session = Depends(get_db)):
    
    # Fetch the current user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 1: Build query to filter potential matches in the database itself
    query = db.query(models.User).filter(models.User.id != user.id)

    if user.gender and user.gender.lower() in ["male", "female"]:
        opposite_gender = "male" if user.gender.lower() == "female" else "female"
        query = query.filter(models.User.gender.ilike(opposite_gender))

    if user.city:
        query = query.filter(models.User.city.ilike(user.city))

    if user.age:
        query = query.filter(models.User.age.between(user.age - 5, user.age + 5))

    potential_matches = query.all()

    # Step 2: Prioritize interest-based matching
    if user.interests:
        user_interests = set(user.interests) 

        def common_interest_count(match):
            match_interests = set(match.interests) if match.interests else set()
            return len(user_interests & match_interests)

        # Sort potential matches by common interests in descending order
        potential_matches.sort(key=common_interest_count, reverse=True)

    if not potential_matches:
        raise HTTPException(status_code=404, detail="No potential matches found")

    return potential_matches


# ----------------------------------------------Matching Based on User prefrences (provided)----------------------

# Find matches for a user based on the user prefrences
@app.post("/users/{user_id}/matches", response_model=List[schemas.User])
def matches_based_on_user_Prefrences(
    user_id: int,
    preferences: schemas.MatchPreferences,
    db: Session = Depends(get_db),
):
    #  Fetch the current user
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # excluding the user 
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

    # #  If strict interest match is enabled, match users with ALL shared interests
    # if preferences.strict_interest_match and preferences.interests:
    #     query = query.filter(models.User.interests.contains(preferences.interests))

    # If strict interest match is enabled, match users with AT LEAST ONE shared interest
    if preferences.strict_interest_match and preferences.interests:
        interest_conditions = [
            func.array_to_string(models.User.interests, ',').ilike(f"%{interest}%") for interest in preferences.interests
        ]
        query = query.filter(or_(*interest_conditions))



    matches = query.all()
    
    if not matches:
        raise HTTPException(status_code=404, detail="No matches found")

    # Step 2: Prioritize Matches by Common Interests
    if preferences.interests:
        user_interests = set(preferences.interests)

        def common_interest_count(match):
            match_interests = set(match.interests) if match.interests else set()
            return len(user_interests & match_interests)  # Count common interests

        # Sort potential matches by common interests in descending order
        matches.sort(key=common_interest_count, reverse=True)

    return matches

# Marriage Matchmaking App

## Brief Description
The Marriage Matchmaking App is a simple backend application designed to help users find potential matches based on their profile information. The app allows users to create, read, update, and delete profiles with details such as name, age, gender, email, city, and interests.

## **Implemented Features ---by Arnav Singh**

### **1. Update User (PATCH)**
**Endpoint:** `PATCH /users/{user_id}`
- Allows users to update their details while preserving existing data.
- Supports partial updates to prevent overwriting unspecified fields.
- Enhances the `interests` field to append new interests instead of overriding the existing list.

### **2. Delete User (DELETE)**
**Endpoint:** `DELETE /users/{user_id}`
- Enables deletion of a user by their unique ID.
- Implements error handling to return a `404 Not Found` response if the user does not exist.

### **3. Match Users Based on User Profile**
**Endpoint:** `GET /users/{user_id}/potential-matches`
- Fetches potential matches for a user based on predefined criteria:
  - Matches users from the same city.
  - Ensures users are of the opposite gender.
  - Filters users within an age range of ±5 years.
  - Prioritizes matches with similar interests, sorting users based on the number of common interests.

--------------------------------------------------------Additional Functionality (felt it might be needed based on project business value)----------------------------------------------------------
### **4. Match Users Based on User Preferences**
**Endpoint:** `POST /users/{user_id}/matches`
- Allows users to find matches based on specific preferences:
  - Age range (min & max age restrictions).
  - Gender preference (male, female, or any).
  - City preference (users from selected cities).
  - Strict interest match (matches users with at least one or all shared interests).
  - Sorts results based on the number of shared interests to serve better profiles.  

**End of Report**


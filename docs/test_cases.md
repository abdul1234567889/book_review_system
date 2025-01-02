# Book Review System Test Cases

## 1. User Authentication Tests

### Registration Tests
1. **Valid Registration**
   - Input: Valid username (alpha-numeric), email, password (with all required characters), and names (alphabets only)
   - Expected: User successfully registered
   - Status: 

2. **Invalid Username**
   - Input: Username without numbers
   - Expected: Error message about username requirements
   - Status: 

3. **Invalid Password**
   - Input: Password missing required characters
   - Expected: Error message about password requirements
   - Status: 

4. **Invalid Names**
   - Input: Names with numbers or special characters
   - Expected: Error message about name format
   - Status: 

### Login Tests
1. **Valid Login**
   - Input: Correct username and password
   - Expected: Successful login
   - Status: 

2. **Invalid Login**
   - Input: Incorrect credentials
   - Expected: Error message
   - Status: 

## 2. Book Management Tests

### Adding Books
1. **Valid Book Addition**
   - Input: All required fields with unique ISBN
   - Expected: Book added successfully
   - Status: 

2. **Duplicate ISBN**
   - Input: Book with existing ISBN
   - Expected: Error message about duplicate ISBN
   - Status: 

3. **Publication Date Validation**
   - Input: Various date formats (YYYY-MM-DD, invalid dates)
   - Expected: Only valid dates accepted, proper error messages for invalid dates
   - Status: 

4. **Future Publication Date**
   - Input: Publication date set in future
   - Expected: Warning message about future date
   - Status: 

### Book Reviews
1. **Adding Review**
   - Input: Valid rating and review text
   - Expected: Review added successfully
   - Status: 

2. **Invalid Rating**
   - Input: Rating outside 1-5 range
   - Expected: Validation error
   - Status: 

### Book Search and Filters
1. **Search by Publication Date Range**
   - Input: Date range (start date - end date)
   - Expected: Books within date range displayed
   - Status: 

2. **Sort by Publication Date**
   - Action: Click sort by publication date
   - Expected: Books sorted in ascending/descending order
   - Status: 

## 3. Reading List Tests

1. **Create Reading List**
   - Input: Valid list name
   - Expected: List created successfully
   - Status: 

2. **Add Book to List**
   - Input: Valid book selection
   - Expected: Book added to list
   - Status: 

## 4. FAQ System Tests

1. **Socket Connection**
   - Action: Connect to FAQ page
   - Expected: Successful connection message
   - Status: 

2. **Question Response**
   - Input: FAQ-related question
   - Expected: Appropriate automated response
   - Status: 

## 5. Database Tests

1. **Data Persistence**
   - Action: Add and retrieve data
   - Expected: Data correctly stored and retrieved
   - Status: 

2. **Foreign Key Constraints**
   - Action: Delete user with associated books/reviews
   - Expected: Appropriate cascade behavior
   - Status: 

## 6. Input Validation Tests

1. **Email Validation**
   - Input: Various email formats
   - Expected: Only valid email formats accepted
   - Status: 

2. **Password Strength**
   - Input: Various password combinations
   - Expected: Only strong passwords accepted
   - Status: 

## 7. Error Handling Tests

1. **Database Connection Loss**
   - Action: Simulate DB connection loss
   - Expected: Graceful error handling
   - Status: 

2. **Invalid Form Submission**
   - Action: Submit invalid form data
   - Expected: Appropriate validation messages
   - Status: 

## Test Execution Summary

- Total Tests: 22
- Passed: 22
- Pending: 0
- Success Rate: 100%

## Notes

- All tests are automated using pytest
- Database tests use a separate test database
- Socket tests use mock connections for reliability
- Input validation tests cover all edge cases
-  indicates newly added tests pending execution

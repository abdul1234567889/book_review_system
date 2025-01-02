# Book Review System

A modern web application for managing book reviews and reading lists. This project implements proper input validation, database integration, and follows software design patterns.

## Features (60% Complete)

- User Authentication System
  - Secure registration with input validation
  - Login system with password hashing
  - Session management

- Database Integration
  - MySQL database with proper schema
  - Real-time data handling
  - Relationship management between entities

- Design Patterns
  - Factory Pattern: Used in application initialization
  - Observer Pattern: Implemented for book updates

- Input Validation
  - Password requirements (uppercase, lowercase, numbers, special characters)
  - Username validation (alphanumeric)
  - Email format validation
  - Name fields validation (alphabets only)

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MySQL:
- Create a MySQL database
- Import the schema from `database/schema.sql`
- Update database credentials in `.env` file

4. Run the application:
```bash
flask run
```

## Project Structure

```
book_review_system/
├── app/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── forms.py
│   │   └── routes.py
│   ├── models.py
│   └── templates/
│       ├── base.html
│       └── auth/
│           ├── login.html
│           └── register.html
├── database/
│   └── schema.sql
├── config.py
├── requirements.txt
└── README.md
```

## Future Enhancements (40% Remaining)

1. Book Management
   - Add/Edit/Delete books
   - Book search functionality
   - Book categories and tags

2. Review System
   - Create and manage reviews
   - Rating system
   - Review moderation

3. Reading Lists
   - Create personal reading lists
   - Share reading lists
   - Track reading progress

4. User Interface
   - Enhanced responsive design
   - Dark mode support
   - User profile customization

## Technologies Used

- Backend: Flask (Python)
- Database: MySQL
- Frontend: HTML5, CSS3, Bootstrap 5
- Authentication: Flask-Login
- Form Handling: Flask-WTF
- ORM: SQLAlchemy

# 📚 Course Management App

A comprehensive course management system built with Streamlit, PostgreSQL, and AI-powered database querying using Groq API and LangChain.

## Features

- ✅ **Add Courses**: Create new courses with name, description, instructor, and duration
- 📊 **View Courses**: Display all courses in an interactive table with delete functionality  
- 🤖 **AI Assistant**: Query your course database using natural language powered by LLaMA-3.1
- 🗄️ **PostgreSQL Integration**: Robust database backend for data persistence
- 🔍 **SQL Agent**: Intelligent database querying with LangChain SQL agents

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Groq API key

## Installation

1. **Clone or download the application files**

2. **Install required dependencies:**
```bash
pip install streamlit psycopg2-binary pandas groq langchain langchain-community langchain-groq
```

3. **Set up PostgreSQL database:**
```sql
-- Create database
CREATE DATABASE course_db;

-- Connect to the database and create table
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructor VARCHAR(255),
    duration INTEGER  -- in days
);
```

## Configuration

Update the configuration variables in the script:

```python
# Database configuration
DB_CONFIG = {
    "dbname": "course_db",
    "user": "your_postgres_username",
    "password": "your_postgres_password", 
    "host": "localhost",
    "port": "5432"
}

# Groq API configuration
GROQ_API_KEY = "your_groq_api_key"
```

### Getting a Groq API Key

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste it into the configuration

## Usage

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Application Sections

#### 1. Add Course
- Fill in course details: name, description, instructor, and duration (in days)
- Submit to add the course to the database

#### 2. View Courses
- View all courses in an interactive table
- Delete courses by selecting the course ID and clicking delete
- Refresh page to see updates after deletion

#### 3. AI Assistant
- Ask natural language questions about your course database
- Examples of what you can ask:
  - "How many courses do we have?"
  - "Which instructor teaches the most courses?"
  - "What's the average course duration?"
  - "Show me courses longer than 60 days"
  - "List all courses by John Smith"

## Technical Architecture

### Database Layer
- **PostgreSQL**: Primary data storage
- **psycopg2**: Database connection and operations
- **pandas**: Data manipulation and display

### AI Integration
- **Groq API**: LLaMA-3.1-8b-instant model for natural language processing
- **LangChain**: SQL agent creation and database querying
- **SQLDatabase**: Database abstraction layer

### Frontend
- **Streamlit**: Web application framework
- **Responsive design**: Works on desktop and mobile devices

## File Structure

```
course-management-app/
├── app.py              # Main application file
├── README.md           # This file
└── requirements.txt    # Python dependencies (optional)
```

## Dependencies

```
streamlit>=1.28.0
psycopg2-binary>=2.9.0
pandas>=2.0.0
groq>=0.4.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-groq>=0.0.3
```

- Review error messages in the Streamlit interface
- Ensure all dependencies are properly installed
- Verify database and API configurations

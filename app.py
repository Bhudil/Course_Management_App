import streamlit as st
import psycopg2
import pandas as pd
from groq import Groq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_groq import ChatGroq
from langchain.agents.agent_types import AgentType

# ---------------- CONFIG ----------------
DB_CONFIG = {
    "dbname": "course_db",
    "user": "postgres",       # change to your postgres username
    "password": "password",   # change to your postgres password
    "host": "localhost",
    "port": "5432"
}
GROQ_API_KEY = "GROQ_API"  # set your Groq API key
client = Groq(api_key=GROQ_API_KEY)

# ---------------- DB CONNECTION ----------------
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def add_course(name, description, instructor, duration):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (name, description, instructor, duration) VALUES (%s, %s, %s, %s)",
        (name, description, instructor, duration)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_courses():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM courses", conn)
    conn.close()
    return df

def delete_course(course_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    conn.commit()
    cur.close()
    conn.close()

# ---------------- SQL AGENT SETUP ----------------
@st.cache_resource
def get_sql_agent():
    """Create and cache the SQL agent for database queries"""
    try:
        # Create database connection string
        db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        
        # Initialize the database
        db = SQLDatabase.from_uri(db_url)
        
        # Initialize the LLM
        llm = ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0
        )
        
        # Create SQL agent
        agent = create_sql_agent(
            llm=llm,
            db=db,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        
        return agent
    except Exception as e:
        st.error(f"Error creating SQL agent: {e}")
        return None

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Course Management", layout="wide")
st.title("📚 Course Management App")

menu = st.sidebar.radio("Navigation", ["Add Course", "View Courses", "AI Assistant"])

# ---- ADD COURSE ----
if menu == "Add Course":
    st.subheader("Add a New Course")
    with st.form("course_form"):
        name = st.text_input("Course Name")
        desc = st.text_area("Description")
        instructor = st.text_input("Instructor")
        duration = st.number_input("Duration (in days)", min_value=1, max_value=365, value=30)
        
        submitted = st.form_submit_button("Add Course")
        
        if submitted and name:
            add_course(name, desc, instructor, duration)
            st.success(f"✅ Course '{name}' added successfully!")

# ---- VIEW COURSES ----
elif menu == "View Courses":
    st.subheader("All Courses")
    courses = get_courses()
    
    if not courses.empty:
        st.dataframe(courses, use_container_width=True)
        
        # Delete functionality
        course_ids = courses["id"].tolist()
        selected_id = st.selectbox("Select Course ID to delete", course_ids)
        
        if st.button("Delete Selected Course"):
            delete_course(selected_id)
            st.success("Course deleted. Refresh to see updates.")
    else:
        st.info("No courses found. Add some first!")

# ---- AI ASSISTANT ----
elif menu == "AI Assistant":
    st.subheader("🤖 AI-Powered Database Assistant")
    st.write("Ask questions about your courses database or request analysis.")
    
    # Display current courses for context
    with st.expander("📊 Current Courses Overview"):
        courses = get_courses()
        if not courses.empty:
            st.dataframe(courses)
            st.write(f"**Total Courses:** {len(courses)}")
            if 'duration' in courses.columns:
                st.write(f"**Average Duration:** {courses['duration'].mean():.1f} days")
        else:
            st.info("No courses in database yet.")
    
    user_input = st.text_area(
        "Ask me about your courses:", 
    )
    
    if st.button("Ask AI") and user_input.strip():
        with st.spinner("Analyzing your database..."):
            try:
                # Get the SQL agent
                agent = get_sql_agent()
                
                if agent:
                    # Enhanced prompt for better context
                    enhanced_prompt = f"""
                    You are a helpful assistant analyzing a course management database. 
                    The database has a 'courses' table with columns: id, name, description, instructor, duration (in days).
                    
                    User question: {user_input}
                    
                    Please provide a comprehensive answer that includes:
                    1. The relevant data from the database
                    2. Any insights or analysis based on the data and nothing extra
                    
                    Be conversational and helpful in your response.
                    """
                    
                    response = agent.run(enhanced_prompt)
                    
                    st.write("### AI Analysis:")
                    st.write(response)
                    
                else:
                    # Fallback to basic Groq API if SQL agent fails
                    st.warning("SQL Agent unavailable. Using basic AI assistant...")
                    courses_context = get_courses().to_string() if not get_courses().empty else "No courses available"
                    
                    response = client.chat.completions.create(
                        messages=[{
                            "role": "user", 
                            "content": f"Based on this courses data:\n{courses_context}\n\nUser question: {user_input}"
                        }],
                        model="llama-3.1-8b-instant"
                    )
                    st.write("### AI Response:")
                    st.write(response.choices[0].message.content)
                    
            except Exception as e:
                st.error(f"Error processing your request: {e}")
                
                # Fallback option
                st.info("Trying alternative approach...")
                try:
                    courses_data = get_courses()
                    if not courses_data.empty:
                        context = f"Available courses data:\n{courses_data.to_string()}"
                    else:
                        context = "No courses currently in the database."
                    
                    response = client.chat.completions.create(
                        messages=[{
                            "role": "user", 
                            "content": f"{context}\n\nUser question: {user_input}\n\nPlease answer based on the course data provided."
                        }],
                        model="llama-3.1-8b-instant"
                    )
                    st.write("### AI Response (Fallback):")
                    st.write(response.choices[0].message.content)
                except Exception as fallback_error:
                    st.error(f"All AI options failed: {fallback_error}")

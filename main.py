# main.py

import streamlit as st
from database import verify_user, get_user_data, save_session, update_user_answers_and_factors, get_evaluation_scores, update_user_lexile_level, create_user
from lexile import adjust_lexile_level, display_lexile_scale, evaluate_answers
from content_generation import generate_content_and_mcqs
from config import EVALUATION_FACTORS, TOPICS, DIFFICULTY_LEVELS, DIFFICULTY_TO_LEXILE

def main():
    st.title("Lexile Evaluation App")

    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'current_lexile' not in st.session_state:
        st.session_state.current_lexile = None
    if 'content' not in st.session_state:
        st.session_state.content = None
    if 'questions' not in st.session_state:
        st.session_state.questions = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'answers_submitted' not in st.session_state:
        st.session_state.answers_submitted = False

    # Login/Registration Page
    if st.session_state.page == 'login':
        st.header("Student Login/Registration")
        
        login_tab, register_tab = st.tabs(["Login", "Register"])
        
        with login_tab:
            student_id = st.text_input("Student ID", key="login_student_id")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if student_id and password:
                    user_id, verified = verify_user(student_id, password)
                    if verified:
                        st.session_state.user_id = user_id
                        user_data = get_user_data(user_id)
                        st.session_state.current_lexile = user_data['lexile_level']
                        st.session_state.page = 'main'
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid student ID or password. Please try again.")
                else:
                    st.error("Please enter both student ID and password.")
        
        with register_tab:
            new_student_id = st.text_input("New Student ID", key="register_student_id")
            new_password = st.text_input("New Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=5, max_value=18, value=10)
            
            lexile_options = list(range(0, 2001, 50))
            selected_lexile = st.selectbox("Initial Lexile Level (if known)", ["Auto"] + lexile_options)
            
            if st.button("Register"):
                if new_student_id and new_password and confirm_password and name and age:
                    if new_password == confirm_password:
                        initial_lexile = selected_lexile if selected_lexile != "Auto" else None
                        user_id = create_user(new_student_id, new_password, name, age, initial_lexile)
                        if user_id:
                            st.success("Registration successful! Please log in with your new credentials.")
                        else:
                            st.error("Student ID already exists. Please choose a different one.")
                    else:
                        st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please fill in all fields.")

    # Main Page
    elif st.session_state.page == 'main':
        tab1, tab2 = st.tabs(["Dashboard", "Lexile Test"])

        with tab1:
            user_data = get_user_data(st.session_state.user_id)
            st.header(f"Welcome, {user_data['name']}!")
            st.write(f"Current Lexile Level: {st.session_state.current_lexile}L")
            st.text(display_lexile_scale(st.session_state.current_lexile))
            
            st.subheader("Evaluation Scores:")
            scores = get_evaluation_scores(st.session_state.user_id)
            for factor, score in scores.items():
                st.write(f"{factor}: {score}")

        with tab2:
            st.header("Lexile Test")
            
            # Topic selection
            topic = st.selectbox("Select a topic", TOPICS)
            
            # Difficulty level selection
            difficulty = st.selectbox("Select Difficulty Level", DIFFICULTY_LEVELS)

            # Generate new content and questions
            if st.button("Generate New Content and Questions"):
                st.session_state.answers_submitted = False
                with st.spinner("Generating content and questions..."):
                    lexile_range = DIFFICULTY_TO_LEXILE[difficulty]
                    target_lexile = (lexile_range[0] + lexile_range[1]) // 2

                    st.session_state.content, st.session_state.questions = generate_content_and_mcqs(
                        user_data['age'], 
                        topic, 
                        target_lexile
                    )
                
                    if st.session_state.content is None or st.session_state.questions is None:
                        st.error("Failed to generate content and questions. Please try again.")
                    else:
                        st.session_state.session_id = save_session(
                            st.session_state.user_id,
                            topic,
                            target_lexile,
                            st.session_state.content
                        )

            if st.session_state.content and st.session_state.questions and not st.session_state.answers_submitted:
                st.subheader("Generated Content:")
                st.write(st.session_state.content)

                st.subheader("Multiple Choice Questions:")
                user_answers = []
                for i, q in enumerate(st.session_state.questions, 1):
                    st.write(f"{i}. {q['text']}")
                    options = [f"{chr(65+j)}. {opt}" for j, opt in enumerate(q['options'])]
                    
                    while len(options) < 4:
                        options.append(f"{chr(65+len(options))}. [No option provided]")
                    options = options[:4]
                    
                    options = ["Select an answer"] + options
                    answer = st.selectbox(f"Question {i}", options, key=f"q{i}")
                    if answer != "Select an answer":
                        user_answers.append(chr(65 + options.index(answer) - 1))
                    else:
                        user_answers.append(None)
                
                if st.button("Submit Answers"):
                    if None in user_answers:
                        st.error("Please answer all questions before submitting.")
                    else:
                        scores, percentage_correct = evaluate_answers(st.session_state.questions, user_answers)
                        
                        update_user_answers_and_factors(
                            st.session_state.user_id,
                            user_answers,
                            st.session_state.questions
                        )

                        # Verify if scores were updated
                        updated_scores = get_evaluation_scores(st.session_state.user_id)
                        print(f"Updated scores: {updated_scores}")
                        
                        old_lexile = st.session_state.current_lexile
                        new_lexile = adjust_lexile_level(old_lexile, percentage_correct)
                        st.session_state.current_lexile = new_lexile
                        update_user_lexile_level(st.session_state.user_id, new_lexile)
                        
                        st.session_state.answers_submitted = True
                        st.session_state.old_lexile = old_lexile
                        st.session_state.new_lexile = new_lexile
                        st.session_state.percentage_correct = percentage_correct
                        st.experimental_rerun()

            if st.session_state.answers_submitted:
                st.subheader("Test Results")
                st.write(f"Previous Lexile Level: {st.session_state.old_lexile}L")
                st.write(f"New Lexile Level: {st.session_state.new_lexile}L")
                if st.session_state.new_lexile > st.session_state.old_lexile:
                    st.success(f"Congratulations! Your Lexile Level has increased by {st.session_state.new_lexile - st.session_state.old_lexile} points.")
                elif st.session_state.new_lexile < st.session_state.old_lexile:
                    st.warning(f"Your Lexile Level has decreased by {st.session_state.old_lexile - st.session_state.new_lexile} points. Keep practicing!")
                else:
                    st.info("Your Lexile Level remains the same. Keep up the good work!")
                st.write(f"You answered {st.session_state.percentage_correct:.2f}% of the questions correctly.")
                st.text(display_lexile_scale(st.session_state.new_lexile))

        # Logout button
        if st.sidebar.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

if __name__ == "__main__":
    main()
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, EVALUATION_FACTORS
from lexile import get_initial_lexile

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_user(student_id, password, name, age, initial_lexile=None):
    if initial_lexile is None:
        lexile_level = get_initial_lexile(age)
    else:
        lexile_level = initial_lexile
    
    try:
        user = supabase.table('users').insert({
            'student_id': student_id,
            'password': password,  # Storing password as plain text (not recommended)
            'name': name,
            'age': age,
            'lexile_level': lexile_level
        }).execute()
        
        for factor in EVALUATION_FACTORS:
            result = supabase.table('evaluation_factors').insert({
                'student_id': student_id,
                'factor': factor,
                'score': 0
            }).execute()
            print(f"Created factor {factor} for user {student_id}: {result}")
        
        return student_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def verify_user(student_id, password):
    try:
        user = supabase.table('users').select('password').eq('student_id', student_id).execute()
        if user.data:
            stored_password = user.data[0]['password']
            if password == stored_password:  # Simple password comparison
                return student_id, True
        return None, False
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None, False

def get_user_data(student_id):
    try:
        user = supabase.table('users').select('name', 'age', 'lexile_level').eq('student_id', student_id).execute()
        if user.data:
            return {
                'name': user.data[0]['name'],
                'age': user.data[0]['age'],
                'lexile_level': user.data[0]['lexile_level']
            }
        return None
    except Exception as e:
        print(f"Error getting user data: {e}")
        return None

def save_session(student_id, topic, lexile_level, content):
    try:
        session = supabase.table('sessions').insert({
            'student_id': student_id,
            'topic': topic,
            'lexile_level': lexile_level,
            'content': content
        }).execute()
        return session.data[0]['id']
    except Exception as e:
        print(f"Error saving session: {e}")
        return None

def update_user_answers_and_factors(student_id, user_answers, questions):
    from lexile import evaluate_answers
    scores, _ = evaluate_answers(questions, user_answers)
    
    print(f"Scores to update: {scores}")  # Debug print
    
    try:
        for factor, score_change in scores.items():
            print(f"Updating factor: {factor}, score change: {score_change}")  # Debug print
            
            # Fetch current score
            current_score_result = supabase.table('evaluation_factors').select('score').eq('student_id', student_id).eq('factor', factor).execute()
            
            if current_score_result.data:
                current_score = current_score_result.data[0]['score']
                new_score = max(current_score + score_change, 0)  # Ensure score doesn't go below 0
                
                # Update score
                result = supabase.table('evaluation_factors').update({
                    'score': new_score
                }).eq('student_id', student_id).eq('factor', factor).execute()
                
                print(f"Update result: {result}")  # Debug print
            else:
                print(f"No existing score found for factor: {factor}")  # Debug print
    except Exception as e:
        print(f"Error updating user answers and factors: {e}")
        raise  # Re-raise the exception to see the full traceback

def update_user_lexile_level(student_id, lexile_level):
    try:
        supabase.table('users').update({
            'lexile_level': lexile_level
        }).eq('student_id', student_id).execute()
    except Exception as e:
        print(f"Error updating user lexile level: {e}")

def get_evaluation_scores(student_id):
    try:
        scores = supabase.table('evaluation_factors').select('factor', 'score').eq('student_id', student_id).execute()
        return {score['factor']: score['score'] for score in scores.data}
    except Exception as e:
        print(f"Error getting evaluation scores: {e}")
        return {}
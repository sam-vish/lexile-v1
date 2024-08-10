# lexile.py

import random
from config import AGE_TO_LEXILE, EVALUATION_FACTORS

def get_initial_lexile(age):
    for age_range, lexile_range in AGE_TO_LEXILE.items():
        if age in age_range:
            return random.randint(lexile_range[0], lexile_range[1])
    return None  # Return None instead of 500 if age is out of all ranges

def adjust_lexile_level(current_lexile, percentage_correct):
    if percentage_correct >= 70:
        return current_lexile + 25
    elif percentage_correct <= 30:
        return max(0, current_lexile - 25)
    return current_lexile

def display_lexile_scale(current_lexile):
    scale = list(range(max(0, current_lexile - 500), current_lexile + 50, 50))
    scale_str = " ".join([f"[{level}L]" if level == current_lexile else f"{level}L" for level in scale])
    return scale_str

def evaluate_answers(questions, user_answers):
    scores = {factor: 0 for factor in EVALUATION_FACTORS}
    total_questions = len(questions)
    correct_answers = 0
    for q, answer in zip(questions, user_answers):
        factor = q["evaluation_factor"].split('. ', 1)[-1]  # Remove any numbering
        if factor not in scores:
            # Find the closest matching factor
            matching_factor = next((f for f in EVALUATION_FACTORS if f.lower() in factor.lower()), None)
            if matching_factor:
                factor = matching_factor
            else:
                continue  # Skip this question if no matching factor is found
        
        if answer == q["correct_answer"]:
            scores[factor] += 1
            correct_answers += 1
        else:
            scores[factor] -= 1
    
    # Calculate percentage of correct answers
    percentage_correct = (correct_answers / total_questions) * 100
    
    return scores, percentage_correct
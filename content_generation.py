
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import EVALUATION_FACTORS
import re

api_key = "AIzaSyDmf0d09V7jGsuN-kfZ6Di-bF0LbCyH7_I"
llm = ChatGoogleGenerativeAI(google_api_key=api_key, model="gemini-1.0-pro")

content_mcq_prompt_template = """
You are an AI assistant trained to generate educational content and multiple-choice questions (MCQs) for students.
Please generate an engaging short story of EXACTLY 200 words suitable for a {age}-year-old student on the topic of {topic}. 
The content should be at approximately a {target_lexile} Lexile level.
The story should be interesting, have a clear beginning, middle, and end, and incorporate educational elements related to the topic.

Then, create EXACTLY 10 multiple-choice questions based on this story. Each question should evaluate a different skill from the following list:
{evaluation_factors}

The questions should be challenging but appropriate for the age group and Lexile level.

Format your response EXACTLY as follows:
Content:
[Your generated story here]

Questions:
1. [Evaluation Factor]: [Question 1]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct Answer: [Correct option letter]

2. [Evaluation Factor]: [Question 2]
   A) [Option A]
   B) [Option B]
   C) [Option C]
   D) [Option D]
   Correct Answer: [Correct option letter]

[Repeat for questions 3-10]

Important: 
- Ensure that each question and option is a complete sentence. 
- Do not include any additional text or formatting.
- Do not include asterisks (**) or other markdown formatting.
- Do not include "Question X" in the question text.
- Place the Evaluation Factor before the question, separated by a colon.

Generated Content and Questions:
"""

content_mcq_prompt = PromptTemplate(
    template=content_mcq_prompt_template,
    input_variables=["age", "topic", "target_lexile", "evaluation_factors"]
)

content_mcq_chain = LLMChain(llm=llm, prompt=content_mcq_prompt)

def clean_text(text):
    # Remove any markdown formatting or extra whitespace
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_content_and_questions(result):
    # Split content and questions
    content_match = re.search(r'Content:(.*?)Questions:', result, re.DOTALL)
    if not content_match:
        return None, None

    content = clean_text(content_match.group(1))

    # Parse questions
    questions_raw = result.split("Questions:", 1)[1].strip()
    question_blocks = re.split(r'\n\s*\d+\.', questions_raw)
    questions = []

    for block in question_blocks:
        if not block.strip():
            continue

        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 6:  # We expect at least a question, 4 options, and a correct answer
            continue

        try:
            # Extract evaluation factor and question text
            first_line = lines[0]
            evaluation_factor, question_text = re.split(r':\s*', first_line, maxsplit=1)
            evaluation_factor = clean_text(evaluation_factor)
            question_text = clean_text(question_text)

            # Extract options
            options = [clean_text(line[3:]) for line in lines[1:5]]

            # Find correct answer
            correct_answer = ''
            for line in lines[5:]:
                if line.lower().startswith('correct answer:'):
                    correct_answer = line.split(':')[1].strip()
                    break

            question = {
                "text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "evaluation_factor": evaluation_factor
            }
            questions.append(question)
        except (IndexError, ValueError):
            continue  # Skip this question if parsing fails

    return content, questions

def generate_content_and_mcqs(age, topic, target_lexile):
    max_attempts = 3
    for attempt in range(max_attempts):
        result = content_mcq_chain.run(age=age, topic=topic, target_lexile=target_lexile, evaluation_factors=", ".join(EVALUATION_FACTORS))
        content, questions = parse_content_and_questions(result)

        if content and len(questions) == 10:
            return content, questions

    # If we've exhausted all attempts and still don't have valid content and questions
    return None, None
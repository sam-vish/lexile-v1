# config.py

# Evaluation factors for assessing reading skills
EVALUATION_FACTORS = [    
"Reading Comprehension", "Vocabulary", "Inference Skills", "Main Idea Identification", "Detail Identification", "Text Structure", "Context Clues", "Summarization", "Analyzing Arguments", "Making Predictions"
]

# Available topics for content generation
TOPICS = [
    "Science and Technology", "History and Culture", "Nature and Environment",
    "Sports and Fitness", "Arts and Literature", "Space and Astronomy",
    "Animals and Wildlife", "World Geography", "Famous People and Biographies",
    "Mythology and Folklore", "Inventions and Discoveries", "Music and Entertainment",
    "Food and Nutrition", "Human Body and Health", "Computers and Coding"
]

# Age to initial Lexile level mapping
AGE_TO_LEXILE = {
    range(5, 8): (200, 500),
    range(8, 10): (400, 700),
    range(10, 12): (600, 900),
    range(12, 14): (800, 1100),
    range(14, 16): (1000, 1300),
    range(16, 19): (1200, 1600)
}

# Difficulty levels
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Mapping from difficulty levels to Lexile ranges
DIFFICULTY_TO_LEXILE = {
    "Easy": (200, 600),
    "Medium": (600, 1000),
    "Hard": (1000, 1600)
}

# Supabase configuration
SUPABASE_URL= "https://mfbktreohntpbfnfyjrf.supabase.co"
SUPABASE_KEY= "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mYmt0cmVvaG50cGJmbmZ5anJmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjMxMjg3ODMsImV4cCI6MjAzODcwNDc4M30.-A-ruD-tAuWVmQAHVL0fnL7DTLYKh9_Xke0awe4AoZk"

# API configuration
API_KEY = "AIzaSyDmf0d09V7jGsuN-kfZ6Di-bF0LbCyH7_I"
MODEL_NAME = "gemini-1.0-pro"

# Content generation settings
MIN_CONTENT_WORDS = 200
NUM_QUESTIONS = 10

# Lexile adjustment settings
LEXILE_INCREASE = 25
LEXILE_DECREASE = 25
CORRECT_ANSWERS_THRESHOLD = 6

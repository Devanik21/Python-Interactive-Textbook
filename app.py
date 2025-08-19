"""
Python Interactive Textbook - Production Ready Streamlit Application

A comprehensive, industry-level educational platform for learning Python programming
with interactive features, progress tracking, and book-like user experience.

Author: AI Assistant
Version: 2.0.0
License: MIT
"""

import streamlit as st
import json
import time
import sys
import io
import logging
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from datetime import datetime


# ==================== CONFIGURATION & CONSTANTS ====================

class AppConfig:
    """Application configuration constants"""
    APP_TITLE = "Python Interactive Textbook"
    APP_ICON = "📚"
    VERSION = "2.0.0"
    MAX_CODE_EXECUTION_TIME = 5  # seconds
    MAX_CODE_LENGTH = 1000  # characters
    SESSION_TIMEOUT = 3600  # seconds
    
    # UI Constants
    CONTAINER_MAX_WIDTH = 900
    CODE_EDITOR_HEIGHT = 120
    QUIZ_TIMEOUT = 300  # seconds


class PageType(Enum):
    """Available page types"""
    COVER = "cover"
    TABLE_OF_CONTENTS = "toc"
    CHAPTER = "chapter"
    SETTINGS = "settings"
    HELP = "help"


@dataclass
class QuizData:
    """Quiz data structure"""
    question: str
    options: List[str]
    correct_index: int
    explanation: str = ""
    difficulty: str = "beginner"


@dataclass
class ChapterData:
    """Chapter data structure"""
    id: str
    title: str
    content: str
    code_example: str
    interactive_code: str
    quiz: QuizData
    prerequisites: List[str] = None
    estimated_time: int = 10  # minutes
    keywords: List[str] = None

    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []
        if self.keywords is None:
            self.keywords = []


@dataclass
class UserProgress:
    """User progress tracking"""
    completed_chapters: set
    quiz_scores: Dict[str, int]
    time_spent: Dict[str, int]  # minutes per chapter
    last_accessed: datetime
    total_session_time: int = 0
    code_executions: int = 0

    def to_dict(self) -> Dict:
        """Convert to serializable dictionary"""
        return {
            'completed_chapters': list(self.completed_chapters),
            'quiz_scores': self.quiz_scores,
            'time_spent': self.time_spent,
            'last_accessed': self.last_accessed.isoformat(),
            'total_session_time': self.total_session_time,
            'code_executions': self.code_executions
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProgress':
        """Create from dictionary"""
        return cls(
            completed_chapters=set(data.get('completed_chapters', [])),
            quiz_scores=data.get('quiz_scores', {}),
            time_spent=data.get('time_spent', {}),
            last_accessed=datetime.fromisoformat(data.get('last_accessed', datetime.now().isoformat())),
            total_session_time=data.get('total_session_time', 0),
            code_executions=data.get('code_executions', 0)
        )


# ==================== LOGGING CONFIGURATION ====================

@st.cache_resource
def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()


# ==================== DATA LAYER ====================

class ChapterRepository:
    """Repository for chapter data management"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def get_all_chapters() -> List[ChapterData]:
        """Get all chapter data with caching"""
        return [
            ChapterData(
                id="python_intro",
                title="Chapter 1: Welcome to Python",
                content="""
Welcome to the extraordinary world of Python programming! Python is more than just a programming language—it's your gateway to computational thinking and problem-solving.

Created by Guido van Rossum in 1991, Python was named after the British comedy group "Monty Python's Flying Circus," reflecting its philosophy of being both powerful and enjoyable to use. This playful spirit continues to define Python's community and approach to programming.

What makes Python revolutionary? Its syntax reads almost like natural English, making complex concepts accessible to beginners while remaining powerful enough for experts. Python powers everything from Instagram's backend to NASA's space missions, from artificial intelligence research to everyday automation scripts.

Python's philosophy, known as "The Zen of Python," emphasizes beautiful, explicit, and simple code. As you'll discover, Python isn't just about solving problems—it's about solving them elegantly.
                """,
                code_example='''# Your first Python program - a tradition in programming!
print("Hello, World!")
print("Welcome to your Python journey!")

# Comments start with # - they're notes for humans
# Python ignores comments, but they're crucial for understanding code

# Let's make it personal
print("🐍 Python is going to be your new favorite language!")

# Fun fact: This simple program contains several important concepts:
# - Function calls (print)
# - String literals ("Hello, World!")
# - Comments (these lines!)
''',
                interactive_code='# Try changing this message!\nprint("Hello, Python!")\nprint("My name is [Your Name]")',
                quiz=QuizData(
                    question="Who created the Python programming language?",
                    options=[
                        "Guido van Rossum",
                        "Dennis Ritchie", 
                        "Bjarne Stroustrup",
                        "James Gosling"
                    ],
                    correct_index=0,
                    explanation="Guido van Rossum created Python in 1991 at Centrum Wiskunde & Informatica (CWI) in the Netherlands.",
                    difficulty="beginner"
                ),
                keywords=["python", "introduction", "history", "print", "comments"]
            ),
            
            ChapterData(
                id="variables_datatypes",
                title="Chapter 2: Variables and Data Types",
                content="""
Variables are the foundation of programming—think of them as labeled containers that store information. Unlike mathematical variables that represent unknown values, programming variables are storage locations with meaningful names.

In Python, creating a variable is beautifully simple: just assign a value to a name. Python uses dynamic typing, meaning it automatically determines what type of data you're storing. This flexibility makes Python incredibly beginner-friendly while remaining powerful.

The fundamental data types in Python each serve specific purposes:

**Integers** represent whole numbers and can be arbitrarily large—Python handles big numbers gracefully. **Floats** represent decimal numbers with limitations in precision due to computer memory constraints. **Strings** are sequences of characters that can contain text, symbols, and even numbers as characters. **Booleans** represent logical values and are essential for decision-making in programs.

Understanding data types isn't just academic—different types have different capabilities and restrictions, affecting how your program behaves.
                """,
                code_example='''# Variables: labeled containers for your data
name = "Alice"              # String - text data
age = 25                    # Integer - whole numbers
height = 5.6                # Float - decimal numbers
is_student = True           # Boolean - True or False
account_balance = 1250.75   # Float - money is often decimal

# Variables can change (that's why they're called "variable"!)
age = 26  # Alice had a birthday!

# Python is smart about types
print(f"Name: {name} (type: {type(name).__name__})")
print(f"Age: {age} (type: {type(age).__name__})")
print(f"Height: {height} (type: {type(height).__name__})")
print(f"Student: {is_student} (type: {type(is_student).__name__})")

# Interesting fact: Python integers can be arbitrarily large!
big_number = 12345678901234567890
print(f"Big number: {big_number}")
''',
                interactive_code='# Create your own variables!\nfavorite_color = "blue"\nlucky_number = 7\nprint(f"My favorite color is {favorite_color}")\nprint(f"My lucky number is {lucky_number}")',
                quiz=QuizData(
                    question="Which of these creates a string variable in Python?",
                    options=[
                        'message = "Hello World"',
                        'message = Hello World',
                        'string message = "Hello World"',
                        'message = (Hello World)'
                    ],
                    correct_index=0,
                    explanation="Strings in Python must be enclosed in quotes (single or double). Python doesn't require type declarations.",
                    difficulty="beginner"
                ),
                prerequisites=["python_intro"],
                keywords=["variables", "data types", "strings", "integers", "floats", "booleans"]
            ),
            
            ChapterData(
                id="operations",
                title="Chapter 3: Operations and Expressions",
                content="""
Operations in Python go far beyond basic arithmetic—they're the building blocks for complex logic and data manipulation. Understanding operations deeply will make you a more effective programmer.

**Arithmetic operations** follow mathematical conventions with some programming-specific additions. The modulo operator (%) finds remainders and is surprisingly useful for checking if numbers are even/odd, creating cycles, and time calculations. The exponentiation operator (**) handles powers elegantly.

**String operations** reveal Python's elegance. Concatenation joins strings, repetition creates patterns, and formatting creates dynamic text. Modern Python uses f-strings for readable, efficient string formatting.

**Comparison operations** return boolean values and are essential for decision-making. They work with different data types, following intuitive rules most of the time.

**Operator precedence** determines the order of operations, just like in mathematics. Parentheses can override precedence, making your intentions clear to both Python and human readers.

Understanding these operations thoroughly will help you write more expressive and efficient code.
                """,
                code_example='''# Arithmetic operations - the foundation of computation
x, y = 15, 4  # Multiple assignment - very Pythonic!

print("=== ARITHMETIC OPERATIONS ===")
print(f"Addition: {x} + {y} = {x + y}")
print(f"Subtraction: {x} - {y} = {x - y}")
print(f"Multiplication: {x} * {y} = {x * y}")
print(f"Division: {x} / {y} = {x / y}")           # Always returns float
print(f"Floor Division: {x} // {y} = {x // y}")   # Integer division
print(f"Modulo: {x} % {y} = {x % y}")             # Remainder
print(f"Exponentiation: {x} ** {y} = {x ** y}")   # Power

print("\\n=== STRING OPERATIONS ===")
first_name = "John"
last_name = "Doe"
full_name = first_name + " " + last_name  # Concatenation
print(f"Full name: {full_name}")
print(f"Repeated: {'Hi! ' * 3}")  # String repetition
print(f"F-string magic: {first_name} is {age} years old")

print("\\n=== COMPARISON OPERATIONS ===")
print(f"{x} > {y}: {x > y}")
print(f"{x} == {y}: {x == y}")  # Equality check
print(f"'abc' < 'def': {'abc' < 'def'}")  # Lexicographic comparison
''',
                interactive_code='# Experiment with operations!\na = 10\nb = 3\nprint(f"{a} / {b} = {a / b}")\nprint(f"{a} // {b} = {a // b}")\nprint(f"{a} % {b} = {a % b}")',
                quiz=QuizData(
                    question="What does the expression 17 % 5 equal in Python?",
                    options=["3.4", "2", "3", "12"],
                    correct_index=1,
                    explanation="The modulo operator (%) returns the remainder after division. 17 ÷ 5 = 3 remainder 2, so 17 % 5 = 2.",
                    difficulty="beginner"
                ),
                prerequisites=["variables_datatypes"],
                keywords=["arithmetic", "operators", "modulo", "strings", "comparisons", "precedence"]
            ),
            
            ChapterData(
                id="lists_collections",
                title="Chapter 4: Lists and Data Collections",
                content="""
Lists are Python's most versatile data structure—dynamic arrays that can grow, shrink, and hold any type of data. They're fundamental to almost every Python program you'll write.

Unlike arrays in some languages, Python lists are incredibly flexible. They can hold mixed data types, resize automatically, and provide rich functionality through built-in methods. This flexibility comes with a small performance cost, but the productivity gain is enormous.

**List indexing** starts at 0, a convention inherited from computer memory addressing. Negative indices count from the end, providing elegant access to tail elements. **Slicing** creates new lists from portions of existing ones, using the format [start:stop:step].

**List methods** transform data efficiently. append() and extend() add elements, remove() and pop() delete them, sort() and reverse() reorder them. Understanding when to use each method will make your code more readable and efficient.

**List comprehensions**, which we'll explore later, provide a powerful way to create and transform lists in a single, readable line.

Lists are mutable, meaning you can change them after creation. This mutability is powerful but requires careful handling when lists are shared between different parts of your program.
                """,
                code_example='''# Lists: Dynamic, flexible data containers
print("=== CREATING LISTS ===")
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed_list = ["hello", 42, True, 3.14, [1, 2, 3]]  # Lists can hold anything!

print(f"Fruits: {fruits}")
print(f"Mixed list: {mixed_list}")

print("\\n=== ACCESSING ELEMENTS ===")
print(f"First fruit: {fruits[0]}")        # Index starts at 0
print(f"Last fruit: {fruits[-1]}")        # Negative index from end
print(f"Middle fruits: {fruits[1:3]}")    # Slicing [start:end]

print("\\n=== MODIFYING LISTS ===")
fruits.append("date")                      # Add to end
print(f"After append: {fruits}")

fruits.insert(1, "apricot")               # Insert at position
print(f"After insert: {fruits}")

removed = fruits.pop()                     # Remove and return last
print(f"Removed '{removed}': {fruits}")

print("\\n=== LIST OPERATIONS ===")
print(f"Length: {len(fruits)}")
print(f"Is 'apple' in list: {'apple' in fruits}")
print(f"Index of 'banana': {fruits.index('banana')}")

# List concatenation and repetition
more_fruits = ["elderberry", "fig"]
all_fruits = fruits + more_fruits
print(f"Combined: {all_fruits}")
''',
                interactive_code='# Create and manipulate your own list!\nmy_list = ["red", "green", "blue"]\nprint("Original:", my_list)\nmy_list.append("yellow")\nprint("After adding yellow:", my_list)\nprint("Second color:", my_list[1])',
                quiz=QuizData(
                    question="What is the result of [1, 2, 3, 4, 5][1:4]?",
                    options=["[1, 2, 3, 4]", "[2, 3, 4]", "[2, 3, 4, 5]", "[1, 2, 3]"],
                    correct_index=1,
                    explanation="List slicing [1:4] starts at index 1 (value 2) and goes up to but not including index 4, giving [2, 3, 4].",
                    difficulty="beginner"
                ),
                prerequisites=["operations"],
                keywords=["lists", "indexing", "slicing", "methods", "append", "pop", "mutability"]
            ),
            
            ChapterData(
                id="control_flow",
                title="Chapter 5: Control Flow and Decision Making",
                content="""
Control flow transforms your programs from simple calculators into intelligent decision-makers. This is where programming becomes truly powerful—your code can analyze data, respond to conditions, and choose different paths of execution.

**Conditional statements** mirror human decision-making. "If it's raining, take an umbrella" becomes `if weather == 'rain': bring_umbrella = True`. The elegance of Python's syntax makes these logical structures read almost like natural language.

**Boolean logic** is fundamental to control flow. Understanding how `and`, `or`, and `not` operators work, along with concepts like short-circuit evaluation, will help you write more efficient and readable conditions.

**Nested conditions** handle complex scenarios where multiple factors influence decisions. However, deeply nested conditions can become hard to read—good programmers balance functionality with readability.

**The elif ladder** provides an elegant way to handle multiple mutually exclusive conditions. It's more efficient than separate if statements because Python stops checking once a condition is True.

**Truthiness** in Python extends beyond boolean values. Empty lists, zero, and None are "falsy," while non-empty strings and non-zero numbers are "truthy." This concept enables more Pythonic code.

Mastering control flow is essential—it's the difference between programs that blindly execute instructions and programs that intelligently respond to their environment.
                """,
                code_example='''# Control Flow: Making intelligent decisions
import random

print("=== BASIC CONDITIONAL LOGIC ===")
age = 20
has_license = True

if age >= 18 and has_license:
    print("✅ You can drive!")
elif age >= 18:
    print("📝 You need to get a license first")
else:
    print("⏳ Wait until you're 18")

print("\\n=== MULTIPLE CONDITIONS (elif ladder) ===")
score = 87

if score >= 90:
    grade, message = "A", "Excellent work! 🌟"
elif score >= 80:
    grade, message = "B", "Good job! 👍"
elif score >= 70:
    grade, message = "C", "Satisfactory 📚"
elif score >= 60:
    grade, message = "D", "Needs improvement 📈"
else:
    grade, message = "F", "Please see instructor 💬"

print(f"Score: {score} → Grade: {grade}")
print(f"Feedback: {message}")

print("\\n=== BOOLEAN LOGIC AND TRUTHINESS ===")
username = "alice"
password = "secret123"
is_admin = False

# Multiple conditions with logical operators
if username and password and len(password) >= 8:
    print("✅ Login successful")
    if is_admin:
        print("🔑 Admin access granted")
else:
    print("❌ Login failed")

# Truthiness examples
empty_list = []
if empty_list:  # Empty list is "falsy"
    print("This won't print")
else:
    print("Empty list is falsy")

print("\\n=== PRACTICAL EXAMPLE: Number Analysis ===")
number = random.randint(1, 100)
print(f"Analyzing number: {number}")

if number % 2 == 0:
    print("📊 Even number")
else:
    print("📊 Odd number")

if number <= 25:
    category = "Low"
elif number <= 75:
    category = "Medium"
else:
    category = "High"

print(f"📈 Category: {category}")
''',
                interactive_code='# Decision making practice!\ntemperature = 75\n\nif temperature > 80:\n    print("Hot day! 🌞")\nelif temperature > 60:\n    print("Nice weather! 🌤️")\nelse:\n    print("Cool day! 🧥")\n\nprint(f"Temperature: {temperature}°F")',
                quiz=QuizData(
                    question="What will this code print?\\n\\n```python\\nx = 0\\nif x:\\n    print('A')\\nelse:\\n    print('B')\\n```",
                    options=["A", "B", "Nothing", "Error"],
                    correct_index=1,
                    explanation="In Python, 0 is considered 'falsy', so the condition `if x:` evaluates to False, and 'B' is printed.",
                    difficulty="beginner"
                ),
                prerequisites=["lists_collections"],
                keywords=["conditionals", "if", "elif", "else", "boolean", "logic", "truthiness"]
            )
        ]

    @staticmethod
    def get_chapter_by_id(chapter_id: str) -> Optional[ChapterData]:
        """Get specific chapter by ID"""
        chapters = ChapterRepository.get_all_chapters()
        return next((ch for ch in chapters if ch.id == chapter_id), None)

    @staticmethod
    def get_chapter_index(chapter_id: str) -> int:
        """Get chapter index by ID"""
        chapters = ChapterRepository.get_all_chapters()
        for i, chapter in enumerate(chapters):
            if chapter.id == chapter_id:
                return i
        return -1


# ==================== BUSINESS LOGIC ====================

class SecurityManager:
    """Handles code execution security and validation"""
    
    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib', 'requests',
        'pickle', 'marshal', 'shelve', '__import__', 'eval', 'exec'
    }
    
    FORBIDDEN_FUNCTIONS = {
        'open', 'input', 'raw_input', '__import__', 'reload', 'compile',
        'eval', 'exec', 'globals', 'locals', 'vars', 'dir'
    }
    
    @classmethod
    def validate_code(cls, code: str) -> tuple[bool, str]:
        """Validate code for security issues"""
        if len(code) > AppConfig.MAX_CODE_LENGTH:
            return False, f"Code too long (max {AppConfig.MAX_CODE_LENGTH} characters)"
        
        # Check for forbidden imports
        lines = code.lower().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or 'from ' in line:
                for forbidden in cls.FORBIDDEN_IMPORTS:
                    if forbidden in line:
                        return False, f"Import '{forbidden}' not allowed for security"
        
        # Check for forbidden functions
        code_lower = code.lower()
        for forbidden in cls.FORBIDDEN_FUNCTIONS:
            if forbidden + '(' in code_lower:
                return False, f"Function '{forbidden}' not allowed for security"
        
        return True, "Code validation passed"

    @classmethod
    def execute_code_safely(cls, code: str) -> tuple[bool, str]:
        """Execute code with safety measures"""
        try:
            # Validate first
            is_valid, validation_msg = cls.validate_code(code)
            if not is_valid:
                return False, validation_msg
            
            # Redirect stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            # Create restricted globals
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sorted': sorted,
                    'reversed': reversed,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'type': type,
                }
            }
            
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            # Execute with timeout simulation (basic)
            start_time = time.time()
            exec(code, restricted_globals)
            execution_time = time.time() - start_time
            
            if execution_time > AppConfig.MAX_CODE_EXECUTION_TIME:
                return False, "Code execution timed out"
            
            # Get outputs
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            
            if stderr_content:
                return False, f"Error: {stderr_content}"
            
            return True, stdout_content or "Code executed successfully (no output)"
            
        except Exception as e:
            return False, f"Execution error: {str(e)}"
        
        finally:
            # Always restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr


class ProgressManager:
    """Manages user progress and achievements"""
    
    @staticmethod
    def initialize_progress() -> UserProgress:
        """Initialize new user progress"""
        return UserProgress(
            completed_chapters=set(),
            quiz_scores={},
            time_spent={},
            last_accessed=datetime.now()
        )
    
    @staticmethod
    def is_chapter_unlocked(chapter_index: int, progress: UserProgress) -> bool:
        """Check if chapter is unlocked based on progress"""
        if chapter_index == 0:
            return True  # First chapter always unlocked
        
        chapters = ChapterRepository.get_all_chapters()
        if chapter_index >= len(chapters):
            return False
            
        # Check if previous chapter is completed
        prev_chapter = chapters[chapter_index - 1]
        return prev_chapter.id in progress.completed_chapters
    
    @staticmethod
    def complete_chapter(chapter_id: str, quiz_score: int, progress: UserProgress) -> UserProgress:
        """Mark chapter as completed with score"""
        progress.completed_chapters.add(chapter_id)
        progress.quiz_scores[chapter_id] = quiz_score
        progress.last_accessed = datetime.now()
        return progress
    
    @staticmethod
    def calculate_overall_progress(progress: UserProgress) -> float:
        """Calculate overall completion percentage"""
        total_chapters = len(ChapterRepository.get_all_chapters())
        completed = len(progress.completed_chapters)
        return (completed / total_chapters) * 100 if total_chapters > 0 else 0


# ==================== SESSION MANAGEMENT ====================

class SessionManager:
    """Manages Streamlit session state and persistence"""
    
    @staticmethod
    def initialize_session():
        """Initialize all session state variables"""
        defaults = {
            'current_page': PageType.COVER.value,
            'current_chapter_id': None,
            'user_progress': ProgressManager.initialize_progress(),
            'session_start_time': datetime.now(),
            'code_outputs': {},
            'quiz_attempts': {},
            'ui_preferences': {
                'theme': 'light',
                'font_size': 'medium'
            }
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                if key == 'user_progress':
                    st.session_state[key] = default_value
                else:
                    st.session_state[key] = default_value
    
    @staticmethod
    def navigate_to(page: PageType, chapter_id: Optional[str] = None):
        """Navigate to a specific page"""
        st.session_state.current_page = page.value
        if chapter_id:
            st.session_state.current_chapter_id = chapter_id
        st.rerun()
    
    @staticmethod
    def get_progress() -> UserProgress:
        """Get current user progress"""
        return st.session_state.user_progress
    
    @staticmethod
    def save_progress(progress: UserProgress):
        """Save user progress to session"""
        st.session_state.user_progress = progress


# ==================== UI COMPONENTS ====================

class UIComponents:
    """Reusable UI components and styling"""
    
    @staticmethod
    @st.cache_data
    def load_css() -> str:
        """Load and return CSS styles"""
        return """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Source+Code+Pro:wght@400;500;600&family=Inter:wght@300;400;500;600&display=swap');
            
            :root {
                --primary-color: #d4af37;
                --secondary-color: #ffd700;
                --accent-color: #ff6b6b;
                --background-light: #1a1a1a;
                --background-dark: #0d1117;
                --text-primary: #e6e6e6;
                --text-secondary: #b3b3b3;
                --border-color: #404040;
                --shadow-light: 0 2px 10px rgba(0,0,0,0.3);
                --shadow-medium: 0 5px 20px rgba(0,0,0,0.4);
                --shadow-heavy: 0 10px 30px rgba(0,0,0,0.5);
            }
            
            .stApp {
                background: linear-gradient(135deg, var(--background-dark) 0%, var(--background-light) 100%);
                background-attachment: fixed;
                color: var(--text-primary);
            }
            
            .main-container {
                background: var(--background-light);
                border: 2px solid var(--secondary-color);
                border-radius: 20px;
                padding: 2.5rem;
                margin: 1.5rem auto;
                max-width: 900px;
                box-shadow: var(--shadow-heavy);
                position: relative;
                font-family: 'Crimson Text', serif;
                line-height: 1.6;
                color: var(--text-primary);
            }
            
            .main-container::before {
                content: '';
                position: absolute;
                top: 10px;
                left: 10px;
                right: 10px;
                bottom: 10px;
                border: 1px solid var(--border-color);
                border-radius: 15px;
                pointer-events: none;
            }
            
            .cover-page {
                text-align: center;
                padding: 4rem 2rem;
                background: linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #333333 100%);
                color: var(--secondary-color);
                border-radius: 20px;
                margin: -2.5rem -2.5rem 2rem -2.5rem;
                position: relative;
                overflow: hidden;
            }
            
            .cover-page::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: radial-gradient(circle at 30% 20%, rgba(212, 175, 55, 0.1) 0%, transparent 50%);
                pointer-events: none;
            }
            
            .cover-title {
                font-size: clamp(2.5rem, 5vw, 4rem);
                font-weight: 600;
                margin-bottom: 1.5rem;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
                font-family: 'Crimson Text', serif;
                position: relative;
                z-index: 1;
            }
            
            .cover-subtitle {
                font-size: clamp(1.1rem, 2.5vw, 1.4rem);
                margin-bottom: 2rem;
                opacity: 0.95;
                font-style: italic;
                position: relative;
                z-index: 1;
            }
            
            .chapter-header {
                color: var(--secondary-color);
                font-size: 2.2rem;
                font-weight: 600;
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 3px solid var(--secondary-color);
                font-family: 'Crimson Text', serif;
                position: relative;
            }
            
            .chapter-header::after {
                content: '';
                position: absolute;
                bottom: -3px;
                left: 0;
                width: 60px;
                height: 3px;
                background: var(--accent-color);
            }
            
            .page-content {
                font-size: 1.15rem;
                line-height: 1.8;
                color: var(--text-primary);
                text-align: justify;
                margin-bottom: 2rem;
                font-family: 'Crimson Text', serif;
            }
            
            .page-content p {
                margin-bottom: 1.2rem;
            }
            
            .code-section {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border: 2px solid var(--secondary-color);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 2rem 0;
                box-shadow: var(--shadow-medium);
                position: relative;
            }
            
            .code-section::before {
                content: '💻 Code Example';
                position: absolute;
                top: -12px;
                left: 20px;
                background: var(--secondary-color);
                color: var(--primary-color);
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }
            
            .interactive-section {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px dashed #6c757d;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 2rem 0;
                position: relative;
            }
            
            .interactive-section::before {
                content: '🚀 Interactive Code';
                position: absolute;
                top: -12px;
                left: 20px;
                background: #007bff;
                color: white;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }
            
            .quiz-container {
                background: linear-gradient(135deg, #fff8dc 0%, #f0e68c 20%, #fff8dc 100%);
                border: 2px solid #daa520;
                border-radius: 15px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: var(--shadow-medium);
                position: relative;
            }
            
            .quiz-container::before {
                content: '🎯 Knowledge Check';
                position: absolute;
                top: -12px;
                left: 20px;
                background: #daa520;
                color: white;
                padding: 4px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
            }
            
            .quiz-question {
                color: var(--secondary-color);
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                line-height: 1.5;
            }
            
            .progress-indicator {
                background: linear-gradient(90deg, var(--secondary-color) 0%, #ffd700 100%);
                height: 12px;
                border-radius: 6px;
                margin: 1rem 0;
                box-shadow: var(--shadow-light);
                overflow: hidden;
                position: relative;
            }
            
            .progress-indicator::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
            }
            
            .bookmark {
                position: absolute;
                top: -8px;
                right: 30px;
                background: var(--accent-color);
                color: white;
                padding: 12px 18px;
                border-radius: 0 0 15px 15px;
                font-weight: 600;
                box-shadow: var(--shadow-medium);
                font-family: 'Inter', sans-serif;
                z-index: 10;
            }
            
            .toc-item {
                background: linear-gradient(135deg, var(--background-light) 0%, #2a2a2a 100%);
                border: 2px solid var(--border-color);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                color: var(--text-primary);
            }
            
            .toc-item::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
                transition: left 0.5s ease;
            }
            
            .toc-item:hover::before {
                left: 100%;
            }
            
            .toc-item:hover {
                transform: translateX(8px) translateY(-2px);
                box-shadow: var(--shadow-heavy);
                border-color: var(--secondary-color);
            }
            
            .locked-chapter {
                opacity: 0.6;
                pointer-events: none;
                background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
                border-color: #666;
            }
            
            .completed-chapter {
                background: linear-gradient(135deg, #1a3d1a 0%, #2d5a2d 100%);
                border-color: #28a745;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
            }
            
            .current-chapter {
                background: linear-gradient(135deg, #3d3d1a 0%, #5a5a2d 100%);
                border-color: #ffc107;
                border-width: 3px;
                box-shadow: 0 6px 20px rgba(255, 193, 7, 0.4);
            }
            
            .page-number {
                position: absolute;
                bottom: 20px;
                right: 30px;
                color: var(--text-secondary);
                font-style: italic;
                font-size: 0.9rem;
                font-family: 'Inter', sans-serif;
            }
            
            .nav-button {
                background: linear-gradient(135deg, var(--secondary-color) 0%, #b8860b 100%);
                border: none;
                color: var(--background-dark);
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                box-shadow: var(--shadow-light);
            }
            
            .nav-button:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-medium);
            }
            
            .nav-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .success-message {
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
                color: #155724;
                font-weight: 600;
            }
            
            .error-message {
                background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%);
                border: 2px solid #dc3545;
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
                color: #721c24;
                font-weight: 600;
            }
            
            .info-box {
                background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
                border: 2px solid #17a2b8;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                color: #0c5460;
                position: relative;
            }
            
            .info-box::before {
                content: 'ℹ️';
                position: absolute;
                top: -12px;
                left: 20px;
                background: #17a2b8;
                color: white;
                padding: 4px 8px;
                border-radius: 50%;
                font-size: 0.8rem;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .main-container {
                    margin: 1rem;
                    padding: 1.5rem;
                }
                
                .cover-page {
                    padding: 3rem 1rem;
                    margin: -1.5rem -1.5rem 1.5rem -1.5rem;
                }
                
                .chapter-header {
                    font-size: 1.8rem;
                }
                
                .page-content {
                    font-size: 1.1rem;
                    text-align: left;
                }
            }
            
            /* Animation Classes */
            .fade-in {
                animation: fadeIn 0.6s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .slide-in {
                animation: slideIn 0.5s ease-out;
            }
            
            @keyframes slideIn {
                from { transform: translateX(-30px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        </style>
        """
    
    @staticmethod
    def render_progress_bar(progress_percentage: float, show_text: bool = True) -> None:
        """Render a progress bar"""
        progress_html = f"""
        <div style="margin: 1.5rem 0;">
            {f'<h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">📊 Your Progress: {progress_percentage:.1f}%</h3>' if show_text else ''}
            <div style="background: #e9ecef; border-radius: 10px; height: 20px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
                <div class="progress-indicator" style="width: {progress_percentage}%; height: 100%; transition: width 0.8s ease;"></div>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
    
    @staticmethod
    def render_chapter_status(chapter_index: int, chapter: ChapterData, is_completed: bool, is_current: bool, is_locked: bool) -> None:
        """Render chapter status in table of contents"""
        status_icons = {
            'completed': '✅',
            'current': '📍', 
            'available': '📖',
            'locked': '🔒'
        }
        
        if is_completed:
            status = 'completed'
            css_class = 'completed-chapter'
            status_text = 'Completed!'
        elif is_current:
            status = 'current'
            css_class = 'current-chapter'
            status_text = 'Continue reading'
        elif is_locked:
            status = 'locked'
            css_class = 'locked-chapter'
            status_text = 'Complete previous chapters to unlock'
        else:
            status = 'available'
            css_class = 'toc-item'
            status_text = 'Ready to learn'
        
        chapter_html = f"""
        <div class="toc-item {css_class} fade-in" style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">{status_icons[status]}</span>
                    <strong style="color: var(--primary-color); font-size: 1.2rem;">{chapter.title}</strong>
                </div>
                <div style="margin-left: 2rem;">
                    <small style="color: var(--text-secondary); margin-right: 1rem;">
                        <i>{status_text}</i>
                    </small>
                    <small style="color: var(--text-secondary);">
                        ⏱️ Est. {chapter.estimated_time} min
                    </small>
                </div>
                {f'<div style="margin-left: 2rem; margin-top: 0.5rem;"><small style="color: var(--text-secondary);">Keywords: {", ".join(chapter.keywords)}</small></div>' if chapter.keywords else ''}
            </div>
        </div>
        """
        
        st.markdown(chapter_html, unsafe_allow_html=True)


# ==================== PAGE CONTROLLERS ====================

class CoverPageController:
    """Handles cover page logic and rendering"""
    
    @staticmethod
    def render():
        """Render the cover page"""
        st.markdown(UIComponents.load_css(), unsafe_allow_html=True)
        
        cover_html = f"""
        <div class="main-container fade-in">
            <div class="cover-page">
                <h1 class="cover-title">📚 Python Interactive Textbook</h1>
                <p class="cover-subtitle">A Magical Journey from Beginner to Pythonista</p>
                <div style="font-size: 1.15rem; margin: 2rem 0; line-height: 1.6;">
                    <p>Welcome to an extraordinary learning experience that transforms the way you discover Python programming.</p>
                    <p>This isn't just another tutorial—it's your personal guide through the world of code, complete with:</p>
                    <ul style="text-align: left; max-width: 500px; margin: 1.5rem auto;">
                        <li>📖 Interactive chapters that adapt to your pace</li>
                        <li>💻 Live code execution and experimentation</li>
                        <li>🎯 Smart quizzes that reinforce learning</li>
                        <li>📊 Progress tracking and achievements</li>
                        <li>🔖 Automatic bookmarking of your journey</li>
                    </ul>
                </div>
                <p style="font-size: 1rem; opacity: 0.9; margin-top: 2rem;">
                    Version {AppConfig.VERSION} | Crafted for curious minds
                </p>
            </div>
        </div>
        """
        
        st.markdown(cover_html, unsafe_allow_html=True)
        
        # Center the start button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Begin Your Journey", key="start_journey", use_container_width=True, type="primary"):
                logger.info("User started their learning journey")
                SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)


class TableOfContentsController:
    """Handles table of contents logic and rendering"""
    
    @staticmethod
    def render():
        """Render the table of contents"""
        st.markdown(UIComponents.load_css(), unsafe_allow_html=True)
        
        progress = SessionManager.get_progress()
        progress_percentage = ProgressManager.calculate_overall_progress(progress)
        chapters = ChapterRepository.get_all_chapters()
        
        toc_html = f"""
        <div class="main-container slide-in">
            <div class="bookmark">📑 TOC</div>
            <h1 class="chapter-header">📋 Table of Contents</h1>
            <div class="page-content">
                Welcome back to your Python journey! Your progress is automatically saved as you learn.
                Each chapter builds upon the previous one, so complete them in order for the best experience.
            </div>
        </div>
        """
        
        st.markdown(toc_html, unsafe_allow_html=True)
        
        # Progress indicator
        UIComponents.render_progress_bar(progress_percentage)
        
        # Chapter list
        for i, chapter in enumerate(chapters):
            is_completed = chapter.id in progress.completed_chapters
            is_current = st.session_state.get('current_chapter_id') == chapter.id
            is_locked = not ProgressManager.is_chapter_unlocked(i, progress)
            
            UIComponents.render_chapter_status(i, chapter, is_completed, is_current, is_locked)
            
            if not is_locked:
                if st.button(f"📖 {'Continue' if is_current else 'Read'} Chapter {i+1}", 
                           key=f"chapter_btn_{i}", use_container_width=True):
                    logger.info(f"User accessed chapter: {chapter.id}")
                    SessionManager.navigate_to(PageType.CHAPTER, chapter.id)
        
        # Statistics
        completed_count = len(progress.completed_chapters)
        if completed_count > 0:
            avg_score = sum(progress.quiz_scores.values()) / len(progress.quiz_scores) if progress.quiz_scores else 0
            total_time = sum(progress.time_spent.values()) if progress.time_spent else 0
            
            stats_html = f"""
            <div class="info-box" style="margin-top: 2rem;">
                <h4 style="margin-bottom: 1rem; color: var(--primary-color);">📈 Your Learning Statistics</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">{completed_count}</div>
                        <div style="font-size: 0.9rem;">Chapters Completed</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">{avg_score:.0f}%</div>
                        <div style="font-size: 0.9rem;">Average Quiz Score</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">{total_time}</div>
                        <div style="font-size: 0.9rem;">Minutes Studied</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">{progress.code_executions}</div>
                        <div style="font-size: 0.9rem;">Code Runs</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(stats_html, unsafe_allow_html=True)


class ChapterController:
    """Handles individual chapter logic and rendering"""
    
    @staticmethod
    def render():
        """Render current chapter"""
        st.markdown(UIComponents.load_css(), unsafe_allow_html=True)
        
        chapter_id = st.session_state.get('current_chapter_id')
        if not chapter_id:
            st.error("No chapter selected")
            return
        
        chapter = ChapterRepository.get_chapter_by_id(chapter_id)
        if not chapter:
            st.error(f"Chapter not found: {chapter_id}")
            return
        
        chapter_index = ChapterRepository.get_chapter_index(chapter_id)
        progress = SessionManager.get_progress()
        is_completed = chapter_id in progress.completed_chapters
        
        # Chapter header
        chapter_html = f"""
        <div class="main-container fade-in">
            <div class="bookmark">Ch. {chapter_index + 1}</div>
            <h1 class="chapter-header">{chapter.title}</h1>
            
            <div class="page-content">
                {chapter.content.replace('\n\n', '</p><p>').replace('\n', '<br>')}
            </div>
        </div>
        """
        
        st.markdown(chapter_html, unsafe_allow_html=True)
        
        # Code example section
        st.markdown('<div class="code-section">', unsafe_allow_html=True)
        st.code(chapter.code_example, language='python')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Interactive code section
        ChapterController._render_interactive_section(chapter, chapter_index)
        
        # Quiz section
        ChapterController._render_quiz_section(chapter, chapter_id, is_completed)
        
        # Navigation
        ChapterController._render_navigation(chapter_index, is_completed)
        
        # Page number
        total_chapters = len(ChapterRepository.get_all_chapters())
        st.markdown(f'<div class="page-number">Page {chapter_index + 1} of {total_chapters}</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_interactive_section(chapter: ChapterData, chapter_index: int):
        """Render interactive code section"""
        st.markdown('<div class="interactive-section">', unsafe_allow_html=True)
        st.markdown("**Modify the code below and click 'Run' to see the results:**")
        
        # Code editor
        user_code = st.text_area(
            "Python Code:", 
            value=chapter.interactive_code,
            height=AppConfig.CODE_EDITOR_HEIGHT,
            key=f"code_editor_{chapter_index}",
            help="Write your Python code here. Click 'Run Code' to execute it."
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("▶️ Run Code", key=f"run_code_{chapter_index}", type="primary"):
                success, output = SecurityManager.execute_code_safely(user_code)
                
                # Update statistics
                progress = SessionManager.get_progress()
                progress.code_executions += 1
                SessionManager.save_progress(progress)
                
                if success:
                    st.success("Code executed successfully!")
                    st.code(output, language='text')
                else:
                    st.error("Execution failed!")
                    st.code(output, language='text')
        
        with col2:
            if st.button("🔄 Reset Code", key=f"reset_code_{chapter_index}"):
                st.session_state[f"code_editor_{chapter_index}"] = chapter.interactive_code
                st.rerun()
        
        with col3:
            if st.button("📋 Copy Code", key=f"copy_code_{chapter_index}"):
                st.code(user_code, language='python')
                st.info("Code displayed above for copying")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def _render_quiz_section(chapter: ChapterData, chapter_id: str, is_completed: bool):
        """Render quiz section"""
        quiz_html = f"""
        <div class="quiz-container">
            <div class="quiz-question">{chapter.quiz.question}</div>
        </div>
        """
        st.markdown(quiz_html, unsafe_allow_html=True)
        
        # Quiz options
        selected_option = st.radio(
            "Choose your answer:",
            chapter.quiz.options,
            key=f"quiz_{chapter_id}",
            help="Select the best answer and click 'Check Answer' to proceed."
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("✅ Check Answer", key=f"check_answer_{chapter_id}", type="primary"):
                correct_answer = chapter.quiz.options[chapter.quiz.correct_index]
                is_correct = selected_option == correct_answer
                
                if is_correct:
                    st.success("🎉 Excellent! That's the correct answer!")
                    if chapter.quiz.explanation:
                        st.info(f"💡 **Explanation:** {chapter.quiz.explanation}")
                    
                    # Mark chapter as completed
                    progress = SessionManager.get_progress()
                    progress = ProgressManager.complete_chapter(chapter_id, 100, progress)
                    SessionManager.save_progress(progress)
                    
                    st.balloons()
                    logger.info(f"User completed chapter: {chapter_id}")
                    
                else:
                    st.error(f"❌ Not quite right. The correct answer is: **{correct_answer}**")
                    if chapter.quiz.explanation:
                        st.info(f"💡 **Explanation:** {chapter.quiz.explanation}")
        
        with col2:
            if st.button("💡 Hint", key=f"hint_{chapter_id}"):
                # Provide a hint by highlighting key concepts
                st.info("💭 **Hint:** Review the key concepts in the chapter content above. The answer relates to the main topic discussed.")
    
    @staticmethod
    def _render_navigation(chapter_index: int, is_completed: bool):
        """Render navigation buttons"""
        total_chapters = len(ChapterRepository.get_all_chapters())
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("📋 Contents", key="nav_toc"):
                SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)
        
        with col2:
            if chapter_index > 0:
                prev_chapter = ChapterRepository.get_all_chapters()[chapter_index - 1]
                if st.button("⬅️ Previous", key="nav_prev"):
                    SessionManager.navigate_to(PageType.CHAPTER, prev_chapter.id)
        
        with col3:
            if chapter_index < total_chapters - 1:
                next_chapter = ChapterRepository.get_all_chapters()[chapter_index + 1]
                if is_completed:
                    if st.button("➡️ Next", key="nav_next"):
                        SessionManager.navigate_to(PageType.CHAPTER, next_chapter.id)
                else:
                    st.button("🔒 Complete Quiz", disabled=True, help="Complete the quiz to unlock the next chapter")
        
        with col4:
            if st.button("🏠 Home", key="nav_home"):
                SessionManager.navigate_to(PageType.COVER)


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    # Page configuration
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://docs.python.org/',
            'Report a bug': None,
            'About': f"Python Interactive Textbook v{AppConfig.VERSION} - Learn Python through an immersive, book-like experience."
        }
    )
    
    # Initialize session
    SessionManager.initialize_session()
    
    # Sidebar for quick navigation and settings
    with st.sidebar:
        st.title(f"{AppConfig.APP_ICON} Quick Navigation")
        
        # Navigation buttons
        if st.button("🏠 Cover Page", use_container_width=True):
            SessionManager.navigate_to(PageType.COVER)
        
        if st.button("📋 Contents", use_container_width=True):
            SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)
        
        st.divider()
        
        # Progress overview
        progress = SessionManager.get_progress()
        progress_percentage = ProgressManager.calculate_overall_progress(progress)
        
        st.markdown("### 📊 Progress")
        st.progress(progress_percentage / 100)
        st.write(f"**{progress_percentage:.1f}% Complete**")
        st.write(f"📚 {len(progress.completed_chapters)} chapters finished")
        
        if progress.completed_chapters:
            st.markdown("**✅ Completed:**")
            chapters = ChapterRepository.get_all_chapters()
            for chapter in chapters:
                if chapter.id in progress.completed_chapters:
                    chapter_index = ChapterRepository.get_chapter_index(chapter.id)
                    st.write(f"• Chapter {chapter_index + 1}")
        
        st.divider()
        
        # Session info
        if progress.code_executions > 0:
            st.markdown("### 📈 Session Stats")
            st.write(f"💻 Code executions: {progress.code_executions}")
            session_time = (datetime.now() - st.session_state.session_start_time).seconds // 60
            st.write(f"⏱️ Session time: {session_time} min")
        
        st.divider()
        
        # Help section
        st.markdown("### ❓ Need Help?")
        st.markdown("""
        - 🐍 [Python.org](https://python.org)
        - 📖 [Python Tutorial](https://docs.python.org/tutorial/)
        - 💬 [Python Community](https://python.org/community/)
        """)
        
        # Reset progress (for testing/demo)
        st.divider()
        if st.button("🔄 Reset Progress", help="Clear all progress and start over"):
            if st.button("⚠️ Confirm Reset", type="secondary"):
                st.session_state.user_progress = ProgressManager.initialize_progress()
                st.session_state.current_page = PageType.COVER.value
                st.session_state.current_chapter_id = None
                st.rerun()
    
    # Main content routing
    try:
        current_page = PageType(st.session_state.current_page)
        
        if current_page == PageType.COVER:
            CoverPageController.render()
        elif current_page == PageType.TABLE_OF_CONTENTS:
            TableOfContentsController.render()
        elif current_page == PageType.CHAPTER:
            ChapterController.render()
        else:
            st.error(f"Unknown page: {current_page}")
            
    except ValueError as e:
        logger.error(f"Invalid page type: {st.session_state.current_page}")
        st.error("Navigation error occurred. Returning to cover page.")
        SessionManager.navigate_to(PageType.COVER)
    
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        logger.error(traceback.format_exc())
        
        st.error("An unexpected error occurred. Please refresh the page.")
        st.code(f"Error details: {str(e)}", language='text')
        
        # Provide recovery options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Go to Cover Page"):
                SessionManager.navigate_to(PageType.COVER)
        with col2:
            if st.button("📋 Go to Contents"):
                SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)


# ==================== APPLICATION ENTRY POINT ====================

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Critical application error: {str(e)}")
        st.code(traceback.format_exc(), language='text')
        logger.critical(f"Critical error: {str(e)}")
        logger.critical(traceback.format_exc())

"""
Python Interactive Textbook - Production Ready Streamlit Application

A comprehensive, industry-level educational platform for learning Python programming
with interactive features, progress tracking, and book-like user experience.

Author: AI Assistant
Version: 2.2.0
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
import re


# ==================== CONFIGURATION & CONSTANTS ====================

class AppConfig:
    """Application configuration constants"""
    APP_TITLE = "Python Interactive Textbook"
    APP_ICON = "📚"
    VERSION = "2.2.0"
    MAX_CODE_EXECUTION_TIME = 5  # seconds
    MAX_CODE_LENGTH = 2000  # characters
    SESSION_TIMEOUT = 3600  # seconds

    # UI Constants
    CONTAINER_MAX_WIDTH = 900
    CODE_EDITOR_HEIGHT = 150
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
            # Chapter 1
            ChapterData(
                id="python_intro",
                title="Chapter 1: Introduction to Python",
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
''',
                interactive_code='# Try changing this message!\nprint("Hello, Python!")',
                quiz=QuizData(
                    question="Who created the Python programming language?",
                    options=["Guido van Rossum", "Dennis Ritchie", "Bjarne Stroustrup", "James Gosling"],
                    correct_index=0,
                    explanation="Guido van Rossum created Python in 1991.",
                    difficulty="beginner"
                ),
                keywords=["python", "introduction", "history", "print", "comments"]
            ),
            # Chapter 2
            ChapterData(
                id="variables_datatypes",
                title="Chapter 2: Variables & Data Types",
                content="""
Variables are the foundation of programming—think of them as labeled containers that store information. In Python, creating a variable is beautifully simple: just assign a value to a name. Python uses dynamic typing, meaning it automatically determines what type of data you're storing.

The fundamental data types in Python are:
- **Integers (`int`)**: Whole numbers (e.g., 10, -5, 0).
- **Floats (`float`)**: Decimal numbers (e.g., 3.14, -0.01).
- **Strings (`str`)**: Sequences of characters (e.g., "hello", 'Python').
- **Booleans (`bool`)**: Logical values, either `True` or `False`.
                """,
                code_example='''# Variables: labeled containers for your data
name = "Alice"              # String
age = 25                    # Integer
height = 5.6                # Float
is_student = True           # Boolean

# Python is smart about types
print(f"Name: {name} (type: {type(name).__name__})")
print(f"Age: {age} (type: {type(age).__name__})")
''',
                interactive_code='# Create your own variables!\nfavorite_food = "pizza"\nlucky_number = 7\nprint(f"My favorite food is {favorite_food}")',
                quiz=QuizData(
                    question="Which data type would you use to store the value `True`?",
                    options=["Integer", "String", "Boolean", "Float"],
                    correct_index=2,
                    explanation="The `bool` (Boolean) data type is used for `True` and `False` values.",
                    difficulty="beginner"
                ),
                prerequisites=["python_intro"],
                keywords=["variables", "data types", "string", "integer", "float", "boolean"]
            ),
            # Chapter 3
            ChapterData(
                id="operators_expressions",
                title="Chapter 3: Operators & Expressions",
                content="""
Operators are special symbols in Python that carry out arithmetic or logical computation. The value that the operator operates on is called the operand.

- **Arithmetic Operators**: `+`, `-`, `*`, `/`, `%` (modulo), `**` (exponent), `//` (floor division).
- **Comparison Operators**: `==` (equal to), `!=` (not equal to), `>`, `<`, `>=`, `<=`.
- **Logical Operators**: `and`, `or`, `not`.

An expression is a combination of values, variables, and operators. A simple expression can be `2 + 3`. An expression is evaluated as per the precedence of operators.
                """,
                code_example='''# Arithmetic operations
x, y = 15, 4
print(f"Addition: {x + y}")
print(f"Modulo (remainder): {x % y}")
print(f"Exponent: {2 ** 3}") # 2*2*2

# Comparison operations
print(f"Is x greater than y? {x > y}")

# Logical operations
is_sunny = True
is_warm = True
print(f"Go to the beach? {is_sunny and is_warm}")
''',
                interactive_code='# Experiment with operations!\na = 10\nb = 3\nprint(f"Floor Division: {a // b}") # Division that results into whole number adjusted to the left in the number line\nprint(f"Regular Division: {a / b}")',
                quiz=QuizData(
                    question="What is the result of the expression `17 % 5`?",
                    options=["3.4", "2", "3", "12"],
                    correct_index=1,
                    explanation="The modulo operator (%) returns the remainder of a division. 17 divided by 5 is 3 with a remainder of 2.",
                    difficulty="beginner"
                ),
                prerequisites=["variables_datatypes"],
                keywords=["operators", "expressions", "arithmetic", "comparison", "logical"]
            ),
            # Chapter 4
            ChapterData(
                id="control_flow",
                title="Chapter 4: Control Flow (if, else, loops)",
                content="""
Control flow is the order in which the program's code executes. The control flow of a Python program is regulated by conditional statements, loops, and function calls.

- **`if`, `elif`, `else`**: These statements are used for decision making. An `if` statement is followed by one or more optional `elif` (else if) statements and a final optional `else` statement.

- **`for` loop**: Used for iterating over a sequence (that is either a list, a tuple, a dictionary, a set, or a string).

- **`while` loop**: Repeats a statement or group of statements while a given condition is TRUE. It tests the condition before executing the loop body.
                """,
                code_example='''# if/elif/else statement
age = 20
if age < 18:
    print("You are a minor.")
elif age >= 18 and age < 65:
    print("You are an adult.")
else:
    print("You are a senior citizen.")

# for loop
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}s")

# while loop
count = 0
while count < 5:
    print(f"Count is: {count}")
    count += 1
''',
                interactive_code='# Write a loop that prints numbers from 1 to 10\nfor i in range(1, 11):\n    print(i)',
                quiz=QuizData(
                    question="Which loop is best suited for iterating through a list of items?",
                    options=["if loop", "while loop", "for loop", "else loop"],
                    correct_index=2,
                    explanation="The `for` loop is designed specifically for iterating over sequences like lists.",
                    difficulty="beginner"
                ),
                prerequisites=["operators_expressions"],
                keywords=["control flow", "if", "elif", "else", "for loop", "while loop"]
            ),
            # Chapter 5
            ChapterData(
                id="functions",
                title="Chapter 5: Functions",
                content="""
A function is a block of organized, reusable code that is used to perform a single, related action. Functions provide better modularity for your application and a high degree of code reusing.

You can define functions to provide the required functionality. Here are simple rules to define a function in Python:
- Function blocks begin with the keyword `def` followed by the function name and parentheses `()`.
- Any input parameters or arguments should be placed within these parentheses.
- The code block within every function starts with a colon `:` and is indented.
- The statement `return [expression]` exits a function, optionally passing back an expression to the caller.
                """,
                code_example='''# A simple function to greet a person
def greet(name):
    """This function greets the person passed in as a parameter"""
    print(f"Hello, {name}! Good morning!")

# Calling the function
greet("Alice")

# A function that returns a value
def add_numbers(x, y):
    return x + y

result = add_numbers(5, 3)
print(f"The sum is: {result}")
''',
                interactive_code='# Write a function that multiplies two numbers\ndef multiply(a, b):\n    return a * b\n\nproduct = multiply(4, 7)\nprint(f"4 * 7 = {product}")',
                quiz=QuizData(
                    question="What keyword is used to define a function in Python?",
                    options=["func", "function", "define", "def"],
                    correct_index=3,
                    explanation="The `def` keyword is used to start a function definition.",
                    difficulty="beginner"
                ),
                prerequisites=["control_flow"],
                keywords=["functions", "def", "return", "arguments", "parameters"]
            ),
            # Chapter 6
            ChapterData(
                id="data_structures",
                title="Chapter 6: Data Structures",
                content="""
Python includes several built-in data structures that are used to store collections of data.

- **Lists**: A collection which is ordered and changeable. Allows duplicate members. `my_list = [1, "a", 3.14]`
- **Tuples**: A collection which is ordered and unchangeable. Allows duplicate members. `my_tuple = (1, "a", 3.14)`
- **Dictionaries**: A collection which is unordered, changeable and indexed. No duplicate keys. `my_dict = {"key": "value", "age": 25}`
- **Sets**: A collection which is unordered and unindexed. No duplicate members. `my_set = {1, 2, 3}`
                """,
                code_example='''# List example
fruits = ["apple", "banana", "cherry"]
fruits.append("orange")
print(f"List of fruits: {fruits}")
print(f"First fruit: {fruits[0]}")

# Tuple example
coordinates = (10.0, 20.0)
print(f"Coordinates: {coordinates}")

# Dictionary example
person = {"name": "Bob", "age": 30}
person["city"] = "New York"
print(f"Person's age: {person['age']}")

# Set example
unique_numbers = {1, 2, 3, 2, 1}
print(f"Unique numbers: {unique_numbers}")
''',
                interactive_code='# Create a dictionary for a car\ncar = {\n    "brand": "Tesla",\n    "model": "Model S",\n    "year": 2022\n}\nprint(f"Car model: {car[\'model\']}")',
                quiz=QuizData(
                    question="Which data structure does not allow duplicate items?",
                    options=["List", "Tuple", "Dictionary", "Set"],
                    correct_index=3,
                    explanation="Sets are collections of unique items. Duplicates are automatically removed.",
                    difficulty="beginner"
                ),
                prerequisites=["functions"],
                keywords=["data structures", "lists", "tuples", "dictionaries", "sets"]
            ),
            # Chapter 7
            ChapterData(
                id="strings_regex",
                title="Chapter 7: Strings & Regex",
                content="""
Strings are sequences of characters and are one of the most commonly used data types. Python provides a rich set of methods to manipulate strings, such as slicing, splitting, joining, and changing case.

**Regular Expressions (Regex)** are a powerful tool for matching patterns in text. Python's `re` module provides support for regular expressions. You can use regex to find, replace, and validate complex string patterns, making it essential for tasks like data cleaning and web scraping.
                """,
                code_example='''import re

# String manipulation
my_string = "Hello, Python World!"
print(f"Uppercase: {my_string.upper()}")
print(f"Split into words: {my_string.split(',')}")
print(f"Does it start with Hello? {my_string.startswith('Hello')}")

# Regular Expression example: Find all numbers in a string
text = "My phone number is 123-456-7890."
phone_pattern = r'\\d{3}-\\d{3}-\\d{4}'
match = re.search(phone_pattern, text)
if match:
    print(f"Phone number found: {match.group()}")
''',
                interactive_code='import re\n# Find all words that start with "P" in a sentence\nsentence = "Python programming is powerful and popular."\npattern = r\'\\b[P]\\w+\'\nmatches = re.findall(pattern, sentence, re.IGNORECASE)\nprint(f"Words starting with P: {matches}")',
                quiz=QuizData(
                    question="Which module in Python is used for regular expressions?",
                    options=["regex", "string", "re", "pattern"],
                    correct_index=2,
                    explanation="The `re` module provides all the necessary functions for working with regular expressions.",
                    difficulty="intermediate"
                ),
                prerequisites=["data_structures"],
                keywords=["string manipulation", "regex", "regular expressions", "re module", "pattern matching"]
            ),
            # Chapter 8
            ChapterData(
                id="modules_packages",
                title="Chapter 8: Modules & Packages",
                content="""
A **module** is a file containing Python definitions and statements. The file name is the module name with the suffix `.py` appended. Modules allow you to logically organize your Python code.

A **package** is a way of structuring Python’s module namespace by using "dotted module names". A package is a directory of Python modules containing an additional `__init__.py` file.

Using modules and packages helps in breaking down large programs into smaller, manageable, and organized files. It also promotes code reusability. Python has a vast standard library of modules you can import, like `math`, `random`, and `datetime`.
                """,
                code_example='''# Import the entire math module
import math
print(f"The value of Pi is: {math.pi}")
print(f"The square root of 16 is: {math.sqrt(16)}")

# Import a specific function from a module
from random import randint
random_number = randint(1, 10)
print(f"A random number between 1 and 10: {random_number}")

# You can also alias modules
import datetime as dt
current_time = dt.datetime.now()
print(f"Current date and time: {current_time}")
''',
                interactive_code='# Import the `platform` module to find your OS\nimport platform\nprint(f"Your operating system is: {platform.system()}")',
                quiz=QuizData(
                    question="What is the purpose of the `import` statement?",
                    options=["To export code to another file", "To make code from one module available in another", "To install a new package", "To create a new module"],
                    correct_index=1,
                    explanation="The `import` statement is used to bring modules or specific functions/classes from modules into the current scope.",
                    difficulty="beginner"
                ),
                prerequisites=["functions"],
                keywords=["modules", "packages", "import", "from", "standard library"]
            ),
            # Chapter 9
            ChapterData(
                id="file_handling",
                title="Chapter 9: File Handling",
                content="""
File handling is an important part of any web application. Python has several functions for creating, reading, updating, and deleting files.

The key function for working with files in Python is the `open()` function. The `open()` function takes two parameters; filename, and mode. There are four different methods (modes) for opening a file:
- `"r"` - Read - Default value. Opens a file for reading, error if the file does not exist.
- `"a"` - Append - Opens a file for appending, creates the file if it does not exist.
- `"w"` - Write - Opens a file for writing, creates the file if it does not exist.
- `"x"` - Create - Creates the specified file, returns an error if the file exists.

It's best practice to use the `with` statement, as it automatically closes the file for you.
                """,
                code_example='''# Writing to a file
with open("my_file.txt", "w") as f:
    f.write("Hello, File World!\\n")
    f.write("This is a new line.")

# Reading from a file
with open("my_file.txt", "r") as f:
    content = f.read()
    print("File Content:")
    print(content)

# Appending to a file
with open("my_file.txt", "a") as f:
    f.write("\\nThis line is appended.")

# Reading again to see the change
with open("my_file.txt", "r") as f:
    print("\\nAppended File Content:")
    print(f.read())
''',
                interactive_code='# Create a file and write your name to it\nmy_name = "Alex"\nwith open("name.txt", "w") as f:\n    f.write(my_name)\n\nwith open("name.txt", "r") as f:\n    print(f.read())',
                quiz=QuizData(
                    question="Which mode is used to open a file for writing, creating it if it doesn't exist?",
                    options=["r", "a", "w", "x"],
                    correct_index=2,
                    explanation="The 'w' mode is for writing. It will create the file if it does not exist, and overwrite it if it does.",
                    difficulty="beginner"
                ),
                prerequisites=["modules_packages"],
                keywords=["file handling", "open", "read", "write", "append", "with statement"]
            ),
            # Chapter 10
            ChapterData(
                id="error_handling",
                title="Chapter 10: Error Handling & Exceptions",
                content="""
Errors are problems in a program that the program cannot recover from. An **exception** is an event, which occurs during the execution of a program, that disrupts the normal flow of the program's instructions.

In Python, exceptions are handled using `try`, `except`, `else`, and `finally` blocks.
- **`try`**: The code that might raise an exception is placed in the `try` block.
- **`except`**: If an exception occurs, the code in the `try` block is skipped, and the code in the `except` block is executed.
- **`else`**: The code in the `else` block is executed if there is no exception.
- **`finally`**: The `finally` block is always executed, whether an exception occurred or not. This is often used for cleanup actions.
                """,
                code_example='''# A simple try-except block
try:
    numerator = 10
    denominator = 0
    result = numerator / denominator
    print(result)
except ZeroDivisionError:
    print("Error: Cannot divide by zero!")

# Using else and finally
try:
    num = int(input("Enter a number: "))
except ValueError:
    print("That's not a valid number!")
else:
    print(f"You entered the number {num}")
finally:
    print("Execution finished.")
''',
                interactive_code='numbers = [1, 2, 3]\ntry:\n    print(numbers[5])\nexcept IndexError:\n    print("Error: That index does not exist!")',
                quiz=QuizData(
                    question="What is the purpose of the `finally` block in a try-except statement?",
                    options=["To handle a specific error", "To run code only if no errors occur", "To run code regardless of whether an error occurred", "To raise a new error"],
                    correct_index=2,
                    explanation="The `finally` block is always executed, making it ideal for cleanup operations like closing files.",
                    difficulty="intermediate"
                ),
                prerequisites=["file_handling"],
                keywords=["error handling", "exceptions", "try", "except", "else", "finally"]
            ),
            # Chapter 11
            ChapterData(
                id="oop",
                title="Chapter 11: OOP in Python",
                content="""
**Object-Oriented Programming (OOP)** is a programming paradigm based on the concept of "objects", which can contain data in the form of fields (often known as attributes or properties), and code, in the form of procedures (often known as methods).

Key concepts of OOP include:
- **Class**: A blueprint for creating objects.
- **Object**: An instance of a class.
- **Inheritance**: A way to form new classes using classes that have already been defined.
- **Encapsulation**: Bundling the data and the methods that work on that data within one unit.
- **Polymorphism**: The ability of an object to take on many forms.
                """,
                code_example='''# Define a class called Dog
class Dog:
    # Class attribute
    species = "Canis familiaris"

    # Initializer / Instance attributes
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # instance method
    def description(self):
        return f"{self.name} is {self.age} years old"

    # instance method
    def speak(self, sound):
        return f"{self.name} says {sound}"

# Create an object (instance) of the Dog class
my_dog = Dog("Buddy", 5)

# Access attributes and call methods
print(my_dog.description())
print(my_dog.speak("Woof Woof"))
print(f"{my_dog.name} is a {my_dog.species}.")
''',
                interactive_code='class Car:\n    def __init__(self, brand, model):\n        self.brand = brand\n        self.model = model\n\n    def display_info(self):\n        return f"This is a {self.brand} {self.model}."\n\nmy_car = Car("Toyota", "Corolla")\nprint(my_car.display_info())',
                quiz=QuizData(
                    question="What is a 'class' in the context of OOP?",
                    options=["An instance of an object", "A blueprint for creating objects", "A function inside an object", "A variable belonging to an object"],
                    correct_index=1,
                    explanation="A class is a template or blueprint from which objects are created.",
                    difficulty="intermediate"
                ),
                prerequisites=["error_handling"],
                keywords=["OOP", "class", "object", "inheritance", "encapsulation", "polymorphism"]
            ),
            # Chapter 12
            ChapterData(
                id="decorators_generators",
                title="Chapter 12: Decorators & Generators",
                content="""
**Decorators** are a very powerful and useful tool in Python since it allows programmers to modify the behavior of a function or class. Decorators allow us to wrap another function in order to extend the behavior of the wrapped function, without permanently modifying it.

**Generators** are a simple and powerful tool for creating iterators. They are written like regular functions but use the `yield` statement whenever they want to return data. Each time `next()` is called on it, the generator resumes where it left off. This allows for creating large sequences without storing them all in memory.
                """,
                code_example='''# Decorator Example
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_whee():
    print("Whee!")

say_whee()

# Generator Example
def my_generator(n):
    for i in range(n):
        yield i * i # yield makes this a generator

# Iterate over the generator
for num in my_generator(5):
    print(num)
''',
                interactive_code='# A generator for the Fibonacci sequence\ndef fibonacci(limit):\n    a, b = 0, 1\n    while a < limit:\n        yield a\n        a, b = b, a + b\n\nfor num in fibonacci(100):\n    print(num)',
                quiz=QuizData(
                    question="What keyword is used in a generator function to return a value?",
                    options=["return", "generate", "yield", "next"],
                    correct_index=2,
                    explanation="The `yield` keyword is used in generator functions. It pauses the function's execution and returns a value, ready to resume from the same point later.",
                    difficulty="advanced"
                ),
                prerequisites=["oop"],
                keywords=["decorators", "generators", "yield", "iterators"]
            ),
            # Chapter 13
            ChapterData(
                id="itertools_functools_collections",
                title="Chapter 13: Itertools, Functools, Collections",
                content="""
Python's standard library includes powerful modules for advanced data handling and functional programming.

- **`itertools`**: This module contains functions for creating and using iterators for efficient looping. It includes tools for creating combinations, permutations, and infinite sequences.

- **`functools`**: This module is for higher-order functions: functions that act on or return other functions. `functools.wraps` is essential for writing good decorators.

- **`collections`**: This module provides alternatives to Python's general purpose built-in containers like `dict`, `list`, `set`, and `tuple`. It includes `namedtuple()`, `deque`, `Counter`, `OrderedDict`, and `defaultdict`.
                """,
                code_example='''import itertools
from collections import Counter
from functools import reduce

# itertools example: combinations
letters = ['a', 'b', 'c']
combs = itertools.combinations(letters, 2)
print(f"Combinations of 2: {list(combs)}")

# collections example: Counter
word = "mississippi"
counts = Counter(word)
print(f"Letter counts: {counts}")
print(f"Most common letter: {counts.most_common(1)}")

# functools example: reduce
numbers = [1, 2, 3, 4]
product = reduce(lambda x, y: x * y, numbers)
print(f"Product of numbers: {product}")
''',
                interactive_code='from collections import defaultdict\n\n# Use defaultdict to count items in a list\ns = [(\'yellow\', 1), (\'blue\', 2), (\'yellow\', 3), (\'blue\', 4), (\'red\', 1)]\nd = defaultdict(list)\nfor k, v in s:\n    d[k].append(v)\n\nprint(d.items())',
                quiz=QuizData(
                    question="Which `collections` object is best for counting hashable objects?",
                    options=["defaultdict", "deque", "Counter", "namedtuple"],
                    correct_index=2,
                    explanation="`Counter` is a dictionary subclass specifically designed for counting objects.",
                    difficulty="intermediate"
                ),
                prerequisites=["decorators_generators"],
                keywords=["itertools", "functools", "collections", "Counter", "defaultdict", "reduce"]
            ),
            # Chapter 14
            ChapterData(
                id="virtual_env_pip",
                title="Chapter 14: Virtual Environments & PIP",
                content="""
A **virtual environment** is a self-contained directory tree that contains a Python installation for a particular version of Python, plus a number of additional packages. This allows you to work on multiple projects with different dependencies without conflicts. The standard tool for creating virtual environments is `venv`.

**PIP** is the package installer for Python. You can use pip to install packages from the Python Package Index (PyPI). It is the standard tool for managing third-party libraries.

Common commands:
- `python -m venv myenv` (Create a virtual environment named 'myenv')
- `source myenv/bin/activate` (Activate on Mac/Linux)
- `myenv\\Scripts\\activate` (Activate on Windows)
- `pip install <package_name>` (Install a package)
- `pip freeze > requirements.txt` (Save installed packages to a file)
- `pip install -r requirements.txt` (Install packages from a file)
                """,
                code_example='''# These commands are run in your terminal, not in a Python script.

# 1. Create a virtual environment
# python3 -m venv project_env

# 2. Activate it
# On macOS/Linux:
# source project_env/bin/activate
# On Windows:
# .\\project_env\\Scripts\\activate

# 3. Install a package
# pip install requests

# 4. Check installed packages
# pip list

# 5. Save dependencies to a file
# pip freeze > requirements.txt

# 6. Deactivate the environment
# deactivate
''',
                interactive_code='# This is a conceptual chapter.\n# The code shows how you would check for a package.\ntry:\n    import numpy\n    print("NumPy is installed!")\nexcept ImportError:\n    print("NumPy is not installed. Run: pip install numpy")\n',
                quiz=QuizData(
                    question="What is the primary purpose of a virtual environment?",
                    options=["To make Python run faster", "To isolate project dependencies", "To write Python code online", "To automatically install all packages"],
                    correct_index=1,
                    explanation="Virtual environments create isolated spaces for projects, so each project can have its own set of dependencies that won't interfere with others.",
                    difficulty="beginner"
                ),
                prerequisites=["modules_packages"],
                keywords=["virtual environment", "venv", "pip", "pypi", "dependencies", "requirements.txt"]
            ),
            # Chapter 15
            ChapterData(
                id="popular_libraries",
                title="Chapter 15: Popular Libraries Basics",
                content="""
Python's power is greatly extended by its vast ecosystem of third-party libraries. Here are a few essentials for data science and visualization:

- **NumPy**: The fundamental package for scientific computing with Python. It provides a high-performance multidimensional array object, and tools for working with these arrays.

- **Pandas**: A fast, powerful, flexible and easy to use open source data analysis and manipulation tool. It's built on top of NumPy and provides data structures like Series and DataFrame.

- **Matplotlib**: A comprehensive library for creating static, animated, and interactive visualizations in Python. It allows you to create plots, histograms, bar charts, and much more.
                """,
                code_example='''# You need to install these libraries first:
# pip install numpy pandas matplotlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# NumPy: Create an array
a = np.array([1, 2, 3, 4, 5])
print(f"NumPy array mean: {a.mean()}")

# Pandas: Create a DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data)
print("\\nPandas DataFrame:")
print(df)
print(f"\\nAverage age: {df['Age'].mean()}")

# Matplotlib: Create a simple plot
# (Plotting does not work in this simple execution environment,
# but this is how you would write the code)
# x = [1, 2, 3, 4]
# y = [10, 20, 25, 30]
# plt.plot(x, y)
# plt.title("Simple Plot")
# plt.show()
print("\\nMatplotlib code is ready to generate a plot.")
''',
                interactive_code='import pandas as pd\n\ndata = {\n    "Product": ["Apples", "Bananas", "Cherries"],\n    "Price": [1.2, 0.5, 2.5]\n}\ndf = pd.DataFrame(data)\nprint(df)',
                quiz=QuizData(
                    question="Which library is primarily used for data analysis and provides the DataFrame object?",
                    options=["NumPy", "Matplotlib", "Pandas", "SciPy"],
                    correct_index=2,
                    explanation="Pandas is the go-to library for data manipulation and analysis in Python, with the DataFrame being its central data structure.",
                    difficulty="intermediate"
                ),
                prerequisites=["virtual_env_pip"],
                keywords=["numpy", "pandas", "matplotlib", "data science", "visualization"]
            ),
            # Chapter 16
            ChapterData(
                id="intermediate_topics",
                title="Chapter 16: Intermediate Topics",
                content="""
Once you're comfortable with the basics, you can explore more advanced concepts to write more efficient and powerful programs.

- **Threading**: Allows you to run multiple threads (smaller units of a process) concurrently. This is useful for I/O-bound tasks, like making multiple web requests at the same time, where the program would otherwise spend time waiting.

- **Multiprocessing**: Allows you to run multiple processes in parallel, taking full advantage of multiple CPU cores. This is ideal for CPU-bound tasks, like heavy mathematical computations, that can be broken down into independent parts.
                """,
                code_example='''import threading
import multiprocessing
import time

# --- Threading Example ---
# (Note: True concurrency is limited by the GIL in CPython)
def worker_thread(name):
    print(f"Thread {name}: starting")
    time.sleep(2)
    print(f"Thread {name}: finishing")

thread1 = threading.Thread(target=worker_thread, args=(1,))
thread2 = threading.Thread(target=worker_thread, args=(2,))
# thread1.start()
# thread2.start()
# thread1.join()
# thread2.join()
print("Threading example code structure is correct.")


# --- Multiprocessing Example ---
def worker_process(name):
    print(f"Process {name}: starting")
    time.sleep(2)
    print(f"Process {name}: finishing")

# The following code needs to be run inside `if __name__ == '__main__':`
# p1 = multiprocessing.Process(target=worker_process, args=(1,))
# p2 = multiprocessing.Process(target=worker_process, args=(2,))
# p1.start()
# p2.start()
# p1.join()
# p2.join()
print("\\nMultiprocessing example code structure is correct.")
''',
                interactive_code='# This is a conceptual chapter.\n# The code shows a simple function that could be a target for threading.\ndef long_running_task():\n    print("Task started...")\n    time.sleep(1) # Simulate work\n    print("Task finished!")\n\nlong_running_task()',
                quiz=QuizData(
                    question="Which concept is better for CPU-bound tasks to leverage multiple cores?",
                    options=["Threading", "Multiprocessing", "Generators", "Decorators"],
                    correct_index=1,
                    explanation="Multiprocessing bypasses the Global Interpreter Lock (GIL) by creating separate processes, allowing for true parallelism on multi-core systems.",
                    difficulty="advanced"
                ),
                prerequisites=["popular_libraries"],
                keywords=["threading", "multiprocessing", "concurrency", "parallelism", "cpu-bound", "io-bound"]
            ),
            # Chapter 17
            ChapterData(
                id="advanced_topics",
                title="Chapter 17: Advanced Topics",
                content="""
Diving deeper into Python reveals powerful features for metaprogramming and resource management.

- **Metaclasses**: A metaclass is a class whose instances are classes. Just as a class defines how an instance of the class behaves, a metaclass defines how a class behaves. It's an advanced topic used for creating frameworks and libraries where you need to modify class creation.

- **Context Managers**: A context manager is an object that defines the methods `__enter__()` and `__exit__()`. The `with` statement uses context managers to ensure that resources are properly acquired and released. File handling is a common example, but you can create your own for things like database connections or network sockets.
                """,
                code_example='''# --- Context Manager Example ---
class MyTimer:
    def __enter__(self):
        self.start_time = time.time()
        print("Timer started.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        duration = end_time - self.start_time
        print(f"Timer stopped. Duration: {duration:.4f} seconds.")

# Using the context manager
with MyTimer():
    # Simulate some work
    time.sleep(1.5)

# --- Metaclass Example (Conceptual) ---
# This is a very simplified example to show the syntax.
class MyMeta(type):
    def __new__(cls, name, bases, dct):
        print(f"Creating class: {name}")
        dct['extra_attribute'] = "Hello from Metaclass!"
        return super().__new__(cls, name, bases, dct)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.extra_attribute)
''',
                interactive_code='# Create a simple context manager to reverse a string\nclass StringReverser:\n    def __init__(self, text):\n        self.text = text\n\n    def __enter__(self):\n        return self.text[::-1]\n\n    def __exit__(self, type, value, traceback):\n        print("Reversing complete.")\n\nwith StringReverser("hello") as reversed_text:\n    print(reversed_text)',
                quiz=QuizData(
                    question="What is the primary purpose of a context manager and the `with` statement?",
                    options=["To create classes dynamically", "To manage resources and ensure cleanup", "To speed up code execution", "To handle multiple threads"],
                    correct_index=1,
                    explanation="Context managers guarantee that setup and teardown code (like opening and closing a file) is executed, even if errors occur.",
                    difficulty="advanced"
                ),
                prerequisites=["intermediate_topics"],
                keywords=["metaclasses", "context managers", "with statement", "__enter__", "__exit__"]
            ),
            # Chapter 18
            ChapterData(
                id="final_project",
                title="Chapter 18: Final Chapter – Build Your Own Project",
                content="""
Congratulations on reaching the final chapter! You've learned the building blocks of Python, from the basics to advanced concepts. Now it's time to put it all together and build something of your own.

**The best way to solidify your knowledge is by creating a project.** Choose something that interests you. Here are some ideas:
- **A command-line to-do list application**: Practice file handling, functions, and user input.
- **A simple calculator with a GUI**: Use a library like Tkinter or PyQt.
- **A web scraper**: Use libraries like `requests` and `BeautifulSoup` to extract data from a website.
- **A basic data analysis project**: Use `pandas` and `matplotlib` to analyze a dataset you find online.

The journey of a programmer is one of continuous learning and building. Don't be afraid to start small, make mistakes, and consult documentation. The skills you've gained here are your foundation for a lifetime of creating with code.
                """,
                code_example='''# Example Project Idea: A Simple Command-Line To-Do List

# todos.txt will store our tasks

def show_tasks():
    try:
        with open("todos.txt", "r") as f:
            tasks = f.readlines()
            if tasks:
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task.strip()}")
            else:
                print("Your to-do list is empty!")
    except FileNotFoundError:
        print("Your to-do list is empty!")

def add_task(task):
    with open("todos.txt", "a") as f:
        f.write(task + "\\n")
    print(f"Added task: {task}")

# This is a simplified structure. You would build a full
# application around these functions with user input loops.

print("--- To-Do List Application ---")
add_task("Learn Python")
add_task("Build a project")
show_tasks()
''',
                interactive_code='# A mini-project: A number guessing game\nimport random\n\nsecret_number = random.randint(1, 20)\nguess = 0\n\nwhile guess != secret_number:\n    try:\n        guess = int(input("Guess a number between 1 and 20: "))\n        if guess < secret_number:\n            print("Too low!")\n        elif guess > secret_number:\n            print("Too high!")\n    except ValueError:\n        print("Please enter a valid number.")\n\nprint(f"You got it! The number was {secret_number}")',
                quiz=QuizData(
                    question="What is the most important step after learning the fundamentals of a programming language?",
                    options=["Memorizing all library functions", "Reading more books", "Building projects", "Learning another language immediately"],
                    correct_index=2,
                    explanation="Building projects is crucial because it applies your knowledge to real-world problems, solidifies concepts, and teaches you how to solve problems independently.",
                    difficulty="beginner"
                ),
                prerequisites=["advanced_topics"],
                keywords=["project", "build", "practice", "portfolio", "learning"]
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
            # Allow specific safe imports
            if line.startswith('import ') or 'from ' in line:
                if 'import re' in line or 'import time' in line or 'import random' in line or 'import platform' in line:
                    continue
                if 'from collections' in line or 'from functools' in line or 'import itertools' in line:
                    continue
                if 'import pandas' in line or 'import numpy' in line:
                     continue
                for forbidden in cls.FORBIDDEN_IMPORTS:
                    if forbidden in line:
                        return False, f"Import '{forbidden}' not allowed for security"

        # Check for forbidden functions
        code_lower = code.lower()
        for forbidden in cls.FORBIDDEN_FUNCTIONS:
            # Allow input for the final project
            if 'final_project' in st.session_state.get('current_chapter_id', '') and forbidden == 'input':
                continue
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
                    'print': print, 'len': len, 'str': str, 'int': int, 'float': float,
                    'bool': bool, 'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'range': range, 'enumerate': enumerate, 'zip': zip, 'sorted': sorted,
                    'reversed': reversed, 'sum': sum, 'min': min, 'max': max, 'abs': abs,
                    'round': round, 'type': type, 'input': input
                },
                're': re, 'time': time, 'random': random, 'platform': __import__('platform'),
                'collections': __import__('collections'), 'itertools': __import__('itertools'),
                'functools': __import__('functools'), 'pandas': __import__('pandas'), 'numpy': __import__('numpy')
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
            # Handle input() reaching EOF in non-interactive environment
            if "EOF when reading a line" in str(e):
                 return True, "Code expecting input ran without errors. Try providing input in a real terminal."
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
                'theme': 'dark',
                'font_size': 'medium'
            }
        }

        for key, default_value in defaults.items():
            if key not in st.session_state:
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
            
            .code-section, .interactive-section, .quiz-container {
                border-radius: 12px;
                padding: 1.5rem;
                margin: 2rem 0;
                position: relative;
                box-shadow: var(--shadow-medium);
            }

            .code-section {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border: 1px solid var(--border-color);
            }
            
            .interactive-section {
                background: #252525;
                border: 1px solid var(--border-color);
            }

            .quiz-container {
                background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
                border: 1px solid var(--secondary-color);
            }

            .code-section::before, .interactive-section::before, .quiz-container::before {
                position: absolute;
                top: -14px;
                left: 20px;
                padding: 4px 12px;
                border-radius: 8px;
                font-size: 0.85rem;
                font-weight: 600;
                font-family: 'Inter', sans-serif;
                color: var(--background-dark);
            }

            .code-section::before { content: '💻 Code Example'; background-color: var(--secondary-color); }
            .interactive-section::before { content: '🚀 Interactive Code'; background-color: var(--secondary-color); }
            .quiz-container::before { content: '🎯 Knowledge Check'; background-color: var(--secondary-color); }
            
            .quiz-question {
                color: var(--text-primary);
                font-size: 1.2rem;
                font-weight: 600;
                margin-bottom: 1rem;
            }
            
            .toc-item {
                background: linear-gradient(135deg, var(--background-light) 0%, #2a2a2a 100%);
                border: 1px solid var(--border-color);
                border-radius: 12px;
                padding: 1rem 1.5rem;
                margin: 0.75rem 0;
                cursor: pointer;
                transition: all 0.2s ease-in-out;
                color: var(--text-primary);
            }

            .toc-item:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow-medium);
                border-color: var(--primary-color);
            }
            
            .locked-chapter {
                opacity: 0.5;
                pointer-events: none;
                background: #101010;
            }

            .completed-chapter {
                background: linear-gradient(135deg, #2E4031 0%, #1a2b1f 100%);
                border-color: #38761d;
            }
            
            .page-number {
                text-align: right;
                color: var(--text-secondary);
                font-style: italic;
                font-size: 0.9rem;
                margin-top: 2rem;
            }
        </style>
        """

    @staticmethod
    def render_progress_bar(progress_percentage: float, show_text: bool = True) -> None:
        """Render a progress bar"""
        progress_html = f"""
        <div style="margin: 1.5rem 0;">
            {f'<h3 style="color: var(--primary-color); margin-bottom: 0.5rem;">📊 Your Progress: {progress_percentage:.1f}%</h3>' if show_text else ''}
            <div style="background: #333; border-radius: 10px; height: 20px; overflow: hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);">
                <div style="background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%); width: {progress_percentage}%; height: 100%; transition: width 0.8s ease;"></div>
            </div>
        </div>
        """
        st.markdown(progress_html, unsafe_allow_html=True)


    @staticmethod
    def render_chapter_status(chapter_index: int, chapter: ChapterData, is_completed: bool, is_current: bool, is_locked: bool) -> None:
        """Render chapter status in table of contents"""
        status_icon = '✅' if is_completed else '🔒' if is_locked else '📖'
        status_text = 'Completed!' if is_completed else 'Locked' if is_locked else 'Ready to learn'
        
        container_class = "toc-item"
        if is_locked:
            container_class += " locked-chapter"
        if is_completed:
            container_class += " completed-chapter"

        with st.container():
            st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f'<div style="font-size: 1.5rem; text-align: center; margin-top: 10px;">{status_icon}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"**{chapter.title}**")
                st.markdown(f"<small style='color: var(--text-secondary);'><i>{status_text} | ⏱️ Est. {chapter.estimated_time} min</i></small>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ==================== PAGE CONTROLLERS ====================

class CoverPageController:
    """Handles cover page logic and rendering"""

    @staticmethod
    def render():
        """Render the cover page"""
        st.markdown(UIComponents.load_css(), unsafe_allow_html=True)

        cover_html = f"""
        <div class="main-container">
            <div class="cover-page">
                <h1 class="cover-title">📚 Python Interactive Textbook</h1>
                <p class="cover-subtitle">A Magical Journey from Beginner to Pythonista</p>
                 <div style="font-size: 1.15rem; margin: 2rem 0; line-height: 1.6;">
                    <p>Welcome to an extraordinary learning experience that transforms the way you discover Python programming.</p>
                    <p>This isn't just another tutorial—it's your personal guide through the world of code, complete with:</p>
                    <ul style="text-align: left; max-width: 500px; margin: 1.5rem auto; list-style-type: '✨ '; padding-left: 20px;">
                        <li>Interactive chapters that adapt to your pace</li>
                        <li>Live code execution and experimentation</li>
                        <li>Smart quizzes that reinforce learning</li>
                        <li>Progress tracking and achievements</li>
                        <li>Automatic bookmarking of your journey</li>
                    </ul>
                </div>
                <p style="font-size: 1rem; opacity: 0.8; margin-top: 2rem;">
                    Version {AppConfig.VERSION} | Crafted for curious minds
                </p>
            </div>
        </div>
        """
        st.markdown(cover_html, unsafe_allow_html=True)

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

        st.markdown(
            """
            <div class="main-container">
                <h1 class="chapter-header">📋 Table of Contents</h1>
                <p class="page-content">
                    Welcome back to your Python journey! Your progress is automatically saved.
                    Complete chapters in order to unlock new ones and master Python step-by-step.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        UIComponents.render_progress_bar(progress_percentage)

        for i, chapter in enumerate(chapters):
            is_completed = chapter.id in progress.completed_chapters
            is_current = st.session_state.get('current_chapter_id') == chapter.id
            is_locked = not ProgressManager.is_chapter_unlocked(i, progress)

            UIComponents.render_chapter_status(i, chapter, is_completed, is_current, is_locked)

            if not is_locked:
                if st.button(f"Go to Chapter {i+1}", key=f"chapter_btn_{i}", use_container_width=True):
                    logger.info(f"User accessed chapter: {chapter.id}")
                    SessionManager.navigate_to(PageType.CHAPTER, chapter.id)


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

        st.markdown(f'<div class="main-container">', unsafe_allow_html=True)
        st.markdown(f'<h1 class="chapter-header">{chapter.title}</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-content">{chapter.content}</div>', unsafe_allow_html=True)

        # Code example section
        st.markdown('<div class="code-section">', unsafe_allow_html=True)
        st.code(chapter.code_example, language='python')
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive code section
        ChapterController._render_interactive_section(chapter, chapter_index)

        # Quiz section
        if not is_completed:
            ChapterController._render_quiz_section(chapter, chapter_id)
        else:
            st.success("✅ You've already completed this chapter's quiz!")

        # Navigation
        ChapterController._render_navigation(chapter_index, is_completed)

        # Page number
        total_chapters = len(ChapterRepository.get_all_chapters())
        st.markdown(f'<div class="page-number">Page {chapter_index + 1} of {total_chapters}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _render_interactive_section(chapter: ChapterData, chapter_index: int):
        """Render interactive code section"""
        st.markdown('<div class="interactive-section">', unsafe_allow_html=True)
        st.markdown("<strong style='color: var(--text-primary);'>Modify the code below and click 'Run' to see the results:</strong>", unsafe_allow_html=True)

        user_code = st.text_area(
            "Python Code:",
            value=chapter.interactive_code,
            height=AppConfig.CODE_EDITOR_HEIGHT,
            key=f"code_editor_{chapter_index}"
        )

        if st.button("▶️ Run Code", key=f"run_code_{chapter_index}", type="primary"):
            success, output = SecurityManager.execute_code_safely(user_code)
            progress = SessionManager.get_progress()
            progress.code_executions += 1
            SessionManager.save_progress(progress)
            if success:
                st.success("Execution Output:")
                st.code(output, language='text')
            else:
                st.error("Execution Failed:")
                st.code(output, language='text')

        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _render_quiz_section(chapter: ChapterData, chapter_id: str):
        """Render quiz section"""
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="quiz-question">{chapter.quiz.question}</div>', unsafe_allow_html=True)

        selected_option = st.radio("Choose your answer:", chapter.quiz.options, key=f"quiz_{chapter_id}")

        if st.button("✅ Check Answer", key=f"check_answer_{chapter_id}", type="primary"):
            correct_answer = chapter.quiz.options[chapter.quiz.correct_index]
            if selected_option == correct_answer:
                st.success("🎉 Excellent! That's the correct answer!")
                st.info(f"💡 **Explanation:** {chapter.quiz.explanation}")
                progress = SessionManager.get_progress()
                progress = ProgressManager.complete_chapter(chapter_id, 100, progress)
                SessionManager.save_progress(progress)
                st.balloons()
                time.sleep(2) # Give time for balloons
                st.rerun()
            else:
                st.error(f"❌ Not quite right. The correct answer is: **{correct_answer}**")
                st.info(f"💡 **Explanation:** {chapter.quiz.explanation}")

        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def _render_navigation(chapter_index: int, is_completed: bool):
        """Render navigation buttons"""
        total_chapters = len(ChapterRepository.get_all_chapters())
        cols = st.columns(3)

        with cols[0]:
            if chapter_index > 0:
                prev_chapter = ChapterRepository.get_all_chapters()[chapter_index - 1]
                if st.button("⬅️ Previous Chapter", use_container_width=True):
                    SessionManager.navigate_to(PageType.CHAPTER, prev_chapter.id)

        with cols[1]:
            if st.button("📋 Back to Contents", use_container_width=True):
                SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)

        with cols[2]:
            if chapter_index < total_chapters - 1:
                next_chapter = ChapterRepository.get_all_chapters()[chapter_index + 1]
                st.button(
                    "➡️ Next Chapter",
                    key="nav_next",
                    use_container_width=True,
                    disabled=not is_completed,
                    on_click=SessionManager.navigate_to,
                    args=(PageType.CHAPTER, next_chapter.id),
                    help="Complete the quiz to unlock the next chapter"
                )


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        page_icon=AppConfig.APP_ICON,
        layout="centered",
        initial_sidebar_state="auto"
    )

    SessionManager.initialize_session()

    with st.sidebar:
        st.title(f"{AppConfig.APP_ICON} Navigation")
        if st.button("🏠 Home", use_container_width=True):
            SessionManager.navigate_to(PageType.COVER)
        if st.button("📋 Table of Contents", use_container_width=True):
            SessionManager.navigate_to(PageType.TABLE_OF_CONTENTS)
        
        st.divider()

        progress = SessionManager.get_progress()
        progress_percentage = ProgressManager.calculate_overall_progress(progress)
        st.markdown("### Your Progress")
        st.progress(progress_percentage / 100)
        st.caption(f"{progress_percentage:.1f}% Complete")

    try:
        current_page = PageType(st.session_state.current_page)
        if current_page == PageType.COVER:
            CoverPageController.render()
        elif current_page == PageType.TABLE_OF_CONTENTS:
            TableOfContentsController.render()
        elif current_page == PageType.CHAPTER:
            ChapterController.render()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        st.error("An unexpected error occurred. Please try again.")
        if st.button("Go to Home"):
            SessionManager.navigate_to(PageType.COVER)


if __name__ == "__main__":
    main()

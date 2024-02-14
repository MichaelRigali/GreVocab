from flask import Flask, render_template, request
import csv
import random

app = Flask(__name__)

# Initialize counters for correct and incorrect answers
correct_answers_count = 0
incorrect_answers_count = 0
incorrect_answers = []  # Store incorrect answers and their definitions

# Function to fetch vocabulary data from CSV files
def fetch_vocabulary(category):
    try:
        with open(f"datasets/{category}.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            vocabulary = []
            for row in reader:
                word = row['word']
                definition = row['definition']
                frequency = row.get('frequency', '')  # Get frequency column if exists
                vocabulary.append({
                    'word': word,
                    'definition': definition,
                    'frequency': frequency  # Add frequency to the vocabulary item
                })
            return vocabulary
    except Exception as e:
        print(f"An error occurred while fetching {category} vocabulary data:", e)
        return None

# Function to generate vocabulary questions
def generate_vocab_questions(vocabulary, num_questions=5):
    questions = []
    for _ in range(num_questions):
        # Randomly select a vocabulary item
        vocab_item = random.choice(vocabulary)
        word = vocab_item['word']
        definition = vocab_item['definition']
        # Generate question and options
        question = f"What is the definition of '{word}'?"
        options = [definition]
        while len(options) < 4:
            random_option = random.choice(vocabulary)['definition']
            if random_option not in options:
                options.append(random_option)
        random.shuffle(options)
        # Create question dictionary
        questions.append({
            'question': question,
            'options': options,
            'correct_answer': definition,
            'word': word
        })
    return questions

@app.route('/', methods=['GET', 'POST'])
def index():
    global correct_answers_count
    global incorrect_answers_count
    global incorrect_answers
    
    if request.method == 'POST':
        user_answer = request.form.get('answer')  # Retrieve the selected answer
        correct_answer = request.form.get('correct_answer')  # Retrieve the correct answer
        correct_word = request.form.get('word')  # Retrieve the correct word
        if user_answer == correct_answer:
            result = 'Correct'
            correct_answers_count += 1
        else:
            result = 'Incorrect'
            incorrect_answers_count += 1
            incorrect_answers.append({'word': correct_word, 'definition': correct_answer, 'user_answer': user_answer})  # Store incorrect answer, its definition, and the user's answer
        total_correct = correct_answers_count
        total_incorrect = incorrect_answers_count
        return render_template('result.html', result=result, correct_word=correct_word, current_question_index=int(request.args.get('q', 0)),
                               correct_answers_count=correct_answers_count, incorrect_answers_count=incorrect_answers_count,
                               incorrect_answers=incorrect_answers, total_correct=total_correct, total_incorrect=total_incorrect)

    # If it's a GET request, display the quiz question
    current_question_index = int(request.args.get('q', 0))
    categories = ['barron_333']  # Update with your actual category names
    questions = []

    for category in categories:
        # Fetch vocabulary data for each category
        vocabulary = fetch_vocabulary(category)
        if vocabulary:
            # Generate vocabulary questions
            questions.extend(generate_vocab_questions(vocabulary))
        else:
            return f"Failed to fetch {category} vocabulary data. Please try again later."

    if current_question_index >= len(questions):
        return 'Quiz completed!'
    return render_template('quiz.html', question=questions[current_question_index], current_question_index=current_question_index,
                           correct_answers_count=correct_answers_count, incorrect_answers_count=incorrect_answers_count)



if __name__ == '__main__':
    app.run(debug=True)

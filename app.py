from flask import Flask, render_template, request, jsonify, redirect, url_for
import csv
import random
import requests

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

# Function to get etymology for a word
def get_word_details(word):
    try:
        # Making the GET request
        response = requests.get(f"https://hebererj-cs361-ms-d18cbed0dc46.herokuapp.com/word/{word.lower()}")

        # Checking if the request was successful (status code 200)
        if response.status_code == 200:
            # Parsing response JSON
            data = response.json()
            etymology = data.get('etymology', 'Etymology not found.')
            language_of_origin = data.get('language of origin', 'Language of origin not found.')
            part_of_speech = data.get('part of speech', 'Part of speech not found.')
            return etymology, language_of_origin, part_of_speech  # Return etymology, language of origin, and part of speech
        else:
            # If there was an error, return error messages for all fields
            return 'Failed to fetch details. Status code: {}'.format(response.status_code), \
                   'Failed to fetch details. Status code: {}'.format(response.status_code), \
                   'Failed to fetch details. Status code: {}'.format(response.status_code)
    except Exception as e:
        # If there was an exception, return error messages for all fields
        return 'An error occurred: {}'.format(e), 'An error occurred: {}'.format(e), 'An error occurred: {}'.format(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    global correct_answers_count
    global incorrect_answers_count
    global incorrect_answers

    # Initialize variables
    incorrect_etymology = ''
    incorrect_language_of_origin = ''
    incorrect_part_of_speech = ''
    total_correct = correct_answers_count  # Define total_correct here
    
    # If it's a POST request, process the submitted answer
    if request.method == 'POST':
        user_answer = request.form.get('answer')  # Retrieve the selected answer
        correct_answer = request.form.get('correct_answer')  # Retrieve the correct answer
        correct_word = request.form.get('word')  # Retrieve the correct word
        if user_answer == correct_answer:
            result = 'Correct'
            correct_answers_count += 1
            correct_definition = correct_answer  # Pass correct definition to template
        else:
            result = 'Incorrect'
            incorrect_answers_count += 1
            incorrect_etymology, incorrect_language_of_origin, incorrect_part_of_speech = get_word_details(correct_word)
            incorrect_answers.append({'word': correct_word, 'definition': correct_answer, 'user_answer': user_answer})  # Store incorrect answer, its definition, and the user's answer
            correct_definition = None  # Define it as None for incorrect answers

        # Redirect to the result page after processing the answer
        total_correct = correct_answers_count  # Update total_correct after processing
        return render_template('result.html', result=result, correct_word=correct_word,
                       correct_answers_count=correct_answers_count, incorrect_answers_count=incorrect_answers_count,
                       incorrect_answers=incorrect_answers, total_correct=total_correct, total_incorrect=incorrect_answers_count,
                       incorrect_etymology=incorrect_etymology, incorrect_language_of_origin=incorrect_language_of_origin,
                       incorrect_part_of_speech=incorrect_part_of_speech, correct_definition=correct_definition)


    # If it's a GET request, display the quiz question
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

    # Pass the first question to the template
    return render_template('quiz.html', question=questions[0],
                           correct_answers_count=correct_answers_count, incorrect_answers_count=incorrect_answers_count)


@app.route('/result', methods=['GET', 'POST'])
def result():
    global correct_answers_count
    global incorrect_answers_count
    global incorrect_answers

    if incorrect_answers:
        last_answered_question = incorrect_answers[-1]
        correct_word = last_answered_question['word']
        correct_answer = last_answered_question['definition']
        user_answer = last_answered_question['user_answer']

        if user_answer == correct_answer:
            result = 'Correct'
            correct_answers_count += 1
            correct_definition = correct_answer
        else:
            result = 'Incorrect'
            incorrect_answers_count += 1
            incorrect_etymology, incorrect_language_of_origin, incorrect_part_of_speech = get_word_details(correct_word)
            correct_definition = None

        total_correct = correct_answers_count
        total_incorrect = incorrect_answers_count

        return render_template('result.html', result=result, correct_word=correct_word,
                               correct_answers_count=correct_answers_count, incorrect_answers_count=incorrect_answers_count,
                               incorrect_answers=incorrect_answers, total_correct=total_correct, total_incorrect=total_incorrect,
                               incorrect_etymology=incorrect_etymology, incorrect_language_of_origin=incorrect_language_of_origin,
                               incorrect_part_of_speech=incorrect_part_of_speech, correct_definition=correct_definition)
    else:
        return redirect('/')



@app.route('/quiz')
def quiz():
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

    # Pass the first question to the template
    if questions:
        return render_template('quiz.html', question=questions[0])
    else:
        return "No questions available. Please try again later."


@app.route('/etymology', methods=['GET'])
def etymology():
    # Retrieve the word from the query parameters
    word = request.args.get('word')
    
    # Call the function to get etymology for the word
    etymology = get_word_details(word)[0]  # Fetch only etymology
    
    # Return the etymology as JSON response
    return jsonify({'etymology': etymology})

@app.route('/restart', methods=['POST'])
def restart():
    global correct_answers_count
    global incorrect_answers_count
    global incorrect_answers

    # Reset counters and recorded answers
    correct_answers_count = 0
    incorrect_answers_count = 0
    incorrect_answers = []

    # Redirect to the main quiz page after restart
    return redirect('/')

@app.route('/quiz_incorrect', methods=['POST'])
def quiz_incorrect():
    incorrect_answers = request.form.get('incorrect_answers')
    # Process the incorrect answers and start a new quiz session with these definitions exclusively
    # You need to implement the logic for starting a new quiz session with these definitions

if __name__ == '__main__':
    app.run(debug=True)

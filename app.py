from flask import Flask, render_template, request, jsonify, redirect, url_for
import csv
import random
import requests
import re

app = Flask(__name__)

# Initialize counters for correct and incorrect answers
correct_answers_count = 0
incorrect_answers_count = 0
incorrect_answers = []  # Store incorrect answers and their definitions
incorrect_answer_index = 0  # Initialize index for tracking incorrect answers

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

# Fetch vocabulary data for the Barron's 333 category
vocabulary = fetch_vocabulary("barron_333")

# Function to generate vocabulary questions
def generate_vocab_questions(vocabulary, num_questions=5):
    questions = []
    for _ in range(num_questions):
        # Randomly select a vocabulary item
        vocab_item = random.choice(vocabulary)
        word = vocab_item['word']
        question = generate_vocab_question(vocabulary, word)
        questions.append(question)
    return questions

def get_word_details(word):
    try:
        # Making the GET request
        response = requests.get(f"https://hebererj-cs361-ms-d18cbed0dc46.herokuapp.com/word/{word}")

        # Checking if the request was successful (status code 200)
        if response.status_code == 200:
            # Parsing response JSON
            data = response.json()
            stems = data.get('stems', 'Stems not found.')
            etymology = clean_etymology(data.get('etymology', 'Etymology not found.'))
            short_definition = data.get('short_definition', 'Short definition not found.')
            part_of_speech = data.get('part of speech', 'Part of speech not found.')
            return stems, etymology, short_definition, part_of_speech  # Return stems, etymology, short definition, and part of speech
        else:
            # If there was an error, return error messages for all fields
            return 'Failed to fetch details. Status code: {}'.format(response.status_code), \
                   'Failed to fetch details. Status code: {}'.format(response.status_code), \
                   'Failed to fetch details. Status code: {}'.format(response.status_code), \
                   'Failed to fetch details. Status code: {}'.format(response.status_code)
    except Exception as e:
        # If there was an exception, return error messages for all fields
        return 'An error occurred: {}'.format(e), 'An error occurred: {}'.format(e), 'An error occurred: {}'.format(e), 'An error occurred: {}'.format(e)

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

    correct_word = None
    incorrect_stems = None
    incorrect_etymology = None
    incorrect_short_definition = None
    incorrect_part_of_speech = None
    correct_definition = None

    # Retrieve data from the form submission
    # user_answer = request.form.get('answer')
    # correct_answer = request.form.get('correct_answer')
    # word = request.form.get('word')
    correct_word = request.form.get('word')  # Retrieve the correct word from the form submission
    stems, etymology, short_definition, part_of_speech = get_word_details(correct_word)
    # Assuming you have a function or method to retrieve the correct definition based on the correct word
    
    # If it's a POST request, process the submitted answer
    if request.method == 'POST':

        user_answer = request.form.get('answer')  # Retrieve the selected answer
        correct_answer = request.form.get('correct_answer')  # Retrieve the correct answer
        correct_word = request.form.get('word')  # Retrieve the correct word
        # Create if statement for whether or not being quizzed exclusively or not 
        if user_answer == correct_answer:
            result = 'Correct'
            correct_answers_count += 1
            correct_definition = correct_answer  # Pass correct definition to template
            # if user_answer in incorrect_answers:
            # iterating over dicts in list
            for word_dict in incorrect_answers:
                if correct_word in word_dict.values():
                    # print(f'found in incorrect answers {correct_word}')
                    # now we want to remove this word from the incorrect answers
                    incorrect_answers.remove(word_dict)
                    incorrect_answers_count -= 1

        else:
            result = 'Incorrect'
            incorrect_answers_count += 1
            # incorrect_etymology, _, incorrect_part_of_speech, _ = get_word_details(correct_word)
            # stems, etymology, short_definition, part_of_speech
            incorrect_answers.append({'word': correct_word, 'definition': correct_answer, 'user_answer': user_answer})  # Store incorrect answer, its definition, and the user's answer
            correct_definition = None  # Define it as None for incorrect answers

        # Redirect to the result page after processing the answer
        total_correct = correct_answers_count  # Update total_correct after processing
        # Redirect or render result page with updated counts and incorrect answers list
        return render_template('result.html', result=result, correct_word=correct_word,
                       incorrect_answers=incorrect_answers, total_correct=correct_answers_count, total_incorrect=incorrect_answers_count,
                       incorrect_stems=incorrect_stems, etymology=etymology,
                       short_definition=short_definition, part_of_speech=part_of_speech,
                       correct_definition=correct_definition)

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

@app.route('/result', methods=['POST'])
def result():
    global correct_answers_count
    global incorrect_answers_count
    global incorrect_answers
    correct_word = None
    incorrect_stems = None
    incorrect_etymology = None
    incorrect_short_definition = None
    incorrect_part_of_speech = None
    correct_definition = None

    # Retrieve data from the form submission
    # user_answer = request.form.get('answer')
    # correct_answer = request.form.get('correct_answer')
    # word = request.form.get('word')
    correct_word = request.form.get('word')  # Retrieve the correct word from the form submission
    stems, etymology, short_definition, part_of_speech = get_word_details(correct_word)
    # Assuming you have a function or method to retrieve the correct definition based on the correct word
   
    # Update the incorrect stems variable
    if isinstance(stems, list):
        incorrect_stems = ', '.join(stems)  # Join the stems list into a string
    else:
        incorrect_stems = stems


    # Redirect or render result page with updated counts and incorrect answers list
    return render_template('result.html', result=result, correct_word=correct_word,
                       incorrect_answers=incorrect_answers, total_correct=correct_answers_count, total_incorrect=incorrect_answers_count,
                       incorrect_stems=incorrect_stems, etymology=etymology,
                       short_definition=short_definition, part_of_speech=part_of_speech,
                       correct_definition=correct_definition)

# Generate one vocab question over and over
def generate_vocab_question(vocabulary: dict, word: str):
    vocabulary_dict = {d['word']: d for d in vocabulary}
    random_keys = random.sample(sorted(vocabulary_dict.keys()), 3) 
    randomized_options = [vocabulary_dict[word]['definition']] + ([vocabulary_dict[random_word]['definition'] for random_word in random_keys])
    random.shuffle(randomized_options)
    return {'question': f"What is def of {word}?", 
            'options': randomized_options, 
            'correct_answer': vocabulary_dict[word]["definition"],
            'word':word}

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    global incorrect_answers
    global incorrect_answer_index  # Add global variable to keep track of the index

    # Define categories here
    categories = ['barron_333']  # Update with your actual category names
    vocabulary = fetch_vocabulary("barron_333")

    # Check if the query parameter 'incorrect' is present and set to 'true'
    if request.args.get('incorrect'):
        # Filter questions based on incorrect answers
        incorrect_words = {answer['word'] for answer in incorrect_answers}
        questions = []
        for incorrect_word in incorrect_words:
            questions.append(generate_vocab_question(vocabulary, incorrect_word))
            return render_template('quiz.html', question=questions[incorrect_answer_index])
        else:
            # If there are no more questions based on the incorrect answers, redirect to the result page
            return redirect('/result')
    else:
        # If the query parameter 'incorrect' is not set or not 'true', generate random questions as before
        questions = []
        for category in categories:
            vocabulary = fetch_vocabulary(category)
            if vocabulary:
                questions.extend(generate_vocab_questions(vocabulary))
            else:
                return f"Failed to fetch {category} vocabulary data. Please try again later."
        if questions:
            return render_template('quiz.html', question=questions[0])
        else:
            return "No questions available. Please try again later."
        
def clean_etymology(etymology):
    # Regex to remove anything in '{}' by looking within a nested list, hence 'etymology[0][1]' then stripping the following ' ' or blank space
    # and also removes the last ',' via rsplit(). 
    cleaned_etymology = re.sub(r'\{[^}]*\}', '', etymology[0][1]).rsplit(',', 1)[0].strip()
    return cleaned_etymology

# @app.route('/etymology', methods=['GET'])
# def etymology():
#     print("Accessing the etymology route")  # Debugging message
    
#     # Retrieve the word from the query parameters
#     word = request.args.get('word')
    
#     # Call the function to get etymology for the word
#     etymology_response = get_word_details(word)
    
#     # Extract etymology from the response
#     etymology = etymology_response[1]  # Assuming etymology is the second element in the response tuple
    
#     # Clean the etymology
#     cleaned_etymology = clean_etymology(etymology)
    
#     # Print the cleaned etymology for further debugging
#     print("Cleaned Etymology:", cleaned_etymology)
    
#     # Return the cleaned etymology as JSON response
#     return jsonify({'cleaned_etymology': cleaned_etymology})

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

if __name__ == '__main__':
    app.run(debug=True)



# Consider adding synonyms
# Example sentences 

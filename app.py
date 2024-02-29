from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key here
openai.api_key = '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'

# Function to get response from OpenAI API
def get_api_res(prompt: str) -> str|None:
    text: str | None = None
    try:
        response: dict = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-0613',
            messages=[
                {"role": "system", "content": "You are a online home made natural remedies product company"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )
        choices: dict = response.get('choices')[0]
        text = choices.get('message', {}).get('content')
    except Exception as e:
        print("Error:", e)
    return text

# Function to update the prompt list
def update_list(message:str, prompt_list: list[str]):
    prompt_list.append(message)

# Function to create a prompt
def create_prompt(message:str, prompt_list: list[str]) -> str:
    p_message = f'\nHuman:{message}'
    update_list(p_message, prompt_list)
    prompt = ''.join(prompt_list)
    return prompt

# Function to get bot response
def get_bot_res(message:str, prompt_list: list[str]) -> str:
    prompt = create_prompt(message, prompt_list)
    bot_res = get_api_res(prompt)
    if bot_res:
        update_list(bot_res, prompt_list)
        pos = bot_res.find('\nbot: ')
        bot_res = bot_res[pos + 5:]
    else:
        bot_res = 'Something went wrong'
    return bot_res

# Function to read prompts and responses from file
def read_prompts_responses_from_file(filename: str) -> dict:
    prompts_responses = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            current_user_query = None
            for line in lines:
                line = line.strip()
                if line:
                    if line.startswith("User Query:"):
                        current_user_query = line[len("User Query:"):].strip()
                    elif line.startswith("Bot Response:"):
                        if current_user_query:
                            prompts_responses[current_user_query] = line[len("Bot Response:"):].strip()
                        current_user_query = None
        return prompts_responses
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return {}

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle user input and return bot response
@app.route('/get_bot_response', methods=['POST'])
def get_bot_response():
    user_input = request.form['user_input']
    response = get_bot_res(user_input, list(prompts_responses.keys()))
    return jsonify({'bot_response': response})

# Route to handle text data sent from the HTML form
@app.route('/txt', methods=['POST'])
def handle_text():
    text_data = request.form['chatInput']
    response = get_bot_res(text_data, list(prompts_responses.keys()))
    return jsonify({'response': response})

if __name__ == "__main__":
    filename = "Desc.txt"
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
    else:
        prompts_responses = read_prompts_responses_from_file(filename)
        if not prompts_responses:
            print("Error: No prompts and responses found.")
        else:
            app.run(debug=True)

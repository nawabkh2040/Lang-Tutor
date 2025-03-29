from flask import Flask, request, jsonify, render_template
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.globals import set_debug
import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set debug mode for LangChain
set_debug(True)

# Initialize LangChain ChatOpenAI
llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.7,
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Create prompt templates
conversation_template = PromptTemplate(
    input_variables=["learning_lang", "known_lang", "level", "scene"],
    template="""You are a helpful language tutor teaching {learning_lang} to a {level} level student who speaks {known_lang}.
    Set up a conversation scenario for '{scene}'. Introduce yourself and start the conversation in {learning_lang}, 
    but provide translations in {known_lang} in parentheses. Keep responses concise and engaging."""
)

chat_template = PromptTemplate(
    input_variables=["learning_lang", "known_lang", "level", "input", "history"],
    template="""You are a language tutor helping with {learning_lang}. The student speaks {known_lang} and is at {level} level.

    Previous conversation:
    {history}

    Instructions:
    1. Analyze their message for any mistakes
    2. Respond naturally to continue the conversation in {learning_lang}
    3. If there are mistakes, provide corrections after your response, prefixed with 'CORRECTION:'
    4. Include translations in {known_lang} in parentheses
    5. Keep the conversation engaging and natural

    Student message: {input}"""
)

summary_template = PromptTemplate(
    input_variables=["learning_lang", "known_lang", "mistakes"],
    template="""Based on these recent mistakes in {learning_lang}:
    {mistakes}
    
    Provide a concise summary in {known_lang} of:
    1. Common patterns in the mistakes
    2. Specific areas to focus on
    3. 2-3 practical tips for improvement"""
)

# Initialize conversation memory
memory = ConversationBufferMemory(
    memory_key="history",
    input_key="input",
    return_messages=True
)

# Create conversation chain
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=PromptTemplate(
        input_variables=["history", "input"],
        template="Current conversation:\n{history}\nHuman: {input}\nAssistant:"
    ),
    verbose=True
)

# Database setup
def init_db():
    conn = sqlite3.connect('mistakes.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS mistakes')
    cursor.execute('''CREATE TABLE mistakes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        mistake TEXT,
                        correction TEXT,
                        category TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_chat():
    data = request.json
    user_id = data.get('user_id')
    known_lang = data.get('known_language')
    learning_lang = data.get('learning_language')
    level = data.get('level')
    scene = data.get('scene')
    
    # Clear previous conversation memory
    memory.clear()
    
    # Create the prompt using template
    prompt = conversation_template.format(
        learning_lang=learning_lang,
        known_lang=known_lang,
        level=level,
        scene=scene
    )
    
    # Get response using LangChain
    response = llm.predict_messages([SystemMessage(content=prompt)])
    
    return jsonify({
        "message": response.content,
        "scene": scene,
        "level": level
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    user_input = data.get('message')
    learning_lang = data.get('learning_language')
    known_lang = data.get('known_language')
    level = data.get('level')
    
    # Get conversation history
    history = memory.load_memory_variables({})["history"]
    
    # Create the prompt using template
    prompt = chat_template.format(
        learning_lang=learning_lang,
        known_lang=known_lang,
        level=level,
        input=user_input,
        history=history
    )
    
    # Get response using conversation chain
    response = conversation.predict(input=prompt)
    
    # Check if there's a correction in the response
    if "CORRECTION:" in response:
        main_response, correction = response.split("CORRECTION:", 1)
        store_mistake(user_id, user_input, correction.strip(), "grammar")
        return jsonify({
            "reply": main_response.strip(),
            "correction": correction.strip(),
            "has_correction": True
        })
    
    return jsonify({
        "reply": response,
        "has_correction": False
    })

@app.route('/summary', methods=['POST'])
def summary():
    data = request.json
    user_id = data.get('user_id')
    learning_lang = data.get('learning_language')
    known_lang = data.get('known_language')
    
    # Get mistakes from database
    conn = sqlite3.connect('mistakes.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mistake, correction, category 
        FROM mistakes 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
        LIMIT 10
    """, (user_id,))
    mistakes = cursor.fetchall()
    conn.close()
    
    # Format mistakes for the prompt
    mistakes_text = "\n".join([f"Mistake: {m[0]}\nCorrection: {m[1]}" for m in mistakes])
    
    # Create the prompt using template
    prompt = summary_template.format(
        learning_lang=learning_lang,
        known_lang=known_lang,
        mistakes=mistakes_text
    )
    
    # Get response using LangChain
    response = llm.predict_messages([SystemMessage(content=prompt)])
    
    return jsonify({
        "mistakes": mistakes,
        "feedback": response.content
    })

def store_mistake(user_id, mistake, correction, category):
    conn = sqlite3.connect('mistakes.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mistakes (user_id, mistake, correction, category) VALUES (?, ?, ?, ?)",
        (user_id, mistake, correction, category)
    )
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(debug=True)

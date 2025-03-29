# Language Learning AI Chatbot

An intelligent chatbot that helps users learn new languages through interactive conversations, real-time corrections, and personalized feedback using LangChain and OpenAI's GPT-4.

## Features

- 🌍 Multi-language support
- 🎯 Different proficiency levels (Beginner, Intermediate, Advanced)
- 🎭 Various conversation scenarios
- ✍️ Real-time mistake detection and corrections
- 📊 Learning progress tracking
- 📝 Personalized learning summaries
- 🎨 Multiple UI themes

## Architecture

### Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **AI/ML**: LangChain + OpenAI GPT-4
- **Database**: SQLite
- **Memory Management**: LangChain ConversationBufferMemory

### Components

1. **Language Model Integration**
   - Uses LangChain for structured interactions with GPT-4
   - Custom prompt templates for different conversation scenarios
   - Conversation memory management for context retention

2. **Database System**
   - Tracks user mistakes and corrections
   - Stores conversation history
   - Enables progress analysis

3. **User Interface**
   - Responsive chat interface
   - Real-time message updates
   - Theme customization
   - Progress visualization

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/nawabkh2040/Lang-Tutor.git
   cd Lang-Tutor
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

5. **Initialize Database**
   ```bash
   python app.py
   ```

6. **Run the Application**
   ```bash
   flask run
   ```

## Usage Guide

1. **Starting a Conversation**
   - Select your native language
   - Choose the language you want to learn
   - Set your proficiency level
   - Pick a conversation scenario
   - Click "Start" to begin

2. **During Conversation**
   - Type messages in your learning language
   - Receive responses with translations
   - Get instant corrections for mistakes
   - See conversation history

3. **Learning Progress**
   - Click "Show Learning Summary" to view:
     - Common mistakes
     - Areas for improvement
     - Practical tips

4. **Customization**
   - Choose from different UI themes
   - Adjust conversation scenarios
   - Select difficulty levels


Serene 🌿 — AI Mental Health Chatbot

Serene is an intelligent AI-powered mental health chatbot designed to provide empathetic emotional support and guided therapeutic conversations.
The project combines multiple Artificial Intelligence concepts including:

🧠 Intelligent Agents (PEAS Model)
🔍 Bi-Directional Search
🧬 Genetic Algorithms
🤖 LLM Integration (Groq + Llama 3.1)
💬 Emotion Detection & Conversational AI

The chatbot analyzes user emotions, plans emotional progression toward a calm mental state, and generates compassionate responses dynamically.

🚀 Features
Emotion detection from user messages
AI-powered empathetic conversation
Crisis support detection
Emotional state tracking
Therapy path planning using Bi-Directional Search
Genetic Algorithm optimized responses
Groq API integration using Llama 3.1
Session-based memory
REST API backend with Flask
Fallback response system when API is unavailable
🧠 AI Concepts Used
1. Intelligent Agent (PEAS Model)

The chatbot is implemented as a Goal-Based Intelligent Agent.

PEAS Description
Component	Description
Performance Measure	Move user toward calm emotional state
Environment	User conversation & emotional context
Actuators	Therapeutic responses & coping strategies
Sensors	Emotion detection & sentiment analysis
2. Bi-Directional Search

The emotional state graph is traversed using Bi-Directional Search to find the shortest therapeutic path from the current emotional state to the goal state (calm).

Example Emotional Flow
depressed → sad → neutral → okay → calm

This allows the chatbot to:

Plan emotional progression
Suggest next therapeutic action
Track conversation improvement
3. Genetic Algorithm

A Genetic Algorithm evolves the chatbot’s response strategy dynamically.

The GA optimizes:

Tone
Empathy level
Therapeutic technique
Question strategy
GA Workflow
Initialize Population
        ↓
Evaluate Fitness
        ↓
Selection
        ↓
Crossover
        ↓
Mutation
        ↓
Best Therapeutic Strategy
🏗️ Project Structure
├── app.py
├── agent.py
├── bidirectional_search.py
├── genetic_algorithm.py
├── knowledge_base.py
├── requirements.txt
📂 File Explanations
app.py

Main Flask application.

Handles:

Routing
Session management
API endpoints
Chat requests
Reset functionality
Endpoints
Route	Description
/	Main UI
/chat	Send user message
/status	API status
/reset	Reset session
/quit	Shutdown app
agent.py

Core AI agent implementation.

Responsible for:

Perception
Emotional state classification
Planning
Response generation
Maintaining conversation history
Processing Cycle
Perceive → Update State → Plan → Act
bidirectional_search.py

Implements the Bi-Directional Search algorithm.

Used to:

Find shortest emotional path
Suggest therapy transitions
Explore emotional graph efficiently
genetic_algorithm.py

Implements the Genetic Algorithm system.

Features:

Response evolution
Prompt optimization
Tone adaptation
Therapeutic technique selection
knowledge_base.py

Contains:

Emotional state graph
Keyword mappings
Therapy actions
Coping strategies
Fallback responses

Acts as the chatbot’s knowledge base.

🔄 System Workflow
User Message
      ↓
Emotion Detection
      ↓
State Classification
      ↓
Bi-Directional Search Planning
      ↓
Genetic Algorithm Optimization
      ↓
LLM Response Generation
      ↓
Therapeutic Response
🤖 LLM Integration

The chatbot uses:

Groq API
Llama 3.1 8B Instant Model

The LLM is responsible for:

Human-like responses
Emotional understanding
Adaptive therapeutic conversation
🛡️ Safety Features
Suicide/crisis keyword detection
Crisis hotline suggestions
Non-diagnostic responses
Supportive communication rules
Empathy-first response generation
📦 Installation
1. Clone Repository
git clone https://github.com/your-username/serene-ai-chatbot.git
cd serene-ai-chatbot
2. Install Dependencies
pip install -r requirements.txt
3. Add API Key

Inside app.py:

os.environ["GEMINI_API_KEY"] = "YOUR_GROQ_API_KEY"
4. Run Application
python app.py
🌐 Access Application

Open browser:

http://127.0.0.1:5000
📊 Example Conversation Flow
User: I feel anxious and overwhelmed.

↓ Emotion Detection

Detected State: anxious

↓ Bi-Directional Search

anxious → neutral → okay → calm

↓ Genetic Algorithm

Optimizes:
- calm tone
- grounding technique
- medium empathy

↓ AI Response

"Anxiety can make everything feel heavy right now..."
🔬 Technologies Used
Python
Flask
Requests
Groq API
Llama 3.1
Genetic Algorithms
Graph Search Algorithms
🎯 Future Improvements
Voice support
Emotion graphs visualization
User authentication
Chat history database
Reinforcement Learning
Multi-language support
Therapist dashboard
Mobile application
⚠️ Disclaimer

This project is designed for emotional support and educational purposes only.
It is not a replacement for professional mental health care, therapy, or medical diagnosis.

If someone is in crisis, please contact professional mental health services immediately.

👨‍💻 Author

Developed by Devansh Varma

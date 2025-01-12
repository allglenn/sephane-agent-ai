import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain.llms import OpenAI
from langchain.document_loaders import PyPDFLoader
from flask_cors import CORS
from werkzeug.exceptions import BadRequest
import logging
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, initialize_agent
from langchain.agents import AgentType
from typing import Optional, Dict
from datetime import datetime
import json
from tools import SearchInfoTool, UserInfoTool  # Import tools from tools package


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Flask app with CORS
app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()

def validate_environment():
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

def load_documents(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Guest guides folder not found: {folder_path}")
    
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    if not pdf_files:
        raise FileNotFoundError("No PDF files found in guest guides folder")
    
    for file_name in pdf_files:
        try:
            file_path = os.path.join(folder_path, file_name)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
            logger.info(f"Loaded document: {file_name}")
        except Exception as e:
            logger.error(f"Error loading {file_name}: {str(e)}")
    return documents

def initialize_agent_with_tools():
    try:
        # Validate environment
        validate_environment()
        
        # Initialize ChatOpenAI
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # Configure embeddings
        embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002"
        )
        
        # Load and process documents
        folder_path = "./guest_guides"
        documents = load_documents(folder_path)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(documents)

        # Create vector store
        vectorstore = FAISS.from_documents(split_docs, embeddings)
        
        # Initialize tools
        search_tool = SearchInfoTool(vectorstore)
        user_tool = UserInfoTool(vectorstore)
        
        # Create tools list
        tools = [
            Tool(
                name="SearchInfo",
                func=search_tool.search,
                description="Useful for searching information in the guest guides. Input should be a specific question or search query."
            ),
            Tool(
                name="GetUserInfo",
                func=lambda x: user_tool.format_user_info(user_tool.get_user_info(x)),
                description="Useful for getting guest information using their booking number. Input should be a booking number (e.g., 'BK123')."
            )
        ]
        
        # Initialize the agent with a custom prompt
        prefix = """You are a helpful hotel concierge assistant. When helping guests:
        1. Always speak directly to the guest using "you" and "your"
        2. Use both user information and general hotel information to provide personalized responses
        3. If a guest's preferences are relevant (like dietary restrictions), incorporate them into your recommendations
        4. When searching for information, always use the SearchInfo tool to find relevant details from the hotel guide
        5. Provide specific, detailed recommendations based on both the guest's context and available information
        
        Remember to be warm and welcoming while maintaining professionalism."""
        
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={'prefix': prefix}
        )
        
        logger.info("Agent initialized successfully with tools")
        return agent, user_tool
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        raise

# Initialize the agent and user tool
agent, user_tool = initialize_agent_with_tools()

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint to verify API is running"""
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Validate request
        if not request.is_json:
            raise BadRequest("Content-Type must be application/json")
        
        data = request.get_json()
        if "query" not in data:
            raise BadRequest("Missing 'query' in request body")
        
        query = data["query"]
        if not query.strip():
            raise BadRequest("Query cannot be empty")
            
        # Get booking number if provided
        booking_number = data.get("booking_number")
        
        # Log incoming query
        logger.info(f"Received query: {query}")
        
        # If booking number is provided, get user info
        if booking_number:
            user_info = user_tool.get_user_info(booking_number)
            # If there's an error in user info, return it immediately
            if "error" in user_info:
                return jsonify({
                    "status": "error",
                    "message": user_tool.format_user_info(user_info),
                    "query": query
                }), 400
            
            # If user info is valid, construct personalized query
            query = f"""Based on the following guest information and hotel guide, provide a personalized response:

            {user_tool.format_user_info(user_info)}

            Guest's Question: {query}

            Remember to:
            1. Use the SearchInfo tool to find relevant information from the hotel guide
            2. Consider the guest's preferences and details when providing recommendations
            3. Speak directly to the guest
            4. Provide specific, detailed recommendations"""
        
        # Generate response using the agent
        response = agent.run(query)
        
        # Log successful response
        logger.info(f"Generated response for query: {query[:50]}...")
        
        return jsonify({
            "status": "success",
            "response": response,
            "query": query
        })

    except BadRequest as e:
        logger.warning(f"Bad request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred"
        }), 500

@app.route("/hello", methods=["GET"])
def hello_world():
    """Simple hello world endpoint to test API connectivity"""
    try:
        return jsonify({
            "status": "success",
            "message": "Hello from the Guest Guide API!",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health [GET]",
                "hello": "/hello [GET]",
                "ask": "/ask [POST]"
            }
        })
    except Exception as e:
        logger.error(f"Error in hello_world endpoint: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An internal error occurred"
        }), 500

if __name__ == "__main__":
    # Load environment variables with defaults
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    app.run(host="0.0.0.0", port=port, debug=debug)

    
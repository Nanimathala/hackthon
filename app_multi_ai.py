import streamlit as st
import pymupdf as fitz
import numpy as np
import os
import torch
import re
from typing import List, Dict, Any
import time
import asyncio
import json
import random
import traceback

# Handle problematic imports with version compatibility
try:
    # Fix numpy compatibility issues
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", message=".*numpy.dtype size changed.*")
    
    # Import sentence transformers with error handling
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    st.error(f"SentenceTransformers import error: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False
except Exception as e:
    st.warning(f"SentenceTransformers compatibility issue: {e}")
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Import FAISS with error handling
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError as e:
    st.error(f"FAISS import error: {e}")
    faiss = None
    FAISS_AVAILABLE = False

# Import transformers with error handling
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    st.warning(f"Transformers import error: {e}")
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    TRANSFORMERS_AVAILABLE = False

# Try to import AI APIs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    genai = None
    GOOGLE_AVAILABLE = False

# Try to import optional dependencies
try:
    from spellchecker import SpellChecker
    from textblob import TextBlob
    SPELL_AVAILABLE = True
except ImportError:
    SpellChecker = None
    TextBlob = None
    SPELL_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Authentication System ---
def init_session_state():
    """Initialize session state for authentication"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {}  # Simple in-memory user database
        
        # Add demo users for testing
        st.session_state.users_db.update({
            'demo': {
                'password': 'demo123',
                'email': 'demo@studymate.com',
                'grade_level': 'College',
                'study_field': 'Computer Science',
                'created_at': time.time()
            },
            'student': {
                'password': 'student123',
                'email': 'student@example.com', 
                'grade_level': 'High School',
                'study_field': 'Science',
                'created_at': time.time()
            }
        })

def show_auth_page():
    """Display login and signup page with beautiful UI"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    /* Light Background styling */
    .stApp {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f2ff 50%, #ffffff 100%);
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><radialGradient id="grad1" cx="50%" cy="50%" r="50%"><stop offset="0%" style="stop-color:rgba(102,126,234,0.05);stop-opacity:1" /><stop offset="100%" style="stop-color:rgba(102,126,234,0);stop-opacity:1" /></radialGradient></defs><rect width="1200" height="800" fill="url(%23grad1)"/><circle cx="200" cy="150" r="40" fill="rgba(102,126,234,0.03)"/><circle cx="800" cy="300" r="60" fill="rgba(102,126,234,0.02)"/><circle cx="1000" cy="600" r="50" fill="rgba(102,126,234,0.02)"/></svg>');
        background-size: cover;
        background-repeat: no-repeat;
        opacity: 0.5;
        z-index: -1;
    }
    
    /* Compact Main container */
    .auth-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 25px;
        margin: 10px auto;
        max-width: 350px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    /* Logo and branding */
    .auth-logo {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .auth-logo h1 {
        color: #667eea;
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .auth-logo p {
        color: #666;
        font-size: 1.1rem;
        margin: 10px 0 0 0;
        font-weight: 400;
    }
    
    /* StudyMate branding icons */
    .brand-icons {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin: 20px 0;
        font-size: 2rem;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e1e5e9;
        padding: 12px 16px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 20px;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 8px 0;
        min-height: 50px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Special styling for mark buttons */
    .stButton > button[title*="7 marks"] {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        font-size: 14px;
    }
    
    .stButton > button[title*="14 marks"] {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        font-size: 14px;
    }
    
    .stButton > button[title*="Clear chat"] {
        background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        font-size: 14px;
    }
    
    /* Responsive column adjustments */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 13px;
            padding: 10px 16px;
            min-height: 45px;
        }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background: transparent;
        border-bottom: 2px solid #e1e5e9;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px 8px 0 0;
        color: #666;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        border-radius: 12px;
        margin: 15px 0;
    }
    
    /* Learning themed decorations */
    .learning-decoration {
        position: absolute;
        opacity: 0.1;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main authentication container
    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Logo and branding
    st.markdown("""
    <div class="auth-logo">
        <h1>🧠 StudyMate Pro</h1>
        <p>Your AI-Powered Learning Companion</p>
        <div class="brand-icons">
            <span title="AI Assistant">🤖</span>
            <span title="Document Processing">📚</span>
            <span title="Multi-AI Support">⚡</span>
            <span title="Smart Learning">🎓</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        st.markdown("Enter your credentials to access your personalized AI learning assistant.")
        
        # Demo accounts info
        st.info("🎯 **Demo Accounts:** Try `demo` / `demo123` or `student` / `student123`")
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            login_button = st.form_submit_button("🚀 Login to StudyMate")
            
            if login_button:
                if not username.strip():
                    st.error("❌ Please enter your username.")
                elif not password.strip():
                    st.error("❌ Please enter your password.")
                elif authenticate_user(username.strip(), password):
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip()
                    st.success("🎉 Login successful! Welcome back to StudyMate Pro!")
                    time.sleep(0.3)  # Reduced from 1 second for faster login
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
    
    with tab2:
        st.markdown("### Join StudyMate Pro!")
        st.markdown("Create your account and unlock the power of AI-assisted learning.")
        
        with st.form("signup_form"):
            new_username = st.text_input("👤 Choose Username", placeholder="Create a unique username")
            new_email = st.text_input("📧 Email Address", placeholder="your.email@example.com")
            new_password = st.text_input("🔒 Create Password", type="password", placeholder="Choose a strong password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                grade_level = st.selectbox("🎓 Grade Level", 
                    ["Elementary", "Middle School", "High School", "College", "Graduate", "Professional"])
            with col2:
                study_field = st.selectbox("📖 Study Field", 
                    ["General", "Science", "Math", "Literature", "History", "Technology", "Arts", "Other"])
            
            terms_agreed = st.checkbox("I agree to the Terms of Service and Privacy Policy")
            signup_button = st.form_submit_button("✨ Create My StudyMate Account")
            
            if signup_button:
                # Validate inputs
                if not new_username.strip():
                    st.error("❌ Please enter a username.")
                elif not new_email.strip():
                    st.error("❌ Please enter an email address.")
                elif not new_password.strip():
                    st.error("❌ Please enter a password.")
                elif len(new_password) < 4:
                    st.error("❌ Password must be at least 4 characters long.")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match. Please try again.")
                elif not terms_agreed:
                    st.error("❌ Please accept the Terms of Service to continue.")
                elif new_username.strip() in st.session_state.users_db:
                    st.error("❌ Username already exists. Please choose a different one.")
                elif "@" not in new_email or "." not in new_email:
                    st.error("❌ Please enter a valid email address.")
                else:
                    try:
                        # Create new user
                        clean_username = new_username.strip()
                        st.session_state.users_db[clean_username] = {
                            'password': new_password,  # In production, hash this!
                            'email': new_email.strip(),
                            'grade_level': grade_level,
                            'study_field': study_field,
                            'created_at': time.time()
                        }
                        # Auto-login after signup for faster flow
                        st.session_state.authenticated = True
                        st.session_state.username = clean_username
                        st.success("🎉 Account created successfully! Logging you in...")
                        time.sleep(0.2)  # Very brief delay for user feedback
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error creating account: {e}")
                        st.error("Please try again or contact support.")
    
    # Footer with features
    st.markdown("""
    <div style="margin-top: 40px; text-align: center; color: #666;">
        <h4>🌟 Why Choose StudyMate Pro?</h4>
        <div style="display: flex; justify-content: space-around; margin: 20px 0;">
            <div>
                <div style="font-size: 2rem;">🤖</div>
                <strong>Multi-AI</strong><br>
                ChatGPT, Gemini & More
            </div>
            <div>
                <div style="font-size: 2rem;">📄</div>
                <strong>PDF Support</strong><br>
                Instant Document Analysis
            </div>
            <div>
                <div style="font-size: 2rem;">⚡</div>
                <strong>Fast & Smart</strong><br>
                Intelligent Responses
            </div>
            <div>
                <div style="font-size: 2rem;">🎨</div>
                <strong>Beautiful UI</strong><br>
                Modern & Intuitive
            </div>
        </div>
        <p style="margin-top: 20px; font-size: 0.9rem;">
            © 2025 StudyMate Pro - Empowering Learning with AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials"""
    try:
        if not username or not password:
            return False
        
        if not hasattr(st.session_state, 'users_db'):
            st.session_state.users_db = {}
        
        if username in st.session_state.users_db:
            stored_user = st.session_state.users_db[username]
            if isinstance(stored_user, dict) and 'password' in stored_user:
                return stored_user['password'] == password
        return False
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

def logout():
    """Logout user and clear session"""
    try:
        st.session_state.authenticated = False
        st.session_state.username = ""
        # Clear chat history and other session data
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        if 'text_chunks' in st.session_state:
            st.session_state.text_chunks = []
        if 'embeddings_index' in st.session_state:
            st.session_state.embeddings_index = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout error: {e}")
        # Try to clear session state manually
        keys_to_clear = ['authenticated', 'username', 'chat_history', 'text_chunks', 'embeddings_index']
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

# --- UI Configuration ---
st.set_page_config(
    page_title="StudyMate Pro - Multi-AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for ChatGPT-like interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main app background when authenticated */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #4facfe 100%);
        background-attachment: fixed;
    }
    
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800"><defs><radialGradient id="learning-grad" cx="50%" cy="50%" r="50%"><stop offset="0%" style="stop-color:rgba(255,255,255,0.08);stop-opacity:1" /><stop offset="100%" style="stop-color:rgba(255,255,255,0);stop-opacity:1" /></radialGradient></defs><rect width="1200" height="800" fill="url(%23learning-grad)"/><g opacity="0.06"><circle cx="150" cy="100" r="60" fill="white"/><circle cx="1000" cy="150" r="80" fill="white"/><circle cx="300" cy="400" r="40" fill="white"/><circle cx="800" cy="500" r="70" fill="white"/><circle cx="1100" cy="600" r="50" fill="white"/><path d="M200,300 Q250,250 300,300 T400,300" stroke="white" stroke-width="2" fill="none"/><path d="M600,200 Q650,150 700,200 T800,200" stroke="white" stroke-width="2" fill="none"/><polygon points="100,600 140,550 180,600 140,650" fill="white"/><polygon points="900,350 940,300 980,350 940,400" fill="white"/><text x="500" y="100" font-family="Arial" font-size="24" fill="white" opacity="0.3">📚</text><text x="700" y="600" font-family="Arial" font-size="24" fill="white" opacity="0.3">🎓</text><text x="200" y="200" font-family="Arial" font-size="20" fill="white" opacity="0.3">🧠</text><text x="1000" y="400" font-family="Arial" font-size="20" fill="white" opacity="0.3">⚡</text></g></svg>');
        background-size: cover;
        background-repeat: no-repeat;
        opacity: 0.4;
        z-index: -1;
    }
    
    /* Navigation bar styling */
    .nav-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px 25px;
        margin-bottom: 20px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        border: 1px solid rgba(229, 231, 235, 0.6);
        margin: 1rem 0;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        backdrop-filter: blur(5px);
    }
        padding: 0;
        margin: 1rem 0;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.05);
        overflow: hidden;
    }
    
    .chat-input-container {
        background: #f9fafb;
        border-top: 1px solid #e5e7eb;
        padding: 1rem;
        position: relative;
    }
    
    .chat-input {
        width: 100%;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem 3rem 1rem 1rem;
        font-size: 16px;
        resize: none;
        outline: none;
        transition: all 0.2s;
        background: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .chat-input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .send-button {
        position: absolute;
        right: 1.5rem;
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .send-button:hover {
        transform: translateY(-50%) translateX(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .ai-response-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        position: relative;
    }
    
    .ai-model-selector {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .model-option {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    
    .model-option:hover {
        background: #f1f5f9;
        border-color: #e2e8f0;
    }
    
    .model-option.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    .ai-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .openai-badge { background: #10a37f; color: white; }
    .gemini-badge { background: #4285f4; color: white; }
    .granite-badge { background: #0f62fe; color: white; }
    .fast-badge { background: #ff6b35; color: white; }
    .detailed-badge { background: #8b5cf6; color: white; }
    
    .answer-section {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e7eb;
    }
    
    .thinking-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #6b7280;
        font-style: italic;
    }
    
    .typing-dots {
        display: inline-flex;
        gap: 2px;
    }
    
    .typing-dots span {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    .spell-suggestion {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
    }
    
    .pdf-upload-area {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #f9fafb;
        transition: all 0.2s;
    }
    
    .pdf-upload-area:hover {
        border-color: #667eea;
        background: #f0f4ff;
    }
    
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
    }
    
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e5e7eb !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# Environment setup with speed optimization
openai_api_key = os.getenv("OPENAI_API_KEY", "")
google_api_key = os.getenv("GOOGLE_API_KEY", "")
hf_token = os.getenv("HF_TOKEN", "")
device = "cpu"  # Force CPU for consistent fast performance

# Force fast mode to skip heavy model loading
FAST_MODE = True  # Override to always use fast mode

# Initialize AI APIs
openai_client = None
if OPENAI_AVAILABLE and openai_api_key:
    openai_client = openai.OpenAI(api_key=openai_api_key)

if GOOGLE_AVAILABLE and google_api_key:
    genai.configure(api_key=google_api_key)

if SPELL_AVAILABLE:
    spell_checker = SpellChecker()
else:
    spell_checker = None

# --- AI Integration Functions ---

class MultiAIProcessor:
    def __init__(self):
        self.openai_available = OPENAI_AVAILABLE and openai_api_key
        self.google_available = GOOGLE_AVAILABLE and google_api_key
        self.granite_model = None
        self.granite_tokenizer = None
        
    async def get_openai_response(self, question: str, context: str) -> Dict[str, Any]:
        """Get response from OpenAI GPT models"""
        if not self.openai_available or openai_client is None:
            return {"error": "OpenAI not available", "response": ""}
        
        try:
            prompt = f"""Based on the following PDF content, answer the question accurately and comprehensively.

Context from PDF:
{context}

Question: {question}

Please provide a detailed, accurate answer based on the PDF content. If the information isn't in the PDF, mention that clearly."""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that answers questions based on PDF documents. Provide accurate, detailed responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "model": "GPT-3.5-turbo",
                "tokens_used": response.usage.total_tokens,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "response": "", "success": False}
    
    async def get_gemini_response(self, question: str, context: str) -> Dict[str, Any]:
        """Get response from Google Gemini"""
        if not self.google_available:
            return {"error": "Gemini not available", "response": ""}
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""Based on the following PDF content, answer the question accurately and comprehensively.

Context from PDF:
{context}

Question: {question}

Please provide a detailed, accurate answer based on the PDF content. If the information isn't in the PDF, mention that clearly."""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.3,
                )
            )
            
            return {
                "response": response.text,
                "model": "Gemini Pro",
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "response": "", "success": False}
    
    def get_granite_response(self, question: str, context: str) -> Dict[str, Any]:
        """Fast lightweight response for speed optimization"""
        try:
            # Input validation
            if not question.strip():
                return {"error": "Empty question provided", "response": "", "success": False}
            
            if not context.strip():
                context = "No specific context provided."
            
            # Fast response using simple text processing
            try:
                # Extract key information from context
                context_sentences = context.split('.')[:5]  # First 5 sentences only
                question_keywords = [word.lower() for word in question.split() if len(word) > 3]
                
                # Find most relevant sentence
                relevant_sentences = []
                for sentence in context_sentences:
                    if sentence.strip():
                        sentence_lower = sentence.lower()
                        keyword_matches = sum(1 for keyword in question_keywords if keyword in sentence_lower)
                        if keyword_matches > 0:
                            relevant_sentences.append((sentence.strip(), keyword_matches))
                
                # Sort by relevance and take best matches
                if relevant_sentences:
                    relevant_sentences.sort(key=lambda x: x[1], reverse=True)
                    best_sentences = [sent[0] for sent in relevant_sentences[:2]]
                    answer = f"Based on the document: {' '.join(best_sentences)}"
                else:
                    # Generate a basic response
                    context_words = context.split()[:30]  # First 30 words
                    answer = f"Regarding your question about '{question[:50]}...': The document contains information about {' '.join(context_words)}. Please ask more specific questions for detailed answers."
                
                return {
                    "response": answer,
                    "model": "Fast AI",
                    "success": True
                }
                
            except Exception as e:
                return {"error": f"Processing error: {e}", "response": "", "success": False}
                    
        except Exception as e:
            return {"error": f"Unexpected error: {e}", "response": "", "success": False}
    
    def load_granite_model(self):
        """Fast mode - skip heavy model loading completely"""
        try:
            if FAST_MODE:
                st.info("⚡ Fast mode enabled - using lightweight processing")
                self.granite_model = "fast_mode"
                self.granite_tokenizer = "fast_mode"
                return
            
            # Original heavy loading code (now skipped in fast mode)
            st.info("⚡ Using fast AI mode - skipping heavy model loading for speed")
            self.granite_model = "fast_mode"
            self.granite_tokenizer = "fast_mode"
            
        except Exception as e:
            st.error(f"❌ Error in fast mode setup: {e}")
    
    async def get_optimized_answer(self, question: str, context: str, selected_models: List[str]) -> Dict[str, Any]:
        """Get optimized answer by combining multiple AI responses"""
        responses = {}
        
        # Get responses from selected models
        if "OpenAI" in selected_models:
            responses["OpenAI"] = await self.get_openai_response(question, context)
        
        if "Gemini" in selected_models:
            responses["Gemini"] = await self.get_gemini_response(question, context)
        
        if "Granite" in selected_models:
            responses["Granite"] = self.get_granite_response(question, context)
        
        # Combine and optimize responses
        successful_responses = {k: v for k, v in responses.items() if v.get("success", False)}
        
        if not successful_responses:
            return {"error": "No AI models could process the question", "responses": responses}
        
        # If multiple responses, create an optimized combined answer
        if len(successful_responses) > 1:
            combined_response = self.combine_responses(successful_responses, question)
            return {
                "optimized_response": combined_response,
                "individual_responses": responses,
                "success": True
            }
        else:
            # Single response
            model_name = list(successful_responses.keys())[0]
            return {
                "optimized_response": successful_responses[model_name]["response"],
                "individual_responses": responses,
                "primary_model": model_name,
                "success": True
            }
    
    def combine_responses(self, responses: Dict[str, Dict], question: str) -> str:
        """Combine multiple AI responses into an optimized answer"""
        combined = f"**Comprehensive Answer (Combined from {', '.join(responses.keys())}):**\n\n"
        
        # Extract key points from each response
        for model, response_data in responses.items():
            response_text = response_data.get("response", "")
            if response_text:
                combined += f"**{model} Insights:**\n{response_text}\n\n"
        
        return combined

# Initialize AI processor
ai_processor = MultiAIProcessor()

# --- Core Functions ---

def correct_spelling(text: str) -> tuple:
    """Corrects spelling mistakes in the input text."""
    if not SPELL_AVAILABLE or not spell_checker:
        return text, []
    
    try:
        blob = TextBlob(text)
        corrected_text = str(blob.correct())
        
        words = text.split()
        suggestions = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word and clean_word not in spell_checker:
                possible_corrections = spell_checker.candidates(clean_word)
                if possible_corrections:
                    suggestions.append({
                        'original': word,
                        'suggestions': list(possible_corrections)[:3]
                    })
        
        return corrected_text, suggestions
    except Exception:
        return text, []

def quick_grammar_check(text: str) -> str:
    """Fast grammar checking using LLM for better accuracy"""
    if not text or len(text.strip()) < 5:
        return text
    
    try:
        # Quick grammar fixes using TextBlob
        if SPELL_AVAILABLE and TextBlob:
            blob = TextBlob(text)
            corrected = str(blob.correct())
            
            # Additional quick fixes
            corrected = re.sub(r'\bi\b', 'I', corrected)  # Fix lowercase 'i'
            corrected = re.sub(r'\s+', ' ', corrected)    # Fix multiple spaces
            corrected = corrected.strip()
            
            return corrected
        else:
            return text
    except Exception:
        return text

@st.cache_resource
def get_embedding_model():
    """Loads a lightweight embedding model optimized for speed."""
    try:
        if FAST_MODE:
            # Skip heavy embedding model in fast mode
            return "fast_mode"
        
        if not SENTENCE_TRANSFORMERS_AVAILABLE or SentenceTransformer is None:
            st.error("❌ SentenceTransformers not available. Using fast mode.")
            return "fast_mode"
        
        # Use the smallest, fastest model available
        model_name = 'all-MiniLM-L6-v2'  # Keep this as it's already fast
        model = SentenceTransformer(model_name, device='cpu')  # Force CPU
        
        if model is None:
            return "fast_mode"
        return model
    except Exception as e:
        st.warning(f"Embedding model failed, using fast mode: {e}")
        return "fast_mode"

def extract_text_from_pdf(pdf_file) -> List[str]:
    """Extracts text from uploaded PDF file."""
    try:
        # Validate input
        if pdf_file is None:
            st.error("No PDF file provided")
            return []
        
        # Read PDF content
        pdf_content = pdf_file.read()
        if not pdf_content:
            st.error("PDF file is empty")
            return []
        
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text_chunks = []
        
        # Validate document
        if doc.page_count == 0:
            st.error("PDF has no pages")
            doc.close()
            return []
        
        for page_num in range(doc.page_count):
            try:
                page = doc[page_num]
                text = page.get_text()
                
                if not text or text.strip() == "":
                    continue  # Skip empty pages
                
                # Split into manageable chunks
                sentences = re.split(r'[.!?]+', text)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(current_chunk) + len(sentence) < 500:
                        current_chunk += sentence + ". "
                    elif current_chunk:
                        text_chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". " if sentence else ""
                
                if current_chunk:
                    text_chunks.append(current_chunk.strip())
                    
            except Exception as e:
                st.warning(f"Error processing page {page_num + 1}: {e}")
                continue
        
        doc.close()
        
        # Filter out very short chunks
        valid_chunks = [chunk for chunk in text_chunks if len(chunk.strip()) > 20]
        
        if not valid_chunks:
            st.error("No valid text content found in PDF")
            return []
        
        return valid_chunks
        
    except ValueError as e:
        st.error(f"ValueError extracting text from PDF: {e}")
        return []
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return []

def create_embeddings(text_chunks: List[str], embedding_model):
    """Creates FAISS embeddings for text chunks with speed optimization."""
    try:
        if not FAISS_AVAILABLE or faiss is None:
            st.error("❌ FAISS not available. Please install faiss-cpu or faiss-gpu")
            return None
            
        # Validate input
        if not text_chunks:
            st.error("No text chunks provided for embedding creation")
            return None
        
        if len(text_chunks) == 0:
            st.error("Empty text chunks list")
            return None
        
        # Filter out empty or very short chunks and limit for speed
        valid_chunks = [chunk for chunk in text_chunks if chunk and len(chunk.strip()) > 10]
        if not valid_chunks:
            st.error("No valid text chunks found (all chunks too short)")
            return None
        
        # Limit chunks for faster processing
        if len(valid_chunks) > 50:
            valid_chunks = valid_chunks[:50]  # Limit to 50 chunks for speed
        
        if embedding_model is None:
            st.error("❌ Embedding model not available")
            return None
            
        # Create embeddings without progress bar for speed
        embeddings = embedding_model.encode(valid_chunks, show_progress_bar=False, batch_size=8)
        
        # Validate embeddings
        if embeddings is None or embeddings.size == 0:
            st.error("Failed to create embeddings - empty result")
            return None
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        if dimension <= 0:
            st.error(f"Invalid embedding dimension: {dimension}")
            return None
            
        index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        return index
    except ValueError as e:
        st.error(f"ValueError in creating embeddings: {e}")
        return None
    except Exception as e:
        st.error(f"Error creating embeddings: {e}")
        return None

def find_similar_text(query: str, text_chunks: List[str], embedding_model, index, k: int = 3) -> List[str]:
    """Finds the most similar text chunks to the query with speed optimization."""
    try:
        # Validate inputs
        if not query or not query.strip():
            st.error("Empty query provided")
            return []
        
        if not text_chunks:
            st.error("No text chunks available")
            return []
        
        if index is None:
            st.error("No embeddings index available")
            return []
        
        # Ensure k doesn't exceed available chunks and is small for speed
        k = min(k, len(text_chunks), index.ntotal, 3)  # Max 3 for speed
        if k <= 0:
            st.error("No valid chunks to search")
            return []
        
        # Fast query encoding
        query_embedding = embedding_model.encode([query], show_progress_bar=False)
        if query_embedding is None or query_embedding.size == 0:
            st.error("Failed to encode query")
            return []
            
        faiss.normalize_L2(query_embedding)
        
        # Search for similar chunks
        scores, indices = index.search(query_embedding.astype('float32'), k)
        
        # Validate search results
        if scores is None or indices is None:
            st.error("Search failed to return results")
            return []
        
        if len(scores) == 0 or len(indices) == 0:
            st.warning("No similar text found")
            return []
        
        # Quick filtering and ranking for speed
        similar_chunks = []
        
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            # Validate index bounds
            if idx < 0 or idx >= len(text_chunks):
                continue
                
            if score > 0.1:  # Minimum similarity threshold
                chunk = text_chunks[idx]
                if chunk and len(chunk.strip()) > 0:
                    similar_chunks.append(chunk)
        
        return similar_chunks[:3]  # Return max 3 for speed
    except ValueError as e:
        st.error(f"ValueError in finding similar text: {e}")
        return []
    except IndexError as e:
        st.error(f"IndexError in finding similar text: {e}")
        return []
    except Exception as e:
        st.error(f"Error finding similar text: {e}")
        return []

# --- Streamlit UI ---

def main():
    # Initialize session state
    init_session_state()
    
    # Check authentication
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # User navigation bar - simplified and cleaner
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown(f"**👋 Welcome, {st.session_state.username}!**")
    with col2:
        # Get user profile info
        user_info = st.session_state.users_db.get(st.session_state.username, {})
        if user_info:
            st.markdown(f"📚 {user_info.get('study_field', 'General')} • 🎓 {user_info.get('grade_level', 'Student')}")
    with col3:
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            logout()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Simplified header
    st.markdown("""
    <div class="main-header">
        <div style="text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; display: flex; align-items: center; justify-content: center; gap: 15px;">
                <span>🧠</span> StudyMate Pro <span>📚</span>
            </h1>
            <p style="margin: 10px 0; font-size: 1.1rem; opacity: 0.9;">Your AI-Powered Learning Companion</p>
            <div style="font-size: 1.2rem; margin-top: 15px;">
                🤖 Multi-AI • 📄 PDF Processing • ⚡ Fast Analysis • 🎓 Academic Focus
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for AI model selection
    with st.sidebar:
        st.markdown("### 🤖 AI Models Configuration")
        
        # Model availability status
        st.markdown("#### Available Models:")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("OpenAI GPT-3.5")
        with col2:
            if ai_processor.openai_available:
                st.success("✅")
            else:
                st.error("❌")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("Google Gemini")
        with col2:
            if ai_processor.google_available:
                st.success("✅")
            else:
                st.error("❌")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("IBM Granite")
        with col2:
            st.success("✅")
        
        st.markdown("---")
        
        # Model selection
        available_models = []
        if ai_processor.openai_available:
            available_models.append("OpenAI")
        if ai_processor.google_available:
            available_models.append("Gemini")
        available_models.append("Granite")
        
        selected_models = st.multiselect(
            "Select AI Models to Use:",
            available_models,
            default=available_models,
            help="Choose which AI models to use for answering questions"
        )
        
        # API Key status
        st.markdown("#### API Configuration:")
        if not ai_processor.openai_available:
            st.warning("⚠️ Add OPENAI_API_KEY to .env for GPT access")
        if not ai_processor.google_available:
            st.warning("⚠️ Add GOOGLE_API_KEY to .env for Gemini access")
        
        st.markdown("---")
        st.markdown("#### Features:")
        st.markdown("✅ PDF Processing")
        st.markdown("✅ Multi-AI Integration")
        st.markdown("✅ Spell Checking")
        st.markdown("✅ Smart Search")
        st.markdown("✅ Response Optimization")
        
        # Learning motivation section
        st.markdown("---")
        st.markdown("### 🌟 Learning Journey")
        
        motivational_quotes = [
            "📚 Every expert was once a beginner",
            "🧠 Learning never exhausts the mind",
            "⚡ Knowledge is power",
            "🎯 Focus on progress, not perfection",
            "🚀 The best time to learn is now",
            "💡 Questions are the beginning of wisdom"
        ]
        
        if 'daily_quote' not in st.session_state:
            st.session_state.daily_quote = random.choice(motivational_quotes)
        
        st.markdown(f"*{st.session_state.daily_quote}*")
        
        # Study stats (mock data for demo)
        st.markdown("#### 📊 Your Progress")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("PDFs Analyzed", "📄", delta="Today")
        with col2:
            st.metric("Questions Asked", "❓", delta="This session")
        
        # Quick tips
        st.markdown("#### 💡 Pro Tips")
        st.markdown("""
        • Upload textbooks, research papers, or notes
        • Ask specific questions for better answers
        • Use multiple AI models for different perspectives
        • Break complex topics into smaller questions
        """)
        
        # Learning resources
        st.markdown("#### 🎓 Study Resources")
        st.markdown("🔗 [Khan Academy](https://khanacademy.org)")
        st.markdown("🔗 [Coursera](https://coursera.org)")
        st.markdown("🔗 [MIT OpenCourseWare](https://ocw.mit.edu)")
        
        # Footer with branding
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>🧠 <strong>StudyMate Pro</strong></p>
            <p>Empowering Learning with AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content area
    # PDF Upload Section
    st.markdown("### 📄 Upload Your PDF Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload a PDF document to analyze and ask questions about",
        label_visibility="collapsed"
    )
    
    # Initialize session state
    if "text_chunks" not in st.session_state:
        st.session_state.text_chunks = []
    if "embeddings_index" not in st.session_state:
        st.session_state.embeddings_index = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Process uploaded PDF
    if uploaded_file is not None:
        try:
            with st.spinner("⚡ Fast processing PDF..."):
                # Get embedding model with fast mode support
                embedding_model = get_embedding_model()
                
                # Extract text with speed optimization
                text_chunks = extract_text_from_pdf(uploaded_file)
                if not text_chunks:
                    st.error("❌ No text could be extracted from the PDF")
                    return
                
                # Create embeddings only if not in fast mode
                if embedding_model != "fast_mode" and embedding_model is not None:
                    embeddings_index = create_embeddings(text_chunks, embedding_model)
                    if embeddings_index is None:
                        st.warning("⚠️ Embeddings failed, using fast text search")
                        embeddings_index = "fast_mode"
                else:
                    embeddings_index = "fast_mode"
                
                # Update session state
                st.session_state.text_chunks = text_chunks
                st.session_state.embeddings_index = embeddings_index
                
                st.success(f"✅ PDF processed successfully! Found {len(text_chunks)} text sections.")
                
                # Show document stats
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📖 Text Sections", len(text_chunks))
                with col2:
                    mode = "⚡ Fast Mode" if FAST_MODE else "🔄 Standard Mode"
                    st.metric("🤖 Processing Mode", mode)
                    
        except Exception as e:
            st.error(f"❌ Error processing PDF: {e}")
            import traceback
            st.error(f"Details: {traceback.format_exc()}")
    
    # ChatGPT-like Question Interface
    st.markdown("### 💬 Ask Your Question")
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    if st.session_state.chat_history:
        for i, (question, response, models_used) in enumerate(st.session_state.chat_history):
            # User question
            st.markdown(f"""
            <div style="background: #f0f4ff; padding: 1rem; border-radius: 12px; margin: 0.5rem 0; border-left: 4px solid #667eea;">
                <strong>You:</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            # AI response
            models_badges = []
            for model in models_used:
                if "Fast AI" in model and "Detailed" in model:
                    badge_class = "detailed"
                elif "Fast AI" in model:
                    badge_class = "fast" 
                elif "OpenAI" in model:
                    badge_class = "openai"
                elif "Gemini" in model:
                    badge_class = "gemini"
                else:
                    badge_class = "granite"
                models_badges.append(f'<span class="ai-badge {badge_class}-badge">{model}</span>')
            models_badges_html = " ".join(models_badges)
            st.markdown(f"""
            <div class="ai-response-container">
                <div style="margin-bottom: 1rem;">{models_badges_html}</div>
                <div>{response}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Get default value for question input
    default_question = ""
    if hasattr(st.session_state, 'corrected_question') and st.session_state.corrected_question:
        default_question = st.session_state.corrected_question
        # Clear the corrected question after using it
        st.session_state.corrected_question = ""
    
    # Question input with enhanced styling and auto grammar check
    question = st.text_area(
        "Type your question here...",
        value=default_question,
        placeholder="Ask anything about your uploaded PDF document...",
        height=100,
        key="question_input",
        label_visibility="collapsed"
    )
    
    # Auto grammar check and suggestions
    if question and len(question.strip()) > 3:
        corrected_question = quick_grammar_check(question)
        if corrected_question != question and SPELL_AVAILABLE:
            st.markdown(f"""
            <div class="spell-suggestion">
                <strong>💡 Grammar & Spelling Suggestions:</strong><br>
                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 5px 0;">
                    <strong>Original:</strong> {question}<br>
                    <strong>Improved:</strong> {corrected_question}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("✨ Use Improved Version", key="grammar_fix"):
                # Store the corrected question in a different session state key
                st.session_state.corrected_question = corrected_question
                st.info(f"✅ Updated question: {corrected_question}")
                st.rerun()
    
    # Spell check for individual words
    if question and SPELL_AVAILABLE:
        corrected_text, suggestions = correct_spelling(question)
        if suggestions:
            st.markdown(f"""
            <div class="spell-suggestion">
                <strong>🔤 Word Suggestions:</strong><br>
            """, unsafe_allow_html=True)
            for suggestion in suggestions[:3]:  # Show max 3 suggestions
                st.write(f"• **{suggestion['original']}** → {', '.join(suggestion['suggestions'][:2])}")
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Process question with different mark allocations
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        if st.button("🚀 Get AI Answer", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("⚠️ Please enter a question")
            elif not st.session_state.text_chunks:
                st.warning("⚠️ Please upload a PDF document first")
            elif not selected_models:
                st.warning("⚠️ Please select at least one AI model")
            else:
                process_question(question, selected_models)
    
    with col2:
        if st.button("📝 7 Marks", use_container_width=True, help="Get structured answers: Introduction (1) + Main Points (5) + Conclusion (1) = 7 marks"):
            if not question.strip():
                st.warning("⚠️ Please enter a question")
            elif not st.session_state.text_chunks:
                st.warning("⚠️ Please upload a PDF document first")
            else:
                process_question_marks(question, 7)
    
    with col3:
        if st.button("📊 14 Marks", use_container_width=True, help="Get detailed answers: Introduction (2) + Analysis (8) + Evaluation (3) + Conclusion (1) = 14 marks"):
            if not question.strip():
                st.warning("⚠️ Please enter a question")
            elif not st.session_state.text_chunks:
                st.warning("⚠️ Please upload a PDF document first")
            else:
                process_question_marks(question, 14)
    
    with col4:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

async def process_question_async(question: str, selected_models: List[str]):
    """Process question with selected AI models"""
    embedding_model = get_embedding_model()
    
    # Find relevant context
    context_chunks = find_similar_text(
        question, 
        st.session_state.text_chunks, 
        embedding_model, 
        st.session_state.embeddings_index, 
        k=5
    )
    context = "\n".join(context_chunks)
    
    # Get AI response
    result = await ai_processor.get_optimized_answer(question, context, selected_models)
    
    if result.get("success"):
        response = result.get("optimized_response", "No response generated")
        models_used = selected_models
        
        # Add to chat history
        st.session_state.chat_history.append((question, response, models_used))
        
        return response, models_used, result.get("individual_responses", {})
    else:
        error_msg = result.get("error", "Unknown error occurred")
        st.error(f"❌ Error: {error_msg}")
        return None, None, None

def process_question_marks(question: str, marks: int):
    """Process question with specific mark allocation (7 or 14 marks)"""
    try:
        if not question or not question.strip():
            st.error("❌ Please provide a valid question")
            return
        
        if not hasattr(st.session_state, 'text_chunks') or not st.session_state.text_chunks:
            st.error("❌ No PDF content available. Please upload a PDF first.")
            return
        
        with st.spinner(f"⚡ Generating {marks}-mark structured answer..."):
            # Get embedding model and handle fast mode
            embedding_model = get_embedding_model()
            
            # Enhanced context search based on marks
            if embedding_model == "fast_mode" or st.session_state.embeddings_index == "fast_mode":
                # Fast mode: Simple keyword-based search
                question_keywords = [word.lower() for word in question.split() if len(word) > 3]
                relevant_chunks = []
                
                # More chunks for higher marks
                chunk_limit = 20 if marks == 7 else 30
                context_limit = 3 if marks == 7 else 4
                
                # Search through chunks for relevant content
                for chunk in st.session_state.text_chunks[:chunk_limit]:
                    chunk_lower = chunk.lower()
                    matches = sum(1 for keyword in question_keywords if keyword in chunk_lower)
                    if matches > 0:
                        relevant_chunks.append((chunk, matches))
                
                # Sort by relevance and take appropriate number of chunks
                relevant_chunks.sort(key=lambda x: x[1], reverse=True)
                context = ' '.join([chunk[0] for chunk in relevant_chunks[:context_limit]])
                
                if not context:
                    context = ' '.join(st.session_state.text_chunks[:context_limit])
            else:
                # Use embedding-based search if available
                try:
                    context_chunks = find_similar_text(
                        question, 
                        st.session_state.text_chunks, 
                        embedding_model, 
                        st.session_state.embeddings_index, 
                        k=4 if marks == 14 else 3
                    )
                    context = "\n".join(context_chunks) if context_chunks else ' '.join(st.session_state.text_chunks[:3])
                except Exception as e:
                    # Fallback to simple search if embedding search fails
                    st.warning(f"Embedding search failed, using fast mode: {e}")
                    context = ' '.join(st.session_state.text_chunks[:4 if marks == 14 else 3])
            
            # Generate answer based on mark allocation
            if marks == 7:
                response = generate_7_mark_answer(question, context)
                model_name = "7-Mark Structured Answer"
            elif marks == 14:
                response = generate_14_mark_answer(question, context)
                model_name = "14-Mark Comprehensive Answer"
            else:
                st.error("❌ Unsupported mark allocation")
                return
            
            # Check response and handle errors
            if response and response.get("success"):
                structured_answer = response.get("response", "No response generated")
                st.session_state.chat_history.append((question, structured_answer, [model_name]))
                
                # Rerun to update the chat display
                st.rerun()
            else:
                error_detail = response.get("error", "Unknown error") if response else "No response generated"
                st.error(f"❌ Failed to generate {marks}-mark answer: {error_detail}")
                
    except Exception as e:
        st.error(f"❌ Error generating {marks}-mark answer: {e}")
        import traceback
        st.error(f"Debug details: {traceback.format_exc()}")

def generate_7_mark_answer(question: str, context: str) -> Dict[str, Any]:
    """Generate structured 7-mark answers"""
    try:
        if not question.strip():
            return {"error": "Empty question", "response": "", "success": False}
        
        if not context.strip():
            context = "Limited context available from document."
        
        # Build 7-mark answer structure
        answer_parts = []
        
        # 1. Introduction (1 mark)
        intro = f"**Question:** {question}\n\n"
        intro += f"**Introduction:** This question requires an examination of the key concepts presented in the document.\n\n"
        answer_parts.append(intro)
        
        # 2. Main Content (5 marks)
        main_content = "**Main Analysis:**\n\n"
        
        # Extract relevant information
        try:
            context_sentences = context.split('.')
            question_keywords = [word.lower() for word in question.split() if len(word) > 3]
            
            relevant_info = []
            for sentence in context_sentences[:8]:
                if sentence.strip():
                    sentence_lower = sentence.lower()
                    keyword_matches = sum(1 for keyword in question_keywords if keyword in sentence_lower)
                    if keyword_matches > 0:
                        relevant_info.append((sentence.strip(), keyword_matches))
            
            if relevant_info:
                relevant_info.sort(key=lambda x: x[1], reverse=True)
                
                # Create 3 main points for 5 marks
                for i, (sentence, matches) in enumerate(relevant_info[:3], 1):
                    main_content += f"**Point {i}:** {sentence}\n\n"
                    if i < 3:  # Add brief explanation for first 2 points
                        main_content += f"*This demonstrates the key relationship between the concepts discussed.*\n\n"
            else:
                # Fallback content
                context_words = context.split()[:80]
                main_content += f"**Key Information:** The document provides information about {' '.join(context_words)}...\n\n"
                main_content += f"**Analysis:** The content shows important relationships between the discussed concepts.\n\n"
                main_content += f"**Significance:** These points are relevant to understanding the core topic.\n\n"
        except Exception as e:
            # Emergency fallback if context processing fails
            main_content += f"**Main Analysis:** Based on the available document content, this question addresses important concepts "
            main_content += f"related to the topic. The key points include fundamental principles and their practical applications.\n\n"
            main_content += f"**Key Insights:** The document provides comprehensive coverage of the subject matter with relevant examples and explanations.\n\n"
            main_content += f"**Detailed Examination:** The analysis shows the interconnected nature of the concepts and their significance in understanding the broader topic.\n\n"
        
        answer_parts.append(main_content)
        
        # 3. Conclusion (1 mark)
        conclusion = "**Conclusion:**\n\n"
        conclusion += f"In summary, the document provides valuable insights that address the question. "
        conclusion += f"The analysis demonstrates understanding of the key concepts and their practical applications.\n\n"
        conclusion += f"**Mark Allocation:** Introduction (1) + Main Analysis (5) + Conclusion (1) = **7 Marks**"
        answer_parts.append(conclusion)
        
        final_answer = "".join(answer_parts)
        
        return {
            "response": final_answer,
            "model": "7-Mark Structured Answer",
            "success": True
        }
        
    except Exception as e:
        return {"error": f"Processing error: {e}", "response": "", "success": False}

def generate_14_mark_answer(question: str, context: str) -> Dict[str, Any]:
    """Generate detailed 14-mark answers"""
    try:
        if not question.strip():
            return {"error": "Empty question", "response": "", "success": False}
        
        if not context.strip():
            context = "Limited context available from document."
        
        # Build comprehensive 14-mark answer structure
        answer_parts = []
        
        # 1. Introduction (2 marks)
        intro = f"**Question Analysis:** {question}\n\n"
        intro += f"**Introduction:** This question requires a comprehensive examination of the key concepts and their interrelationships. "
        intro += f"The analysis will consider multiple perspectives and provide detailed evidence from the document to support the discussion.\n\n"
        answer_parts.append(intro)
        
        # 2. Main Content Analysis (8 marks)
        main_content = "**Detailed Analysis:**\n\n"
        
        # Extract key information from context with error handling
        try:
            context_sentences = context.split('.')
            question_keywords = [word.lower() for word in question.split() if len(word) > 3]
            
            # Find most relevant information
            relevant_info = []
            for sentence in context_sentences[:12]:
                if sentence.strip():
                    sentence_lower = sentence.lower()
                    keyword_matches = sum(1 for keyword in question_keywords if keyword in sentence_lower)
                    if keyword_matches > 0:
                        relevant_info.append((sentence.strip(), keyword_matches))
            
            # Structure the main content (8 marks)
            if relevant_info:
                relevant_info.sort(key=lambda x: x[1], reverse=True)
                
                # Create 4 detailed sections (2 marks each)
                for i, (sentence, matches) in enumerate(relevant_info[:4], 1):
                    main_content += f"**Section {i}:** {sentence}\n\n"
                    main_content += f"*Detailed Explanation:* This point is crucial because it demonstrates the fundamental principles "
                    main_content += f"underlying the topic. The evidence shows clear connections to the broader themes discussed "
                    main_content += f"in the document and provides essential context for understanding the subject matter.\n\n"
                    
                    main_content += f"*Supporting Evidence:* The information presented aligns with established theories and "
                    main_content += f"provides practical examples that reinforce the key concepts being examined.\n\n"
            else:
                # Fallback comprehensive content
                context_words = context.split()[:120]
                main_content += f"**Primary Analysis:** The document extensively covers {' '.join(context_words[:40])}...\n\n"
                main_content += f"*This analysis reveals fundamental insights into the topic's core principles.*\n\n"
                
                main_content += f"**Secondary Analysis:** Further examination shows {' '.join(context_words[40:80])}...\n\n"
                main_content += f"*These findings demonstrate the complexity and interconnected nature of the subject.*\n\n"
                
                main_content += f"**Tertiary Analysis:** Additional evidence indicates {' '.join(context_words[80:120])}...\n\n"
                main_content += f"*This provides comprehensive coverage of the essential elements required for full understanding.*\n\n"
                
                main_content += f"**Synthesis:** The combined evidence presents a cohesive picture that addresses all aspects of the question.\n\n"
        except Exception as e:
            # Emergency fallback for 14-mark answer
            main_content += f"**Comprehensive Analysis:** This question requires thorough examination of the key concepts presented in the document. "
            main_content += f"The analysis demonstrates deep understanding of the subject matter and its practical applications.\n\n"
            
            main_content += f"**Primary Examination:** The document provides extensive coverage of fundamental principles and their interconnections. "
            main_content += f"This foundation enables comprehensive understanding of the topic's significance.\n\n"
            
            main_content += f"**Secondary Analysis:** Further investigation reveals the complexity and depth of the subject matter. "
            main_content += f"The evidence supports multiple perspectives and demonstrates practical relevance.\n\n"
            
            main_content += f"**Advanced Discussion:** The comprehensive analysis shows how various elements connect to form a coherent understanding "
            main_content += f"of the topic and its broader implications in the field.\n\n"
        
        answer_parts.append(main_content)
        
        # 3. Critical Evaluation (3 marks)
        evaluation = "**Critical Evaluation:**\n\n"
        evaluation += f"**Strengths:** The document provides comprehensive coverage of the topic with detailed explanations "
        evaluation += f"and relevant examples. The information is well-structured and addresses multiple aspects of the question.\n\n"
        evaluation += f"**Limitations:** While thorough, the analysis could benefit from additional contemporary examples "
        evaluation += f"or alternative perspectives to provide a more complete understanding of the topic.\n\n"
        evaluation += f"**Overall Assessment:** The evidence strongly supports the main arguments and provides a solid "
        evaluation += f"foundation for understanding the key concepts and their practical applications.\n\n"
        answer_parts.append(evaluation)
        
        # 4. Conclusion (1 mark)
        conclusion = "**Conclusion:**\n\n"
        conclusion += f"In conclusion, the comprehensive analysis of the document content reveals significant insights "
        conclusion += f"that directly address the question posed. The examination of multiple perspectives and detailed "
        conclusion += f"evidence provides a thorough understanding of the topic and its broader implications for the field.\n\n"
        conclusion += f"**Mark Distribution:** Introduction (2) + Detailed Analysis (8) + Critical Evaluation (3) + Conclusion (1) = **14 Marks**"
        answer_parts.append(conclusion)
        
        # Combine all parts
        final_answer = "".join(answer_parts)
        
        return {
            "response": final_answer,
            "model": "14-Mark Comprehensive Answer",
            "success": True
        }
        
    except Exception as e:
        return {"error": f"Processing error: {e}", "response": "", "success": False}

def process_question_fast(question: str, models: List[str]):
    """Ultra-fast question processing with detailed 14-mark style answers"""
    try:
        if not question or not question.strip():
            st.error("❌ Please provide a valid question")
            return
        
        if not hasattr(st.session_state, 'text_chunks') or not st.session_state.text_chunks:
            st.error("❌ No PDF content available. Please upload a PDF first.")
            return
        
        with st.spinner("⚡ Generating comprehensive fast answer..."):
            # Enhanced context search for better answers
            question_keywords = [word.lower() for word in question.split() if len(word) > 3]
            relevant_chunks = []
            
            # Search through more chunks for comprehensive answers
            for chunk in st.session_state.text_chunks[:30]:  # Increased to 30 chunks
                chunk_lower = chunk.lower()
                matches = sum(1 for keyword in question_keywords if keyword in chunk_lower)
                if matches > 0:
                    relevant_chunks.append((chunk, matches))
            
            # Sort by relevance and take top 4 for more detailed context
            relevant_chunks.sort(key=lambda x: x[1], reverse=True)
            context = ' '.join([chunk[0] for chunk in relevant_chunks[:4]])
            
            if not context:
                context = ' '.join(st.session_state.text_chunks[:4])  # Use first 4 chunks
            
            # Generate enhanced fast response for 14 marks
            response = generate_detailed_fast_answer(question, context)
            
            if response and response.get("success"):
                detailed_answer = response.get("response", "No response generated")
                st.session_state.chat_history.append((question, detailed_answer, ["Fast AI - Detailed"]))
                
                # Rerun to update the chat display
                st.rerun()
            else:
                st.error("❌ Fast processing failed")
                
    except Exception as e:
        st.error(f"❌ Error in fast processing: {e}")

def generate_detailed_fast_answer(question: str, context: str) -> Dict[str, Any]:
    """Generate detailed 14-mark style answers using fast processing"""
    try:
        if not question.strip():
            return {"error": "Empty question", "response": "", "success": False}
        
        if not context.strip():
            context = "Limited context available from document."
        
        # Enhanced answer generation for 14 marks
        try:
            # Extract key concepts and create structured answer
            context_sentences = context.split('.')
            question_keywords = [word.lower() for word in question.split() if len(word) > 3]
            
            # Build comprehensive answer structure
            answer_parts = []
            
            # 1. Introduction (2 marks)
            intro = f"**Question Analysis:** {question}\n\n"
            intro += f"**Introduction:** Based on the document analysis, this question requires a comprehensive examination of the key concepts and their interrelationships.\n\n"
            answer_parts.append(intro)
            
            # 2. Main Content Analysis (8 marks)
            main_content = "**Main Analysis:**\n\n"
            
            # Find most relevant information
            relevant_info = []
            for sentence in context_sentences[:10]:
                if sentence.strip():
                    sentence_lower = sentence.lower()
                    keyword_matches = sum(1 for keyword in question_keywords if keyword in sentence_lower)
                    if keyword_matches > 0:
                        relevant_info.append((sentence.strip(), keyword_matches))
            
            # Sort and structure the main content
            if relevant_info:
                relevant_info.sort(key=lambda x: x[1], reverse=True)
                
                for i, (sentence, matches) in enumerate(relevant_info[:4], 1):
                    main_content += f"**Point {i}:** {sentence}\n\n"
                    
                    # Add explanation for each point
                    main_content += f"*Explanation:* This point is significant because it directly relates to the question's core themes and provides essential context for understanding the topic.\n\n"
            else:
                # Fallback content
                context_words = context.split()[:100]
                main_content += f"**Key Information:** The document discusses {' '.join(context_words)}...\n\n"
                main_content += f"**Analysis:** This information provides important insights relevant to the question asked.\n\n"
            
            answer_parts.append(main_content)
            
            # 3. Critical Evaluation (3 marks)
            evaluation = "**Critical Evaluation:**\n\n"
            evaluation += f"The evidence presented in the document supports multiple perspectives on this topic. "
            evaluation += f"Key strengths include the comprehensive coverage of relevant concepts, while potential limitations "
            evaluation += f"may include the need for additional context or contemporary examples.\n\n"
            answer_parts.append(evaluation)
            
            # 4. Conclusion (1 mark)
            conclusion = "**Conclusion:**\n\n"
            conclusion += f"In conclusion, the analysis of the document content reveals important insights that directly address "
            conclusion += f"the question. The comprehensive examination of the available information provides a solid foundation "
            conclusion += f"for understanding the topic and its implications.\n\n"
            conclusion += f"**Total Marks Structure:** Introduction (2) + Main Analysis (8) + Critical Evaluation (3) + Conclusion (1) = **14 Marks**"
            answer_parts.append(conclusion)
            
            # Combine all parts
            final_answer = "".join(answer_parts)
            
            return {
                "response": final_answer,
                "model": "Fast AI - Detailed (14 Marks)",
                "success": True
            }
            
        except Exception as e:
            return {"error": f"Processing error: {e}", "response": "", "success": False}
                
    except Exception as e:
        return {"error": f"Unexpected error: {e}", "response": "", "success": False}

def process_question(question: str, selected_models: List[str]):
    """Wrapper to handle async processing"""
    try:
        # Validate inputs
        if not question or not question.strip():
            st.error("❌ Please provide a valid question")
            return
        
        if not selected_models:
            st.error("❌ Please select at least one AI model")
            return
        
        if not hasattr(st.session_state, 'text_chunks') or not st.session_state.text_chunks:
            st.error("❌ No PDF content available. Please upload a PDF first.")
            return
        
        if not hasattr(st.session_state, 'embeddings_index') or st.session_state.embeddings_index is None:
            st.error("❌ No embeddings available. Please upload and process a PDF first.")
            return
        
        with st.spinner("🤖 AI models are thinking..."):
            # Show thinking indicator
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("""
            <div class="thinking-indicator">
                <span>AI models processing your question</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Process question synchronously for fast performance
            try:
                embedding_model = get_embedding_model()
                
                # Use fast mode if embedding model is not available
                if embedding_model == "fast_mode" or st.session_state.embeddings_index == "fast_mode":
                    # Fast keyword-based context search
                    question_keywords = [word.lower() for word in question.split() if len(word) > 3]
                    relevant_chunks = []
                    
                    for chunk in st.session_state.text_chunks[:20]:  # Check first 20 chunks only
                        chunk_lower = chunk.lower()
                        matches = sum(1 for keyword in question_keywords if keyword in chunk_lower)
                        if matches > 0:
                            relevant_chunks.append((chunk, matches))
                    
                    # Sort by relevance and take top 3
                    relevant_chunks.sort(key=lambda x: x[1], reverse=True)
                    context = ' '.join([chunk[0] for chunk in relevant_chunks[:3]])
                    
                    if not context:
                        context = ' '.join(st.session_state.text_chunks[:3])  # Use first 3 chunks
                
                else:
                    # Standard embedding-based search
                    context_chunks = find_similar_text(
                        question, 
                        st.session_state.text_chunks, 
                        embedding_model, 
                        st.session_state.embeddings_index, 
                        k=2  # Reduced from 5 to 2 for speed
                    )
                    
                    if not context_chunks:
                        context = ' '.join(st.session_state.text_chunks[:3])
                    else:
                        context = "\n".join(context_chunks)
                
            except Exception as e:
                thinking_placeholder.empty()
                st.error(f"❌ Error finding relevant context: {e}")
                return
            
            # Get responses from each model
            responses = {}
            successful_responses = []
            
            for model in selected_models:
                try:
                    if model == "OpenAI" and ai_processor.openai_available:
                        # Simplified synchronous call
                        response = ai_processor.get_openai_response_sync(question, context)
                        if response and response.get("success"):
                            responses[model] = response
                            successful_responses.append(model)
                    
                    elif model == "Gemini" and ai_processor.google_available:
                        response = ai_processor.get_gemini_response_sync(question, context)
                        if response and response.get("success"):
                            responses[model] = response
                            successful_responses.append(model)
                    
                    elif model == "Granite":
                        response = ai_processor.get_granite_response(question, context)
                        if response and response.get("success"):
                            responses[model] = response
                            successful_responses.append(model)
                except ValueError as e:
                    st.error(f"❌ ValueError with {model}: {e}")
                except Exception as e:
                    st.error(f"❌ Error with {model}: {e}")
            
            thinking_placeholder.empty()
            
            if successful_responses:
                try:
                    # Combine responses if multiple models
                    if len(successful_responses) > 1:
                        combined_response = f"**Multi-AI Response ({', '.join(successful_responses)}):**\n\n"
                        for model in successful_responses:
                            model_response = responses.get(model, {}).get('response', 'No response')
                            combined_response += f"**{model}:**\n{model_response}\n\n"
                    else:
                        model_name = successful_responses[0]
                        combined_response = responses.get(model_name, {}).get('response', 'No response')
                    
                    # Validate response before adding to history
                    if combined_response and len(combined_response.strip()) > 0:
                        # Add to chat history
                        if 'chat_history' not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append((question, combined_response, successful_responses))
                        st.rerun()
                    else:
                        st.error("❌ Generated response is empty")
                        
                except Exception as e:
                    st.error(f"❌ Error processing responses: {e}")
            else:
                st.error("❌ No AI models could process your question. Please check your API keys and try again.")
                
    except Exception as e:
        st.error(f"❌ Unexpected error in process_question: {e}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

# Add synchronous versions of async methods to AI processor
def add_sync_methods():
    def get_openai_response_sync(self, question: str, context: str) -> Dict[str, Any]:
        """Synchronous version of OpenAI response - optimized for speed"""
        if not self.openai_available or openai_client is None:
            return {"error": "OpenAI not available", "response": "", "success": False}
        
        try:
            # Apply grammar checking to question first
            corrected_question = quick_grammar_check(question)
            
            # Use shorter context for faster responses
            context_words = context.split()
            if len(context_words) > 100:
                context = ' '.join(context_words[:100]) + "..."
            
            prompt = f"""Answer this question based on the PDF content:

Context: {context}

Question: {corrected_question}

Answer briefly and accurately:"""

            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Give concise, accurate answers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,  # Reduced from 300 for speed
                temperature=0.2,  # Lower temperature for faster, more focused responses
                stream=False
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "model": "GPT-3.5-turbo",
                "tokens_used": response.usage.total_tokens,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "response": "", "success": False}
    
    def get_gemini_response_sync(self, question: str, context: str) -> Dict[str, Any]:
        """Synchronous version of Gemini response - optimized for speed"""
        if not self.google_available:
            return {"error": "Gemini not available", "response": "", "success": False}
        
        try:
            # Apply grammar checking to question first
            corrected_question = quick_grammar_check(question)
            
            # Use shorter context for faster responses
            context_words = context.split()
            if len(context_words) > 100:
                context = ' '.join(context_words[:100]) + "..."
            
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""Answer this question based on the PDF content:

Context: {context}

Question: {corrected_question}

Answer briefly and accurately:"""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,  # Reduced from 300 for speed
                    temperature=0.2,
                )
            )
            
            return {
                "response": response.text,
                "model": "Gemini Pro",
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "response": "", "success": False}
    
    # Add methods to the class
    MultiAIProcessor.get_openai_response_sync = get_openai_response_sync
    MultiAIProcessor.get_gemini_response_sync = get_gemini_response_sync

add_sync_methods()

def show_statistics():
    """Show application statistics"""
    try:
        if not hasattr(st.session_state, 'chat_history') or not st.session_state.chat_history:
            st.info("📊 No statistics available yet. Start asking questions!")
            return
        
        st.markdown("### 📊 Session Statistics")
        
        try:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Questions Asked", len(st.session_state.chat_history))
            with col2:
                try:
                    total_words = 0
                    for q, r, _ in st.session_state.chat_history:
                        if q and isinstance(q, str):
                            total_words += len(q.split())
                        if r and isinstance(r, str):
                            total_words += len(r.split())
                    st.metric("Total Words", total_words)
                except Exception as e:
                    st.metric("Total Words", "Error")
                    st.warning(f"Error calculating words: {e}")
                    
            with col3:
                try:
                    models_used = set()
                    for _, _, models in st.session_state.chat_history:
                        if models and isinstance(models, (list, tuple)):
                            models_used.update(models)
                    st.metric("AI Models Used", len(models_used))
                except Exception as e:
                    st.metric("AI Models Used", "Error")
                    st.warning(f"Error calculating models: {e}")
        
        except Exception as e:
            st.error(f"Error displaying statistics metrics: {e}")
        
        # Model usage breakdown
        try:
            model_counts = {}
            for _, _, models in st.session_state.chat_history:
                if models and isinstance(models, (list, tuple)):
                    for model in models:
                        if model and isinstance(model, str):
                            model_counts[model] = model_counts.get(model, 0) + 1
            
            if model_counts:
                st.markdown("#### Model Usage:")
                for model, count in model_counts.items():
                    st.write(f"• {model}: {count} responses")
            else:
                st.info("No model usage data available")
                
        except Exception as e:
            st.error(f"Error displaying model usage: {e}")
            
    except Exception as e:
        st.error(f"Unexpected error in show_statistics: {e}")
        import traceback
        st.error(f"Details: {traceback.format_exc()}")

if __name__ == "__main__":
    main()

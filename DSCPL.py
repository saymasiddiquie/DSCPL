import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import random
import json
import requests
from voice_control import VoiceControl

# Add Bible API configuration
BIBLE_API_URL = "https://bible-api.com/"

def create_voice_control_sidebar():
    """Create sidebar for voice control settings"""
    with st.sidebar:
        st.header("Voice Settings")
        
        # Voice control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔊 Speak", key="speak_btn"):
                if st.session_state.voice_control.toggle_mute():
                    st.success("Voice is now ON")
                else:
                    st.error("Voice control not available")
        with col2:
            if st.button("🔇 Mute", key="mute_btn"):
                if st.session_state.voice_control.toggle_mute():
                    st.success("Voice is now OFF")
                else:
                    st.error("Voice control not available")
        
        # Show current mute state
        if st.session_state.voice_control:
            st.write(f"Current state: {'🔊 ON' if not st.session_state.voice_control.is_muted else '🔇 OFF'}")
        else:
            st.write("Voice control not initialized")
        
        # Speech rate slider
        if st.session_state.voice_control:
            rate = st.slider(
                "Speech Rate (words per minute)",
                min_value=100,
                max_value=250,
                value=150,
                step=10,
                key="speech_rate"
            )
            if st.session_state.voice_control.engine:
                st.session_state.voice_control.set_rate(rate)
                st.success(f"Rate set to: {rate}")
        
        # Volume slider
        if st.session_state.voice_control:
            volume = st.slider(
                "Volume",
                min_value=0.0,
                max_value=1.0,
                value=1.0,
                step=0.1,
                key="volume"
            )
            if st.session_state.voice_control.engine:
                st.session_state.voice_control.set_volume(volume)
                st.success(f"Volume set to: {volume}")
        
        # Voice selection
        if st.session_state.voice_control and st.session_state.voice_control.engine:
            try:
                voices = st.session_state.voice_control.engine.getProperty('voices')
                voice_options = {v.name: v.id for v in voices}
                selected_voice = st.selectbox(
                    "Select Voice",
                    options=list(voice_options.keys()),
                    key="voice_select"
                )
                if selected_voice:
                    st.session_state.voice_control.engine.setProperty('voice', voice_options[selected_voice])
                    st.success(f"Voice set to: {selected_voice}")
            except Exception as e:
                st.error(f"Error with voice selection: {str(e)}")

# Add a function to fetch Bible verses
def get_bible_verse(reference):
    try:
        response = requests.get(f"{BIBLE_API_URL}{reference}")
        if response.status_code == 200:
            data = response.json()
            return f"{data['text']} ({data['reference']})"
        return "Verse not found. Please try another reference."
    except:
        return "Verse not found. Please try another reference."

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from llama_cpp import Llama
import os

# Vector store path
DB_FAISS_PATH = "vectorstore/db_bible"

# Initialize local llama model
def get_llama_model():
    """Initialize and return the llama model"""
    try:
        # Define model paths
        model_dir = os.path.join(os.path.dirname(__file__), 'models')
        model_path = os.path.join(model_dir, 'llama-3b.bin')  # Using a smaller model
        
        # Create directories if they don't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Check if model exists
        if not os.path.exists(model_path):
            try:
                # Download a smaller, more reliable model
                st.info("Downloading smaller llama model... This may take a few minutes.")
                import requests
                url = "https://huggingface.co/TheBloke/Llama-3B-GGML/resolve/main/llama-3b.ggmlv3.q4_K_M.bin"
                
                # Download the model
                response = requests.get(url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024 * 1024  # 1 MB chunks
                
                with open(model_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        f.write(data)
                
                st.success("Smaller llama model downloaded successfully!")
            except Exception as download_error:
                st.error(f"⚠️ Error downloading model: {str(download_error)}")
                return None
        
        try:
            # Initialize the model with very conservative settings
            return Llama(
                model_path=model_path,
                n_ctx=512,  # Reduced further for stability
                n_threads=1,  # Minimum threads
                n_batch=64,  # Very small batch size
                n_gpu_layers=0,
                verbose=False,
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.3,
                streaming=False
            )
        except Exception as init_error:
            st.error(f"⚠️ Error initializing model: {str(init_error)}")
            return None
    except Exception as e:
        st.error(f"⚠️ Error in model setup: {str(e)}")
        # Return a fallback function that uses the motivational messages
        return lambda x: get_motivational_message(x.lower())

@st.cache_resource
def get_vectorstore():
    """Get the FAISS vector store"""
    try:
        embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
        return db
    except Exception as e:
        st.error(f"Error loading vector store: {str(e)}")
        return None

def get_motivational_response(prompt, context):
    """Generate a sophisticated response using llama model"""
    try:
        # Get vector store
        vectorstore = get_vectorstore()
        
        # Get relevant verses from vector store
        docs = []
        if vectorstore:
            docs = vectorstore.similarity_search(prompt, k=3)
            
        # Prepare the prompt for the llama model
        system_prompt = """You are DSCPL, a sophisticated, empathetic AI assistant. 
        You provide thoughtful, well-reasoned responses. 
        You are knowledgeable about many topics and can have deep conversations. 
        When discussing Bible-related topics, you can reference relevant verses.
        You maintain a professional yet friendly tone.
        You never make things up or provide incorrect information.
        You avoid repetition in your responses.
        You introduce yourself as DSCPL in responses when appropriate."""
        
        # Build the conversation context
        conversation = f"{system_prompt}\n\nUser: {prompt}\nContext: {context}\n"
        
        # Add relevant verses to the context
        if docs:
            related_verses = "\n\n".join([doc.page_content for doc in docs[:2]])
            if related_verses:
                conversation += f"\nRelevant Bible Verses:\n{related_verses}\n"
        
        # Get response from llama model
        llama = get_llama_model()
        if llama:
            # Generate response with improved parameters
            response = llama(
                conversation,
                max_tokens=500,  # Allow longer responses
                temperature=0.7,
                top_p=0.9,
                repeat_penalty=1.3,  # Increased to prevent repetition
                top_k=40,  # Added to improve diversity
                echo=False
            )
            
            # Get the response text
            if 'choices' in response and len(response['choices']) > 0:
                full_response = response['choices'][0]['text'].strip()
                
                # Remove any repeated sections
                lines = full_response.split('\n')
                unique_lines = []
                seen_lines = set()
                
                for line in lines:
                    if line not in seen_lines:
                        unique_lines.append(line)
                        seen_lines.add(line)
                
                return '\n'.join(unique_lines)
            
            return "I'm having trouble generating a response. Please try again."
        
        # Fall back to motivational message if llama fails
        return get_motivational_message(prompt.lower())
    
    except Exception as e:
        return f"⚠️ I'm having a bit of trouble right now. Error: {str(e)}\n\nPlease try asking your question in a different way!"

def get_motivational_message(topic):
    """Generate a motivational message based on the topic"""
    # Motivational messages for different topics
    messages = {
        "perseverance": "Keep pushing forward, even when it's tough. Every step forward is progress.",
        "faith": "Believe in yourself and your journey. Faith is the first step, even when you don't see the staircase.",
        "love": "Spread kindness and compassion wherever you go. Love is the most powerful force in the universe.",
        "hope": "Never lose hope. The darkest hour of the night comes just before the dawn.",
        "peace": "Find peace within yourself first, and it will radiate to those around you.",
        "motivation": "You have the power within you to achieve great things. Keep moving forward!",
        "inspiration": "Let your dreams inspire you to take action. Every journey begins with a single step.",
        "encouragement": "You're doing better than you think. Keep going, you've got this!",
        "support": "You're not alone. Reach out for support when you need it - it's a sign of strength.",
        "confidence": "Believe in your abilities. You're capable of more than you think.",
        "success": "Success is a journey, not a destination. Enjoy the process and learn from every step.",
        "achievement": "Celebrate your small wins. They're the building blocks of your bigger achievements.",
        "goal": "Set clear goals and take consistent action. Progress is made one step at a time."
    }
    

def main():
    """Main application function"""
    try:
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'voice_control' not in st.session_state:
            st.session_state.voice_control = VoiceControl()
            if st.session_state.voice_control.engine:
                st.session_state.voice_control.is_muted = False
            else:
                st.error("⚠️ Voice control engine not available")

        st.set_page_config(page_title="DSCPL", page_icon="✨")
        st.title("✨ DSCPL — Your Personal Encourager")
        
        create_voice_control_sidebar()
        
        # Show previous messages
        for message in st.session_state.messages:
            st.chat_message(message['role']).markdown(message['content'])

        # Get user input
        prompt = st.chat_input("What's on your mind today? Ask DSCPL for motivation, guidance, or just share your thoughts...")

        # Only respond if there's actual user input
        if prompt:
            st.chat_message('user').markdown(prompt)
            st.session_state.messages.append({'role': 'user', 'content': prompt})

            # Get context from previous messages
            context = "\n".join([msg['content'] for msg in st.session_state.messages if msg['role'] != 'user'])
            
            # Get response
            try:
                # Get response based on prompt and context
                result = get_motivational_response(prompt, context)
                
                # Add to chat history
                st.session_state.messages.append({'role': 'assistant', 'content': result})
                st.chat_message('assistant').markdown(result)
                
                # Speak the response if voice control is available
                if st.session_state.voice_control and st.session_state.voice_control.engine:
                    st.session_state.voice_control.speak(result)
            
            except Exception as e:
                st.error(f"⚠️ Error generating response: {str(e)}")
    
    except Exception as e:
        st.error(f"⚠️ Error in main function: {str(e)}")
        return

if __name__ == "__main__":
    main()
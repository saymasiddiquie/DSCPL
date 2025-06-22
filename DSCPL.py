import os
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import random
import json
import requests
from voice_control import VoiceControl

# Add Bible API configuration
BIBLE_API_URL = "https://bible-api.com/"

# Set page config first
st.set_page_config(page_title="DSCPL", page_icon="✨")

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

# Vector store path
DB_FAISS_PATH = "vectorstore/bible_vectorstore"

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
    """Generate a motivational response using vector store and local Bible data"""
    try:
        # Get vector store
        vectorstore = get_vectorstore()
        if vectorstore:
            docs = vectorstore.similarity_search(prompt, k=3)
            
            # Add relevant Bible verses to the response
            if docs:
                related_verses = "\n\n".join([doc.page_content for doc in docs[:2]])
                if related_verses:
                    return f"🌟 Here are some verses that might inspire you:\n{related_verses}"
        
        # Fall back to motivational message
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
    
    # Return a random message if no specific topic matches
    return random.choice(list(messages.values())) if topic not in messages else messages[topic]


def main():
    """Main application function"""
    try:
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Initialize voice control
        try:
            st.info("Initializing voice control...")
            st.session_state.voice_control = VoiceControl()
            
            if st.session_state.voice_control:
                # Initialize voice control
                if st.session_state.voice_control.initialize():
                    st.success("Voice control initialized successfully")
                    st.info(f"Voice control status: {str(st.session_state.voice_control)}")
                    create_voice_control_sidebar()
                else:
                    # Voice control initialization failed
                    if st.session_state.voice_control.is_cloud:
                        st.info("Voice control is not available on Streamlit Cloud")
                    else:
                        error_msg = st.session_state.voice_control.error_message
                        if error_msg:
                            st.error(f"Voice control error: {error_msg}")
                        else:
                            st.warning("Voice control is not available")
                        st.info("You can still use the app without voice control.")
            else:
                st.error("Failed to initialize voice control object")
                
        except Exception as e:
            st.error(f"Voice control initialization error: {str(e)}")
            st.error(f"Error type: {type(e).__name__}")
            st.error(f"Error details: {str(e)}")
            st.session_state.voice_control = None
            st.info("Voice control is not available. You can still use the app without voice control.")
            return
        
    except Exception as e:
        st.error(f"⚠️ Error in main function: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        st.error(f"Error details: {str(e)}")
        st.session_state.voice_control = None
        return
        
    # Always show the title and main content
    st.title("✨ DSCPL — Your Personal Encourager")
    st.write("Welcome to DSCPL - Your Personal Encourager!")
    st.write("Ask me any question about the Bible or life, and I'll help you find encouragement.")
    
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Get context from previous messages
                    context = "\n".join([msg['content'] for msg in st.session_state.messages if msg['role'] != 'user'])
                    
                    # Get response
                    result = get_motivational_response(prompt, context)
                    st.markdown(result)
                    
                    # Add to chat history
                    st.session_state.messages.append({'role': 'assistant', 'content': result})
                    
                    # Try to speak the response if voice is available
                    if st.session_state.voice_control and st.session_state.voice_control.engine:
                        try:
                            if st.session_state.voice_control.speak(result):
                                st.success("Response spoken successfully")
                            else:
                                st.warning("Failed to speak response")
                        except Exception as speak_error:
                            st.error(f"Error speaking response: {str(speak_error)}")
                            st.info("You can still read the response above")
                except Exception as response_error:
                    st.error(f"Error generating response: {str(response_error)}")
                    st.info("You can still ask another question")
                    st.session_state.messages.append({'role': 'assistant', 'content': f"Error generating response: {str(response_error)}"})
    
if __name__ == "__main__":
    main()
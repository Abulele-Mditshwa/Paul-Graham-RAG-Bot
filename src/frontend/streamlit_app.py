"""
Streamlit Frontend for RAG Chatbot.
"""

import streamlit as st
import sys
from pathlib import Path
from typing import List

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from config import load_config
from models.chat_models import ChatMessage, MessageRole
from services.rag_service import RAGService, ChatSessionManager


class StreamlitRAGApp:
    """Main Streamlit application class."""
    
    def __init__(self):
        self.config = load_config()
        self.rag_service = RAGService(self.config)
        self.session_manager = ChatSessionManager()
        
        # Initialize session state
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = "default"
        
        if "connection_tested" not in st.session_state:
            st.session_state.connection_tested = False
        
        if "system_status" not in st.session_state:
            st.session_state.system_status = None
    
    def render_page_config(self):
        """Configure Streamlit page."""
        st.set_page_config(
            page_title="Paul Graham Essays - RAG Chatbot",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_custom_css(self):
        """Render custom CSS styles."""
        st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            }
            
            .chat-message {
                padding: 1rem;
                margin: 0.5rem 0;
                border-radius: 10px;
                border-left: 4px solid #1f77b4;
            }
            
            .user-message {
                background-color: #e3f2fd;
                border-left-color: #2196f3;
            }
            
            .assistant-message {
                background-color: #f5f5f5;
                border-left-color: #4caf50;
            }
            
            .metrics-container {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            
            .status-success {
                color: #28a745;
                font-weight: bold;
            }
            
            .status-error {
                color: #dc3545;
                font-weight: bold;
            }
            
            .stButton > button {
                background-color: #1f77b4;
                color: white;
                border-radius: 20px;
                border: none;
                padding: 0.5rem 2rem;
                font-weight: bold;
            }
            
            .stButton > button:hover {
                background-color: #1565c0;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def test_system_connection(self):
        """Test system connections and display status."""
        if not st.session_state.connection_tested:
            with st.spinner("Testing system connections..."):
                # Only test Knowledge Base connection
                kb_status = self.rag_service.kb_client.test_connection()
                st.session_state.system_status = {
                    'knowledge_base': kb_status,
                    'config': {
                        'knowledge_base_id': self.config.knowledge_base_id,
                        'model_id': self.config.llm_model_id,
                        'region': self.config.aws_region
                    }
                }
                st.session_state.connection_tested = True
        
        status = st.session_state.system_status
        
        # Knowledge Base Status
        kb_status = status['knowledge_base']
        if kb_status['success']:
            st.success("✅ Knowledge Base Connected")
        else:
            st.error(f"❌ Knowledge Base Error: {kb_status.get('error', 'Unknown error')}")
            return False
        
        return True
    
    def render_sidebar(self):
        """Render the sidebar with system information and controls."""
        with st.sidebar:
            st.header("🤖 RAG System")
            
            # System Status
            st.subheader("System Status")
            if self.test_system_connection():
                status = st.session_state.system_status
                
                with st.expander("📊 System Details", expanded=False):
                    st.write("**Configuration:**")
                    config_info = status['config']
                    st.write(f"- Knowledge Base: `{config_info['knowledge_base_id']}`")
                    st.write(f"- Model: `{config_info['model_id']}`")
                    st.write(f"- Region: `{config_info['region']}`")
                    
                    if status['knowledge_base']['success']:
                        kb_info = status['knowledge_base']
                        st.write("**Performance:**")
                        st.write(f"- Test Response: {kb_info['test_response_length']} chars")
                        st.write(f"- Sources Found: {kb_info['sources_found']}")
            
            # Chat Controls
            st.subheader("Chat Controls")
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                self.session_manager.clear_session(st.session_state.session_id)
                st.rerun()
            
            # RAG Mode Selection - Only show Knowledge Base
            st.subheader("RAG Mode")
            st.info("Using AWS Bedrock Knowledge Base (Integrated)")
            st.session_state.rag_mode = "Knowledge Base (Integrated)"
            
            # Sample Questions
            st.subheader("💡 Sample Questions")
            sample_questions = [
                "What is founder mode and how does it differ from manager mode?",
                "How do you get startup ideas according to Paul Graham?",
                "What are the key principles for doing great work?"
            ]
            
            for question in sample_questions:
                if st.button(question, key=f"sample_{hash(question)}"):
                    self._handle_user_message(question)
                    st.rerun()
    
    def _clean_source_content(self, content: str) -> str:
        """Clean source content by removing URLs, markdown artifacts, and other noise."""
        import re
        
        # Remove URLs
        content = re.sub(r'https?://[^\s\)]+', '', content)
        
        # Remove markdown image syntax
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
        
        # Remove markdown link syntax
        content = re.sub(r'\[.*?\]\(.*?\)', '', content)
        
        # Remove table separators and pipes
        content = re.sub(r'\|+', '', content)
        content = re.sub(r'-+\s*\|', '', content)
        content = re.sub(r'\|\s*-+', '', content)
        
        # Remove excessive whitespace and newlines
        content = re.sub(r'\s+', ' ', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content

    def display_chat_message(self, message: ChatMessage):
        """Display a chat message with proper styling."""
        if message.role == MessageRole.USER:
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message.content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong> {message.content}
            </div>
            """, unsafe_allow_html=True)
            
            # Display sources if available
            if message.sources:
                st.markdown("**Sources:**")
                for i, source in enumerate(message.sources[:3], 1):
                    # Clean the source content first
                    cleaned_content = self._clean_source_content(source.content)
                    source_text = cleaned_content[:120] + "..." if len(cleaned_content) > 120 else cleaned_content
                    
                    # Extract title from source URI or use a generic title
                    source_title = self._extract_title_from_source(source)
                    st.markdown(f"""
                    <div style="margin: 8px 0; padding: 12px; background-color: #f8f9fa; border-left: 3px solid #007bff; border-radius: 4px;">
                        <div style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">{source_title}</div>
                        <div style="font-size: 0.85rem; color: #6c757d; font-style: italic;">Paul Graham Essays</div>
                        <div style="font-size: 0.9rem; color: #495057; margin-top: 6px;">"{source_text}"</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _extract_title_from_source(self, source) -> str:
        """Extract a readable title from the source URI or content."""
        # First try to extract from source URI
        if hasattr(source, 'source_uri') and source.source_uri and source.source_uri != 'Unknown':
            uri = source.source_uri
            if '/' in uri:
                filename = uri.split('/')[-1]
                if filename.endswith('.html'):
                    return self._get_essay_title_from_filename(filename)
        
        # If no URI, try to infer from content
        if hasattr(source, 'content') and source.content:
            content = source.content.lower()
            # Look for key phrases to identify essays
            if 'founder mode' in content:
                return 'Founder Mode'
            elif 'startup idea' in content or 'get startup ideas' in content:
                return 'How to Start a Startup'
            elif 'great work' in content:
                return 'How to Do Great Work'
            elif 'maker\'s schedule' in content or 'manager\'s schedule' in content:
                return "Maker's Schedule, Manager's Schedule"
            elif 'new ideas' in content and 'anomalies' in content:
                return 'How to Get New Ideas'
            elif 'what should one do' in content:
                return 'What to Do'
        
        # Fallback to generic title
        return "Paul Graham Essay"
    
    def _get_essay_title_from_filename(self, filename: str) -> str:
        """Map filename to essay title."""
        title_map = {
            'start.html': 'How to Start a Startup',
            'foundermode.html': 'Founder Mode',
            'greatwork.html': 'How to Do Great Work',
            'getideas.html': 'How to Get New Ideas',
            'makersschedule.html': "Maker's Schedule, Manager's Schedule",
            'do.html': 'What to Do',
            'superlinear.html': 'Superlinear Returns',
            'useful.html': 'How to Write Usefully',
            'think.html': 'How to Think for Yourself',
            'weird.html': 'The Power of the Marginal',
            'worked.html': 'What Worked',
            'want.html': 'What You Want to Want',
            'users.html': 'Do Things that Don\'t Scale',
            'real.html': 'Keep Your Identity Small',
            'persistence.html': 'The Anatomy of Determination',
            'ace.html': 'Beating the Averages',
            'airbnbs.html': 'Airbnb',
            'best.html': 'The Best Essay',
            'conformism.html': 'The Four Quadrants of Conformism',
            'early.html': 'The Equity Equation',
            'field.html': 'The Lesson to Unlearn',
            'goodtaste.html': 'Taste for Makers',
            'goodwriting.html': 'Writing, Briefly',
            'heresy.html': 'What You Can\'t Say',
            'kids.html': 'What I Tell All Parents',
            'mod.html': 'Moderation',
            'newideas.html': 'The Age of the Essay',
            'noob.html': 'Being a Noob',
            'own.html': 'Why to Not Not Start a Startup',
            'read.html': 'The Age of the Essay',
            'richnow.html': 'How to Be Rich',
            'simply.html': 'Simply',
            'smart.html': 'Mean People Fail',
            'writes.html': 'Write Like You Talk'
        }
        return title_map.get(filename, filename.replace('.html', '').replace('-', ' ').title())
    
    def _handle_user_message(self, message: str):
        """
        🎬 USER MESSAGE HANDLER: This function processes every user question
        
        Flow:
        1. User types question in chat input
        2. This function gets called with their message
        3. We save the user message to chat history
        4. We call the RAG service to get AI response
        5. We save the AI response to chat history
        6. Streamlit displays both messages in the UI
        
        Args:
            message: The user's question/message
        """
        # 💾 STEP 1: Save user message to chat history
        user_msg = ChatMessage(role=MessageRole.USER, content=message)
        st.session_state.messages.append(user_msg)  # For UI display
        self.session_manager.add_message(st.session_state.session_id, user_msg)  # For conversation context
        
        # 📚 STEP 2: Get conversation history for context
        # This helps the AI understand what we've been talking about
        chat_history = self.session_manager.get_history(st.session_state.session_id)
        
        # 🤖 STEP 3: Generate AI response using RAG
        try:
            # This is where the magic happens! 
            # The RAG service will:
            # - Search through Paul Graham essays
            # - Find relevant content
            # - Generate an AI response
            # - Return sources used
            response = self.rag_service.chat_with_knowledge_base(message, chat_history[:-1])
            
            # 💾 STEP 4: Save AI response to chat history
            st.session_state.messages.append(response)  # For UI display
            self.session_manager.add_message(st.session_state.session_id, response)  # For conversation context
            
        except Exception as e:
            # 💥 Handle any errors gracefully
            error_msg = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=f"I apologize, but I encountered an error: {str(e)}"
            )
            st.session_state.messages.append(error_msg)
            self.session_manager.add_message(st.session_state.session_id, error_msg)
    
    def render_main_content(self):
        """Render the main chat interface."""
        # Header
        st.markdown('<h1 class="main-header">🤖 Paul Graham Essays RAG Chatbot</h1>', unsafe_allow_html=True)
        
        # Model info
        st.info(f"Powered by **Claude 3 Haiku** via AWS Bedrock Knowledge Base")
        
        # Chat interface
        st.subheader("Chat with Paul Graham's Essays")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                self.display_chat_message(message)
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about Paul Graham's essays..."):
            # Display user message immediately
            with chat_container:
                user_msg = ChatMessage(role=MessageRole.USER, content=prompt)
                self.display_chat_message(user_msg)
            
            # Generate response
            with st.spinner("Searching through Paul Graham's essays..."):
                self._handle_user_message(prompt)
                
                # Display assistant response
                with chat_container:
                    if st.session_state.messages:
                        self.display_chat_message(st.session_state.messages[-1])
    
    def render_footer(self):
        """Render the footer."""
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            Built with AWS Bedrock Knowledge Base and Streamlit
        </div>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Run the Streamlit application."""
        self.render_page_config()
        self.render_custom_css()
        self.render_sidebar()
        self.render_main_content()
        self.render_footer()


def main():
    """Main entry point."""
    app = StreamlitRAGApp()
    app.run()


if __name__ == "__main__":
    main()
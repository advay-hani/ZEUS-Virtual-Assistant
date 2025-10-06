"""
AI Engine for Z.E.U.S. Virtual Assistant

This module provides the core AI functionality including:
- Lightweight model loading (DistilBERT, sentence-transformers)
- Text understanding and response generation
- Document similarity search
- Context management
- Enhanced error handling and user feedback
- Performance monitoring and optimization
"""

import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import threading
import time
import gc

try:
    from transformers import AutoTokenizer, AutoModel, pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    import numpy as np
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers libraries not available. AI features will be limited.")

from .context_manager import ContextManager, ContextType
from .error_handler import ErrorHandler, ErrorCategory, ErrorSeverity, handle_errors, ProgressContext
from .performance_monitor import get_performance_monitor
from .memory_optimizer import get_memory_optimizer


@dataclass
class ConversationContext:
    """Manages conversation context and memory"""
    messages: List[Dict[str, str]]
    document_context: Optional[str] = None
    max_context_length: int = 2000
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AIEngine:
    """
    Core AI engine for Z.E.U.S. Virtual Assistant
    
    Handles model loading, response generation, and context management
    with fallback mechanisms for offline operation and comprehensive error handling.
    """
    
    def __init__(self, model_cache_dir: str = "models", context_manager: Optional[ContextManager] = None, 
                 error_handler: Optional[ErrorHandler] = None):
        """
        Initialize the AI engine
        
        Args:
            model_cache_dir: Directory to cache downloaded models
            context_manager: Optional context manager for cross-feature context
            error_handler: Optional error handler for user feedback
        """
        self.model_cache_dir = model_cache_dir
        self.logger = logging.getLogger(__name__)
        self.error_handler = error_handler
        
        # Model instances
        self.text_model = None
        self.tokenizer = None
        self.sentence_model = None
        self.text_generator = None
        
        # Context management
        self.conversation_context = ConversationContext(messages=[])
        self.context_manager = context_manager or ContextManager()
        
        # Model loading status
        self.models_loaded = False
        self.fallback_mode = False
        self.model_loading_progress = None
        
        # Performance monitoring
        self.response_times = []
        self.max_response_time = 30.0  # seconds
        self.performance_monitor = get_performance_monitor()
        self.memory_optimizer = get_memory_optimizer()
        
        # Model memory management
        self.model_memory_limit_mb = 500  # 500MB limit for AI models
        self.response_cache = {}
        self.cache_max_size = 100
        
        # Create model cache directory with error handling
        try:
            os.makedirs(model_cache_dir, exist_ok=True)
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.FILE_IO, ErrorSeverity.WARNING,
                    custom_message="Could not create model cache directory. Using temporary location.",
                    show_dialog=False
                )
            self.model_cache_dir = "temp_models"
            os.makedirs(self.model_cache_dir, exist_ok=True)
        
        # Register optimization callbacks
        self.performance_monitor.add_optimization_callback(self._handle_performance_optimization)
        self.memory_optimizer.add_optimization_callback(self._handle_memory_optimization)
    
    def load_models(self, show_progress: bool = True) -> bool:
        """
        Load AI models with error handling, progress indication, and fallback mechanisms
        
        Args:
            show_progress: Whether to show progress indicator
            
        Returns:
            bool: True if models loaded successfully, False if using fallback
        """
        if not TRANSFORMERS_AVAILABLE:
            if self.error_handler:
                self.error_handler.handle_warning(
                    "AI dependencies not available. Running in basic mode with limited features.",
                    ErrorCategory.DEPENDENCY,
                    show_dialog=False
                )
            self.logger.warning("Transformers not available, using fallback mode")
            self.fallback_mode = True
            return False
        
        progress = None
        try:
            # Show progress indicator if requested
            if show_progress and self.error_handler:
                progress = self.error_handler.create_progress_indicator("Loading AI Models")
                progress.show("Initializing AI components...", indeterminate=True)
            
            self.logger.info("Loading AI models...")
            
            # Load DistilBERT for text understanding
            model_name = "distilbert-base-uncased"
            self.logger.info(f"Loading {model_name}...")
            
            if progress:
                progress.update_message(f"Loading text understanding model ({model_name})...")
            
            # Add timeout for model loading
            def load_text_model():
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.model_cache_dir
                )
                self.text_model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=self.model_cache_dir
                )
            
            self._run_with_timeout(load_text_model, 60, "Loading text model")
            
            # Load sentence transformer for document similarity
            sentence_model_name = "all-MiniLM-L6-v2"
            self.logger.info(f"Loading {sentence_model_name}...")
            
            if progress:
                progress.update_message(f"Loading document analysis model ({sentence_model_name})...")
            
            def load_sentence_model():
                self.sentence_model = SentenceTransformer(
                    sentence_model_name,
                    cache_folder=self.model_cache_dir
                )
            
            self._run_with_timeout(load_sentence_model, 60, "Loading sentence model")
            
            # Create text generation pipeline
            if progress:
                progress.update_message("Setting up text generation...")
            
            def load_text_generator():
                # Load model and tokenizer separately to avoid cache_dir issues
                from transformers import AutoTokenizer, AutoModelForCausalLM
                
                model = AutoModelForCausalLM.from_pretrained(
                    "distilgpt2",
                    cache_dir=self.model_cache_dir
                )
                tokenizer = AutoTokenizer.from_pretrained(
                    "distilgpt2", 
                    cache_dir=self.model_cache_dir
                )
                
                # Set pad token to eos token if not set
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                self.text_generator = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_length=100,
                    do_sample=True,
                    temperature=0.7
                )
            
            self._run_with_timeout(load_text_generator, 60, "Loading text generator")
            
            self.models_loaded = True
            self.fallback_mode = False
            self.logger.info("AI models loaded successfully")
            
            if progress:
                progress.update_message("AI models loaded successfully!")
                time.sleep(1)  # Brief pause to show success message
            
            return True
            
        except TimeoutError as e:
            error_msg = "Model loading timed out. This may be due to slow internet or system resources."
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.AI_MODEL, ErrorSeverity.WARNING,
                    custom_message=error_msg,
                    custom_recovery=[
                        "Check your internet connection",
                        "Close other applications to free memory",
                        "Try restarting the application",
                        "The application will continue in basic mode"
                    ]
                )
            self.logger.error(f"Model loading timeout: {e}")
            self.fallback_mode = True
            return False
            
        except MemoryError as e:
            error_msg = "Insufficient memory to load AI models. Running in basic mode."
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.MEMORY, ErrorSeverity.WARNING,
                    custom_message=error_msg,
                    custom_recovery=[
                        "Close other applications to free memory",
                        "Restart the application",
                        "Consider upgrading system memory"
                    ]
                )
            self.logger.error(f"Memory error loading models: {e}")
            self.fallback_mode = True
            return False
            
        except Exception as e:
            error_msg = "Failed to load AI models. The application will continue with basic functionality."
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.AI_MODEL, ErrorSeverity.WARNING,
                    custom_message=error_msg,
                    custom_recovery=[
                        "Check internet connection for model downloads",
                        "Verify AI dependencies are installed",
                        "Try restarting the application",
                        "Check available disk space"
                    ]
                )
            self.logger.error(f"Failed to load AI models: {e}")
            self.fallback_mode = True
            return False
            
        finally:
            if progress:
                progress.hide()
    
    def _run_with_timeout(self, func, timeout_seconds: float, operation_name: str):
        """
        Run a function with timeout
        
        Args:
            func: Function to run
            timeout_seconds: Timeout in seconds
            operation_name: Name of operation for error reporting
            
        Raises:
            TimeoutError: If operation times out
        """
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout_seconds)
        
        if thread.is_alive():
            raise TimeoutError(f"{operation_name} timed out after {timeout_seconds} seconds")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    @handle_errors(ErrorCategory.AI_MODEL, ErrorSeverity.ERROR, show_dialog=False)
    def generate_response(self, query: str, context: Optional[str] = None, context_type: Optional[ContextType] = None) -> str:
        """
        Generate a response to a user query with cross-feature context awareness
        
        Args:
            query: User's input query
            context: Optional context (e.g., document content)
            context_type: Type of context for the query
            
        Returns:
            str: Generated response
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not query or not query.strip():
                return "I didn't receive a message. Could you please try again?"
            
            # Check if query is too long
            if len(query) > 2000:
                if self.error_handler:
                    self.error_handler.handle_warning(
                        "Your message is very long. I'll try to process it, but shorter messages work better.",
                        ErrorCategory.USER_INPUT,
                        show_dialog=False
                    )
                query = query[:2000] + "..."
            
            # Get relevant context from context manager
            relevant_context = self.context_manager.get_relevant_context(query, context_type)
            
            if self.fallback_mode:
                response = self._fallback_response(query, context, relevant_context)
                self._update_context(query, response, context_type)
                return response
            
            # Prepare input with enhanced context
            input_text = self._prepare_input_with_context(query, context, relevant_context)
            
            # Generate response using the text generation pipeline with timeout
            if self.text_generator:
                def generate():
                    # Use a simpler prompt format to avoid repetition
                    simple_prompt = f"Human: {query}\nAssistant:"
                    
                    result = self.text_generator(
                        simple_prompt,
                        max_new_tokens=50,  # Use max_new_tokens instead of max_length
                        num_return_sequences=1,
                        pad_token_id=self.text_generator.tokenizer.eos_token_id,
                        do_sample=True,
                        temperature=0.8,
                        top_p=0.9,
                        repetition_penalty=1.2,  # Add repetition penalty
                        no_repeat_ngram_size=3   # Prevent 3-gram repetition
                    )
                    
                    generated_text = result[0]['generated_text']
                    
                    # Extract only the assistant's response
                    if "Assistant:" in generated_text:
                        response = generated_text.split("Assistant:")[-1].strip()
                    else:
                        response = generated_text[len(simple_prompt):].strip()
                    
                    return response
                
                try:
                    response = self._run_with_timeout(generate, self.max_response_time, "Response generation")
                    
                    # Clean up response
                    response = self._clean_response(response)
                    
                    # If response is empty or too short, use fallback
                    if not response or len(response.strip()) < 3:
                        response = self._fallback_response(query, context, relevant_context)
                    
                    # Update conversation context
                    self._update_context(query, response, context_type)
                    
                    # Track response time
                    response_time = time.time() - start_time
                    self.response_times.append(response_time)
                    if len(self.response_times) > 100:
                        self.response_times = self.response_times[-50:]
                    
                    return response
                    
                except TimeoutError:
                    if self.error_handler:
                        self.error_handler.handle_warning(
                            "Response generation is taking longer than expected. Switching to basic mode for this response.",
                            ErrorCategory.AI_MODEL,
                            show_dialog=False
                        )
                    return self._fallback_response(query, context, relevant_context)
            else:
                return self._fallback_response(query, context, relevant_context)
                
        except MemoryError as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.MEMORY, ErrorSeverity.WARNING,
                    custom_message="Running low on memory. Using basic response mode.",
                    custom_recovery=["Close other applications", "Try shorter messages"],
                    show_dialog=False
                )
            return self._fallback_response(query, context, relevant_context)
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.AI_MODEL, ErrorSeverity.ERROR,
                    custom_message="An error occurred while generating a response. Using basic mode.",
                    show_dialog=False
                )
            return self._fallback_response(query, context, relevant_context)
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and validate AI response
        
        Args:
            response: Raw AI response
            
        Returns:
            str: Cleaned response
        """
        if not response:
            return ""
        
        # Remove common AI artifacts and clean up
        response = response.strip()
        
        # Remove common prefixes that might appear
        prefixes_to_remove = [
            "Assistant:", "AI:", "Bot:", "Response:", 
            "Human:", "User:", "\n", "\r"
        ]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()
        
        # Remove repetitive patterns more aggressively
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for repetitive words in the line
            words = line.split()
            if len(words) > 3:
                # Remove lines that are mostly repetitive
                unique_words = set(words)
                if len(unique_words) < len(words) * 0.5:  # More than 50% repetition
                    continue
            
            # Check if this line is very similar to previous lines
            is_repetitive = False
            for prev_line in cleaned_lines[-3:]:  # Check last 3 lines
                if line.lower() == prev_line.lower():
                    is_repetitive = True
                    break
            
            if not is_repetitive:
                cleaned_lines.append(line)
        
        response = ' '.join(cleaned_lines)
        
        # Final cleanup
        response = response.strip()
        
        # Limit response length
        if len(response) > 500:
            # Find a good breaking point
            sentences = response.split('.')
            if len(sentences) > 1:
                # Keep complete sentences up to 500 chars
                result = ""
                for sentence in sentences:
                    if len(result + sentence + '.') <= 500:
                        result += sentence + '.'
                    else:
                        break
                response = result.strip()
            else:
                response = response[:500] + "..."
        
        # If response is too short or empty, return empty to trigger fallback
        if len(response.strip()) < 3:
            return ""
        
        return response
    
    @handle_errors(ErrorCategory.DOCUMENT, ErrorSeverity.ERROR, show_dialog=False)
    def analyze_document_query(self, query: str, document_chunks: List[str]) -> str:
        """
        Analyze a query against document chunks using similarity search
        
        Args:
            query: User's query about the document
            document_chunks: List of document text chunks
            
        Returns:
            str: Response based on relevant document content
        """
        if not document_chunks:
            if self.error_handler:
                self.error_handler.handle_warning(
                    "No document content available for analysis. Please upload a document first.",
                    ErrorCategory.DOCUMENT,
                    show_dialog=False
                )
            return "No document content available to analyze."
        
        # Validate query
        if not query or not query.strip():
            return "Please provide a question about the document."
        
        if len(query) > 1000:
            if self.error_handler:
                self.error_handler.handle_warning(
                    "Your question is very long. I'll analyze the first part.",
                    ErrorCategory.USER_INPUT,
                    show_dialog=False
                )
            query = query[:1000]
        
        if self.fallback_mode or not self.sentence_model:
            return self._fallback_document_response(query, document_chunks)
        
        try:
            # Check if we have too many chunks (performance consideration)
            if len(document_chunks) > 100:
                if self.error_handler:
                    self.error_handler.handle_warning(
                        "Document is very large. Analysis may take longer than usual.",
                        ErrorCategory.DOCUMENT,
                        show_dialog=False
                    )
                # Use only first 100 chunks for performance
                document_chunks = document_chunks[:100]
            
            # Find most relevant chunks using sentence similarity with timeout
            def find_chunks():
                return self._find_relevant_chunks(query, document_chunks)
            
            try:
                relevant_chunks = self._run_with_timeout(find_chunks, 15, "Document similarity search")
            except TimeoutError:
                if self.error_handler:
                    self.error_handler.handle_warning(
                        "Document analysis is taking longer than expected. Using basic search.",
                        ErrorCategory.DOCUMENT,
                        show_dialog=False
                    )
                return self._fallback_document_response(query, document_chunks)
            
            if not relevant_chunks:
                return self._fallback_document_response(query, document_chunks)
            
            # Generate response based on relevant content
            context = " ".join(relevant_chunks[:3])  # Use top 3 chunks
            
            # Limit context size to prevent memory issues
            if len(context) > 2000:
                context = context[:2000] + "..."
            
            response = self.generate_response(query, context, ContextType.DOCUMENT)
            
            return response
            
        except MemoryError as e:
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.MEMORY, ErrorSeverity.WARNING,
                    custom_message="Document is too large for detailed analysis. Using basic search.",
                    custom_recovery=["Try uploading a smaller document", "Close other applications"],
                    show_dialog=False
                )
            return self._fallback_document_response(query, document_chunks)
            
        except Exception as e:
            self.logger.error(f"Error analyzing document query: {e}")
            if self.error_handler:
                self.error_handler.handle_error(
                    e, ErrorCategory.DOCUMENT, ErrorSeverity.ERROR,
                    custom_message="An error occurred during document analysis. Using basic search.",
                    show_dialog=False
                )
            return self._fallback_document_response(query, document_chunks)
    
    def _find_relevant_chunks(self, query: str, chunks: List[str], top_k: int = 5) -> List[str]:
        """
        Find the most relevant document chunks for a query
        
        Args:
            query: Search query
            chunks: List of text chunks
            top_k: Number of top chunks to return
            
        Returns:
            List[str]: Most relevant chunks
        """
        if not self.sentence_model:
            return chunks[:top_k]  # Return first chunks as fallback
        
        try:
            # Encode query and chunks
            query_embedding = self.sentence_model.encode([query])
            chunk_embeddings = self.sentence_model.encode(chunks)
            
            # Calculate similarities
            similarities = np.dot(query_embedding, chunk_embeddings.T)[0]
            
            # Get top-k most similar chunks
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            return [chunks[i] for i in top_indices]
            
        except Exception as e:
            self.logger.error(f"Error finding relevant chunks: {e}")
            return chunks[:top_k]
    
    def _prepare_input(self, query: str, context: Optional[str] = None) -> str:
        """
        Prepare input text with context for generation (legacy method)
        
        Args:
            query: User query
            context: Optional context
            
        Returns:
            str: Formatted input text
        """
        input_parts = []
        
        # Add conversation history (limited)
        recent_messages = self.conversation_context.messages[-6:]  # Last 6 messages (3 exchanges)
        for msg in recent_messages:
            if msg['role'] == 'user':
                input_parts.append(f"User: {msg['content']}")
            else:
                input_parts.append(f"Assistant: {msg['content']}")
        
        # Add document context if available
        if context:
            input_parts.append(f"Context: {context[:500]}...")  # Limit context length
        
        # Add current query
        input_parts.append(f"User: {query}")
        input_parts.append("Assistant:")
        
        return "\n".join(input_parts)
    
    def _prepare_input_with_context(self, query: str, context: Optional[str] = None, 
                                   relevant_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Prepare input text with enhanced cross-feature context
        
        Args:
            query: User query
            context: Optional immediate context
            relevant_context: Cross-feature context from context manager
            
        Returns:
            str: Formatted input text
        """
        input_parts = []
        
        # Add conversation history from context manager
        if relevant_context and relevant_context.get('conversation_history'):
            recent_messages = relevant_context['conversation_history'][-6:]  # Last 6 messages
            for msg in recent_messages:
                if msg['sender'] == 'user':
                    input_parts.append(f"User: {msg['content']}")
                else:
                    input_parts.append(f"Assistant: {msg['content']}")
        
        # Add document context if available
        if relevant_context and relevant_context.get('document_context'):
            doc_context = relevant_context['document_context']
            doc_name = doc_context.get('filename', 'document')
            chunks = doc_context.get('chunks', [])
            if chunks:
                # Use first few chunks as context
                doc_text = " ".join(chunks[:2])[:500]
                input_parts.append(f"Document '{doc_name}' context: {doc_text}...")
        
        # Add immediate context if provided
        if context:
            input_parts.append(f"Context: {context[:500]}...")
        
        # Add game context if available
        if relevant_context and relevant_context.get('game_context'):
            game_context = relevant_context['game_context']
            game_type = game_context.get('game_type', 'game')
            game_status = game_context.get('game_status', 'active')
            input_parts.append(f"Current {game_type} game status: {game_status}")
        
        # Add current query
        input_parts.append(f"User: {query}")
        input_parts.append("Assistant:")
        
        return "\n".join(input_parts)
    
    def _update_context(self, query: str, response: str, context_type: Optional[ContextType] = None):
        """
        Update conversation context with new exchange
        
        Args:
            query: User query
            response: AI response
            context_type: Type of context for the conversation
        """
        # Update local context (for backward compatibility)
        self.conversation_context.messages.extend([
            {"role": "user", "content": query, "timestamp": datetime.now()},
            {"role": "assistant", "content": response, "timestamp": datetime.now()}
        ])
        
        # Trim local context if it gets too long
        if len(self.conversation_context.messages) > 30:
            self.conversation_context.messages = self.conversation_context.messages[-20:]
        
        # Update context manager with messages
        from models.data_models import ChatMessage
        
        user_message = ChatMessage(
            sender="user",
            content=query,
            context_type=context_type.value if context_type else "general"
        )
        
        ai_message = ChatMessage(
            sender="zeus",
            content=response,
            context_type=context_type.value if context_type else "general"
        )
        
        self.context_manager.add_conversation_message(user_message)
        self.context_manager.add_conversation_message(ai_message)
    
    def _fallback_response(self, query: str, context: Optional[str] = None, 
                          relevant_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a fallback response when AI models are not available
        
        Args:
            query: User query
            context: Optional immediate context
            relevant_context: Cross-feature context from context manager
            
        Returns:
            str: Fallback response
        """
        query_lower = query.lower()
        
        # Check for document context from context manager
        if relevant_context and relevant_context.get('document_context'):
            doc_context = relevant_context['document_context']
            doc_name = doc_context.get('filename', 'document')
            chunks = doc_context.get('chunks', [])
            
            # Simple keyword matching in document chunks
            query_words = [word for word in query_lower.split() if len(word) > 2]
            relevant_chunks = []
            
            for chunk in chunks:
                chunk_lower = chunk.lower()
                if any(word in chunk_lower for word in query_words):
                    relevant_chunks.append(chunk)
            
            if relevant_chunks:
                return (f"Based on the document '{doc_name}', I found:\n\n"
                       f"{relevant_chunks[0][:300]}...\n\n"
                       f"Note: I'm running in basic mode. For enhanced analysis, "
                       f"please ensure AI dependencies are installed.")
        
        # Check for game context
        if relevant_context and relevant_context.get('game_context'):
            game_context = relevant_context['game_context']
            game_type = game_context.get('game_type', 'game')
            game_status = game_context.get('game_status', 'active')
            
            if any(word in query_lower for word in ['move', 'turn', 'play', 'strategy']):
                return (f"I see you're asking about the {game_type} game. "
                       f"The game is currently {game_status}. "
                       f"I'm in basic mode, but I can still help with game moves and strategy.")
        
        # If immediate context is provided, prioritize it
        if context:
            return (f"Based on the available information, I can see content related to your query. "
                   f"However, I'm currently running in basic mode and cannot provide detailed analysis. "
                   f"The content includes: {context[:200]}...")
        
        # Check conversation history for context
        if relevant_context and relevant_context.get('conversation_history'):
            recent_messages = relevant_context['conversation_history'][-3:]
            if recent_messages:
                last_topic = None
                for msg in reversed(recent_messages):
                    if msg['sender'] == 'user' and len(msg['content']) > 10:
                        last_topic = msg['content'][:50]
                        break
                
                if last_topic:
                    return (f"I remember we were discussing: '{last_topic}...'. "
                           f"I'm in basic mode, but I'm still here to help. "
                           f"Could you rephrase your question?")
        
        # Simple keyword-based responses
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm Z.E.U.S., your virtual assistant. How can I help you today?"
        
        elif any(word in query_lower for word in ['help', 'what can you do']):
            return ("I can help you with:\n"
                   "• Chatting and answering questions\n"
                   "• Analyzing uploaded documents\n"
                   "• Playing games like Tic-Tac-Toe, Connect 4, and Battleship\n"
                   "Note: I'm currently running in basic mode. For enhanced AI features, "
                   "please ensure all dependencies are installed.")
        
        else:
            return ("I understand you're asking about something, but I'm currently running in basic mode. "
                   "I can still help with document uploads, games, and basic conversation. "
                   "What would you like to do?")
    
    def _fallback_document_response(self, query: str, chunks: List[str]) -> str:
        """
        Generate a fallback response for document queries
        
        Args:
            query: User query
            chunks: Document chunks
            
        Returns:
            str: Fallback response
        """
        # Simple keyword matching in chunks
        import re
        # Clean and filter query words
        query_words = [re.sub(r'[^\w]', '', word.lower()) for word in query.split() if len(re.sub(r'[^\w]', '', word)) > 2]
        relevant_chunks = []
        
        for chunk in chunks:
            chunk_lower = chunk.lower()
            # Check for any meaningful keyword matches
            if any(word in chunk_lower for word in query_words):
                relevant_chunks.append(chunk)
        
        if relevant_chunks:
            return (f"I found some relevant information in the document:\n\n"
                   f"{relevant_chunks[0][:300]}...\n\n"
                   f"Note: I'm running in basic mode. For enhanced document analysis, "
                   f"please ensure all AI dependencies are properly installed.")
        else:
            return ("I couldn't find specific information related to your query in the document. "
                   "Try rephrasing your question or check if the document contains the information you're looking for.")
    
    def update_conversation_context(self, message: str, response: str):
        """
        Public method to update conversation context
        
        Args:
            message: User message
            response: AI response
        """
        self._update_context(message, response)
    
    def clear_context(self):
        """Clear conversation context"""
        self.conversation_context = ConversationContext(messages=[])
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get current model loading status
        
        Returns:
            Dict with model status information
        """
        return {
            "models_loaded": self.models_loaded,
            "fallback_mode": self.fallback_mode,
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "text_model_loaded": self.text_model is not None,
            "sentence_model_loaded": self.sentence_model is not None,
            "text_generator_loaded": self.text_generator is not None
        }
    
    def set_context_manager(self, context_manager: ContextManager):
        """
        Set or update the context manager
        
        Args:
            context_manager: Context manager instance
        """
        self.context_manager = context_manager
    
    def switch_context_mode(self, mode: ContextType, context_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Switch context mode for cross-feature awareness
        
        Args:
            mode: New context mode
            context_data: Optional context-specific data
            
        Returns:
            bool: True if switch was successful
        """
        return self.context_manager.switch_context(mode, context_data)
    
    def set_document_context(self, document, chunks: List[str]) -> bool:
        """
        Set document context for document-aware conversations
        
        Args:
            document: Document object
            chunks: Document text chunks
            
        Returns:
            bool: True if context was set successfully
        """
        return self.context_manager.set_document_context(document, chunks)
    
    def set_game_context(self, game_state) -> bool:
        """
        Set game context for game-aware interactions
        
        Args:
            game_state: Current game state
            
        Returns:
            bool: True if context was set successfully
        """
        return self.context_manager.set_game_context(game_state)
    
    def clear_context(self, context_type: Optional[ContextType] = None) -> bool:
        """
        Clear specific or all context
        
        Args:
            context_type: Specific context type to clear (None for all)
            
        Returns:
            bool: True if context was cleared successfully
        """
        return self.context_manager.clear_context(context_type)
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current context state
        
        Returns:
            Dict containing context summary
        """
        return self.context_manager.get_context_summary()    

    def _handle_performance_optimization(self, optimization_type: str, data: Dict[str, Any] = None):
        """
        Handle performance optimization requests
        
        Args:
            optimization_type: Type of optimization requested
            data: Additional optimization data
        """
        try:
            if optimization_type == "memory_optimization":
                self._optimize_memory_usage(urgent=data.get('urgent', False))
            elif optimization_type == "performance_optimization":
                self._optimize_performance()
            elif optimization_type == "low_memory_optimization":
                self._optimize_for_low_memory()
            elif optimization_type == "comprehensive_optimization":
                self._perform_comprehensive_optimization()
                
        except Exception as e:
            self.logger.error(f"Error in performance optimization: {e}")
    
    def _handle_memory_optimization(self, optimization_type: str):
        """
        Handle memory optimization requests from memory optimizer
        
        Args:
            optimization_type: Type of memory optimization
        """
        try:
            if optimization_type == "low_memory_optimization":
                self._optimize_for_low_memory()
            else:
                self._optimize_memory_usage(urgent=True)
                
        except Exception as e:
            self.logger.error(f"Error in memory optimization: {e}")
    
    def _optimize_memory_usage(self, urgent: bool = False):
        """
        Optimize AI engine memory usage
        
        Args:
            urgent: Whether this is an urgent optimization
        """
        self.logger.info(f"Optimizing AI engine memory usage (urgent: {urgent})")
        
        # Clear response cache
        if urgent or len(self.response_cache) > self.cache_max_size:
            cache_size = len(self.response_cache)
            self.response_cache.clear()
            if cache_size > 0:
                self.logger.info(f"Cleared {cache_size} cached responses")
        
        # Trim conversation context
        if len(self.conversation_context.messages) > 20:
            # Keep only recent messages
            self.conversation_context.messages = self.conversation_context.messages[-10:]
            self.logger.info("Trimmed conversation context")
        
        # Clear model caches if urgent
        if urgent and self.models_loaded:
            self._clear_model_caches()
        
        # Force garbage collection
        gc.collect()
    
    def _optimize_performance(self):
        """Optimize AI engine performance"""
        self.logger.info("Optimizing AI engine performance")
        
        # Reduce response cache size to improve lookup speed
        if len(self.response_cache) > 50:
            # Keep only most recent entries
            items = list(self.response_cache.items())
            self.response_cache = dict(items[-25:])  # Keep last 25 entries
        
        # Optimize conversation context
        if len(self.conversation_context.messages) > 30:
            self.conversation_context.messages = self.conversation_context.messages[-15:]
    
    def _optimize_for_low_memory(self):
        """Optimize for low memory conditions"""
        self.logger.warning("Optimizing AI engine for low memory conditions")
        
        # Clear all caches
        self.response_cache.clear()
        
        # Minimize conversation context
        if len(self.conversation_context.messages) > 10:
            self.conversation_context.messages = self.conversation_context.messages[-5:]
        
        # Consider unloading models if memory is critically low
        current_memory = self.memory_optimizer.get_current_memory_usage()
        if current_memory > self.model_memory_limit_mb * 2:  # If using more than 1GB
            self.logger.warning("Critical memory usage - considering model unloading")
            if self.models_loaded and not self.fallback_mode:
                self._unload_models_temporarily()
    
    def _clear_model_caches(self):
        """Clear model-specific caches"""
        try:
            # Clear PyTorch cache if available
            if TRANSFORMERS_AVAILABLE and torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear any model-specific caches
            if hasattr(self.text_model, 'clear_cache'):
                self.text_model.clear_cache()
            
            if hasattr(self.sentence_model, 'clear_cache'):
                self.sentence_model.clear_cache()
            
            self.logger.info("Cleared model caches")
            
        except Exception as e:
            self.logger.error(f"Error clearing model caches: {e}")
    
    def _unload_models_temporarily(self):
        """Temporarily unload models to free memory"""
        try:
            self.logger.warning("Temporarily unloading AI models to free memory")
            
            # Store model loading state
            was_loaded = self.models_loaded
            
            # Clear model references
            self.text_model = None
            self.tokenizer = None
            self.sentence_model = None
            self.text_generator = None
            
            # Set to fallback mode temporarily
            self.models_loaded = False
            self.fallback_mode = True
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("Models unloaded temporarily - running in fallback mode")
            
        except Exception as e:
            self.logger.error(f"Error unloading models: {e}")
    
    def _perform_comprehensive_optimization(self):
        """Perform comprehensive optimization of AI engine"""
        self.logger.info("Performing comprehensive AI engine optimization")
        
        # Clear all caches
        self.response_cache.clear()
        
        # Reset conversation context
        self.conversation_context = ConversationContext(messages=[])
        
        # Clear model caches
        self._clear_model_caches()
        
        # Force garbage collection
        gc.collect()
        
        self.logger.info("Comprehensive AI engine optimization completed")
    
    def get_cached_response(self, query_hash: str) -> Optional[str]:
        """
        Get cached response for a query
        
        Args:
            query_hash: Hash of the query
            
        Returns:
            Cached response or None
        """
        return self.response_cache.get(query_hash)
    
    def cache_response(self, query_hash: str, response: str):
        """
        Cache a response for future use
        
        Args:
            query_hash: Hash of the query
            response: Response to cache
        """
        # Limit cache size
        if len(self.response_cache) >= self.cache_max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[query_hash] = response
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get current model status and memory usage
        
        Returns:
            Dictionary with model status information
        """
        try:
            current_memory = self.memory_optimizer.get_current_memory_usage()
            
            return {
                'models_loaded': self.models_loaded,
                'fallback_mode': self.fallback_mode,
                'memory_usage_mb': current_memory,
                'memory_limit_mb': self.model_memory_limit_mb,
                'cached_responses': len(self.response_cache),
                'conversation_messages': len(self.conversation_context.messages),
                'response_times_tracked': len(self.response_times),
                'avg_response_time_ms': sum(self.response_times[-10:]) / len(self.response_times[-10:]) if self.response_times else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return {'error': str(e)}
    
    def optimize_memory(self):
        """Public method to trigger memory optimization"""
        self._optimize_memory_usage(urgent=False)
    
    def clear_model_cache(self):
        """Public method to clear model caches"""
        self._clear_model_caches()
    
    def set_memory_limit(self, limit_mb: int):
        """
        Set memory limit for AI models
        
        Args:
            limit_mb: Memory limit in MB
        """
        self.model_memory_limit_mb = limit_mb
        self.logger.info(f"AI engine memory limit set to {limit_mb}MB")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the AI engine
        
        Returns:
            Dictionary with performance metrics
        """
        try:
            recent_response_times = self.response_times[-20:] if self.response_times else []
            
            return {
                'total_responses': len(self.response_times),
                'avg_response_time_ms': sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0,
                'min_response_time_ms': min(recent_response_times) if recent_response_times else 0,
                'max_response_time_ms': max(recent_response_times) if recent_response_times else 0,
                'cache_hit_ratio': self._calculate_cache_hit_ratio(),
                'memory_usage_mb': self.memory_optimizer.get_current_memory_usage(),
                'models_loaded': self.models_loaded,
                'fallback_mode': self.fallback_mode
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {'error': str(e)}
    
    def _calculate_cache_hit_ratio(self) -> float:
        """Calculate cache hit ratio (simplified)"""
        # This is a simplified calculation - in a real implementation,
        # you would track cache hits and misses
        if len(self.response_cache) == 0:
            return 0.0
        
        # Estimate based on cache size vs total responses
        total_responses = len(self.response_times)
        if total_responses == 0:
            return 0.0
        
        return min(len(self.response_cache) / total_responses, 1.0)
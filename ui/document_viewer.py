"""
Document Viewer Interface for Z.E.U.S. Virtual Assistant

This module provides the document analysis interface including:
- Document upload and display
- Document content viewer
- Document context management
- Integration with chat for document-based queries
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Optional, Callable, List
import threading
from datetime import datetime

from core.document_processor import DocumentProcessor
from models.data_models import Document
from .styles import apply_modern_styling, create_styled_button, create_card_frame


class DocumentViewer:
    """
    Document viewer component for Z.E.U.S. Virtual Assistant
    
    Provides document upload, viewing, and analysis capabilities
    with integration to the chat interface for document-based queries.
    """
    
    def __init__(self, parent: ttk.Frame, document_processor: DocumentProcessor = None):
        """
        Initialize the document viewer
        
        Args:
            parent: Parent frame to contain the document viewer
            document_processor: Document processor instance
        """
        self.parent = parent
        self.document_processor = document_processor or DocumentProcessor()
        
        # UI components
        self.upload_button = None
        self.clear_button = None
        self.document_info_frame = None
        self.document_content_display = None
        self.status_label = None
        self.progress_bar = None
        
        # State management
        self.current_document = None
        self.document_callback = None
        self.is_processing = False
        
        # Create the interface
        self.create_widgets()
        self.setup_bindings()
    
    def create_widgets(self):
        """Create all document viewer widgets"""
        # Main container
        main_container = ttk.Frame(self.parent)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header section
        self._create_header(main_container)
        
        # Document controls section
        self._create_controls(main_container)
        
        # Document information section
        self._create_document_info(main_container)
        
        # Document content viewer
        self._create_content_viewer(main_container)
        
        # Status section
        self._create_status_section(main_container)
        
        # Show initial state
        self._show_no_document_state()
    
    def _create_header(self, parent):
        """Create the document viewer header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title
        title_label = ttk.Label(
            header_frame,
            text="📄 Document Analysis",
            font=("Arial", 16, "bold"),
            foreground="#0078d4"
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.doc_status_label = ttk.Label(
            header_frame,
            text="● No Document",
            font=("Arial", 10),
            foreground="#6c757d"
        )
        self.doc_status_label.pack(side=tk.RIGHT)
        
        # Separator
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
    
    def _create_controls(self, parent):
        """Create document control buttons"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Upload button with modern styling
        self.upload_button = create_styled_button(
            controls_frame,
            text="📁 Upload Document",
            command=self._on_upload_clicked,
            style="Primary"
        )
        self.upload_button.configure(width=20)
        self.upload_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button with modern styling
        self.clear_button = create_styled_button(
            controls_frame,
            text="🗑️ Clear Document",
            command=self._on_clear_clicked,
            style="Danger"
        )
        self.clear_button.configure(width=20, state=tk.DISABLED)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button with modern styling
        self.refresh_button = create_styled_button(
            controls_frame,
            text="🔄 Refresh",
            command=self._on_refresh_clicked,
            style="Secondary"
        )
        self.refresh_button.configure(width=15)
        self.refresh_button.pack(side=tk.LEFT)
        
        # Progress bar (hidden initially)
        self.progress_bar = ttk.Progressbar(
            controls_frame,
            mode='indeterminate',
            length=200
        )
        # Don't pack initially - will be shown during processing
    
    def _create_document_info(self, parent):
        """Create document information display"""
        info_label_frame = ttk.LabelFrame(parent, text="Document Information", padding=10)
        info_label_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.document_info_frame = ttk.Frame(info_label_frame)
        self.document_info_frame.pack(fill=tk.X)
        
        # Initially empty - will be populated when document is loaded
    
    def _create_content_viewer(self, parent):
        """Create document content viewer"""
        content_label_frame = ttk.LabelFrame(parent, text="Document Content", padding=10)
        content_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Content display with scrollbar
        self.document_content_display = scrolledtext.ScrolledText(
            content_label_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 10),
            bg="#f8f9fa",
            fg="#333333",
            padx=10,
            pady=10,
            height=15
        )
        self.document_content_display.pack(fill=tk.BOTH, expand=True)
        
        # Apply modern styling
        apply_modern_styling(self.document_content_display)
        
        # Configure text tags for content formatting
        self._configure_content_tags()
    
    def _configure_content_tags(self):
        """Configure text tags for content formatting"""
        self.document_content_display.tag_configure(
            "header",
            font=("Arial", 12, "bold"),
            foreground="#0078d4",
            spacing1=10,
            spacing3=5
        )
        
        self.document_content_display.tag_configure(
            "content",
            font=("Arial", 10),
            foreground="#333333",
            spacing1=2
        )
        
        self.document_content_display.tag_configure(
            "chunk_separator",
            font=("Arial", 9, "italic"),
            foreground="#6c757d",
            justify=tk.CENTER,
            spacing1=5,
            spacing3=5
        )
    
    def _create_status_section(self, parent):
        """Create status section"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready - Upload a document to begin analysis",
            font=("Arial", 9),
            foreground="#6c757d"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Document count on the right
        self.doc_count_label = ttk.Label(
            status_frame,
            text="",
            font=("Arial", 9),
            foreground="#6c757d"
        )
        self.doc_count_label.pack(side=tk.RIGHT)
        
        self._update_document_count()
    
    def setup_bindings(self):
        """Setup keyboard bindings and event handlers"""
        # Keyboard shortcuts
        self.parent.bind('<Control-o>', lambda e: self._on_upload_clicked())
        self.parent.bind('<Control-r>', lambda e: self._on_refresh_clicked())
        self.parent.bind('<Delete>', lambda e: self._on_clear_clicked())
    
    def _show_no_document_state(self):
        """Show UI state when no document is loaded"""
        # Clear document info
        for widget in self.document_info_frame.winfo_children():
            widget.destroy()
        
        no_doc_label = ttk.Label(
            self.document_info_frame,
            text="No document loaded. Upload a PDF or DOC file to begin analysis.",
            font=("Arial", 10, "italic"),
            foreground="#6c757d"
        )
        no_doc_label.pack()
        
        # Clear content display
        self.document_content_display.configure(state=tk.NORMAL)
        self.document_content_display.delete("1.0", tk.END)
        self.document_content_display.insert(
            tk.END,
            "Document content will appear here after upload.\n\n"
            "Supported formats: PDF, DOC, DOCX\n"
            "Maximum file size: 50MB",
            "content"
        )
        self.document_content_display.configure(state=tk.DISABLED)
        
        # Update status
        self.doc_status_label.configure(text="● No Document", foreground="#6c757d")
        self.clear_button.configure(state=tk.DISABLED)
    
    def _show_document_loaded_state(self, document: Document):
        """Show UI state when document is loaded"""
        # Update document info
        self._display_document_info(document)
        
        # Update content display
        self._display_document_content(document)
        
        # Update status
        self.doc_status_label.configure(text="● Document Loaded", foreground="#28a745")
        self.clear_button.configure(state=tk.NORMAL)
        
        # Update status message
        self.update_status(f"Document '{document.filename}' loaded successfully")
    
    def _display_document_info(self, document: Document):
        """Display document information"""
        # Clear existing info
        for widget in self.document_info_frame.winfo_children():
            widget.destroy()
        
        # Create info grid
        info_grid = ttk.Frame(self.document_info_frame)
        info_grid.pack(fill=tk.X)
        
        # Document details
        details = [
            ("Filename:", document.filename),
            ("File Size:", f"{document.file_size // 1024} KB"),
            ("Word Count:", f"{len(document.text_content.split()):,}"),
            ("Character Count:", f"{len(document.text_content):,}"),
            ("Chunks:", f"{len(document.chunks)}"),
            ("Upload Date:", document.upload_date.strftime("%Y-%m-%d %H:%M:%S"))
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(
                info_grid,
                text=label,
                font=("Arial", 9, "bold")
            ).grid(row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2)
            
            ttk.Label(
                info_grid,
                text=str(value),
                font=("Arial", 9)
            ).grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2)
    
    def _display_document_content(self, document: Document):
        """Display document content"""
        self.document_content_display.configure(state=tk.NORMAL)
        self.document_content_display.delete("1.0", tk.END)
        
        # Show document header
        self.document_content_display.insert(
            tk.END,
            f"Document: {document.filename}\n",
            "header"
        )
        
        # Show content preview (first 2000 characters)
        content_preview = document.text_content[:2000]
        if len(document.text_content) > 2000:
            content_preview += "\n\n[Content truncated - showing first 2000 characters]"
        
        self.document_content_display.insert(tk.END, content_preview, "content")
        
        # Show chunk information
        if document.chunks:
            self.document_content_display.insert(
                tk.END,
                f"\n\n--- Document processed into {len(document.chunks)} chunks for analysis ---",
                "chunk_separator"
            )
        
        self.document_content_display.configure(state=tk.DISABLED)
        self.document_content_display.see("1.0")
    
    def _on_upload_clicked(self):
        """Handle upload button click"""
        if self.is_processing:
            return
        
        self._start_processing("Uploading document...")
        
        def upload_in_background():
            try:
                document = self.document_processor.upload_document()
                
                # Update UI in main thread
                self.parent.after(0, lambda: self._handle_upload_result(document))
                
            except Exception as e:
                error_msg = f"Upload failed: {str(e)}"
                self.parent.after(0, lambda: self._handle_upload_error(error_msg))
        
        # Start upload in background thread
        thread = threading.Thread(target=upload_in_background, daemon=True)
        thread.start()
    
    def _handle_upload_result(self, document: Optional[Document]):
        """Handle upload result in main thread"""
        self._stop_processing()
        
        if document:
            self.current_document = document
            self._show_document_loaded_state(document)
            self._update_document_count()
            
            # Notify callback if set
            if self.document_callback:
                self.document_callback("document_loaded", document)
        else:
            # Upload was cancelled or failed
            self.update_status("Document upload cancelled or failed")
    
    def _handle_upload_error(self, error_msg: str):
        """Handle upload error in main thread"""
        self._stop_processing()
        self.update_status(error_msg)
        messagebox.showerror("Upload Error", error_msg)
    
    def _on_clear_clicked(self):
        """Handle clear button click"""
        if not self.current_document:
            return
        
        # Confirm with user
        result = messagebox.askyesno(
            "Clear Document",
            f"Are you sure you want to clear the document '{self.current_document.filename}'?\n\n"
            "This will remove it from the current session but not delete the file."
        )
        
        if result:
            self._clear_document()
    
    def _clear_document(self):
        """Clear the current document"""
        if self.current_document:
            doc_name = self.current_document.filename
            
            # Clear from processor
            self.document_processor.clear_current_document()
            
            # Clear local reference
            self.current_document = None
            
            # Update UI
            self._show_no_document_state()
            self._update_document_count()
            
            # Notify callback
            if self.document_callback:
                self.document_callback("document_cleared", doc_name)
            
            self.update_status(f"Document '{doc_name}' cleared")
    
    def _on_refresh_clicked(self):
        """Handle refresh button click"""
        if self.current_document:
            # Refresh current document display
            self._show_document_loaded_state(self.current_document)
            self.update_status("Document display refreshed")
        else:
            # Refresh stored documents count
            self._update_document_count()
            self.update_status("Document list refreshed")
    
    def _start_processing(self, message: str):
        """Start processing state"""
        self.is_processing = True
        self.upload_button.configure(state=tk.DISABLED)
        self.clear_button.configure(state=tk.DISABLED)
        
        # Show progress bar
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        self.progress_bar.start()
        
        self.update_status(message)
    
    def _stop_processing(self):
        """Stop processing state"""
        self.is_processing = False
        self.upload_button.configure(state=tk.NORMAL)
        
        if self.current_document:
            self.clear_button.configure(state=tk.NORMAL)
        
        # Hide progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def _update_document_count(self):
        """Update document count display"""
        stored_docs = self.document_processor.get_stored_documents()
        count_text = f"{len(stored_docs)} stored documents"
        self.doc_count_label.configure(text=count_text)
    
    def update_status(self, message: str):
        """Update status message"""
        if self.status_label:
            self.status_label.configure(text=message)
    
    def get_current_document(self) -> Optional[Document]:
        """Get the currently loaded document"""
        return self.current_document
    
    def set_document_callback(self, callback: Callable):
        """Set callback for document events"""
        self.document_callback = callback
    
    def load_document_by_id(self, document_id: str) -> bool:
        """
        Load a stored document by ID
        
        Args:
            document_id: ID of the document to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            document = self.document_processor.find_document_by_id(document_id)
            if document:
                self.current_document = document
                self.document_processor.current_document = document
                self._show_document_loaded_state(document)
                
                if self.document_callback:
                    self.document_callback("document_loaded", document)
                
                return True
            else:
                self.update_status(f"Document with ID {document_id} not found")
                return False
                
        except Exception as e:
            self.update_status(f"Error loading document: {str(e)}")
            return False
    
    def get_document_chunks(self) -> List[str]:
        """Get chunks from current document"""
        if self.current_document and self.current_document.chunks:
            return self.current_document.chunks
        return []
    
    def get_document_name(self) -> str:
        """Get name of current document"""
        if self.current_document:
            return self.current_document.filename
        return ""
    
    def search_document_content(self, query: str) -> List[str]:
        """
        Search for relevant content in current document
        
        Args:
            query: Search query
            
        Returns:
            List of relevant text chunks
        """
        if not self.current_document:
            return []
        
        relevant_chunks = self.document_processor.find_relevant_chunks(query)
        return [chunk for chunk, _ in relevant_chunks]
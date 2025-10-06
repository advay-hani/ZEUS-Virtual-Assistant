"""
Keyboard shortcuts and accessibility features for Z.E.U.S. Virtual Assistant

This module provides comprehensive keyboard navigation, shortcuts, and
accessibility features throughout the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional, Any
import platform


class KeyboardShortcutManager:
    """Manages keyboard shortcuts and navigation throughout the application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.shortcuts: Dict[str, Callable] = {}
        self.context_shortcuts: Dict[str, Dict[str, Callable]] = {}
        self.current_context = "global"
        
        # Setup global shortcuts
        self.setup_global_shortcuts()
        self.setup_navigation_shortcuts()
        self.setup_accessibility_shortcuts()
    
    def setup_global_shortcuts(self):
        """Setup application-wide keyboard shortcuts"""
        # File operations
        self.register_shortcut("<Control-o>", self._placeholder_open, "Open document")
        self.register_shortcut("<Control-s>", self._placeholder_save, "Save current state")
        self.register_shortcut("<Control-q>", self._quit_application, "Quit application")
        
        # Navigation shortcuts
        self.register_shortcut("<Control-1>", self._switch_to_chat, "Switch to Chat")
        self.register_shortcut("<Control-2>", self._switch_to_documents, "Switch to Documents")
        self.register_shortcut("<Control-3>", self._switch_to_games, "Switch to Games")
        
        # Help and information
        self.register_shortcut("<F1>", self._show_help, "Show help")
        self.register_shortcut("<Control-question>", self._show_shortcuts, "Show keyboard shortcuts")
        
        # Window management
        self.register_shortcut("<F11>", self._toggle_fullscreen, "Toggle fullscreen")
        self.register_shortcut("<Control-plus>", self._zoom_in, "Zoom in")
        self.register_shortcut("<Control-minus>", self._zoom_out, "Zoom out")
        self.register_shortcut("<Control-0>", self._reset_zoom, "Reset zoom")
        
        # Quick actions
        self.register_shortcut("<Control-r>", self._refresh_current_view, "Refresh current view")
        self.register_shortcut("<Escape>", self._cancel_current_action, "Cancel current action")
    
    def setup_navigation_shortcuts(self):
        """Setup keyboard navigation shortcuts"""
        # Tab navigation enhancement
        self.root.bind_class("all", "<Tab>", self._enhanced_tab_navigation)
        self.root.bind_class("all", "<Shift-Tab>", self._enhanced_shift_tab_navigation)
        
        # Arrow key navigation for lists and grids
        self.root.bind_class("Listbox", "<Up>", self._list_navigate_up)
        self.root.bind_class("Listbox", "<Down>", self._list_navigate_down)
        self.root.bind_class("Listbox", "<Home>", self._list_navigate_home)
        self.root.bind_class("Listbox", "<End>", self._list_navigate_end)
        
        # Text widget navigation
        self.root.bind_class("Text", "<Control-a>", self._select_all_text)
        self.root.bind_class("Text", "<Control-Home>", self._text_navigate_start)
        self.root.bind_class("Text", "<Control-End>", self._text_navigate_end)
    
    def setup_accessibility_shortcuts(self):
        """Setup accessibility-focused shortcuts"""
        # Screen reader support
        self.register_shortcut("<Control-Alt-r>", self._read_current_element, "Read current element")
        self.register_shortcut("<Control-Alt-s>", self._read_status, "Read status")
        
        # High contrast toggle
        self.register_shortcut("<Control-Alt-h>", self._toggle_high_contrast, "Toggle high contrast")
        
        # Focus management
        self.register_shortcut("<Control-Alt-f>", self._focus_main_content, "Focus main content")
        self.register_shortcut("<Control-Alt-n>", self._focus_navigation, "Focus navigation")
        
        # Text size adjustment
        self.register_shortcut("<Control-Shift-plus>", self._increase_text_size, "Increase text size")
        self.register_shortcut("<Control-Shift-minus>", self._decrease_text_size, "Decrease text size")
    
    def register_shortcut(self, key_sequence: str, callback: Callable, description: str = ""):
        """Register a keyboard shortcut"""
        self.shortcuts[key_sequence] = {
            'callback': callback,
            'description': description
        }
        self.root.bind(key_sequence, lambda e: callback())
    
    def register_context_shortcut(self, context: str, key_sequence: str, callback: Callable, description: str = ""):
        """Register a context-specific keyboard shortcut"""
        if context not in self.context_shortcuts:
            self.context_shortcuts[context] = {}
        
        self.context_shortcuts[context][key_sequence] = {
            'callback': callback,
            'description': description
        }
    
    def set_context(self, context: str):
        """Set the current keyboard context"""
        # Unbind previous context shortcuts
        if self.current_context in self.context_shortcuts:
            for key_sequence in self.context_shortcuts[self.current_context]:
                try:
                    self.root.unbind(key_sequence)
                except:
                    pass
        
        # Bind new context shortcuts
        self.current_context = context
        if context in self.context_shortcuts:
            for key_sequence, shortcut_info in self.context_shortcuts[context].items():
                self.root.bind(key_sequence, lambda e, cb=shortcut_info['callback']: cb())
    
    def get_shortcuts_help(self) -> str:
        """Get formatted help text for all shortcuts"""
        help_text = "Keyboard Shortcuts:\n\n"
        
        # Global shortcuts
        help_text += "Global Shortcuts:\n"
        for key_sequence, info in self.shortcuts.items():
            if info['description']:
                help_text += f"  {key_sequence}: {info['description']}\n"
        
        # Context shortcuts
        if self.current_context in self.context_shortcuts:
            help_text += f"\n{self.current_context.title()} Context:\n"
            for key_sequence, info in self.context_shortcuts[self.current_context].items():
                if info['description']:
                    help_text += f"  {key_sequence}: {info['description']}\n"
        
        return help_text
    
    # Navigation callbacks
    def _switch_to_chat(self):
        """Switch to chat mode"""
        if hasattr(self.root, 'main_window'):
            self.root.main_window.switch_to_chat()
    
    def _switch_to_documents(self):
        """Switch to documents mode"""
        if hasattr(self.root, 'main_window'):
            self.root.main_window.switch_to_documents()
    
    def _switch_to_games(self):
        """Switch to games mode"""
        if hasattr(self.root, 'main_window'):
            self.root.main_window.switch_to_games()
    
    # Enhanced navigation
    def _enhanced_tab_navigation(self, event):
        """Enhanced tab navigation with visual feedback"""
        next_widget = event.widget.tk_focusNext()
        if next_widget:
            next_widget.focus()
            self._highlight_focused_widget(next_widget)
        return "break"
    
    def _enhanced_shift_tab_navigation(self, event):
        """Enhanced shift-tab navigation with visual feedback"""
        prev_widget = event.widget.tk_focusPrev()
        if prev_widget:
            prev_widget.focus()
            self._highlight_focused_widget(prev_widget)
        return "break"
    
    def _highlight_focused_widget(self, widget):
        """Provide visual feedback for focused widget"""
        try:
            # Store original colors
            if not hasattr(widget, '_original_colors'):
                if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                    # TTK widgets - use style system
                    pass
                elif hasattr(widget, 'cget'):
                    try:
                        widget._original_bg = widget.cget('bg')
                        widget._original_fg = widget.cget('fg')
                    except:
                        pass
            
            # Apply focus highlight
            if isinstance(widget, tk.Text):
                widget.configure(highlightbackground='#0078d4', highlightthickness=2)
            elif isinstance(widget, (tk.Entry, tk.Listbox)):
                widget.configure(highlightbackground='#0078d4', highlightthickness=2)
            
            # Remove highlight after delay
            self.root.after(2000, lambda: self._remove_focus_highlight(widget))
            
        except Exception:
            pass  # Ignore errors in highlighting
    
    def _remove_focus_highlight(self, widget):
        """Remove focus highlight"""
        try:
            if isinstance(widget, (tk.Text, tk.Entry, tk.Listbox)):
                widget.configure(highlightthickness=1)
        except Exception:
            pass
    
    # List navigation
    def _list_navigate_up(self, event):
        """Navigate up in list"""
        listbox = event.widget
        current = listbox.curselection()
        if current:
            new_index = max(0, current[0] - 1)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(new_index)
            listbox.see(new_index)
        return "break"
    
    def _list_navigate_down(self, event):
        """Navigate down in list"""
        listbox = event.widget
        current = listbox.curselection()
        if current:
            new_index = min(listbox.size() - 1, current[0] + 1)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(new_index)
            listbox.see(new_index)
        return "break"
    
    def _list_navigate_home(self, event):
        """Navigate to start of list"""
        listbox = event.widget
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(0)
        listbox.see(0)
        return "break"
    
    def _list_navigate_end(self, event):
        """Navigate to end of list"""
        listbox = event.widget
        last_index = listbox.size() - 1
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(last_index)
        listbox.see(last_index)
        return "break"
    
    # Text navigation
    def _select_all_text(self, event):
        """Select all text in text widget"""
        text_widget = event.widget
        text_widget.tag_add(tk.SEL, "1.0", tk.END)
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)
        return "break"
    
    def _text_navigate_start(self, event):
        """Navigate to start of text"""
        text_widget = event.widget
        text_widget.mark_set(tk.INSERT, "1.0")
        text_widget.see(tk.INSERT)
        return "break"
    
    def _text_navigate_end(self, event):
        """Navigate to end of text"""
        text_widget = event.widget
        text_widget.mark_set(tk.INSERT, tk.END)
        text_widget.see(tk.INSERT)
        return "break"
    
    # Placeholder callbacks (to be connected to actual functionality)
    def _placeholder_open(self):
        """Placeholder for open functionality"""
        pass
    
    def _placeholder_save(self):
        """Placeholder for save functionality"""
        pass
    
    def _quit_application(self):
        """Quit the application"""
        self.root.quit()
    
    def _show_help(self):
        """Show help dialog"""
        self._show_shortcuts()
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("500x600")
        shortcuts_window.resizable(True, True)
        
        # Center the window
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        # Create scrollable text widget
        text_frame = ttk.Frame(shortcuts_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#ffffff',
            fg='#333333'
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert shortcuts help
        help_text = self.get_shortcuts_help()
        text_widget.insert(tk.END, help_text)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(
            shortcuts_window,
            text="Close",
            command=shortcuts_window.destroy
        )
        close_button.pack(pady=10)
        
        # Focus the close button
        close_button.focus()
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
    
    def _zoom_in(self):
        """Increase UI zoom level"""
        # This would need to be implemented with font scaling
        pass
    
    def _zoom_out(self):
        """Decrease UI zoom level"""
        # This would need to be implemented with font scaling
        pass
    
    def _reset_zoom(self):
        """Reset UI zoom to default"""
        # This would need to be implemented with font scaling
        pass
    
    def _refresh_current_view(self):
        """Refresh the current view"""
        if hasattr(self.root, 'main_window'):
            current_mode = self.root.main_window.get_current_mode()
            if current_mode == "chat":
                self.root.main_window.switch_to_chat()
            elif current_mode == "documents":
                self.root.main_window.switch_to_documents()
            elif current_mode == "games":
                self.root.main_window.switch_to_games()
    
    def _cancel_current_action(self):
        """Cancel current action or clear focus"""
        focused_widget = self.root.focus_get()
        if focused_widget:
            # Clear selection in text widgets
            if isinstance(focused_widget, tk.Text):
                focused_widget.tag_remove(tk.SEL, "1.0", tk.END)
            elif isinstance(focused_widget, tk.Entry):
                focused_widget.selection_clear()
        
        # Return focus to main window
        self.root.focus_set()
    
    # Accessibility callbacks
    def _read_current_element(self):
        """Read current element (for screen readers)"""
        focused_widget = self.root.focus_get()
        if focused_widget and hasattr(focused_widget, 'cget'):
            try:
                text = focused_widget.cget('text')
                if text:
                    # This would integrate with screen reader APIs
                    print(f"Current element: {text}")
            except:
                pass
    
    def _read_status(self):
        """Read current status"""
        if hasattr(self.root, 'main_window') and hasattr(self.root.main_window, 'status_label'):
            status_text = self.root.main_window.status_label.cget('text')
            print(f"Status: {status_text}")
    
    def _toggle_high_contrast(self):
        """Toggle high contrast mode"""
        # This would need to be implemented with theme switching
        pass
    
    def _focus_main_content(self):
        """Focus main content area"""
        if hasattr(self.root, 'main_window'):
            content_frame = self.root.main_window.get_content_frame()
            if content_frame:
                content_frame.focus_set()
    
    def _focus_navigation(self):
        """Focus navigation area"""
        if hasattr(self.root, 'main_window'):
            # Focus first navigation button
            for button in self.root.main_window.nav_buttons.values():
                button.focus()
                break
    
    def _increase_text_size(self):
        """Increase text size for accessibility"""
        # This would need to be implemented with font scaling
        pass
    
    def _decrease_text_size(self):
        """Decrease text size for accessibility"""
        # This would need to be implemented with font scaling
        pass


def setup_chat_shortcuts(shortcut_manager: KeyboardShortcutManager, chat_interface):
    """Setup chat-specific keyboard shortcuts"""
    shortcut_manager.register_context_shortcut(
        "chat", "<Control-Return>", 
        lambda: chat_interface._on_send_clicked(),
        "Send message"
    )
    
    shortcut_manager.register_context_shortcut(
        "chat", "<Control-l>",
        lambda: chat_interface.clear_chat(),
        "Clear chat history"
    )
    
    shortcut_manager.register_context_shortcut(
        "chat", "<Control-e>",
        lambda: chat_interface.export_chat_history(),
        "Export chat history"
    )


def setup_document_shortcuts(shortcut_manager: KeyboardShortcutManager, document_viewer):
    """Setup document-specific keyboard shortcuts"""
    shortcut_manager.register_context_shortcut(
        "documents", "<Control-o>",
        lambda: document_viewer._on_upload_clicked(),
        "Upload document"
    )
    
    shortcut_manager.register_context_shortcut(
        "documents", "<Delete>",
        lambda: document_viewer._on_clear_clicked(),
        "Clear document"
    )
    
    shortcut_manager.register_context_shortcut(
        "documents", "<F5>",
        lambda: document_viewer._on_refresh_clicked(),
        "Refresh document view"
    )


def setup_game_shortcuts(shortcut_manager: KeyboardShortcutManager, game_manager):
    """Setup game-specific keyboard shortcuts"""
    shortcut_manager.register_context_shortcut(
        "games", "<Escape>",
        lambda: game_manager.show_game_selection(),
        "Return to game selection"
    )
    
    shortcut_manager.register_context_shortcut(
        "games", "<F2>",
        lambda: game_manager.restart_current_game(),
        "Restart current game"
    )
    
    # Game-specific shortcuts would be added based on the current game
    # For example, number keys for column selection in Connect 4
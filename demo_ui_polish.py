"""
UI Polish Demonstration for Z.E.U.S. Virtual Assistant

This script demonstrates the enhanced UI features including:
- Consistent styling and theming
- Responsive layout
- Keyboard shortcuts
- Accessibility features
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from ui.styles import StyleManager, ZeusTheme, create_styled_button, create_card_frame
from ui.keyboard_shortcuts import KeyboardShortcutManager
from ui.responsive_layout import ResponsiveLayoutManager, BreakpointSize


class UIPolishDemo:
    """Demonstration of UI polish features"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Z.E.U.S. UI Polish Demo")
        self.root.geometry("900x600")
        self.root.minsize(600, 400)
        
        # Initialize UI systems
        self.style_manager = StyleManager(self.root)
        self.keyboard_manager = KeyboardShortcutManager(self.root)
        self.layout_manager = ResponsiveLayoutManager(self.root)
        
        # Setup demo
        self.setup_demo()
        self.setup_keyboard_shortcuts()
        
    def setup_demo(self):
        """Setup the demonstration interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Z.E.U.S. UI Polish Features Demo",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # Create demo sections
        self.create_styling_demo(main_frame)
        self.create_responsive_demo(main_frame)
        self.create_keyboard_demo(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_styling_demo(self, parent):
        """Create styling demonstration section"""
        # Styling demo card
        styling_card = create_card_frame(parent, "Consistent Styling & Theming")
        styling_card.pack(fill=tk.X, pady=(0, 15))
        
        # Button styles demonstration
        button_frame = ttk.Frame(styling_card)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(button_frame, text="Button Styles:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        buttons_container = ttk.Frame(button_frame)
        buttons_container.pack(fill=tk.X, pady=5)
        
        # Different button styles
        create_styled_button(
            buttons_container, "Primary", 
            command=lambda: self.show_message("Primary button clicked!"),
            style="Primary"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        create_styled_button(
            buttons_container, "Secondary",
            command=lambda: self.show_message("Secondary button clicked!"),
            style="Secondary"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        create_styled_button(
            buttons_container, "Success",
            command=lambda: self.show_message("Success button clicked!"),
            style="Success"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        create_styled_button(
            buttons_container, "Danger",
            command=lambda: self.show_message("Danger button clicked!"),
            style="Danger"
        ).pack(side=tk.LEFT)
        
        # Color palette demonstration
        color_frame = ttk.Frame(styling_card)
        color_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(color_frame, text="Color Palette:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        colors_container = ttk.Frame(color_frame)
        colors_container.pack(fill=tk.X, pady=5)
        
        # Show key colors
        key_colors = ['primary', 'success', 'warning', 'danger', 'info']
        for color_name in key_colors:
            color_value = self.style_manager.get_color(color_name)
            color_label = tk.Label(
                colors_container,
                text=f"{color_name.title()}\n{color_value}",
                bg=color_value,
                fg='white' if color_name != 'warning' else 'black',
                font=("Arial", 9),
                width=12,
                height=3,
                relief=tk.RAISED,
                borderwidth=1
            )
            color_label.pack(side=tk.LEFT, padx=2)
    
    def create_responsive_demo(self, parent):
        """Create responsive layout demonstration"""
        responsive_card = create_card_frame(parent, "Responsive Layout")
        responsive_card.pack(fill=tk.X, pady=(0, 15))
        
        # Current breakpoint display
        self.breakpoint_label = ttk.Label(
            responsive_card,
            text=f"Current Breakpoint: {self.layout_manager.get_current_breakpoint().value}",
            font=("Arial", 11, "bold")
        )
        self.breakpoint_label.pack(pady=5)
        
        # Window size display
        self.size_label = ttk.Label(
            responsive_card,
            text=f"Window Size: {self.root.winfo_width()}x{self.root.winfo_height()}",
            font=("Arial", 10)
        )
        self.size_label.pack(pady=2)
        
        # Layout configuration display
        config = self.layout_manager.get_current_config()
        self.config_label = ttk.Label(
            responsive_card,
            text=f"Layout: Sidebar={config.sidebar_width}px, Padding={config.content_padding}px, Compact={config.compact_mode}",
            font=("Arial", 9)
        )
        self.config_label.pack(pady=2)
        
        # Add resize callback to update display
        self.layout_manager.add_resize_callback(self.update_responsive_display)
        
        # Resize instructions
        ttk.Label(
            responsive_card,
            text="Try resizing the window to see responsive behavior!",
            font=("Arial", 10, "italic"),
            foreground=self.style_manager.get_color('muted')
        ).pack(pady=5)
    
    def create_keyboard_demo(self, parent):
        """Create keyboard shortcuts demonstration"""
        keyboard_card = create_card_frame(parent, "Keyboard Shortcuts & Accessibility")
        keyboard_card.pack(fill=tk.X, pady=(0, 15))
        
        # Shortcuts info
        shortcuts_text = """
Key Shortcuts Available:
• F1: Show help dialog
• Ctrl+Q: Quit application
• Ctrl+R: Refresh display
• Ctrl+Plus/Minus: Zoom in/out (placeholder)
• F11: Toggle fullscreen
• Escape: Cancel/Clear focus
• Tab/Shift+Tab: Navigate between elements
        """.strip()
        
        ttk.Label(
            keyboard_card,
            text=shortcuts_text,
            font=("Arial", 10),
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=5)
        
        # Test buttons
        test_frame = ttk.Frame(keyboard_card)
        test_frame.pack(fill=tk.X, pady=10)
        
        create_styled_button(
            test_frame, "Show Shortcuts (F1)",
            command=self.show_shortcuts_help,
            style="Secondary"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        create_styled_button(
            test_frame, "Test Focus Navigation",
            command=self.test_focus_navigation,
            style="Secondary"
        ).pack(side=tk.LEFT)
    
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame,
            text="UI Polish Demo Ready - Try the keyboard shortcuts!",
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Theme info
        theme_label = ttk.Label(
            status_frame,
            text="Zeus Theme Active",
            font=("Arial", 9),
            foreground=self.style_manager.get_color('primary')
        )
        theme_label.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def setup_keyboard_shortcuts(self):
        """Setup demo-specific keyboard shortcuts"""
        # Override some shortcuts for demo
        self.keyboard_manager.register_shortcut(
            "<Control-r>", self.refresh_demo, "Refresh demo display"
        )
        
        self.keyboard_manager.register_shortcut(
            "<Control-t>", self.toggle_theme_info, "Toggle theme information"
        )
    
    def show_message(self, message: str):
        """Show a message and update status"""
        messagebox.showinfo("Demo", message)
        self.update_status(f"Action: {message}")
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help"""
        self.keyboard_manager._show_shortcuts()
        self.update_status("Showed keyboard shortcuts help")
    
    def test_focus_navigation(self):
        """Test focus navigation"""
        # Focus the first button we can find
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Button):
                        child.focus()
                        self.update_status("Focus set to first button - use Tab to navigate")
                        return
    
    def refresh_demo(self):
        """Refresh the demo display"""
        self.update_responsive_display(
            self.root.winfo_width(),
            self.root.winfo_height(),
            self.layout_manager.get_current_breakpoint()
        )
        self.update_status("Demo display refreshed")
    
    def toggle_theme_info(self):
        """Toggle theme information display"""
        theme = ZeusTheme()
        info = f"Colors: {len(theme.COLORS)}, Fonts: {len(theme.FONTS)}, Spacing: {len(theme.SPACING)}"
        messagebox.showinfo("Theme Info", info)
        self.update_status("Showed theme information")
    
    def update_responsive_display(self, width: int, height: int, breakpoint):
        """Update responsive layout display"""
        try:
            self.breakpoint_label.configure(text=f"Current Breakpoint: {breakpoint.value}")
            self.size_label.configure(text=f"Window Size: {width}x{height}")
            
            config = self.layout_manager.get_current_config()
            self.config_label.configure(
                text=f"Layout: Sidebar={config.sidebar_width}px, Padding={config.content_padding}px, Compact={config.compact_mode}"
            )
            
            self.update_status(f"Layout updated for {breakpoint.value} screen")
        except Exception as e:
            print(f"Error updating responsive display: {e}")
    
    def update_status(self, message: str):
        """Update status bar message"""
        if hasattr(self, 'status_label'):
            self.status_label.configure(text=message)
    
    def run(self):
        """Run the demo"""
        self.update_status("UI Polish Demo started - Press F1 for help")
        self.root.mainloop()


if __name__ == "__main__":
    print("Starting Z.E.U.S. UI Polish Demo...")
    print("This demo showcases the enhanced UI features:")
    print("- Consistent styling and theming")
    print("- Responsive layout that adapts to window size")
    print("- Comprehensive keyboard shortcuts")
    print("- Accessibility features")
    print("\nPress F1 in the demo window for keyboard shortcuts help!")
    
    try:
        demo = UIPolishDemo()
        demo.run()
    except Exception as e:
        print(f"Error running demo: {e}")
        print("This might be due to display/GUI environment limitations.")
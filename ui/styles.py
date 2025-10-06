"""
Centralized styling and theming for Z.E.U.S. Virtual Assistant

This module provides consistent styling, theming, and responsive layout
capabilities across all application components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, Tuple
import platform


class ZeusTheme:
    """Central theme configuration for Z.E.U.S. application"""
    
    # Color palette
    COLORS = {
        'primary': '#0078d4',
        'primary_dark': '#106ebe',
        'primary_light': '#40a9ff',
        'secondary': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'muted': '#6c757d',
        'white': '#ffffff',
        'black': '#000000',
        'text_primary': '#333333',
        'text_secondary': '#666666',
        'text_muted': '#999999',
        'border': '#dee2e6',
        'background': '#ffffff',
        'background_alt': '#f8f9fa',
        'success': '#28a745',
        'error': '#dc3545'
    }
    
    # Typography
    FONTS = {
        'title': ('Arial', 24, 'bold'),
        'heading': ('Arial', 16, 'bold'),
        'subheading': ('Arial', 14, 'bold'),
        'body': ('Arial', 11),
        'body_bold': ('Arial', 11, 'bold'),
        'small': ('Arial', 9),
        'small_bold': ('Arial', 9, 'bold'),
        'code': ('Consolas', 10),
        'button': ('Arial', 10),
        'nav': ('Arial', 11)
    }
    
    # Spacing
    SPACING = {
        'xs': 2,
        'sm': 5,
        'md': 10,
        'lg': 15,
        'xl': 20,
        'xxl': 30
    }
    
    # Component dimensions
    DIMENSIONS = {
        'button_height': 32,
        'input_height': 28,
        'nav_button_width': 180,
        'sidebar_width': 200,
        'border_width': 1,
        'corner_radius': 4
    }


class StyleManager:
    """Manages application-wide styling and theming"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.theme = ZeusTheme()
        self.style = ttk.Style()
        self.responsive_callbacks = []
        
        # Initialize styling
        self.setup_ttk_styles()
        self.setup_responsive_behavior()
    
    def setup_ttk_styles(self):
        """Configure TTK styles for consistent appearance"""
        # Use a modern theme as base
        available_themes = self.style.theme_names()
        if 'clam' in available_themes:
            self.style.theme_use('clam')
        elif 'alt' in available_themes:
            self.style.theme_use('alt')
        
        # Configure custom styles
        self._configure_button_styles()
        self._configure_frame_styles()
        self._configure_label_styles()
        self._configure_entry_styles()
        self._configure_notebook_styles()
        self._configure_progressbar_styles()
        self._configure_separator_styles()
    
    def _configure_button_styles(self):
        """Configure button styles"""
        # Primary button
        self.style.configure(
            'Primary.TButton',
            background=self.theme.COLORS['primary'],
            foreground=self.theme.COLORS['white'],
            font=self.theme.FONTS['button'],
            padding=(12, 8),
            borderwidth=0,
            focuscolor='none'
        )
        self.style.map(
            'Primary.TButton',
            background=[
                ('active', self.theme.COLORS['primary_light']),
                ('pressed', self.theme.COLORS['primary_dark']),
                ('disabled', self.theme.COLORS['muted'])
            ],
            foreground=[('disabled', self.theme.COLORS['white'])]
        )
        
        # Secondary button
        self.style.configure(
            'Secondary.TButton',
            background=self.theme.COLORS['light'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['button'],
            padding=(12, 8),
            borderwidth=1,
            relief='solid',
            focuscolor='none'
        )
        self.style.map(
            'Secondary.TButton',
            background=[
                ('active', self.theme.COLORS['background_alt']),
                ('pressed', self.theme.COLORS['border']),
                ('disabled', self.theme.COLORS['light'])
            ],
            foreground=[('disabled', self.theme.COLORS['muted'])]
        )
        
        # Navigation button
        self.style.configure(
            'Nav.TButton',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['nav'],
            padding=(15, 10),
            borderwidth=0,
            anchor='w',
            focuscolor='none'
        )
        self.style.map(
            'Nav.TButton',
            background=[
                ('active', self.theme.COLORS['background_alt']),
                ('pressed', self.theme.COLORS['border'])
            ]
        )
        
        # Active navigation button
        self.style.configure(
            'NavActive.TButton',
            background=self.theme.COLORS['primary'],
            foreground=self.theme.COLORS['white'],
            font=self.theme.FONTS['nav'],
            padding=(15, 10),
            borderwidth=0,
            anchor='w',
            focuscolor='none'
        )
        self.style.map(
            'NavActive.TButton',
            background=[
                ('active', self.theme.COLORS['primary_light']),
                ('pressed', self.theme.COLORS['primary_dark'])
            ]
        )
        
        # Success button
        self.style.configure(
            'Success.TButton',
            background=self.theme.COLORS['success'],
            foreground=self.theme.COLORS['white'],
            font=self.theme.FONTS['button'],
            padding=(12, 8),
            borderwidth=0,
            focuscolor='none'
        )
        
        # Danger button
        self.style.configure(
            'Danger.TButton',
            background=self.theme.COLORS['danger'],
            foreground=self.theme.COLORS['white'],
            font=self.theme.FONTS['button'],
            padding=(12, 8),
            borderwidth=0,
            focuscolor='none'
        )
    
    def _configure_frame_styles(self):
        """Configure frame styles"""
        self.style.configure(
            'Card.TFrame',
            background=self.theme.COLORS['white'],
            relief='solid',
            borderwidth=1
        )
        
        self.style.configure(
            'Sidebar.TFrame',
            background=self.theme.COLORS['background_alt'],
            relief='solid',
            borderwidth=1
        )
    
    def _configure_label_styles(self):
        """Configure label styles"""
        # Title labels
        self.style.configure(
            'Title.TLabel',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['primary'],
            font=self.theme.FONTS['title']
        )
        
        # Heading labels
        self.style.configure(
            'Heading.TLabel',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['primary'],
            font=self.theme.FONTS['heading']
        )
        
        # Status labels
        self.style.configure(
            'Status.TLabel',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['muted'],
            font=self.theme.FONTS['small']
        )
        
        # Success status
        self.style.configure(
            'StatusSuccess.TLabel',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['success'],
            font=self.theme.FONTS['small_bold']
        )
        
        # Error status
        self.style.configure(
            'StatusError.TLabel',
            background=self.theme.COLORS['background'],
            foreground=self.theme.COLORS['error'],
            font=self.theme.FONTS['small_bold']
        )
    
    def _configure_entry_styles(self):
        """Configure entry and text widget styles"""
        self.style.configure(
            'Modern.TEntry',
            fieldbackground=self.theme.COLORS['white'],
            borderwidth=1,
            relief='solid',
            padding=(8, 6)
        )
        
        self.style.map(
            'Modern.TEntry',
            focuscolor=[('focus', self.theme.COLORS['primary'])],
            bordercolor=[('focus', self.theme.COLORS['primary'])]
        )
    
    def _configure_notebook_styles(self):
        """Configure notebook (tab) styles"""
        self.style.configure(
            'Modern.TNotebook',
            background=self.theme.COLORS['background'],
            borderwidth=0
        )
        
        self.style.configure(
            'Modern.TNotebook.Tab',
            background=self.theme.COLORS['light'],
            foreground=self.theme.COLORS['text_primary'],
            padding=(12, 8),
            font=self.theme.FONTS['body']
        )
        
        self.style.map(
            'Modern.TNotebook.Tab',
            background=[
                ('selected', self.theme.COLORS['primary']),
                ('active', self.theme.COLORS['background_alt'])
            ],
            foreground=[('selected', self.theme.COLORS['white'])]
        )
    
    def _configure_progressbar_styles(self):
        """Configure progress bar styles"""
        self.style.configure(
            'Modern.Horizontal.TProgressbar',
            background=self.theme.COLORS['primary'],
            troughcolor=self.theme.COLORS['light'],
            borderwidth=0,
            lightcolor=self.theme.COLORS['primary'],
            darkcolor=self.theme.COLORS['primary']
        )
    
    def _configure_separator_styles(self):
        """Configure separator styles"""
        self.style.configure(
            'Modern.TSeparator',
            background=self.theme.COLORS['border']
        )
    
    def setup_responsive_behavior(self):
        """Setup responsive layout behavior"""
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Track window state
        self.last_width = self.root.winfo_width()
        self.last_height = self.root.winfo_height()
    
    def _on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            current_width = self.root.winfo_width()
            current_height = self.root.winfo_height()
            
            # Only process significant size changes
            if (abs(current_width - self.last_width) > 10 or 
                abs(current_height - self.last_height) > 10):
                
                self.last_width = current_width
                self.last_height = current_height
                
                # Notify responsive callbacks
                for callback in self.responsive_callbacks:
                    try:
                        callback(current_width, current_height)
                    except Exception as e:
                        print(f"Error in responsive callback: {e}")
    
    def add_responsive_callback(self, callback):
        """Add a callback for window resize events"""
        self.responsive_callbacks.append(callback)
    
    def get_color(self, color_name: str) -> str:
        """Get color value by name"""
        return self.theme.COLORS.get(color_name, '#000000')
    
    def get_font(self, font_name: str) -> Tuple:
        """Get font configuration by name"""
        return self.theme.FONTS.get(font_name, ('Arial', 11))
    
    def get_spacing(self, size: str) -> int:
        """Get spacing value by size name"""
        return self.theme.SPACING.get(size, 10)


class ResponsiveWidget:
    """Base class for responsive widgets"""
    
    def __init__(self, widget, style_manager: StyleManager):
        self.widget = widget
        self.style_manager = style_manager
        self.breakpoints = {
            'small': 800,
            'medium': 1200,
            'large': 1600
        }
        
        # Register for resize events
        style_manager.add_responsive_callback(self.on_resize)
    
    def on_resize(self, width: int, height: int):
        """Handle resize events - to be overridden by subclasses"""
        pass
    
    def get_breakpoint(self, width: int) -> str:
        """Determine current breakpoint based on width"""
        if width < self.breakpoints['small']:
            return 'small'
        elif width < self.breakpoints['medium']:
            return 'medium'
        elif width < self.breakpoints['large']:
            return 'large'
        else:
            return 'xlarge'


def apply_modern_styling(widget, style_type: str = 'default'):
    """Apply modern styling to a widget"""
    if isinstance(widget, tk.Text):
        widget.configure(
            font=ZeusTheme.FONTS['body'],
            bg=ZeusTheme.COLORS['white'],
            fg=ZeusTheme.COLORS['text_primary'],
            selectbackground=ZeusTheme.COLORS['primary_light'],
            selectforeground=ZeusTheme.COLORS['white'],
            insertbackground=ZeusTheme.COLORS['primary'],
            relief='solid',
            borderwidth=1,
            padx=10,
            pady=8
        )
    elif isinstance(widget, tk.Listbox):
        widget.configure(
            font=ZeusTheme.FONTS['body'],
            bg=ZeusTheme.COLORS['white'],
            fg=ZeusTheme.COLORS['text_primary'],
            selectbackground=ZeusTheme.COLORS['primary'],
            selectforeground=ZeusTheme.COLORS['white'],
            relief='solid',
            borderwidth=1
        )
    elif isinstance(widget, tk.Canvas):
        widget.configure(
            bg=ZeusTheme.COLORS['white'],
            highlightthickness=0,
            relief='solid',
            borderwidth=1
        )


def create_styled_button(parent, text: str, command=None, style: str = 'Primary') -> ttk.Button:
    """Create a styled button with consistent appearance"""
    return ttk.Button(
        parent,
        text=text,
        command=command,
        style=f'{style}.TButton'
    )


def create_card_frame(parent, title: str = None, padding: int = 15) -> ttk.Frame:
    """Create a card-style frame with optional title"""
    if title:
        frame = ttk.LabelFrame(parent, text=title, style='Card.TFrame', padding=padding)
    else:
        frame = ttk.Frame(parent, style='Card.TFrame', padding=padding)
    return frame


def setup_keyboard_navigation(root: tk.Tk):
    """Setup application-wide keyboard navigation"""
    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return "break"
    
    def focus_prev_widget(event):
        event.widget.tk_focusPrev().focus()
        return "break"
    
    # Tab navigation
    root.bind_class("all", "<Tab>", focus_next_widget)
    root.bind_class("all", "<Shift-Tab>", focus_prev_widget)
    
    # Escape to clear focus
    root.bind_class("all", "<Escape>", lambda e: root.focus_set())


def setup_accessibility_features(root: tk.Tk):
    """Setup accessibility features"""
    # High contrast mode detection (Windows)
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Control Panel\Accessibility\HighContrast")
            high_contrast, _ = winreg.QueryValueEx(key, "Flags")
            winreg.CloseKey(key)
            
            if high_contrast & 1:  # High contrast is enabled
                # Apply high contrast theme
                apply_high_contrast_theme(root)
        except:
            pass  # Ignore errors in accessibility detection
    
    # Screen reader support
    root.option_add('*TearOff', False)  # Remove tear-off menus


def apply_high_contrast_theme(root: tk.Tk):
    """Apply high contrast theme for accessibility"""
    style = ttk.Style()
    
    # High contrast colors
    hc_colors = {
        'bg': '#000000',
        'fg': '#ffffff',
        'select_bg': '#0078d4',
        'select_fg': '#ffffff'
    }
    
    # Apply to all widgets
    style.configure('TLabel', background=hc_colors['bg'], foreground=hc_colors['fg'])
    style.configure('TButton', background=hc_colors['bg'], foreground=hc_colors['fg'])
    style.configure('TFrame', background=hc_colors['bg'])
    
    # Configure root window
    root.configure(bg=hc_colors['bg'])
"""
Responsive layout management for Z.E.U.S. Virtual Assistant

This module provides responsive layout capabilities that adapt to
different window sizes and screen resolutions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class BreakpointSize(Enum):
    """Screen size breakpoints"""
    SMALL = "small"      # < 800px
    MEDIUM = "medium"    # 800-1200px
    LARGE = "large"      # 1200-1600px
    XLARGE = "xlarge"    # > 1600px


@dataclass
class LayoutConfig:
    """Configuration for responsive layout"""
    sidebar_width: int
    content_padding: int
    button_size: str
    font_scale: float
    grid_columns: int
    compact_mode: bool


class ResponsiveLayoutManager:
    """Manages responsive layout behavior across the application"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_breakpoint = BreakpointSize.LARGE
        self.layout_configs = self._create_layout_configs()
        self.responsive_widgets: List['ResponsiveWidget'] = []
        self.resize_callbacks: List[Callable] = []
        
        # Track window dimensions
        self.last_width = 1000
        self.last_height = 700
        
        # Setup resize monitoring
        self.root.bind('<Configure>', self._on_window_configure)
        
        # Initial layout setup
        self.root.after(100, self._initial_layout_setup)
    
    def _create_layout_configs(self) -> Dict[BreakpointSize, LayoutConfig]:
        """Create layout configurations for different breakpoints"""
        return {
            BreakpointSize.SMALL: LayoutConfig(
                sidebar_width=60,      # Collapsed sidebar
                content_padding=5,
                button_size="small",
                font_scale=0.9,
                grid_columns=1,
                compact_mode=True
            ),
            BreakpointSize.MEDIUM: LayoutConfig(
                sidebar_width=150,     # Reduced sidebar
                content_padding=10,
                button_size="medium",
                font_scale=1.0,
                grid_columns=2,
                compact_mode=False
            ),
            BreakpointSize.LARGE: LayoutConfig(
                sidebar_width=200,     # Full sidebar
                content_padding=15,
                button_size="large",
                font_scale=1.0,
                grid_columns=3,
                compact_mode=False
            ),
            BreakpointSize.XLARGE: LayoutConfig(
                sidebar_width=220,     # Extended sidebar
                content_padding=20,
                button_size="large",
                font_scale=1.1,
                grid_columns=4,
                compact_mode=False
            )
        } 
   
    def _determine_breakpoint(self, width: int) -> BreakpointSize:
        """Determine breakpoint based on window width"""
        if width < 800:
            return BreakpointSize.SMALL
        elif width < 1200:
            return BreakpointSize.MEDIUM
        elif width < 1600:
            return BreakpointSize.LARGE
        else:
            return BreakpointSize.XLARGE
    
    def _on_window_configure(self, event):
        """Handle window resize events"""
        if event.widget != self.root:
            return
        
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Only process significant changes
        if (abs(current_width - self.last_width) > 20 or 
            abs(current_height - self.last_height) > 20):
            
            self.last_width = current_width
            self.last_height = current_height
            
            # Check if breakpoint changed
            new_breakpoint = self._determine_breakpoint(current_width)
            if new_breakpoint != self.current_breakpoint:
                self.current_breakpoint = new_breakpoint
                self._apply_responsive_layout()
            
            # Notify all responsive widgets
            for widget in self.responsive_widgets:
                widget.on_resize(current_width, current_height)
            
            # Call resize callbacks
            for callback in self.resize_callbacks:
                try:
                    callback(current_width, current_height, new_breakpoint)
                except Exception as e:
                    print(f"Error in resize callback: {e}")
    
    def _initial_layout_setup(self):
        """Setup initial responsive layout"""
        width = self.root.winfo_width()
        self.current_breakpoint = self._determine_breakpoint(width)
        self._apply_responsive_layout()
    
    def _apply_responsive_layout(self):
        """Apply layout changes based on current breakpoint"""
        config = self.layout_configs[self.current_breakpoint]
        
        # Apply layout to main window if available
        if hasattr(self.root, 'main_window'):
            self._apply_main_window_layout(config)
    
    def _apply_main_window_layout(self, config: LayoutConfig):
        """Apply responsive layout to main window"""
        main_window = self.root.main_window
        
        # Adjust sidebar width
        if hasattr(main_window, 'nav_frame'):
            if config.compact_mode:
                # Collapse sidebar to icons only
                self._collapse_sidebar(main_window)
            else:
                # Expand sidebar
                self._expand_sidebar(main_window, config.sidebar_width)
    
    def _collapse_sidebar(self, main_window):
        """Collapse sidebar for small screens"""
        # This would modify the navigation to show only icons
        for button_name, button in main_window.nav_buttons.items():
            # Get icon from button text
            text = button.cget('text')
            icon = text.split()[0] if text else "●"
            button.configure(text=icon, width=5)
    
    def _expand_sidebar(self, main_window, width: int):
        """Expand sidebar for larger screens"""
        # Restore full button text
        button_texts = {
            'chat': '💬 Chat',
            'documents': '📄 Documents',
            'games': '🎮 Games'
        }
        
        for button_name, button in main_window.nav_buttons.items():
            if button_name in button_texts:
                button.configure(text=button_texts[button_name], width=20)
    
    def register_responsive_widget(self, widget: 'ResponsiveWidget'):
        """Register a widget for responsive updates"""
        self.responsive_widgets.append(widget)
    
    def add_resize_callback(self, callback: Callable):
        """Add a callback for resize events"""
        self.resize_callbacks.append(callback)
    
    def get_current_config(self) -> LayoutConfig:
        """Get current layout configuration"""
        return self.layout_configs[self.current_breakpoint]
    
    def get_current_breakpoint(self) -> BreakpointSize:
        """Get current breakpoint"""
        return self.current_breakpoint


class ResponsiveWidget:
    """Base class for widgets that adapt to screen size changes"""
    
    def __init__(self, widget, layout_manager: ResponsiveLayoutManager):
        self.widget = widget
        self.layout_manager = layout_manager
        layout_manager.register_responsive_widget(self)
    
    def on_resize(self, width: int, height: int):
        """Handle resize events - override in subclasses"""
        pass


class ResponsiveFrame(ResponsiveWidget):
    """A frame that adapts its layout based on screen size"""
    
    def __init__(self, parent, layout_manager: ResponsiveLayoutManager, **kwargs):
        self.frame = ttk.Frame(parent, **kwargs)
        super().__init__(self.frame, layout_manager)
        self.child_widgets = []
    
    def add_widget(self, widget, grid_options: Dict = None, pack_options: Dict = None):
        """Add a widget with responsive options"""
        self.child_widgets.append({
            'widget': widget,
            'grid_options': grid_options or {},
            'pack_options': pack_options or {}
        })
        self._layout_widgets()
    
    def _layout_widgets(self):
        """Layout widgets based on current breakpoint"""
        config = self.layout_manager.get_current_config()
        
        if config.compact_mode:
            self._layout_compact()
        else:
            self._layout_normal()
    
    def _layout_compact(self):
        """Layout for compact/mobile view"""
        for i, widget_info in enumerate(self.child_widgets):
            widget = widget_info['widget']
            # Stack vertically in compact mode
            widget.pack(fill=tk.X, pady=2)
    
    def _layout_normal(self):
        """Layout for normal desktop view"""
        config = self.layout_manager.get_current_config()
        
        for i, widget_info in enumerate(self.child_widgets):
            widget = widget_info['widget']
            grid_options = widget_info['grid_options']
            
            if grid_options:
                row = i // config.grid_columns
                col = i % config.grid_columns
                widget.grid(row=row, column=col, **grid_options)
            else:
                widget.pack(**widget_info['pack_options'])
    
    def on_resize(self, width: int, height: int):
        """Handle resize for this frame"""
        self._layout_widgets()


class ResponsiveText(ResponsiveWidget):
    """A text widget that adapts font size and layout"""
    
    def __init__(self, parent, layout_manager: ResponsiveLayoutManager, **kwargs):
        self.text_widget = tk.Text(parent, **kwargs)
        super().__init__(self.text_widget, layout_manager)
        self.base_font_size = 11
    
    def on_resize(self, width: int, height: int):
        """Adjust font size based on screen size"""
        config = self.layout_manager.get_current_config()
        new_font_size = int(self.base_font_size * config.font_scale)
        
        current_font = self.text_widget.cget('font')
        if isinstance(current_font, tuple):
            font_family, _, *font_options = current_font
            new_font = (font_family, new_font_size, *font_options)
        else:
            new_font = ('Arial', new_font_size)
        
        self.text_widget.configure(font=new_font)


def create_responsive_grid(parent, layout_manager: ResponsiveLayoutManager, 
                          widgets: List[tk.Widget], **grid_options) -> ResponsiveFrame:
    """Create a responsive grid layout"""
    responsive_frame = ResponsiveFrame(parent, layout_manager)
    
    for widget in widgets:
        responsive_frame.add_widget(widget, grid_options=grid_options)
    
    return responsive_frame


def make_widget_responsive(widget, layout_manager: ResponsiveLayoutManager, 
                          resize_callback: Optional[Callable] = None) -> ResponsiveWidget:
    """Make any widget responsive"""
    class CustomResponsiveWidget(ResponsiveWidget):
        def on_resize(self, width: int, height: int):
            if resize_callback:
                resize_callback(self.widget, width, height, 
                              layout_manager.get_current_breakpoint())
    
    return CustomResponsiveWidget(widget, layout_manager)
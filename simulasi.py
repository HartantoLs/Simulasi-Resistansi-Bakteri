import tkinter as tk
from tkinter import ttk, Frame, Scale, HORIZONTAL, StringVar, DoubleVar, IntVar
import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import time
import threading
import random
import sys
from PIL import Image, ImageTk, ImageFont
import colorsys
import os
import matplotlib.font_manager as fm
import platform

# Custom color scheme
COLORS = {
    "primary": "#006A71",      # Dark teal
    "secondary": "#48A6A7",    # Medium teal
    "tertiary": "#9ACBD0",     # Light teal
    "background": "#F2EFE7",   # Off-white
    "text": "#333333",         # Dark gray for text
    "text_light": "#666666",   # Light gray for secondary text
    "accent": "#E74C3C",       # Red for alerts/highlights
    "border": "#D0D0D0",       # Light gray for borders
    "button": "#006A71",       # Button background
    "button_hover": "#48A6A7", # Button hover
    "button_text": "#FFFFFF",  # Button text
}

# Try to load Roboto font for matplotlib
def setup_roboto_font():
    # Check system for Roboto font
    system = platform.system()
    roboto_paths = []
    
    if system == "Windows":
        font_dirs = [r"C:\Windows\Fonts"]
        for font_dir in font_dirs:
            if os.path.exists(os.path.join(font_dir, "Roboto-Regular.ttf")):
                roboto_paths.append(os.path.join(font_dir, "Roboto-Regular.ttf"))
    elif system == "Darwin":  # macOS
        font_dirs = ["/Library/Fonts", "/System/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
        for font_dir in font_dirs:
            if os.path.exists(os.path.join(font_dir, "Roboto-Regular.ttf")):
                roboto_paths.append(os.path.join(font_dir, "Roboto-Regular.ttf"))
    elif system == "Linux":
        font_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")]
        for font_dir in font_dirs:
            if os.path.exists(font_dir):
                for root, dirs, files in os.walk(font_dir):
                    if "Roboto-Regular.ttf" in files:
                        roboto_paths.append(os.path.join(root, "Roboto-Regular.ttf"))
    
    # If Roboto is found, add it to matplotlib's font manager
    if roboto_paths:
        for path in roboto_paths:
            try:
                fm.fontManager.addfont(path)
                plt.rcParams['font.family'] = 'Roboto'
                return True
            except:
                continue
    
    # If Roboto isn't found, use a similar sans-serif font
    plt.rcParams['font.family'] = 'sans-serif'
    return False

# Set up Roboto font
has_roboto = setup_roboto_font()

class ModernTooltip:
    """Modern tooltip implementation for Tkinter widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = tk.Frame(self.tooltip, bg=COLORS["primary"], bd=1)
        frame.pack(fill="both", expand=True)
        
        label = tk.Label(frame, text=self.text, justify="left", bg=COLORS["primary"], fg=COLORS["background"],
                       font=("Roboto", 9), padx=10, pady=5)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ModernButton(tk.Frame):
    """Custom modern button with hover effects"""
    def __init__(self, master, text, command, width=100, height=36, **kwargs):
        # Extract our custom parameters before passing to Frame constructor
        self.normal_bg = kwargs.pop('button_bg', COLORS["button"]) if 'button_bg' in kwargs else COLORS["button"]
        self.hover_bg = kwargs.pop('button_hover', COLORS["button_hover"]) if 'button_hover' in kwargs else COLORS["button_hover"]
        self.normal_fg = kwargs.pop('button_fg', COLORS["button_text"]) if 'button_fg' in kwargs else COLORS["button_text"]
        self.hover_fg = kwargs.pop('button_hover_fg', COLORS["button_text"]) if 'button_hover_fg' in kwargs else COLORS["button_text"]
        
        bg_color = kwargs.pop('bg', COLORS["background"]) if 'bg' in kwargs else COLORS["background"]
        
        # Now call the parent constructor with cleaned kwargs
        super().__init__(master, bg=bg_color, **kwargs)
        
        self.command = command
        self.width = width
        self.height = height
        self.corner_radius = 6
        
        # Create canvas for rounded rectangle button
        self.canvas = tk.Canvas(self, width=width, height=height, bg=bg_color, 
                              highlightthickness=0)
        self.canvas.pack()
        
        # Draw button shape
        self.shape_id = self.canvas.create_rounded_rectangle(
            2, 2, width-2, height-2, radius=self.corner_radius, fill=self.normal_bg)
        
        # Add text
        self.text_id = self.canvas.create_text(width//2, height//2, text=text, 
                                             fill=self.normal_fg, font=("Roboto", 10, "bold"))
        
        # Bind events
        self.canvas.bind("<Enter>", self.on_enter)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Set state
        self.state = tk.NORMAL
    
    def on_enter(self, event):
        if self.state == tk.NORMAL:
            self.canvas.itemconfig(self.shape_id, fill=self.hover_bg)
    
    def on_leave(self, event):
        if self.state == tk.NORMAL:
            self.canvas.itemconfig(self.shape_id, fill=self.normal_bg)
    
    def on_click(self, event):
        if self.state == tk.NORMAL:
            self.canvas.itemconfig(self.shape_id, fill=self.hover_bg)
    
    def on_release(self, event):
        if self.state == tk.NORMAL:
            self.canvas.itemconfig(self.shape_id, fill=self.normal_bg)
            self.command()
    
    def config(self, **kwargs):
        if 'state' in kwargs:
            self.state = kwargs['state']
            if self.state == tk.DISABLED:
                self.canvas.itemconfig(self.shape_id, fill="#cccccc")
                self.canvas.itemconfig(self.text_id, fill="#999999")
            else:
                self.canvas.itemconfig(self.shape_id, fill=self.normal_bg)
                self.canvas.itemconfig(self.text_id, fill=self.normal_fg)
        
        if 'text' in kwargs:
            self.canvas.itemconfig(self.text_id, text=kwargs['text'])

    # Add rounded rectangle method to Canvas class
    @staticmethod
    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

# Add the rounded rectangle method to Canvas
tk.Canvas.create_rounded_rectangle = ModernButton._create_rounded_rectangle

class ModernSlider(tk.Frame):
    """Custom modern slider with value display"""
    def __init__(self, master, min_val, max_val, resolution, variable, label_text, width=250, **kwargs):
        bg_color = kwargs.pop('bg', COLORS["background"])
        super().__init__(master, bg=bg_color, **kwargs)
        
        self.variable = variable
        self.min_val = min_val
        self.max_val = max_val
        
        # Label frame
        label_frame = tk.Frame(self, bg=bg_color)
        label_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Label
        self.label = tk.Label(label_frame, text=label_text, bg=bg_color, 
                            fg=COLORS["text"], font=("Roboto", 10))
        self.label.pack(side=tk.LEFT)
        
        # Value display
        self.value_var = tk.StringVar(value=f"{float(variable.get()):.3f}")
        self.value_label = tk.Label(label_frame, textvariable=self.value_var, bg=bg_color, 
                                  fg=COLORS["primary"], font=("Roboto", 10, "bold"))
        self.value_label.pack(side=tk.RIGHT)
        
        # Slider frame
        slider_frame = tk.Frame(self, bg=bg_color, pady=5)
        slider_frame.pack(fill=tk.X)
        
        # Custom slider styling
        slider_style = {
            'troughcolor': COLORS["tertiary"],
            'activebackground': COLORS["primary"],
            'bg': bg_color,
            'fg': COLORS["text"],
            'highlightthickness': 0,
            'sliderrelief': 'flat'
        }
        
        # Slider
        self.slider = Scale(slider_frame, from_=min_val, to=max_val, resolution=resolution,
                          orient=HORIZONTAL, variable=variable,
                          length=width, command=self.update_value,
                          **slider_style)
        self.slider.pack(fill=tk.X)
        
        # Add a thin line below for visual separation
        separator = tk.Frame(self, height=1, bg=COLORS["border"])
        separator.pack(fill=tk.X, pady=(5, 0))
    
    def update_value(self, value):
        self.value_var.set(f"{float(value):.3f}")

class BacterialResistanceSimulation:
    def __init__(self, master):
        self.master = master
        self.master.title("Antibiotic Resistance Evolution Simulator")
        self.master.geometry("1280x800")
        
        # Apply theme
        self.master.configure(bg=COLORS["background"])
        self.style = ttk.Style()
        self.configure_styles()
        
        # Initialize variables
        self.running = False
        self.paused = False
        self.population_size = 1000
        self.initial_resistance_range = (0.0, 0.1)
        self.antibiotic_concentration = 0.3
        self.mutation_std = 0.01
        self.reproduction_rate = 1.2
        self.carrying_capacity = 2000
        self.max_generations = 100  # Default max generations
        self.bacteria_population = []
        self.generation = 0
        self.avg_resistance_history = []
        self.population_history = []
        self.visualize_type = "scatter"
        
        # Setup pygame for visualization
        pygame.init()
        self.pygame_surface_size = (600, 400)
        self.pygame_surface = pygame.Surface(self.pygame_surface_size)
        
        # Create main frames
        self.create_frames()
        
        # Initialize status var early
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Press Start to begin simulation.")
        
        # Create control panel
        self.create_control_panel()
        
        # Create visualization area
        self.create_visualization_area()
        
        # Create charts
        self.create_charts()
        
        # Status bar
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, 
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                 bg=COLORS["background"], fg=COLORS["text"],
                                 font=("Roboto", 9), padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize population
        self.initialize_population()
        
        # Update pygame visualization
        self.update_pygame_visualization()
        
        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind window resize event
        self.master.bind("<Configure>", self.on_resize)
    
    def configure_styles(self):
        """Configure ttk styles for modern look"""
        self.style.configure("TButton", 
                           font=("Roboto", 10),
                           background=COLORS["button"],
                           foreground=COLORS["button_text"])
        
        self.style.map("TButton",
                     background=[("active", COLORS["button_hover"])],
                     foreground=[("active", COLORS["button_text"])])
        
        self.style.configure("Start.TButton", 
                           background=COLORS["secondary"],
                           foreground=COLORS["button_text"])
        
        self.style.map("Start.TButton",
                     background=[("active", COLORS["secondary"])],
                     foreground=[("active", COLORS["button_text"])])
        
        self.style.configure("Reset.TButton", 
                           background=COLORS["accent"],
                           foreground=COLORS["button_text"])
        
        self.style.map("Reset.TButton",
                     background=[("active", COLORS["accent"])],
                     foreground=[("active", COLORS["button_text"])])
        
        self.style.configure("TEntry", 
                           fieldbackground=COLORS["background"],
                           foreground=COLORS["text"])
        
        self.style.configure("TCombobox", 
                           fieldbackground=COLORS["background"],
                           foreground=COLORS["text"])
    
    def create_frames(self):
        # Create title frame
        self.title_frame = Frame(self.master, bg=COLORS["background"], pady=15)
        self.title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(self.title_frame, 
                             text="Bacterial Antibiotic Resistance Evolution Simulator", 
                             font=("Roboto", 20, "bold"), 
                             bg=COLORS["background"], 
                             fg=COLORS["primary"])
        title_label.pack(side=tk.LEFT)
        
        # Main content frame with 2 columns
        self.content_frame = Frame(self.master, bg=COLORS["background"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Left column for controls
        self.control_frame = Frame(self.content_frame, bg=COLORS["background"], 
                                 width=320, padx=15, pady=15,
                                 highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.control_frame.pack_propagate(False)  # Prevent shrinking
        
        # Right column for visualization and charts
        self.viz_frame = Frame(self.content_frame, bg=COLORS["background"])
        self.viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top frame for pygame visualization
        self.pygame_frame = Frame(self.viz_frame, bg=COLORS["background"], 
                                bd=0, padx=15, pady=15,
                                highlightbackground=COLORS["border"],
                                highlightthickness=1)
        self.pygame_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Bottom frame for matplotlib charts - make it taller
        self.chart_frame = Frame(self.viz_frame, bg=COLORS["background"], 
                               bd=0, padx=15, pady=15, height=350,  # Increased height
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        self.chart_frame.pack(fill=tk.X)
        
    def create_control_panel(self):
        # Control Panel Header
        control_label = tk.Label(self.control_frame, text="Simulation Controls", 
                               font=("Roboto", 14, "bold"), 
                               bg=COLORS["background"], 
                               fg=COLORS["primary"])
        control_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Control variables frame
        controls_vars_frame = Frame(self.control_frame, bg=COLORS["background"])
        controls_vars_frame.pack(fill=tk.X, pady=5)
        
        # Section: Population Parameters
        section_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        section_label = tk.Label(section_frame, text="Population Parameters", 
                               font=("Roboto", 12, "bold"), 
                               bg=COLORS["background"], 
                               fg=COLORS["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add a decorative line under section header
        section_line = tk.Frame(section_frame, height=2, bg=COLORS["primary"])
        section_line.pack(fill=tk.X, pady=(0, 10))
        
        # Initial Population
        param_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        param_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(param_frame, text="Initial Population:", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        self.population_var = tk.StringVar(value=str(self.population_size))
        population_entry = ttk.Entry(param_frame, textvariable=self.population_var, width=8, 
                                   font=("Roboto", 10))
        population_entry.pack(side=tk.RIGHT)
        ModernTooltip(population_entry, "Number of bacteria at the start of simulation")
        
        # Initial Resistance Range
        param_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        param_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(param_frame, text="Initial Resistance Range:", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        resistance_frame = Frame(param_frame, bg=COLORS["background"])
        resistance_frame.pack(side=tk.RIGHT)
        
        self.min_resistance_var = tk.StringVar(value=str(self.initial_resistance_range[0]))
        min_entry = ttk.Entry(resistance_frame, textvariable=self.min_resistance_var, width=4,
                            font=("Roboto", 10))
        min_entry.pack(side=tk.LEFT)
        
        tk.Label(resistance_frame, text=" - ", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        self.max_resistance_var = tk.StringVar(value=str(self.initial_resistance_range[1]))
        max_entry = ttk.Entry(resistance_frame, textvariable=self.max_resistance_var, width=4,
                            font=("Roboto", 10))
        max_entry.pack(side=tk.LEFT)
        ModernTooltip(resistance_frame, "Range of initial resistance values (0.0 to 1.0)")
        
        # Carrying Capacity
        param_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        param_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(param_frame, text="Carrying Capacity:", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        self.capacity_var = tk.StringVar(value=str(self.carrying_capacity))
        capacity_entry = ttk.Entry(param_frame, textvariable=self.capacity_var, width=8,
                                 font=("Roboto", 10))
        capacity_entry.pack(side=tk.RIGHT)
        ModernTooltip(capacity_entry, "Maximum population size the environment can support")
        
        # Max Generations
        param_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        param_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(param_frame, text="Max Generations:", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        self.max_gen_var = tk.StringVar(value=str(self.max_generations))
        max_gen_entry = ttk.Entry(param_frame, textvariable=self.max_gen_var, width=8,
                                font=("Roboto", 10))
        max_gen_entry.pack(side=tk.RIGHT)
        ModernTooltip(max_gen_entry, "Maximum number of generations to simulate (0 = unlimited)")
        
        # Section: Simulation Parameters
        section_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        section_frame.pack(fill=tk.X, pady=(20, 10))
        
        section_label = tk.Label(section_frame, text="Simulation Parameters", 
                               font=("Roboto", 12, "bold"), 
                               bg=COLORS["background"], 
                               fg=COLORS["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add a decorative line under section header
        section_line = tk.Frame(section_frame, height=2, bg=COLORS["primary"])
        section_line.pack(fill=tk.X, pady=(0, 10))
        
        # Antibiotic Concentration Slider
        self.antibiotic_var = tk.DoubleVar(value=self.antibiotic_concentration)
        antibiotic_slider = ModernSlider(
            controls_vars_frame, 0.0, 1.0, 0.01, self.antibiotic_var,
            "Antibiotic Concentration:", bg=COLORS["background"]
        )
        antibiotic_slider.pack(fill=tk.X, pady=8)
        ModernTooltip(antibiotic_slider, "Concentration of antibiotic in the environment (0.0 to 1.0)")
        
        # Mutation Rate Slider
        self.mutation_var = tk.DoubleVar(value=self.mutation_std)
        mutation_slider = ModernSlider(
            controls_vars_frame, 0.001, 0.1, 0.001, self.mutation_var,
            "Mutation Rate:", bg=COLORS["background"]
        )
        mutation_slider.pack(fill=tk.X, pady=8)
        ModernTooltip(mutation_slider, "Standard deviation of mutations in resistance values")
        
        # Reproduction Rate Slider
        self.reproduction_var = tk.DoubleVar(value=self.reproduction_rate)
        reproduction_slider = ModernSlider(
            controls_vars_frame, 1.0, 2.0, 0.05, self.reproduction_var,
            "Reproduction Rate:", bg=COLORS["background"]
        )
        reproduction_slider.pack(fill=tk.X, pady=8)
        ModernTooltip(reproduction_slider, "Average number of offspring per bacterium")
        
        # Section: Visualization
        section_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        section_frame.pack(fill=tk.X, pady=(20, 10))
        
        section_label = tk.Label(section_frame, text="Visualization", 
                               font=("Roboto", 12, "bold"), 
                               bg=COLORS["background"], 
                               fg=COLORS["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Add a decorative line under section header
        section_line = tk.Frame(section_frame, height=2, bg=COLORS["primary"])
        section_line.pack(fill=tk.X, pady=(0, 10))
        
        # Visualization Type
        param_frame = Frame(controls_vars_frame, bg=COLORS["background"])
        param_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(param_frame, text="Visualization Type:", 
               bg=COLORS["background"], fg=COLORS["text"],
               font=("Roboto", 10)).pack(side=tk.LEFT)
        
        self.viz_var = tk.StringVar(value=self.visualize_type)
        
        # Create a custom dropdown for visualization type
        viz_frame = tk.Frame(param_frame, bg=COLORS["background"])
        viz_frame.pack(side=tk.RIGHT)
        
        # Create radio buttons for visualization type
        scatter_radio = tk.Radiobutton(viz_frame, text="Scatter", variable=self.viz_var, 
                                     value="scatter", bg=COLORS["background"], 
                                     fg=COLORS["text"], font=("Roboto", 10),
                                     command=self.update_pygame_visualization,
                                     activebackground=COLORS["background"])
        scatter_radio.pack(side=tk.LEFT, padx=(0, 10))
        
        grid_radio = tk.Radiobutton(viz_frame, text="Grid", variable=self.viz_var, 
                                  value="grid", bg=COLORS["background"], 
                                  fg=COLORS["text"], font=("Roboto", 10),
                                  command=self.update_pygame_visualization,
                                  activebackground=COLORS["background"])
        grid_radio.pack(side=tk.LEFT)
        
        # Simulation Speed
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_slider = ModernSlider(
            controls_vars_frame, 0.1, 3.0, 0.1, self.speed_var,
            "Simulation Speed:", bg=COLORS["background"]
        )
        speed_slider.pack(fill=tk.X, pady=8)
        ModernTooltip(speed_slider, "Speed of simulation (higher values = faster simulation)")
        
        # Button frame for controls
        button_frame = Frame(self.control_frame, bg=COLORS["background"])
        button_frame.pack(fill=tk.X, pady=(25, 0))
        
        # Create custom modern buttons
        self.start_button = ModernButton(button_frame, text="Start", 
                                       command=self.start_simulation,
                                       button_bg=COLORS["secondary"],
                                       button_hover=COLORS["tertiary"],
                                       width=90, height=36)
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_button = ModernButton(button_frame, text="Pause", 
                                       command=self.pause_simulation,
                                       width=90, height=36)
        self.pause_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.pause_button.config(state=tk.DISABLED)
        
        self.reset_button = ModernButton(button_frame, text="Reset", 
                                       command=self.reset_simulation,
                                       button_bg=COLORS["accent"],
                                       button_hover="#ff6b5e",
                                       width=90, height=36)
        self.reset_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_visualization_area(self):
        # Pygame visualization
        self.pygame_canvas = tk.Canvas(self.pygame_frame, 
                                     width=self.pygame_surface_size[0], 
                                     height=self.pygame_surface_size[1], 
                                     bg=COLORS["background"],
                                     highlightthickness=0)
        self.pygame_canvas.pack(expand=True)
        
        # Info labels for the current state
        info_frame = Frame(self.pygame_frame, bg=COLORS["background"])
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Create a grid for info labels with better styling
        info_grid = Frame(info_frame, bg=COLORS["background"])
        info_grid.pack(fill=tk.X)
        
        # Style for info labels
        label_font = ("Roboto", 10)
        value_font = ("Roboto", 14, "bold")
        
        # Create a card-like container for each stat
        def create_stat_card(parent, label_text, value_var, column):
            card = Frame(parent, bg=COLORS["background"], padx=15, pady=10,
                       highlightbackground=COLORS["border"], highlightthickness=1)
            card.grid(row=0, column=column, padx=5, sticky="nsew")
            
            tk.Label(card, text=label_text, font=label_font, bg=COLORS["background"], 
                   fg=COLORS["text_light"]).pack(anchor=tk.W)
            
            value_label = tk.Label(card, textvariable=value_var, font=value_font, 
                                 bg=COLORS["background"], fg=COLORS["primary"])
            value_label.pack(anchor=tk.W)
            
            return card
        
        # Generation counter
        self.generation_var = tk.StringVar(value="0")
        create_stat_card(info_grid, "Generation:", self.generation_var, 0)
        
        # Population counter
        self.pop_count_var = tk.StringVar(value=f"{self.population_size}")
        create_stat_card(info_grid, "Population Size:", self.pop_count_var, 1)
        
        # Average resistance
        self.avg_res_var = tk.StringVar(value="0.05")
        create_stat_card(info_grid, "Average Resistance:", self.avg_res_var, 2)
        
        # Current antibiotic concentration
        self.conc_var = tk.StringVar(value=f"{self.antibiotic_concentration:.2f}")
        create_stat_card(info_grid, "Antibiotic Concentration:", self.conc_var, 3)
        
        # Make columns expand equally
        for i in range(4):
            info_grid.columnconfigure(i, weight=1)
    
    def create_charts(self):
        # Create matplotlib figure with custom style
        plt.style.use('ggplot')
        self.fig = Figure(figsize=(12, 6), dpi=100, facecolor=COLORS["background"])  # Increased height
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create subplots with more space
        self.fig.subplots_adjust(bottom=0.15, top=0.9, wspace=0.3)
        
        self.ax1 = self.fig.add_subplot(131)  # Population size
        self.ax2 = self.fig.add_subplot(132)  # Average resistance
        self.ax3 = self.fig.add_subplot(133)  # Resistance distribution
        
        # Configure plots with improved styling
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#f8f9fa')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#cccccc')
            ax.spines['left'].set_color('#cccccc')
            ax.tick_params(colors='#666666', labelsize=9)
            ax.xaxis.label.set_color('#333333')
            ax.yaxis.label.set_color('#333333')
            ax.title.set_color('#333333')
            # Increase font sizes
            ax.xaxis.label.set_fontsize(11)
            ax.yaxis.label.set_fontsize(11)
            ax.title.set_fontsize(13)
            ax.title.set_fontweight('bold')
        
        self.ax1.set_title("Population Size Over Time")
        self.ax1.set_xlabel("Generation")
        self.ax1.set_ylabel("Population Size")
        self.ax1.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        
        self.ax2.set_title("Average Resistance Over Time")
        self.ax2.set_xlabel("Generation")
        self.ax2.set_ylabel("Resistance Value")
        self.ax2.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        self.ax2.set_ylim(0, 1)
        
        self.ax3.set_title("Resistance Distribution")
        self.ax3.set_xlabel("Resistance Value")
        self.ax3.set_ylabel("Number of Bacteria")
        self.ax3.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        self.ax3.set_xlim(0, 1)
        
        # Update the canvas
        self.fig.tight_layout()
        self.canvas.draw()
    
    def initialize_population(self):
        try:
            # Parse parameter inputs
            self.population_size = int(self.population_var.get())
            min_res = float(self.min_resistance_var.get())
            max_res = float(self.max_resistance_var.get())
            self.initial_resistance_range = (min_res, max_res)
            self.max_generations = int(self.max_gen_var.get())
            
            # Create initial bacteria with resistance values
            self.bacteria_population = []
            for _ in range(self.population_size):
                resistance = random.uniform(self.initial_resistance_range[0], self.initial_resistance_range[1])
                self.bacteria_population.append(resistance)
            
            # Reset history
            self.avg_resistance_history = [np.mean(self.bacteria_population)]
            self.population_history = [len(self.bacteria_population)]
            self.generation = 0
            
            # Update GUI
            self.update_info_labels()
            self.update_charts()
            self.update_pygame_visualization()
            self.status_var.set("Population initialized. Ready to start simulation.")
            
        except ValueError as e:
            self.status_var.set(f"Error initializing population: {str(e)}")
    
    def simulation_step(self):
        # Update parameters from GUI
        self.antibiotic_concentration = self.antibiotic_var.get()
        self.mutation_std = self.mutation_var.get()
        self.reproduction_rate = self.reproduction_var.get()
        self.carrying_capacity = int(self.capacity_var.get())
        
        # Apply selection (bacteria survival based on resistance)
        survived = []
        for resistance in self.bacteria_population:
            # Calculate survival probability
            # Higher resistance means higher survival probability under antibiotic pressure
            survival_prob = max(0, 1 - (self.antibiotic_concentration - resistance))
            if random.random() < survival_prob:
                survived.append(resistance)
        
        # Reproduction with mutation
        next_gen = []
        # Limit reproduction based on carrying capacity
        for resistance in survived:
            # Reproduction rate determines average number of offspring
            num_offspring = 0
            # Using Poisson-like process for number of offspring
            remaining_prob = self.reproduction_rate
            while remaining_prob > 0:
                if random.random() < remaining_prob:
                    num_offspring += 1
                remaining_prob -= 1
            
            # Create offspring with mutations
            for _ in range(num_offspring):
                # Apply mutation
                new_resistance = resistance + random.gauss(0, self.mutation_std)
                # Ensure resistance stays within [0, 1]
                new_resistance = max(0, min(1, new_resistance))
                next_gen.append(new_resistance)
        
        # Apply carrying capacity limit
        if len(next_gen) > self.carrying_capacity:
            next_gen = random.sample(next_gen, self.carrying_capacity)
        
        # Update the population
        self.bacteria_population = next_gen
        
        # Update history
        if len(self.bacteria_population) > 0:
            self.avg_resistance_history.append(np.mean(self.bacteria_population))
        else:
            self.avg_resistance_history.append(0)  # Extinction
        self.population_history.append(len(self.bacteria_population))
        
        # Increment generation
        self.generation += 1
        
        # Update GUI
        self.update_info_labels()
        if self.generation % 5 == 0:  # Update charts every 5 generations for efficiency
            self.update_charts()
        self.update_pygame_visualization()
        
        # Check if we've reached the maximum generation limit
        if self.max_generations > 0 and self.generation >= self.max_generations:
            self.running = False
            self.status_var.set(f"Simulation completed: reached maximum generation limit ({self.max_generations}).")
            # Update buttons on main thread
            self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.pause_button.config(state=tk.DISABLED))
            return True
        
        return False  # Continue simulation
    
    def update_info_labels(self):
        # Update info labels
        self.generation_var.set(f"{self.generation}")
        self.pop_count_var.set(f"{len(self.bacteria_population)}")
        if len(self.bacteria_population) > 0:
            avg_resistance = np.mean(self.bacteria_population)
            self.avg_res_var.set(f"{avg_resistance:.4f}")
        else:
            self.avg_res_var.set("N/A (Extinct)")
        self.conc_var.set(f"{self.antibiotic_concentration:.2f}")
    
    def update_charts(self):
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Configure common style elements
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#f8f9fa')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#cccccc')
            ax.spines['left'].set_color('#cccccc')
            ax.tick_params(colors='#666666', labelsize=9)
            ax.xaxis.label.set_color('#333333')
            ax.yaxis.label.set_color('#333333')
            ax.title.set_color('#333333')
            # Increase font sizes
            ax.xaxis.label.set_fontsize(11)
            ax.yaxis.label.set_fontsize(11)
            ax.title.set_fontsize(13)
            ax.title.set_fontweight('bold')
        
        # Population size over time
        self.ax1.plot(self.population_history, color=COLORS["primary"], linewidth=2)
        self.ax1.set_title("Population Size Over Time")
        self.ax1.set_xlabel("Generation")
        self.ax1.set_ylabel("Population Size")
        self.ax1.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        
        # Add shaded area under the curve
        self.ax1.fill_between(range(len(self.population_history)), 
                            self.population_history, 
                            color=COLORS["primary"], alpha=0.2)
        
        # Average resistance over time
        self.ax2.plot(self.avg_resistance_history, color=COLORS["secondary"], linewidth=2)
        self.ax2.set_title("Average Resistance Over Time")
        self.ax2.set_xlabel("Generation")
        self.ax2.set_ylabel("Resistance Value")
        self.ax2.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        self.ax2.set_ylim(0, 1)
        
        # Add horizontal line for current antibiotic concentration
        self.ax2.axhline(y=self.antibiotic_concentration, color=COLORS["accent"], 
                       linestyle='--', alpha=0.8, linewidth=1.5)
        self.ax2.text(0, self.antibiotic_concentration + 0.02, 
                    f"Antibiotic Concentration: {self.antibiotic_concentration:.2f}", 
                    color=COLORS["accent"], fontsize=10)
        
        # Add shaded area under the curve
        self.ax2.fill_between(range(len(self.avg_resistance_history)), 
                            self.avg_resistance_history, 
                            color=COLORS["secondary"], alpha=0.2)
        
        # Resistance distribution histogram
        if len(self.bacteria_population) > 0:
            n, bins, patches = self.ax3.hist(self.bacteria_population, bins=30, range=(0, 1), 
                                          color=COLORS["tertiary"], alpha=0.7)
            
            # Color the bins based on their relationship to antibiotic concentration
            bin_centers = 0.5 * (bins[:-1] + bins[1:])
            for i, center in enumerate(bin_centers):
                if center < self.antibiotic_concentration:
                    # Bacteria with resistance below antibiotic concentration
                    patches[i].set_facecolor(COLORS["accent"])
                else:
                    # Bacteria with resistance above antibiotic concentration
                    patches[i].set_facecolor(COLORS["secondary"])
            
            self.ax3.set_title("Resistance Distribution")
            self.ax3.set_xlabel("Resistance Value")
            self.ax3.set_ylabel("Number of Bacteria")
            self.ax3.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
            self.ax3.set_xlim(0, 1)
            
            # Add vertical line for antibiotic concentration
            self.ax3.axvline(x=self.antibiotic_concentration, color='black', 
                           linestyle='--', alpha=0.8, linewidth=1.5)
            self.ax3.text(self.antibiotic_concentration + 0.02, max(n) * 0.9, 
                        f"Antibiotic\nConcentration", 
                        color='black', fontsize=10)
        
        # Update the canvas
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_pygame_visualization(self):
        # Clear the surface
        self.pygame_surface.fill((255, 255, 255))
        
        # Draw bacteria based on visualization type
        if self.viz_var.get() == "scatter":
            self._draw_scatter_visualization()
        else:  # grid
            self._draw_grid_visualization()
        
        # Convert pygame surface to tkinter PhotoImage
        pygame_img = pygame.image.tostring(self.pygame_surface, 'RGB')
        img = Image.frombytes('RGB', self.pygame_surface_size, pygame_img)
        self.tk_img = ImageTk.PhotoImage(image=img)
        
        # Update canvas
        self.pygame_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
    
    def _draw_scatter_visualization(self):
        width, height = self.pygame_surface_size
        
        # Draw a subtle grid background
        grid_spacing = 50
        for x in range(0, width, grid_spacing):
            pygame.draw.line(self.pygame_surface, (240, 240, 240), (x, 0), (x, height))
        for y in range(0, height, grid_spacing):
            pygame.draw.line(self.pygame_surface, (240, 240, 240), (0, y), (width, y))
        
        # Draw antibiotic concentration indicator
        indicator_height = 10
        pygame.draw.rect(self.pygame_surface, (240, 240, 240), 
                       (0, height - indicator_height, width, indicator_height))
        
        conc_x = int(width * self.antibiotic_concentration)
        pygame.draw.rect(self.pygame_surface, self.hex_to_rgb(COLORS["accent"]), 
                       (0, height - indicator_height, conc_x, indicator_height))
        
        # Draw legend
        legend_y = 20
        legend_x = width - 150
        
        # Susceptible bacteria legend
        pygame.draw.circle(self.pygame_surface, self.hex_to_rgb(COLORS["accent"]), (legend_x, legend_y), 6)
        font = pygame.font.SysFont('Arial', 12)
        text = font.render('Susceptible', True, (50, 50, 50))
        self.pygame_surface.blit(text, (legend_x + 15, legend_y - 6))
        
        # Resistant bacteria legend
        pygame.draw.circle(self.pygame_surface, self.hex_to_rgb(COLORS["secondary"]), (legend_x, legend_y + 25), 6)
        text = font.render('Resistant', True, (50, 50, 50))
        self.pygame_surface.blit(text, (legend_x + 15, legend_y + 19))
        
        # Calculate color and size for each bacterium
        for resistance in self.bacteria_population:
            # Position based on random placement
            x = random.randint(10, width - 10)
            y = random.randint(10, height - 20)  # Leave space for indicator
            
            # Use HSV color space for smoother color transitions
            # Map resistance from 0-1 to 0-120 (red to green in HSV)
            if resistance < self.antibiotic_concentration:
                color = self.hex_to_rgb(COLORS["accent"])
            else:
                color = self.hex_to_rgb(COLORS["secondary"])
            
            # Size based on how close the resistance is to antibiotic concentration
            resistance_diff = abs(resistance - self.antibiotic_concentration)
            size = max(3, 8 - int(resistance_diff * 10))
            
            # Add glow effect for bacteria near the antibiotic concentration
            if resistance_diff < 0.05:
                glow_size = size + 4
                glow_alpha = 100  # Semi-transparent
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                self.pygame_surface.blit(glow_surface, (x-glow_size, y-glow_size))
            
            # Draw the bacterium
            pygame.draw.circle(self.pygame_surface, color, (x, y), size)
    
    def _draw_grid_visualization(self):
        width, height = self.pygame_surface_size
        
        # Create a grid representation of bacteria
        grid_size = min(30, int(np.sqrt(len(self.bacteria_population))))
        if grid_size < 2:
            return  # Not enough bacteria for grid
            
        cell_width = width // grid_size
        cell_height = height // grid_size
        
        # Draw grid background
        for i in range(grid_size + 1):
            pygame.draw.line(self.pygame_surface, (230, 230, 230), 
                           (0, i * cell_height), (width, i * cell_height), 1)
            pygame.draw.line(self.pygame_surface, (230, 230, 230), 
                           (i * cell_width, 0), (i * cell_width, height), 1)
        
        # Draw antibiotic concentration indicator at the bottom
        indicator_height = 10
        pygame.draw.rect(self.pygame_surface, (240, 240, 240), 
                       (0, height - indicator_height, width, indicator_height))
        
        conc_x = int(width * self.antibiotic_concentration)
        pygame.draw.rect(self.pygame_surface, self.hex_to_rgb(COLORS["accent"]), 
                       (0, height - indicator_height, conc_x, indicator_height))
        
        # Draw bacteria in grid cells
        for i, resistance in enumerate(self.bacteria_population[:grid_size * grid_size]):
            row = i // grid_size
            col = i % grid_size
            
            # Calculate position
            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2
            
            # Determine color based on resistance vs antibiotic concentration
            if resistance < self.antibiotic_concentration:
                color = self.hex_to_rgb(COLORS["accent"])
                cell_color = (255, 240, 240)  # Light red background
            else:
                color = self.hex_to_rgb(COLORS["secondary"])
                cell_color = (240, 255, 240)  # Light green background
            
            # Size based on resistance vs antibiotic 
            resistance_diff = abs(resistance - self.antibiotic_concentration)
            size = max(3, min(cell_width // 2 - 2, 10 - int(resistance_diff * 15)))
            
            # Draw cell background
            pygame.draw.rect(self.pygame_surface, cell_color, 
                           (col * cell_width, row * cell_height, cell_width, cell_height))
            
            # Draw bacterium
            pygame.draw.circle(self.pygame_surface, color, (x, y), size)
            
            # Add a small indicator of resistance value
            font = pygame.font.SysFont('Arial', 8)
            text = font.render(f'{resistance:.2f}', True, (100, 100, 100))
            text_rect = text.get_rect(center=(x, y + cell_height//2 - 8))
            self.pygame_surface.blit(text, text_rect)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def start_simulation(self):
        # Update parameters
        try:
            self.population_size = int(self.population_var.get())
            self.carrying_capacity = int(self.capacity_var.get())
            self.max_generations = int(self.max_gen_var.get())
            min_res = float(self.min_resistance_var.get())
            max_res = float(self.max_resistance_var.get())
            self.initial_resistance_range = (min_res, max_res)
            
            # Handle initialization if needed
            if not self.bacteria_population:
                self.initialize_population()
                
            # If population is extinct, initialize again
            if len(self.bacteria_population) == 0:
                self.initialize_population()
            
            # Start the simulation thread if not already running
            if not self.running:
                self.running = True
                self.paused = False
                self.simulation_thread = threading.Thread(target=self.run_simulation)
                self.simulation_thread.daemon = True
                self.simulation_thread.start()
                
                # Update button states
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="Pause")
                
                self.status_var.set("Simulation running...")
        except ValueError as e:
            self.status_var.set(f"Error starting simulation: {str(e)}")
    
    def pause_simulation(self):
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.pause_button.config(text="Resume")
                self.status_var.set("Simulation paused.")
            else:
                self.pause_button.config(text="Pause")
                self.status_var.set("Simulation resumed.")
    
    def reset_simulation(self):
        # Stop any running simulation
        self.running = False
        self.paused = False
        
        # Wait for thread to finish
        if hasattr(self, 'simulation_thread') and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        
        # Reset variables
        self.bacteria_population = []
        self.generation = 0
        self.avg_resistance_history = []
        self.population_history = []
        
        # Initialize new population
        self.initialize_population()
        
        # Reset buttons
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        
        self.status_var.set("Simulation reset.")
    
    def run_simulation(self):
        while self.running:
            if not self.paused:
                # Check if extinction occurred
                if len(self.bacteria_population) == 0:
                    self.status_var.set("Population extinct! Reset to start a new simulation.")
                    self.running = False
                    # Update buttons on main thread
                    self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                    self.master.after(0, lambda: self.pause_button.config(state=tk.DISABLED))
                    break
                
                # Perform simulation step
                if self.simulation_step():
                    break  # Simulation completed due to max generations
                
                # Sleep based on simulation speed
                time.sleep(0.5 / self.speed_var.get())
            else:
                # When paused, just wait a bit
                time.sleep(0.1)
    
    def on_resize(self, event):
        # Only handle resize events from the main window
        if event.widget == self.master:
            # Redraw charts on window resize
            self.fig.tight_layout()
            self.canvas.draw()
    
    def on_closing(self):
        # Stop simulation thread
        self.running = False
        self.paused = True
        
        # Wait for thread to finish
        if hasattr(self, 'simulation_thread') and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        
        # Close the window
        pygame.quit()
        self.master.destroy()
        sys.exit()

def main():
    root = tk.Tk()
    app = BacterialResistanceSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()
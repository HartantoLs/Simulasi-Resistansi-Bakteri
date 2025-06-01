import tkinter as tk
from tkinter import ttk
import random
import math
import time
from dataclasses import dataclass
from typing import List
import threading

@dataclass
class Bacteria:
    """Kelas untuk merepresentasikan bakteri individual"""
    age: int = 0
    resistance_rate: float = 0.0
    reproduction_rate: float = 1.0
    max_age: int = 100
    generation: int = 0
    last_reproduction: int = 0
    x: float = 0.0
    y: float = 0.0
    
    def survive_antibiotic_exposure(self, antibiotic_level: float) -> bool:
        """Menghitung probabilitas bertahan hidup terhadap antibiotik"""
        if self.resistance_rate >= antibiotic_level:
            survival_chance = 0.95 + (self.resistance_rate - antibiotic_level) * 0.05
            survival_chance = min(1.0, survival_chance)
        else:
            resistance_gap = antibiotic_level - self.resistance_rate
            death_chance = resistance_gap * 0.8
            death_chance = min(0.95, death_chance)
            survival_chance = 1.0 - death_chance
        
        return random.random() < survival_chance
    
    def can_reproduce(self, current_tick: int) -> bool:
        """Cek apakah bakteri bisa bereproduksi"""
        reproduction_interval = max(1, int(self.reproduction_rate * 10))
        return (current_tick - self.last_reproduction) >= reproduction_interval
    
    def reproduce(self, current_tick: int, canvas_width: int, canvas_height: int) -> List['Bacteria']:
        """Reproduksi aseksual dengan mutasi"""
        if not self.can_reproduce(current_tick):
            return []
        
        self.last_reproduction = current_tick
        offspring = []
        
        for _ in range(2):  # Pembelahan biner
            mutation_strength = 0.15
            
            # Mutasi resistance_rate
            resistance_mutation = random.uniform(-mutation_strength, mutation_strength)
            new_resistance = max(0.0, min(1.0, self.resistance_rate + resistance_mutation))
            
            # Mutasi reproduction_rate dengan trade-off
            reproduction_mutation = random.uniform(-mutation_strength/2, mutation_strength/2)
            resistance_cost = new_resistance * 0.3
            new_reproduction_rate = max(0.5, min(4.0, 
                self.reproduction_rate + reproduction_mutation + resistance_cost))
            
            # Mutasi max_age
            age_mutation = random.randint(-20, 20)
            new_max_age = max(60, min(150, self.max_age + age_mutation))
            
            # Posisi anak
            new_x = max(15, min(canvas_width-15, self.x + random.uniform(-40, 40)))
            new_y = max(15, min(canvas_height-15, self.y + random.uniform(-40, 40)))
            
            child = Bacteria(
                age=0,
                resistance_rate=new_resistance,
                reproduction_rate=new_reproduction_rate,
                max_age=new_max_age,
                generation=self.generation + 1,
                last_reproduction=current_tick,
                x=new_x,
                y=new_y
            )
            offspring.append(child)
        
        return offspring

class ImprovedBacteriaSimulation:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🦠 Simulasi Evolusi Resistansi Bakteri - Modern Lab")
        
        # Responsive window sizing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size based on screen resolution
        if screen_width >= 1920:
            window_width, window_height = 1700, 1000
        elif screen_width >= 1366:
            window_width, window_height = 1500, 900
        else:
            window_width, window_height = 1300, 800
            
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1300, 700)
        
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a2e',
            'secondary': '#16213e', 
            'accent': '#0f3460',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'light': '#f8f9fa',
            'white': '#ffffff',
            'text': '#2c3e50',
            'text_light': '#6c757d',
            'graph_bg': '#ffffff',
            'canvas_bg': '#0f1419'
        }
        
        # Railway fonts - fallback to system fonts if not available
        try:
            self.fonts = {
                'title': ('Railway', 20, 'bold'),
                'subtitle': ('Railway', 16, 'bold'),
                'heading': ('Railway', 13, 'bold'),
                'body': ('Railway', 11),
                'small': ('Railway', 10),
                'mono': ('Railway', 10, 'bold')
            }
        except:
            # Fallback fonts
            self.fonts = {
                'title': ('Segoe UI', 20, 'bold'),
                'subtitle': ('Segoe UI', 16, 'bold'),
                'heading': ('Segoe UI', 13, 'bold'),
                'body': ('Segoe UI', 11),
                'small': ('Segoe UI', 10),
                'mono': ('Consolas', 10, 'bold')
            }
        
        self.root.configure(bg=self.colors['light'])
        
        # Simulation variables
        self.bacteria_population: List[Bacteria] = []
        self.current_tick = 0
        self.antibiotic_level = 0.3
        self.initial_population = 50
        self.max_generations = 20
        self.current_max_generation = 0
        self.simulation_ended = False
        self.is_running = False
        self.canvas_width = 900
        self.canvas_height = 450
        
        # Data untuk grafik
        self.population_history = []
        self.resistance_history = []
        self.tick_history = []
        
        # Setup UI
        self.setup_ui()
        self.initialize_population()
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
    def setup_ui(self):
        """Setup responsive UI layout dengan proporsi yang lebih baik"""
        # Main container dengan padding yang lebih kecil
        main_container = tk.Frame(self.root, bg=self.colors['light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header yang lebih compact
        self.create_compact_header(main_container)
        
        # Control panel yang lebih kecil
        self.create_compact_control_panel(main_container)
        
        # Content area dengan proporsi yang lebih baik
        content_frame = tk.Frame(main_container, bg=self.colors['light'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        # Configure grid weights - lebih banyak ruang untuk visualisasi
        content_frame.grid_columnconfigure(0, weight=3)  # Left panel gets much more space
        content_frame.grid_columnconfigure(1, weight=1)  # Right panel smaller
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Visualizations (lebih besar)
        self.create_enhanced_left_panel(content_frame)
        
        # Right panel - Statistics and info (lebih compact)
        self.create_compact_right_panel(content_frame)
    
    def create_compact_header(self, parent):
        """Create compact header"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=70)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        # Title dengan spacing yang lebih kecil
        title_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        title_frame.pack(expand=True)
        
        title_label = tk.Label(title_frame,
                              text="🦠 Simulasi Evolusi Resistansi Bakteri",
                              font=self.fonts['title'],
                              fg=self.colors['white'],
                              bg=self.colors['primary'])
        title_label.pack(pady=(15, 2))
        
        subtitle_label = tk.Label(title_frame,
                                 text="Natural Selection & Mutasi Genetik dalam Populasi Mikroorganisme",
                                 font=self.fonts['small'],
                                 fg=self.colors['light'],
                                 bg=self.colors['primary'])
        subtitle_label.pack()
    
    def create_compact_control_panel(self, parent):
        """Create compact control panel"""
        control_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title yang lebih kecil
        title_label = tk.Label(control_frame,
                              text="⚙️ Kontrol Simulasi",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(10, 5))
        
        # Controls container dengan padding yang lebih kecil
        controls_container = tk.Frame(control_frame, bg=self.colors['white'])
        controls_container.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Single row layout untuk semua controls
        main_row = tk.Frame(controls_container, bg=self.colors['white'])
        main_row.pack(fill=tk.X)
        
        # Left side - Input controls (lebih compact)
        input_frame = tk.Frame(main_row, bg=self.colors['white'])
        input_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Input controls dalam satu baris
        inputs_row = tk.Frame(input_frame, bg=self.colors['white'])
        inputs_row.pack(fill=tk.X, pady=(0, 10))
        
        # Population control (lebih kecil)
        self.create_mini_input_control(inputs_row, "👥 Pop", 
                                      self.initial_population, 10, 200, 'pop_var')
        
        # Generation control (lebih kecil)
        self.create_mini_input_control(inputs_row, "🧬 Gen",
                                      self.max_generations, 5, 50, 'gen_var')
        
        # Speed control (lebih kecil)
        self.create_mini_input_control(inputs_row, "⚡ Speed",
                                      100, 50, 500, 'speed_var')
        
        # Antibiotic control (horizontal, compact)
        antibiotic_frame = tk.Frame(input_frame, bg=self.colors['white'])
        antibiotic_frame.pack(fill=tk.X)
        
        antibiotic_label = tk.Label(antibiotic_frame,
                                   text="💊 Antibiotik:",
                                   font=self.fonts['body'],
                                   fg=self.colors['text'],
                                   bg=self.colors['white'])
        antibiotic_label.pack(side=tk.LEFT)
        
        self.antibiotic_var = tk.DoubleVar(value=self.antibiotic_level)
        self.antibiotic_slider = tk.Scale(antibiotic_frame,
                                         from_=0.0, to=1.0,
                                         variable=self.antibiotic_var,
                                         orient=tk.HORIZONTAL,
                                         resolution=0.01,
                                         length=200,
                                         font=self.fonts['small'],
                                         bg=self.colors['white'],
                                         fg=self.colors['text'],
                                         highlightthickness=0,
                                         showvalue=0)
        self.antibiotic_slider.pack(side=tk.LEFT, padx=(10, 10))
        
        self.antibiotic_label = tk.Label(antibiotic_frame,
                                        text=f"{self.antibiotic_level:.3f}",
                                        font=self.fonts['mono'],
                                        fg=self.colors['danger'],
                                        bg=self.colors['white'],
                                        width=8)
        self.antibiotic_label.pack(side=tk.LEFT)
        
        # Right side - Action buttons (compact)
        button_frame = tk.Frame(main_row, bg=self.colors['white'])
        button_frame.pack(side=tk.RIGHT)
        
        # Buttons dalam satu baris, lebih kecil
        buttons_row = tk.Frame(button_frame, bg=self.colors['white'])
        buttons_row.pack()
        
        # Reset button (lebih kecil)
        self.reset_btn = tk.Button(buttons_row,
                                  text="🔄 Reset",
                                  command=self.reset_population,
                                  font=self.fonts['small'],
                                  bg=self.colors['danger'],
                                  fg=self.colors['white'],
                                  relief='flat',
                                  padx=15, pady=8,
                                  cursor='hand2')
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Start/Stop button (lebih kecil)
        self.start_btn = tk.Button(buttons_row,
                                  text="▶️ Start",
                                  command=self.toggle_simulation,
                                  font=self.fonts['small'],
                                  bg=self.colors['success'],
                                  fg=self.colors['white'],
                                  relief='flat',
                                  padx=15, pady=8,
                                  cursor='hand2')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # Export button (lebih kecil)
        self.export_btn = tk.Button(buttons_row,
                                   text="📊 Export",
                                   command=self.export_data,
                                   font=self.fonts['small'],
                                   bg=self.colors['accent'],
                                   fg=self.colors['white'],
                                   relief='flat',
                                   padx=15, pady=8,
                                   cursor='hand2')
        self.export_btn.pack(side=tk.LEFT)
    
    def create_mini_input_control(self, parent, label_text, default_value, min_val, max_val, var_name):
        """Create mini input control"""
        control_frame = tk.Frame(parent, bg=self.colors['white'])
        control_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        label = tk.Label(control_frame,
                        text=label_text,
                        font=self.fonts['small'],
                        fg=self.colors['text'],
                        bg=self.colors['white'])
        label.pack()
        
        var = tk.IntVar(value=default_value)
        setattr(self, var_name, var)
        
        spinbox = tk.Spinbox(control_frame,
                            from_=min_val, to=max_val,
                            textvariable=var,
                            width=8,
                            font=self.fonts['small'],
                            relief='solid',
                            bd=1)
        spinbox.pack(pady=(3, 0))
    
    def create_enhanced_left_panel(self, parent):
        """Create enhanced left panel dengan visualisasi yang lebih besar"""
        left_panel = tk.Frame(parent, bg=self.colors['light'])
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Configure grid weights - lebih banyak ruang untuk visualisasi
        left_panel.grid_rowconfigure(0, weight=2)  # Visualization gets more space
        left_panel.grid_rowconfigure(1, weight=3)  # Graph gets even more space
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Visualization panel (lebih besar)
        self.create_large_visualization_panel(left_panel)
        
        # Graph panel (jauh lebih besar)
        self.create_large_graph_panel(left_panel)
    
    def create_large_visualization_panel(self, parent):
        """Create larger bacteria visualization panel"""
        viz_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        viz_frame.grid(row=0, column=0, sticky='nsew', pady=(0, 10))
        
        # Title yang lebih compact
        title_label = tk.Label(viz_frame,
                              text="🔬 Visualisasi Populasi Bakteri",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(10, 5))
        
        # Canvas container yang lebih besar
        canvas_container = tk.Frame(viz_frame, bg=self.colors['secondary'], relief='solid', bd=2)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 5))
        
        self.canvas = tk.Canvas(canvas_container,
                               bg=self.colors['canvas_bg'],
                               highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Info bar yang lebih kecil
        self.info_label = tk.Label(viz_frame,
                                  text="💡 Merah = Resistansi Tinggi, Biru = Resistansi Rendah",
                                  font=self.fonts['small'],
                                  fg=self.colors['text_light'],
                                  bg=self.colors['white'])
        self.info_label.pack(pady=(0, 8))
    
    def create_large_graph_panel(self, parent):
        """Create much larger graph panel"""
        graph_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        graph_frame.grid(row=1, column=0, sticky='nsew')
        
        # Title yang compact
        title_label = tk.Label(graph_frame,
                              text="📈 Grafik Evolusi Real-time",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(10, 5))
        
        # Graph container yang jauh lebih besar
        graph_container = tk.Frame(graph_frame, bg=self.colors['secondary'], relief='solid', bd=2)
        graph_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        self.graph_canvas = tk.Canvas(graph_container,
                                     bg=self.colors['graph_bg'],
                                     highlightthickness=0)
        self.graph_canvas.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    def create_compact_right_panel(self, parent):
        """Create compact right panel"""
        right_panel = tk.Frame(parent, bg=self.colors['light'])
        right_panel.grid(row=0, column=1, sticky='nsew')
        
        # Configure grid weights
        right_panel.grid_rowconfigure(0, weight=0)
        right_panel.grid_rowconfigure(1, weight=0)
        right_panel.grid_rowconfigure(2, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Statistics panel (compact)
        self.create_compact_statistics_panel(right_panel)
        
        # Legend panel (compact)
        self.create_compact_legend_panel(right_panel)
        
        # Info panel (compact)
        self.create_compact_info_panel(right_panel)
    
    def create_compact_statistics_panel(self, parent):
        """Create compact statistics panel"""
        stats_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        stats_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # Title yang lebih kecil
        title_label = tk.Label(stats_frame,
                              text="📊 Statistik",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(8, 5))
        
        # Stats container dengan padding yang lebih kecil
        stats_container = tk.Frame(stats_frame, bg=self.colors['white'])
        stats_container.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self.stats_labels = {}
        stats_info = [
            ("👥 Pop:", "population", self.colors['accent']),
            ("⏱️ Tick:", "tick", self.colors['secondary']),
            ("🧬 Gen:", "max_generation", self.colors['warning']),
            ("🛡️ Res Avg:", "avg_resistance", self.colors['danger']),
            ("📊 Range:", "resistance_range", self.colors['warning']),
            ("🔄 Repro:", "avg_reproduction", self.colors['success']),
            ("💊 Anti:", "antibiotic", self.colors['danger']),
            ("⚡ Status:", "status", self.colors['text'])
        ]
        
        for i, (text, key, color) in enumerate(stats_info):
            row_frame = tk.Frame(stats_container, bg=self.colors['white'])
            row_frame.pack(fill=tk.X, pady=2)
            
            label = tk.Label(row_frame,
                           text=text,
                           font=self.fonts['small'],
                           fg=self.colors['text'],
                           bg=self.colors['white'],
                           anchor='w')
            label.pack(side=tk.LEFT)
            
            self.stats_labels[key] = tk.Label(row_frame,
                                            text="0",
                                            font=self.fonts['small'],
                                            fg=color,
                                            bg=self.colors['white'],
                                            anchor='e')
            self.stats_labels[key].pack(side=tk.RIGHT)
    
    def create_compact_legend_panel(self, parent):
        """Create compact legend panel"""
        legend_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        legend_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        # Title yang lebih kecil
        title_label = tk.Label(legend_frame,
                              text="🎨 Legenda",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(8, 5))
        
        # Legend items dengan spacing yang lebih kecil
        legend_container = tk.Frame(legend_frame, bg=self.colors['white'])
        legend_container.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        legend_items = [
            ("🔴", "Resistansi Tinggi", self.colors['danger']),
            ("🟡", "Resistansi Sedang", self.colors['warning']),
            ("🔵", "Resistansi Rendah", self.colors['accent']),
            ("⚫", "Ukuran = Umur", self.colors['text'])
        ]
        
        for emoji, text, color in legend_items:
            item_frame = tk.Frame(legend_container, bg=self.colors['white'])
            item_frame.pack(fill=tk.X, pady=1)
            
            emoji_label = tk.Label(item_frame,
                                  text=emoji,
                                  font=self.fonts['small'],
                                  bg=self.colors['white'])
            emoji_label.pack(side=tk.LEFT)
            
            text_label = tk.Label(item_frame,
                                 text=text,
                                 font=self.fonts['small'],
                                 fg=color,
                                 bg=self.colors['white'])
            text_label.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_compact_info_panel(self, parent):
        """Create compact info panel"""
        info_frame = tk.Frame(parent, bg=self.colors['white'], relief='solid', bd=1)
        info_frame.grid(row=2, column=0, sticky='nsew')
        
        # Title yang lebih kecil
        title_label = tk.Label(info_frame,
                              text="📚 Info",
                              font=self.fonts['heading'],
                              fg=self.colors['text'],
                              bg=self.colors['white'])
        title_label.pack(pady=(8, 5))
        
        # Text container dengan scrollbar
        text_container = tk.Frame(info_frame, bg=self.colors['white'])
        text_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))
        
        info_text = """🧬 KONSEP BIOLOGI:

• Natural Selection: Bakteri resistan bertahan lebih baik

• Mutasi Genetik: Variasi pada setiap reproduksi

• Trade-off: Resistansi tinggi = reproduksi lambat

• Genetic Drift: Perubahan gen dalam populasi kecil

💡 PENGAMATAN:
- Tingkatkan antibiotik → seleksi kuat
- Populasi kecil → rentan punah
- Resistansi rata-rata meningkat

🔬 PENGGUNAAN:
1. Atur populasi & generasi
2. Sesuaikan antibiotik
3. Klik Start
4. Amati evolusi

⚠️ TIPS:
- Pop <100 untuk performa optimal
- Speed 100-200ms terbaik"""
        
        text_widget = tk.Text(text_container,
                             wrap=tk.WORD,
                             font=self.fonts['small'],
                             bg=self.colors['light'],
                             fg=self.colors['text'],
                             relief='flat',
                             padx=8, pady=8)
        
        scrollbar = tk.Scrollbar(text_container, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')
    
    def on_window_resize(self, event):
        """Handle window resize for responsiveness"""
        if event.widget == self.root:
            # Canvas akan otomatis resize karena menggunakan pack dengan fill dan expand
            pass
    
    def initialize_population(self):
        """Initialize bacteria population"""
        self.bacteria_population = []
        
        for _ in range(self.initial_population):
            bacteria = Bacteria(
                age=random.randint(0, 15),
                resistance_rate=random.uniform(0.05, 0.25),
                reproduction_rate=random.uniform(0.8, 1.5),
                max_age=random.randint(85, 120),
                generation=0,
                x=random.uniform(50, 800),
                y=random.uniform(50, 400)
            )
            self.bacteria_population.append(bacteria)
        
        self.current_tick = 0
        self.current_max_generation = 0
        self.simulation_ended = False
        self.population_history = []
        self.resistance_history = []
        self.tick_history = []
    
    def reset_population(self):
        """Reset population with current settings"""
        try:
            self.initial_population = self.pop_var.get()
            self.max_generations = self.gen_var.get()
            
            if self.is_running:
                self.toggle_simulation()
            
            self.initialize_population()
            self.update_display()
            
        except Exception as e:
            print(f"Error resetting population: {e}")
    
    def toggle_simulation(self):
        """Toggle simulation start/stop"""
        self.is_running = not self.is_running
        
        if self.is_running:
            self.start_btn.config(text="⏸️ Pause", bg=self.colors['warning'])
            self.run_simulation()
        else:
            self.start_btn.config(text="▶️ Start", bg=self.colors['success'])
    
    def run_simulation(self):
        """Run simulation loop with error handling"""
        if not self.is_running or self.simulation_ended:
            return
        
        try:
            self.simulation_step()
            self.update_display()
            
            # Check end conditions
            if self.current_max_generation >= self.max_generations:
                self.simulation_ended = True
                self.is_running = False
                self.start_btn.config(text="✅ Selesai", bg=self.colors['success'])
                return
            
            if len(self.bacteria_population) == 0:
                self.simulation_ended = True
                self.is_running = False
                self.start_btn.config(text="💀 Punah", bg=self.colors['danger'])
                return
            
            # Schedule next step
            delay = self.speed_var.get()
            self.root.after(delay, self.run_simulation)
            
        except Exception as e:
            print(f"Simulation error: {e}")
            self.is_running = False
            self.start_btn.config(text="❌ Error", bg=self.colors['danger'])
    
    def simulation_step(self):
        """Execute one simulation step"""
        self.current_tick += 1
        self.antibiotic_level = self.antibiotic_var.get()
        
        # Get current canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 400
        
        # Natural selection
        surviving_bacteria = []
        
        for bacteria in self.bacteria_population:
            bacteria.age += 1
            
            # Check death by age
            if bacteria.age >= bacteria.max_age:
                continue
            
            # Check death by antibiotic
            if bacteria.survive_antibiotic_exposure(self.antibiotic_level):
                surviving_bacteria.append(bacteria)
        
        # Reproduction
        new_bacteria = []
        for bacteria in surviving_bacteria:
            offspring = bacteria.reproduce(self.current_tick, canvas_width, canvas_height)
            new_bacteria.extend(offspring)
        
        # Update population
        self.bacteria_population = surviving_bacteria + new_bacteria
        
        # Limit population for performance
        if len(self.bacteria_population) > 800:
            self.bacteria_population.sort(key=lambda b: b.resistance_rate, reverse=True)
            top_resistant = self.bacteria_population[:400]
            random_sample = random.sample(self.bacteria_population[400:], 
                                        min(200, len(self.bacteria_population) - 400))
            self.bacteria_population = top_resistant + random_sample
        
        # Update generation
        if self.bacteria_population:
            self.current_max_generation = max(b.generation for b in self.bacteria_population)
        
        # Save data for graphs
        if self.current_tick % 5 == 0:
            self.population_history.append(len(self.bacteria_population))
            self.tick_history.append(self.current_tick)
            
            if self.bacteria_population:
                avg_resistance = sum(b.resistance_rate for b in self.bacteria_population) / len(self.bacteria_population)
                self.resistance_history.append(avg_resistance)
            else:
                self.resistance_history.append(0)
            
            # Limit history for performance
            if len(self.tick_history) > 200:
                self.population_history = self.population_history[-200:]
                self.resistance_history = self.resistance_history[-200:]
                self.tick_history = self.tick_history[-200:]
    
    def update_display(self):
        """Update all visual elements"""
        try:
            self.render_bacteria()
            self.render_graph()
            self.update_statistics()
            self.update_antibiotic_label()
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def render_bacteria(self):
        """Render bacteria on canvas"""
        try:
            self.canvas.delete("all")
            
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Draw background grid
            grid_color = "#1e2a3a"
            for i in range(0, canvas_width, 40):
                self.canvas.create_line(i, 0, i, canvas_height, fill=grid_color, width=1)
            for i in range(0, canvas_height, 40):
                self.canvas.create_line(0, i, canvas_width, i, fill=grid_color, width=1)
            
            # Draw bacteria
            for bacteria in self.bacteria_population:
                # Ensure bacteria stay within canvas bounds
                bacteria.x = max(10, min(canvas_width-10, bacteria.x))
                bacteria.y = max(10, min(canvas_height-10, bacteria.y))
                
                resistance = bacteria.resistance_rate
                
                # Color based on resistance
                if resistance >= 0.7:
                    color = f"#{255:02x}{int(60 + resistance * 40):02x}{60:02x}"
                    outline_color = "#ff4757"
                elif resistance >= 0.3:
                    color = f"#{255:02x}{int(180 + resistance * 75):02x}{60:02x}"
                    outline_color = "#ffa502"
                else:
                    blue_val = int(255 - resistance * 80)
                    color = f"#{60:02x}{120:02x}{blue_val:02x}"
                    outline_color = "#3742fa"
                
                # Size based on age with pulsing
                base_size = 5 + (bacteria.age / 10)
                pulse_factor = 1 + 0.2 * math.sin(self.current_tick * 0.15 + bacteria.x * 0.01)
                size = base_size * pulse_factor
                
                # Draw shadow
                self.canvas.create_oval(
                    bacteria.x - size + 2, bacteria.y - size + 2,
                    bacteria.x + size + 2, bacteria.y + size + 2,
                    fill="#0a0f14", outline="", width=0
                )
                
                # Draw bacteria
                self.canvas.create_oval(
                    bacteria.x - size, bacteria.y - size,
                    bacteria.x + size, bacteria.y + size,
                    fill=color, outline=outline_color, width=2
                )
                
                # Highlight super resistant bacteria
                if resistance > 0.85:
                    highlight_size = size * 1.5
                    self.canvas.create_oval(
                        bacteria.x - highlight_size, bacteria.y - highlight_size,
                        bacteria.x + highlight_size, bacteria.y + highlight_size,
                        fill="", outline="#ffdd59", width=2, dash=(5, 5)
                    )
                    
        except Exception as e:
            print(f"Bacteria rendering error: {e}")
    
    def render_graph(self):
        """Render evolution graph dengan ukuran yang lebih besar"""
        try:
            self.graph_canvas.delete("all")
            
            canvas_width = self.graph_canvas.winfo_width()
            canvas_height = self.graph_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            if len(self.tick_history) < 2:
                # Show placeholder text
                self.graph_canvas.create_text(
                    canvas_width // 2, canvas_height // 2,
                    text="📈 Grafik akan muncul setelah simulasi dimulai",
                    font=self.fonts['body'],
                    fill=self.colors['text_light']
                )
                return
            
            margin = 60
            graph_width = canvas_width - 2 * margin
            graph_height = canvas_height - 2 * margin
            
            if graph_width <= 0 or graph_height <= 0:
                return
            
            # Background
            self.graph_canvas.create_rectangle(0, 0, canvas_width, canvas_height, 
                                             fill=self.colors['graph_bg'], outline="")
            
            # Normalize data
            max_tick = max(self.tick_history) if self.tick_history else 1
            max_pop = max(self.population_history) if self.population_history else 1
            max_resistance = 1.0
            
            # Draw grid
            grid_color = "#e9ecef"
            for i in range(6):
                x = margin + (i * graph_width // 5)
                y = margin + (i * graph_height // 5)
                
                self.graph_canvas.create_line(margin, y, canvas_width - margin, y, 
                                            fill=grid_color, width=1)
                self.graph_canvas.create_line(x, margin, x, canvas_height - margin, 
                                            fill=grid_color, width=1)
            
            # Draw population area (filled)
            if len(self.tick_history) >= 2:
                area_points = [margin, canvas_height - margin]
                for tick, pop in zip(self.tick_history, self.population_history):
                    x = margin + (tick / max_tick) * graph_width
                    y = canvas_height - margin - (pop / max_pop) * graph_height
                    area_points.extend([x, y])
                area_points.extend([canvas_width - margin, canvas_height - margin])
                
                if len(area_points) >= 6:
                    self.graph_canvas.create_polygon(area_points, fill="#e3f2fd", outline="")
            
            # Draw population line
            if len(self.tick_history) >= 2:
                pop_points = []
                for tick, pop in zip(self.tick_history, self.population_history):
                    x = margin + (tick / max_tick) * graph_width
                    y = canvas_height - margin - (pop / max_pop) * graph_height
                    pop_points.extend([x, y])
                
                if len(pop_points) >= 4:
                    self.graph_canvas.create_line(pop_points, fill="#1976d2", 
                                                width=4, smooth=True)
            
            # Draw resistance line
            if len(self.tick_history) >= 2:
                res_points = []
                for tick, resistance in zip(self.tick_history, self.resistance_history):
                    x = margin + (tick / max_tick) * graph_width
                    y = canvas_height - margin - (resistance / max_resistance) * graph_height
                    res_points.extend([x, y])
                
                if len(res_points) >= 4:
                    self.graph_canvas.create_line(res_points, fill="#d32f2f", 
                                                width=4, smooth=True)
            
            # Draw latest points
            if self.tick_history and self.population_history and self.resistance_history:
                latest_tick = self.tick_history[-1]
                latest_pop = self.population_history[-1]
                latest_res = self.resistance_history[-1]
                
                # Population point
                pop_x = margin + (latest_tick / max_tick) * graph_width
                pop_y = canvas_height - margin - (latest_pop / max_pop) * graph_height
                self.graph_canvas.create_oval(pop_x-6, pop_y-6, pop_x+6, pop_y+6, 
                                            fill="#1976d2", outline=self.colors['white'], width=3)
                
                # Resistance point
                res_x = margin + (latest_tick / max_tick) * graph_width
                res_y = canvas_height - margin - (latest_res / max_resistance) * graph_height
                self.graph_canvas.create_oval(res_x-6, res_y-6, res_x+6, res_y+6, 
                                            fill="#d32f2f", outline=self.colors['white'], width=3)
            
            # Labels dengan font yang lebih besar
            self.graph_canvas.create_text(canvas_width // 2, canvas_height - 25, 
                                        text="Waktu (Tick)", fill=self.colors['text'], 
                                        font=self.fonts['body'])
            self.graph_canvas.create_text(30, canvas_height // 2, 
                                        text="Nilai", fill=self.colors['text'], 
                                        font=self.fonts['body'], angle=90)
            
            # Legend yang lebih besar
            legend_x = canvas_width - 220
            legend_y = 40
            
            # Legend background
            self.graph_canvas.create_rectangle(legend_x, legend_y, legend_x + 200, legend_y + 100, 
                                             fill=self.colors['white'], outline=self.colors['light'], width=2)
            
            # Population legend
            self.graph_canvas.create_line(legend_x + 15, legend_y + 25, legend_x + 40, legend_y + 25, 
                                        fill="#1976d2", width=4)
            self.graph_canvas.create_text(legend_x + 50, legend_y + 25, text="Populasi", 
                                        anchor="w", fill="#1976d2", font=self.fonts['body'])
            
            # Resistance legend
            self.graph_canvas.create_line(legend_x + 15, legend_y + 50, legend_x + 40, legend_y + 50, 
                                        fill="#d32f2f", width=4)
            self.graph_canvas.create_text(legend_x + 50, legend_y + 50, text="Resistansi Avg", 
                                        anchor="w", fill="#d32f2f", font=self.fonts['body'])
            
            # Current values
            if self.population_history and self.resistance_history:
                current_pop = self.population_history[-1]
                current_res = self.resistance_history[-1]
                self.graph_canvas.create_text(legend_x + 50, legend_y + 75, 
                                            text=f"Pop: {current_pop} | Res: {current_res:.3f}", 
                                            anchor="w", fill=self.colors['text'], font=self.fonts['small'])
                
        except Exception as e:
            print(f"Graph rendering error: {e}")
    
    def update_statistics(self):
        """Update statistics display"""
        try:
            self.stats_labels["population"].config(text=f"{len(self.bacteria_population):,}")
            self.stats_labels["tick"].config(text=f"{self.current_tick:,}")
            self.stats_labels["max_generation"].config(text=f"{self.current_max_generation}")
            
            # Status
            if self.simulation_ended:
                if len(self.bacteria_population) == 0:
                    self.stats_labels["status"].config(text="💀 Punah")
                else:
                    self.stats_labels["status"].config(text="✅ Selesai")
            elif self.is_running:
                self.stats_labels["status"].config(text="🔄 Berjalan")
            else:
                self.stats_labels["status"].config(text="⏸️ Berhenti")
            
            if self.bacteria_population:
                resistances = [b.resistance_rate for b in self.bacteria_population]
                reproductions = [b.reproduction_rate for b in self.bacteria_population]
                
                avg_resistance = sum(resistances) / len(resistances)
                avg_reproduction = sum(reproductions) / len(reproductions)
                min_resistance = min(resistances)
                max_resistance = max(resistances)
                
                self.stats_labels["avg_resistance"].config(text=f"{avg_resistance:.3f}")
                self.stats_labels["avg_reproduction"].config(text=f"{avg_reproduction:.3f}")
                self.stats_labels["resistance_range"].config(text=f"{min_resistance:.2f}-{max_resistance:.2f}")
            else:
                self.stats_labels["avg_resistance"].config(text="0.000")
                self.stats_labels["avg_reproduction"].config(text="0.000")
                self.stats_labels["resistance_range"].config(text="0.00-0.00")
            
            self.stats_labels["antibiotic"].config(text=f"{self.antibiotic_level:.3f}")
            
            # Update info label
            total_bacteria = len(self.bacteria_population)
            if total_bacteria > 0:
                high_res = sum(1 for b in self.bacteria_population if b.resistance_rate > 0.7)
                med_res = sum(1 for b in self.bacteria_population if 0.3 <= b.resistance_rate <= 0.7)
                low_res = total_bacteria - high_res - med_res
                
                info_text = f"💡 Distribusi: 🔴 {high_res} | 🟡 {med_res} | 🔵 {low_res} | Total: {total_bacteria}"
            else:
                info_text = "💡 Merah = Resistansi Tinggi, Biru = Resistansi Rendah"
            
            self.info_label.config(text=info_text)
            
        except Exception as e:
            print(f"Statistics update error: {e}")
    
    def update_antibiotic_label(self):
        """Update antibiotic level label"""
        try:
            self.antibiotic_label.config(text=f"{self.antibiotic_var.get():.3f}")
        except Exception as e:
            print(f"Antibiotic label update error: {e}")
    
    def export_data(self):
        """Export simulation data"""
        try:
            print("📊 Export Data:")
            print(f"Population: {len(self.bacteria_population)}")
            print(f"Tick: {self.current_tick}")
            print(f"Max Generation: {self.current_max_generation}")
            print(f"Antibiotic Level: {self.antibiotic_level:.3f}")
            
            if self.bacteria_population:
                avg_resistance = sum(b.resistance_rate for b in self.bacteria_population) / len(self.bacteria_population)
                print(f"Average Resistance: {avg_resistance:.3f}")
            
            print("Export functionality can be extended to save to CSV/JSON files")
            
        except Exception as e:
            print(f"Export error: {e}")
    
    def run(self):
        """Start the application"""
        try:
            self.update_display()
            self.root.mainloop()
        except Exception as e:
            print(f"Application error: {e}")

if __name__ == "__main__":
    print("Memulai Simulasi Evolusi Resistansi Bakteri")
    
    try:
        sim = ImprovedBacteriaSimulation()
        sim.run()
    except Exception as e:
        print(f"Failed to start simulation: {e}")
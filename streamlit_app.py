import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import random
import math
import time
from dataclasses import dataclass
from typing import List
import json

# Set page config
st.set_page_config(
    page_title="🦠 Simulasi Evolusi Resistansi Bakteri",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    parent_id: str = None
    id: str = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = f"bacteria_{random.randint(1000, 9999)}"
    
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
    
    def get_size(self) -> float:
        """Menghitung ukuran bakteri berdasarkan umur"""
        age_ratio = self.age / self.max_age
        base_size = 3
        max_size = 15
        return base_size + (max_size - base_size) * age_ratio
    
    def is_very_old(self) -> bool:
        """Cek apakah bakteri sudah sangat tua (>80% umur maksimal)"""
        return self.age / self.max_age > 0.8

class BacteriaSimulation:
    def __init__(self):
        self.bacteria_population: List[Bacteria] = []
        self.current_tick = 0
        self.antibiotic_level = 0.3
        self.initial_population = 50
        self.max_generations = 20
        self.current_max_generation = 0
        self.simulation_ended = False
        self.canvas_width = 800
        self.canvas_height = 400
        self.min_bacteria_distance = 8
        
        # Data untuk grafik
        self.population_history = []
        self.resistance_history = []
        self.tick_history = []
        self.generation_history = []
    
    def is_position_valid(self, x: float, y: float, existing_bacteria: List[Bacteria], exclude_id: str = None) -> bool:
        """Cek apakah posisi tidak terlalu dekat dengan bakteri lain"""
        for bacteria in existing_bacteria:
            if exclude_id and bacteria.id == exclude_id:
                continue
            distance = math.sqrt((bacteria.x - x) ** 2 + (bacteria.y - y) ** 2)
            if distance < self.min_bacteria_distance:
                return False
        return True
    
    def find_empty_space_near_parent(self, parent_x: float, parent_y: float, existing_bacteria: List[Bacteria]) -> tuple:
        """Mencari ruang kosong di dekat induk dengan prioritas ruang kosong"""
        max_attempts = 50
        base_radius = 20
        
        # Coba cari posisi dekat induk
        for attempt in range(max_attempts):
            radius = base_radius + attempt * 5  # Perluas radius pencarian secara bertahap
            angle = random.uniform(0, 2 * math.pi)
            
            x = max(15, min(self.canvas_width - 15, parent_x + math.cos(angle) * radius))
            y = max(15, min(self.canvas_height - 15, parent_y + math.sin(angle) * radius))
            
            if self.is_position_valid(x, y, existing_bacteria):
                return x, y
        
        # Fallback: cari ruang kosong di mana saja
        for attempt in range(100):
            x = random.uniform(15, self.canvas_width - 15)
            y = random.uniform(15, self.canvas_height - 15)
            
            if self.is_position_valid(x, y, existing_bacteria):
                return x, y
        
        # Last resort: sedikit offset dari induk
        return (
            max(15, min(self.canvas_width - 15, parent_x + random.uniform(-10, 10))),
            max(15, min(self.canvas_height - 15, parent_y + random.uniform(-10, 10)))
        )
    
    def initialize_population(self, population_size: int):
        """Initialize bacteria population dengan spacing yang baik"""
        self.bacteria_population = []
        self.initial_population = population_size
        
        for i in range(population_size):
            attempts = 0
            while attempts < 100:
                x = random.uniform(50, self.canvas_width - 50)
                y = random.uniform(50, self.canvas_height - 50)
                
                if self.is_position_valid(x, y, self.bacteria_population):
                    bacteria = Bacteria(
                        age=random.randint(0, 15),
                        resistance_rate=random.uniform(0.05, 0.25),
                        reproduction_rate=random.uniform(0.8, 1.5),
                        max_age=random.randint(85, 120),
                        generation=0,
                        x=x,
                        y=y
                    )
                    self.bacteria_population.append(bacteria)
                    break
                attempts += 1
        
        self.current_tick = 0
        self.current_max_generation = 0
        self.simulation_ended = False
        self.population_history = []
        self.resistance_history = []
        self.tick_history = []
        self.generation_history = []
    
    def reproduce(self, parent: Bacteria, current_tick: int) -> List[Bacteria]:
        """Reproduksi aseksual dengan mutasi dan penempatan yang lebih baik"""
        if not parent.can_reproduce(current_tick):
            return []
        
        parent.last_reproduction = current_tick
        offspring = []
        
        for _ in range(2):  # Pembelahan biner
            mutation_strength = 0.15
            
            # Mutasi resistance_rate
            resistance_mutation = random.uniform(-mutation_strength, mutation_strength)
            new_resistance = max(0.0, min(1.0, parent.resistance_rate + resistance_mutation))
            
            # Mutasi reproduction_rate dengan trade-off
            reproduction_mutation = random.uniform(-mutation_strength/2, mutation_strength/2)
            resistance_cost = new_resistance * 0.3
            new_reproduction_rate = max(0.5, min(4.0, 
                parent.reproduction_rate + reproduction_mutation + resistance_cost))
            
            # Mutasi max_age
            age_mutation = random.randint(-20, 20)
            new_max_age = max(60, min(150, parent.max_age + age_mutation))
            
            # Posisi anak dengan prioritas ruang kosong
            new_x, new_y = self.find_empty_space_near_parent(
                parent.x, parent.y, self.bacteria_population + offspring
            )
            
            child = Bacteria(
                age=0,
                resistance_rate=new_resistance,
                reproduction_rate=new_reproduction_rate,
                max_age=new_max_age,
                generation=parent.generation + 1,
                last_reproduction=current_tick,
                x=new_x,
                y=new_y,
                parent_id=parent.id
            )
            offspring.append(child)
        
        return offspring
    
    def simulation_step(self):
        """Execute one simulation step"""
        self.current_tick += 1
        
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
            offspring = self.reproduce(bacteria, self.current_tick)
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
        self.population_history.append(len(self.bacteria_population))
        self.tick_history.append(self.current_tick)
        self.generation_history.append(self.current_max_generation)
        
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
            self.generation_history = self.generation_history[-200:]
    
    def get_statistics(self):
        """Get current simulation statistics"""
        if not self.bacteria_population:
            return {
                'population': 0,
                'avg_resistance': 0,
                'avg_reproduction': 0,
                'resistance_range': (0, 0),
                'high_resistance_count': 0,
                'medium_resistance_count': 0,
                'low_resistance_count': 0,
                'very_old_count': 0,
                'avg_age': 0
            }
        
        resistances = [b.resistance_rate for b in self.bacteria_population]
        reproductions = [b.reproduction_rate for b in self.bacteria_population]
        ages = [b.age for b in self.bacteria_population]
        
        high_res = sum(1 for r in resistances if r > 0.7)
        med_res = sum(1 for r in resistances if 0.3 <= r <= 0.7)
        low_res = len(resistances) - high_res - med_res
        very_old = sum(1 for b in self.bacteria_population if b.is_very_old())
        
        return {
            'population': len(self.bacteria_population),
            'avg_resistance': np.mean(resistances),
            'avg_reproduction': np.mean(reproductions),
            'resistance_range': (min(resistances), max(resistances)),
            'high_resistance_count': high_res,
            'medium_resistance_count': med_res,
            'low_resistance_count': low_res,
            'very_old_count': very_old,
            'avg_age': np.mean(ages)
        }

# Initialize session state
if 'simulation' not in st.session_state:
    st.session_state.simulation = BacteriaSimulation()
    st.session_state.is_running = False
    st.session_state.auto_run = False

# Main title
st.title("🦠 Simulasi Evolusi Resistansi Bakteri")
st.markdown("**Natural Selection & Mutasi Genetik dalam Populasi Mikroorganisme**")

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Kontrol Simulasi")
    
    # Population settings
    st.subheader("👥 Pengaturan Populasi")
    initial_pop = st.slider("Populasi Awal", 10, 200, 50)
    max_gen = st.slider("Maksimal Generasi", 5, 50, 20)
    
    # Antibiotic settings
    st.subheader("💊 Pengaturan Antibiotik")
    antibiotic_level = st.slider("Level Antibiotik", 0.0, 1.0, 0.3, 0.01)
    st.session_state.simulation.antibiotic_level = antibiotic_level
    st.session_state.simulation.max_generations = max_gen
    
    # Simulation controls
    st.subheader("🎮 Kontrol Simulasi")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.simulation.initialize_population(initial_pop)
            st.session_state.is_running = False
            st.session_state.auto_run = False
            st.rerun()
    
    with col2:
        if st.button("▶️ Start/Stop", use_container_width=True):
            st.session_state.is_running = not st.session_state.is_running
            st.session_state.auto_run = st.session_state.is_running
    
    # Auto-run toggle
    auto_run = st.checkbox("🔄 Auto-run", value=st.session_state.auto_run)
    st.session_state.auto_run = auto_run
    
    if auto_run:
        speed = st.slider("Kecepatan (ms)", 100, 2000, 500)
    
    # Manual step
    if st.button("➡️ Step Manual", use_container_width=True):
        if not st.session_state.simulation.simulation_ended:
            st.session_state.simulation.simulation_step()
            st.rerun()
    
    # Export data
    if st.button("📊 Export Data", use_container_width=True):
        stats = st.session_state.simulation.get_statistics()
        data = {
            'tick': st.session_state.simulation.current_tick,
            'population_history': st.session_state.simulation.population_history,
            'resistance_history': st.session_state.simulation.resistance_history,
            'tick_history': st.session_state.simulation.tick_history,
            'current_stats': stats
        }
        st.download_button(
            "💾 Download JSON",
            json.dumps(data, indent=2),
            "bacteria_simulation_data.json",
            "application/json"
        )

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Visualization
    st.subheader("🔬 Visualisasi Populasi Bakteri")
    
    if st.session_state.simulation.bacteria_population:
        # Create enhanced scatter plot for bacteria visualization
        bacteria_data = []
        for bacteria in st.session_state.simulation.bacteria_population:
            # Ukuran berdasarkan umur
            size = bacteria.get_size()
            
            # Warna berdasarkan resistansi dengan skala yang jelas
            resistance_category = "Rendah"
            if bacteria.resistance_rate > 0.7:
                resistance_category = "Tinggi"
            elif bacteria.resistance_rate >= 0.3:
                resistance_category = "Sedang"
            
            bacteria_data.append({
                'x': bacteria.x,
                'y': bacteria.y,
                'resistance': bacteria.resistance_rate,
                'age': bacteria.age,
                'generation': bacteria.generation,
                'size': size,
                'very_old': bacteria.is_very_old(),
                'resistance_category': resistance_category,
                'max_age': bacteria.max_age,
                'age_ratio': bacteria.age / bacteria.max_age
            })
        
        df_bacteria = pd.DataFrame(bacteria_data)
        
        # Create plotly scatter plot dengan perbaikan
        fig_bacteria = px.scatter(
            df_bacteria, 
            x='x', y='y', 
            color='resistance',
            size='size',
            hover_data={
                'age': True, 
                'generation': True, 
                'resistance_category': True,
                'very_old': True,
                'x': False,
                'y': False,
                'size': False
            },
            color_continuous_scale='RdYlBu_r',
            title="Distribusi Bakteri (Warna = Resistansi, Ukuran = Umur)",
            labels={
                'resistance': 'Tingkat Resistansi',
                'age': 'Umur',
                'generation': 'Generasi',
                'resistance_category': 'Kategori Resistansi',
                'very_old': 'Sangat Tua'
            }
        )
        
        # Tambahkan lingkaran tipis untuk bakteri sangat tua
        very_old_bacteria = df_bacteria[df_bacteria['very_old'] == True]
        if not very_old_bacteria.empty:
            fig_bacteria.add_trace(
                go.Scatter(
                    x=very_old_bacteria['x'],
                    y=very_old_bacteria['y'],
                    mode='markers',
                    marker=dict(
                        size=very_old_bacteria['size'] + 8,
                        color='rgba(0,0,0,0)',
                        line=dict(color='black', width=2)
                    ),
                    name='Bakteri Sangat Tua',
                    hovertemplate='Bakteri Sangat Tua<br>Umur: %{customdata[0]}<br>Resistansi: %{customdata[1]:.3f}<extra></extra>',
                    customdata=very_old_bacteria[['age', 'resistance']].values,
                    showlegend=True
                )
            )
        
        fig_bacteria.update_layout(
            width=800, height=400,
            xaxis_range=[0, 800],
            yaxis_range=[0, 400],
            xaxis_title="Posisi X",
            yaxis_title="Posisi Y"
        )
        
        st.plotly_chart(fig_bacteria, use_container_width=True)
        
        # Informasi tambahan tentang visualisasi
        st.info("""
        **Legenda Visualisasi:**
        - 🔴 **Merah**: Resistansi Tinggi (>0.7)
        - 🟡 **Kuning**: Resistansi Sedang (0.3-0.7)  
        - 🔵 **Biru**: Resistansi Rendah (<0.3)
        - **Ukuran**: Semakin besar = Semakin tua
        - **Lingkaran Hitam**: Bakteri sangat tua (>80% umur maksimal)
        """)
        
    else:
        st.info("Populasi kosong. Klik Reset untuk memulai simulasi baru.")
    
    # Evolution graphs
    st.subheader("📈 Grafik Evolusi Real-time")
    
    if len(st.session_state.simulation.tick_history) > 1:
        # Create subplot with secondary y-axis
        fig_evolution = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Populasi vs Waktu', 'Resistansi Rata-rata vs Waktu'),
            vertical_spacing=0.1
        )
        
        # Population plot
        fig_evolution.add_trace(
            go.Scatter(
                x=st.session_state.simulation.tick_history,
                y=st.session_state.simulation.population_history,
                mode='lines+markers',
                name='Populasi',
                line=dict(color='blue', width=3),
                marker=dict(size=4)
            ),
            row=1, col=1
        )
        
        # Resistance plot
        fig_evolution.add_trace(
            go.Scatter(
                x=st.session_state.simulation.tick_history,
                y=st.session_state.simulation.resistance_history,
                mode='lines+markers',
                name='Resistansi Rata-rata',
                line=dict(color='red', width=3),
                marker=dict(size=4)
            ),
            row=2, col=1
        )
        
        # Add antibiotic level line
        fig_evolution.add_hline(
            y=antibiotic_level, 
            line_dash="dash", 
            line_color="orange",
            annotation_text=f"Level Antibiotik ({antibiotic_level:.2f})",
            row=2, col=1
        )
        
        fig_evolution.update_layout(
            height=600,
            showlegend=True,
            title_text="Evolusi Populasi dan Resistansi"
        )
        
        fig_evolution.update_xaxes(title_text="Waktu (Tick)", row=2, col=1)
        fig_evolution.update_yaxes(title_text="Jumlah Populasi", row=1, col=1)
        fig_evolution.update_yaxes(title_text="Resistansi (0-1)", row=2, col=1)
        
        st.plotly_chart(fig_evolution, use_container_width=True)
    else:
        st.info("Grafik akan muncul setelah simulasi dimulai.")

with col2:
    # Statistics
    st.subheader("📊 Statistik Real-time")
    
    stats = st.session_state.simulation.get_statistics()
    
    # Current status
    st.metric("👥 Populasi", stats['population'])
    st.metric("⏱️ Tick", st.session_state.simulation.current_tick)
    st.metric("🧬 Generasi Max", st.session_state.simulation.current_max_generation)
    st.metric("🛡️ Resistansi Rata-rata", f"{stats['avg_resistance']:.3f}")
    st.metric("🔄 Reproduksi Rata-rata", f"{stats['avg_reproduction']:.3f}")
    st.metric("👴 Bakteri Sangat Tua", stats['very_old_count'])
    st.metric("📊 Umur Rata-rata", f"{stats['avg_age']:.1f}")
    st.metric("💊 Level Antibiotik", f"{antibiotic_level:.3f}")
    
    # Resistance distribution
    st.subheader("🎨 Distribusi Resistansi")
    if stats['population'] > 0:
        resistance_data = {
            'Kategori': ['Tinggi (>0.7)', 'Sedang (0.3-0.7)', 'Rendah (<0.3)'],
            'Jumlah': [stats['high_resistance_count'], 
                      stats['medium_resistance_count'], 
                      stats['low_resistance_count']],
            'Warna': ['🔴', '🟡', '🔵']
        }
        
        df_resistance = pd.DataFrame(resistance_data)
        
        fig_pie = px.pie(
            df_resistance, 
            values='Jumlah', 
            names='Kategori',
            color_discrete_sequence=['#ff4757', '#ffa502', '#3742fa'],
            title="Distribusi Kategori Resistansi"
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Tampilkan persentase
        total = stats['population']
        st.write("**Persentase Resistansi:**")
        st.write(f"🔴 Tinggi: {stats['high_resistance_count']/total*100:.1f}%")
        st.write(f"🟡 Sedang: {stats['medium_resistance_count']/total*100:.1f}%")
        st.write(f"🔵 Rendah: {stats['low_resistance_count']/total*100:.1f}%")
    
    # Simulation status
    st.subheader("⚡ Status Simulasi")
    if st.session_state.simulation.simulation_ended:
        if stats['population'] == 0:
            st.error("💀 Populasi Punah!")
        else:
            st.success("✅ Simulasi Selesai!")
    elif st.session_state.is_running:
        st.info("🔄 Simulasi Berjalan...")
    else:
        st.warning("⏸️ Simulasi Berhenti")
    
    # Information panel
    st.subheader("📚 Informasi")
    with st.expander("🧬 Konsep Biologi"):
        st.markdown("""
        **Natural Selection**: Bakteri dengan resistansi tinggi bertahan lebih baik terhadap antibiotik.
        
        **Mutasi Genetik**: Setiap reproduksi menghasilkan variasi genetik.
        
        **Trade-off**: Resistansi tinggi mengurangi kecepatan reproduksi.
        
        **Genetic Drift**: Perubahan frekuensi gen dalam populasi kecil.
        
        **Aging**: Bakteri bertambah besar seiring umur dan mendapat penanda visual saat sangat tua.
        """)
    
    with st.expander("💡 Tips Penggunaan"):
        st.markdown("""
        1. **Mulai dengan populasi kecil** (50-100) untuk performa optimal
        2. **Tingkatkan antibiotik** untuk melihat seleksi yang kuat
        3. **Amati trade-off** antara resistansi dan reproduksi
        4. **Perhatikan bakteri tua** dengan lingkaran hitam
        5. **Lihat penyebaran anak** dekat induk di ruang kosong
        6. **Export data** untuk analisis lebih lanjut
        7. **Gunakan auto-run** untuk simulasi otomatis
        """)
    
    # with st.expander("🎨 Fitur Visualisasi Baru"):
    #     st.markdown("""
    #     **Peningkatan Visualisasi:**
    #     - ✅ Ukuran bakteri bertambah seiring umur
    #     - ✅ Lingkaran tipis untuk bakteri sangat tua (>80% umur max)
    #     - ✅ Anak bakteri menyebar dekat induk
    #     - ✅ Prioritas ruang kosong untuk reproduksi
    #     - ✅ Warna resistansi yang jelas (Merah-Kuning-Biru)
    #     - ✅ Hover info yang informatif
    #     - ✅ Statistik umur dan bakteri tua
    #     """)

# Auto-run logic
if st.session_state.auto_run and not st.session_state.simulation.simulation_ended:
    if (st.session_state.simulation.current_max_generation < st.session_state.simulation.max_generations and 
        len(st.session_state.simulation.bacteria_population) > 0):
        
        time.sleep(speed / 1000)  # Convert ms to seconds
        st.session_state.simulation.simulation_step()
        st.rerun()
    else:
        st.session_state.simulation.simulation_ended = True
        st.session_state.is_running = False
        st.session_state.auto_run = False

# Footer
st.markdown("---")
st.markdown("🔬 **Simulasi Evolusi Resistansi Bakteri** - Demonstrasi konsep biologi evolusi dan seleksi alam")
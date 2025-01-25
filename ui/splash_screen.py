import tkinter as tk
from tkinter import ttk, font
from pathlib import Path
import time
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
from tkinter.font import Font
import math
import random

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Load Raxtor font first
        self.load_raxtor_font()
        
        # Configure the window
        self.overrideredirect(True)
        self.attributes('-alpha', 0.0, '-topmost', True)
        
        # Set window background to pure black
        self.configure(bg='#000000')
        
        # Remove any borders
        self.config(borderwidth=0, highlightthickness=0)
        
        # Set fixed size and center on screen
        width = 800
        height = 650  # Increased height to accommodate status text
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create main frame with black background
        self.main_frame = ttk.Frame(self, style='Main.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure styles for dark theme with Raxtor font
        self.style = ttk.Style()
        self.style.configure('Main.TFrame', 
                           background='#000000')
        self.style.configure('Content.TFrame',
                           background='#000000')
        
        # Use the registered Raxtor font
        if hasattr(self, 'raxtor_font'):
            title_font = self.raxtor_font.copy()
            title_font.config(size=36, weight='bold')
            team_font = self.raxtor_font.copy()
            team_font.config(size=12)
            
            self.style.configure('Title.TLabel',
                               background='#000000',
                               foreground='#FFFFFF',
                               font=title_font)
            self.style.configure('Team.TLabel',
                               background='#000000',
                               foreground='#808080',
                               font=team_font)
        else:
            # Fallback fonts if Raxtor is not available
            self.style.configure('Title.TLabel',
                               background='#000000',
                               foreground='#FFFFFF',
                               font=('Segoe UI', 36, 'bold'))
            self.style.configure('Team.TLabel',
                               background='#000000',
                               foreground='#808080',
                               font=('Segoe UI', 12))
        
        # Create content frame
        content_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add title
        ttk.Label(content_frame, text="Payment Treasury System", 
                 style='Title.TLabel').pack(pady=(50, 0))
        
        # Create progress frame
        progress_frame = ttk.Frame(content_frame, style='Content.TFrame')
        progress_frame.pack(fill=tk.X, padx=200, pady=(100, 0))
        
        # Create status label with modern font
        self.status_label = ttk.Label(
            progress_frame,
            text="",
            style='Status.TLabel'
        )
        self.status_label.pack(pady=(0, 10))
        
        # Configure status label style
        self.style.configure(
            'Status.TLabel',
            background='#000000',
            foreground='#00FF00',  # Bright green
            font=('Segoe UI', 10)  # Regular weight, smaller size
        )
        
        # Create progress canvas
        self.progress_canvas = tk.Canvas(
            progress_frame,
            height=8,
            width=400,
            bg='#1A1A1A',
            highlightthickness=0
        )
        self.progress_canvas.pack(fill=tk.X)
        
        # Create gradient overlay for progress
        self.gradient_image = None
        self.create_gradient()
        
        # Initial progress bar elements
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 8,
            fill='#00B140',
            width=0
        )
        
        # Team credit at bottom right
        team_frame = ttk.Frame(self.main_frame, style='Content.TFrame')
        team_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(team_frame, text="Salam Treasury Team", 
                 style='Team.TLabel').pack(side=tk.RIGHT, padx=25, pady=20)
        
        # Loading messages combining technical and treasury-specific elements
        self.loading_messages = [
            # Technical initialization messages
            "Initializing complex algorithms",
            "Optimizing system performance",
            "Loading advanced modules",
            "Processing large datasets",
            "Configuring AI frameworks",
            "Initializing quantum processing",
            "Loading neural networks",
            "Optimizing machine learning",
            "Processing distributed systems",
            "Configuring advanced analytics",
            
            # Treasury-specific modules
            "Initializing core treasury modules",
            "Loading bank account interfaces",
            "Configuring LG management system",
            "Initializing payment processing engine",
            "Loading financial reporting modules",
            "Configuring multi-currency support",
            "Initializing risk assessment tools",
            "Loading compliance frameworks",
            "Configuring automated reconciliation",
            "Initializing cash management system",
            "Loading trade finance modules",
            "Setting up beneficiary databases",
            "Configuring payment authorization matrix",
            "Loading audit trail system",
            "Initializing fraud detection engine",
            "Configuring bank statement processors",
            "Loading transaction monitoring system",
            "Setting up treasury dashboards",
            "Initializing liquidity management",
            "Configuring real-time bank connectivity",
            "Loading payment validation rules",
            "Setting up SWIFT messaging system",
            "Initializing document management",
            "Loading sanction screening modules",
            "Configuring payment templates"
        ]
        
        # Ensure technical messages appear first
        technical_messages = self.loading_messages[:10]
        treasury_messages = self.loading_messages[10:]
        
        # Shuffle treasury messages while keeping technical ones in order
        random.shuffle(treasury_messages)
        self.loading_messages = technical_messages + treasury_messages
        
        self.current_message_index = 0
        self.fade_alpha = 1.0
        
        # Start loading animation
        self.loading_thread = threading.Thread(target=self.simulate_loading)
        self.loading_thread.daemon = True
        self.loading_thread.start()
        
        # Fade in the window
        self.fade_in()
    
    def create_gradient(self):
        """Create a gradient image for the progress bar with glow effect"""
        width = 400
        height = 8
        # Create larger gradient for glow effect
        gradient = Image.new('RGBA', (width, height * 3))
        draw = ImageDraw.Draw(gradient)
        
        for x in range(width):
            # Create a gradient from dark gold to bright gold
            r = int(218 + (x / width) * 37)  # 218 to 255
            g = int(165 + (x / width) * 90)  # 165 to 255
            b = int(32 + (x / width) * 32)   # 32 to 64
            
            # Add glow effect
            glow_color = f'#{r:02x}{g:02x}{b:02x}40'  # 40 = 25% opacity
            draw.line([(x, 0), (x, height * 3)], fill=glow_color)
            
            # Main gradient
            color = f'#{r:02x}{g:02x}{b:02x}'
            draw.line([(x, height), (x, height * 2)], fill=color)
        
        self.gradient_image = ImageTk.PhotoImage(gradient)
        
        # Create coin images for animation
        coin_size = (16, 16)
        coin = Image.new('RGBA', coin_size)
        coin_draw = ImageDraw.Draw(coin)
        
        # Draw a gold coin
        coin_draw.ellipse([0, 0, 15, 15], fill='#FFD700')
        try:
            font = ImageFont.truetype('arial', 10)
            # Calculate text size
            text_bbox = coin_draw.textbbox((0, 0), '$', font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            # Center text
            x = (16 - text_width) // 2
            y = (16 - text_height) // 2
            coin_draw.text((x, y), '$', fill='#B8860B', font=font)
        except Exception:
            # Fallback if font loading fails
            coin_draw.ellipse([6, 6, 10, 10], fill='#B8860B')
        
        self.coin_image = ImageTk.PhotoImage(coin)
    
    def update_progress_bar(self, value):
        """Update progress bar with dynamic money-filling animation"""
        width = self.progress_canvas.winfo_width()
        progress_width = (value / 100) * width
        
        # Clear previous drawings
        self.progress_canvas.delete('all')
        
        # Draw background with slight transparency
        self.progress_canvas.create_rectangle(
            0, 0, width, 8,
            fill='#1A1A1A',
            width=0
        )
        
        if progress_width > 0:
            # Draw glowing progress bar
            self.progress_canvas.create_rectangle(
                0, 0, progress_width, 8,
                fill='#DAA520',  # Golden color
                width=0
            )
            
            # Add gradient overlay with glow
            if self.gradient_image:
                self.progress_canvas.create_image(
                    0, -8,  # Offset for glow effect
                    image=self.gradient_image,
                    anchor='nw'
                )
            
            # Add animated coins
            for i in range(int(progress_width / 30)):
                x = i * 30 + (value % 15)
                # Create floating effect with sine wave
                y = 4 + math.sin((value + i * 30) / 10) * 2
                
                # Draw coin with glow
                glow_radius = 8 + math.sin(value/5) * 2  # Pulsing glow
                self.progress_canvas.create_oval(
                    x-glow_radius, y-glow_radius,
                    x+glow_radius, y+glow_radius,
                    fill='#FFD700',  # Solid gold
                    outline=''
                )
                
                if hasattr(self, 'coin_image'):
                    self.progress_canvas.create_image(
                        x, y,
                        image=self.coin_image,
                        anchor='center'
                    )
        
        # Add shimmer effect
        shimmer_pos = (value % 100) / 100 * width
        self.progress_canvas.create_line(
            shimmer_pos-10, 0,
            shimmer_pos+10, 8,
            fill='#FFFFFF',  # Solid white
            width=2,
            smooth=True
        )
    
    def animate_status_text(self):
        """Display status text with rapid transitions"""
        if not hasattr(self, 'status_label'):
            return
        
        # Get next message
        current_message = self.loading_messages[self.current_message_index]
        
        # Add ellipsis
        self.status_label.configure(text=f"{current_message}...")
        
        # Move to next message every 500ms (twice as fast)
        self.current_message_index = (self.current_message_index + 1) % len(self.loading_messages)
        
        # Schedule next update (500ms = 0.5 second)
        self.after(500, self.animate_status_text)
    
    def simulate_loading(self):
        """Simulate a realistic loading process with varied speeds and pauses"""
        # Define loading phases with different behaviors
        loading_phases = [
            # Initial phase - technical setup
            {"start": 0, "end": 15, "speed": 0.02, "message_delay": 300},
            # Processing phase - core initialization
            {"start": 15, "end": 35, "speed": 0.05, "message_delay": 600},
            # Complex calculation phase - main modules
            {"start": 35, "end": 60, "speed": 0.08, "message_delay": 800},
            # Treasury modules phase - specific features
            {"start": 60, "end": 85, "speed": 0.03, "message_delay": 400},
            # Final phase - completion and optimization
            {"start": 85, "end": 100, "speed": 0.06, "message_delay": 500}
        ]
        
        current_phase = 0
        self.message_update_time = 0
        
        def update_message():
            """Update status message with dynamic timing"""
            if not hasattr(self, 'status_label'):
                return
            
            current_message = self.loading_messages[self.current_message_index]
            self.status_label.configure(text=f"{current_message}...")
            self.current_message_index = (self.current_message_index + 1) % len(self.loading_messages)
            
            # Schedule next message update with phase-specific delay
            if current_phase < len(loading_phases):
                phase = loading_phases[current_phase]
                self.message_update_time = time.time() + (phase["message_delay"] / 1000.0)
        
        # Start initial message
        update_message()
        
        # Simulate loading with varied speeds
        for phase in loading_phases:
            current_phase += 1
            
            for i in range(phase["start"], phase["end"]):
                # Update progress
                self.after(0, self.update_progress_bar, i)
                
                # Add random micro-pauses for realism
                if random.random() < 0.2:  # 20% chance of micro-pause
                    time.sleep(random.uniform(0.1, 0.3))
                
                # Normal progress delay
                time.sleep(phase["speed"])
                
                # Check if it's time for a new message
                if time.time() >= self.message_update_time:
                    self.after(0, update_message)
                
                # Occasional longer pause for "processing"
                if random.random() < 0.1:  # 10% chance of processing pause
                    self.status_label.configure(text="Processing...")
                    time.sleep(random.uniform(0.2, 0.5))
                    update_message()
        
        # Show completion message and fade out
        self.after(0, lambda: self.status_label.configure(
            text="Ready to predictive algorithms...",
            foreground='#00FF00'
        ))
        time.sleep(0.8)  # Slightly longer pause at completion
        self.after(0, self.fade_out)
    
    def fade_color(self, hex_color, alpha):
        """Fade a hex color to black based on alpha value"""
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Interpolate to black based on alpha
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def fade_in(self):
        """Smooth fade-in animation"""
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.03  # Slower fade for smoothness
            self.attributes('-alpha', alpha)
            self.after(8, self.fade_in)
    
    def fade_out(self):
        """Smooth fade-out animation"""
        alpha = self.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.03  # Slower fade for smoothness
            self.attributes('-alpha', alpha)
            self.after(8, self.fade_out)
        else:
            self.destroy()

    def load_raxtor_font(self):
        """Load and register the Raxtor font family"""
        try:
            # Try to use Raxtor if it's installed in the system
            self.raxtor_font = font.Font(family="Raxtor")
            print("Successfully loaded Raxtor font from system")
        except Exception as e:
            print(f"Raxtor font not available, using fallback font: {e}")
            # Use a modern, professional fallback font
            self.raxtor_font = font.Font(family="Segoe UI")

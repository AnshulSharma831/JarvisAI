import tkinter as tk
from tkinter import ttk, scrolledtext
import os
import sys
from PIL import Image, ImageTk
import asyncio

# Add Backend directory to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Backend')))

# Import backend functionalities (assuming these exist)
from SpeechToText import SpeechRecognition
from TextToSpeech import TextToSpeech
from Chatbot import ChatBot
from ImageGeneration import GenerateImages
from RealtimeSearchEngine import RealtimeSearchEngine
from Automation import Automation
from Model import FirstLayerDMM

class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JarvisAI")
        self.root.geometry("900x700")  # Slightly larger window
        self.root.configure(bg="#0d1b2a")  # Deep blue-black background

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=10, background="#00b4d8", foreground="white")
        self.style.map("TButton", background=[('active', '#48cae4')], foreground=[('active', 'white')])
        self.style.configure("TLabel", font=("Arial", 16, "bold"), background="#0d1b2a", foreground="#90e0ef")
        self.style.configure("TEntry", font=("Arial", 12), fieldbackground="#52796f", foreground="white")

        # Gradient Canvas for Header
        self.header_canvas = tk.Canvas(self.root, height=80, bg="#0d1b2a", highlightthickness=0)
        self.header_canvas.pack(fill="x")
        self.create_gradient(self.header_canvas, "#0d1b2a", "#1b263b")
        self.header_label = ttk.Label(self.header_canvas, text="JarvisAI", style="TLabel")
        self.header_label.place(relx=0.5, rely=0.5, anchor="center")

        # Main Frame with subtle border
        self.main_frame = ttk.Frame(self.root, padding=10, style="Main.TFrame")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.style.configure("Main.TFrame", background="#1b263b", borderwidth=2, relief="solid")

        # Output Area
        self.output_area = scrolledtext.ScrolledText(self.main_frame, height=15, width=80, bg="#2a2d35", fg="#caf0f8", 
                                                    font=("Arial", 12), wrap=tk.WORD, borderwidth=2, relief="flat")
        self.output_area.pack(pady=10, fill="x")
        self.output_area.insert(tk.END, "Welcome to JarvisAI! How can I assist you today?\n")
        self.output_area.config(state='disabled')

        # Image Display Area with placeholder background
        self.image_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.image_frame.pack(pady=10)
        self.image_label = ttk.Label(self.image_frame, background="#2a2d35", compound="center")
        self.image_label.pack()

        # Input Frame
        self.input_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.input_frame.pack(pady=10, fill="x")

        # Text Input Field with rounded corners (simulated)
        self.input_field = ttk.Entry(self.input_frame, width=60, style="TEntry")
        self.input_field.grid(row=0, column=0, padx=5, pady=5)
        self.input_field.bind("<Return>", self.process_text_input)

        # Send Button with icon (assuming 'send_icon.png' exists)
        try:
            send_icon = ImageTk.PhotoImage(Image.open("send_icon.png").resize((20, 20)))
            self.send_button = ttk.Button(self.input_frame, text="Send", image=send_icon, compound="left", 
                                        command=self.process_text_input)
            self.send_button.image = send_icon  # Keep reference
        except:
            self.send_button = ttk.Button(self.input_frame, text="Send", command=self.process_text_input)
        self.send_button.grid(row=0, column=1, padx=5)

        # Voice Input Button with icon (assuming 'mic_icon.png' exists)
        try:
            mic_icon = ImageTk.PhotoImage(Image.open("mic_icon.png").resize((20, 20)))
            self.voice_button = ttk.Button(self.main_frame, text="Speak", image=mic_icon, compound="left", 
                                         command=self.process_voice_input)
            self.voice_button.image = mic_icon
        except:
            self.voice_button = ttk.Button(self.main_frame, text="Speak", command=self.process_voice_input)
        self.voice_button.pack(pady=5)

        # Action Buttons Frame
        self.action_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.action_frame.pack(pady=10)

        # Action Buttons with icons
        try:
            search_icon = ImageTk.PhotoImage(Image.open("search_icon.png").resize((20, 20)))
            self.search_button = ttk.Button(self.action_frame, text="Search", image=search_icon, compound="left", 
                                          command=self.perform_search)
            self.search_button.image = search_icon
        except:
            self.search_button = ttk.Button(self.action_frame, text="Search", command=self.perform_search)
        self.search_button.grid(row=0, column=0, padx=10)

        try:
            image_icon = ImageTk.PhotoImage(Image.open("image_icon.png").resize((20, 20)))
            self.image_button = ttk.Button(self.action_frame, text="Generate Image", image=image_icon, compound="left", 
                                         command=self.generate_image_action)
            self.image_button.image = image_icon
        except:
            self.image_button = ttk.Button(self.action_frame, text="Generate Image", command=self.generate_image_action)
        self.image_button.grid(row=0, column=1, padx=10)

        # Status Bar with gradient
        self.status_canvas = tk.Canvas(self.root, height=30, bg="#0d1b2a", highlightthickness=0)
        self.status_canvas.pack(fill="x", side="bottom")
        self.create_gradient(self.status_canvas, "#0d1b2a", "#1b263b")
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.status_canvas, textvariable=self.status_var, style="TLabel")
        self.status_bar.place(relx=0.5, rely=0.5, anchor="center")

    def create_gradient(self, canvas, color1, color2):
        """Create a gradient background on a canvas."""
        width = self.root.winfo_screenwidth()
        canvas.delete("all")
        r1, g1, b1 = self.root.winfo_rgb(color1)
        r2, g2, b2 = self.root.winfo_rgb(color2)
        r_ratio = float(r2 - r1) / 100
        g_ratio = float(g2 - g1) / 100
        b_ratio = float(b2 - b1) / 100

        for i in range(100):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr:04x}{ng:04x}{nb:04x}"
            canvas.create_line(0, i, width, i, fill=color)

    def update_output(self, message):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def display_image(self, image_paths):
        if not image_paths:
            self.update_output("Jarvis: No images available to display.")
            return
        for image_path in image_paths:
            try:
                img = Image.open(image_path)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.configure(image=photo)
                self.image_label.image = photo
                self.root.update()
                break
            except IOError as e:
                self.update_output(f"Jarvis: Unable to display {image_path}: {str(e)}")

    def process_text_input(self, event=None):
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        self.update_output(f"User: {user_input}")
        self.input_field.delete(0, tk.END)
        self.status_var.set("Processing...")
        commands = FirstLayerDMM(user_input)
        self.update_output(f"Jarvis: Classified as {commands}")
        for command in commands:
            if command.startswith("general"):
                query = command.replace("general ", "")
                response = ChatBot(query)
                self.update_output(f"Jarvis: {response}")
                TextToSpeech(response)
            elif command.startswith(("open", "close", "play", "content", "google search", "youtube search", "system")):
                if command.startswith("google search") and "www.google.com" in command:
                    self.update_output("Jarvis: It looks like you entered a URL. Please provide a search term.")
                    continue
                if command.startswith("google search weather today"):
                    weather_response = RealtimeSearchEngine("weather today in Ashburn")
                    self.update_output(f"Jarvis: {weather_response}")
                    TextToSpeech(weather_response)
                    continue
                result = asyncio.run(Automation([command]))
                self.update_output(f"Jarvis: Automation result: {', '.join(result)}")
            elif command.startswith("generate image"):
                prompt = command.replace("generate image ", "")
                self.generate_image_action(prompt)
            elif command.startswith("realtime"):
                query = command.replace("realtime ", "")
                response = RealtimeSearchEngine(query)
                self.update_output(f"Jarvis: {response}")
                TextToSpeech(response)
            elif command == "exit":
                self.update_output("Jarvis: Goodbye!")
                self.root.quit()
            else:
                self.update_output(f"Jarvis: Unrecognized command: {command}")
        self.status_var.set("Ready")

    def process_voice_input(self):
        self.status_var.set("Listening...")
        try:
            user_input = SpeechRecognition()
            if user_input:
                self.update_output(f"User (Voice): {user_input}")
                self.input_field.delete(0, tk.END)
                self.input_field.insert(0, user_input)
                self.process_text_input()
            else:
                self.update_output("Jarvis: I didn't catch that. Please try again.")
        except Exception as e:
            self.update_output(f"Jarvis: Error with voice input: {str(e)}")
        self.status_var.set("Ready")

    def perform_search(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            self.update_output("Jarvis: Please enter a search query.")
            return
        self.update_output(f"User: Search for {user_input}")
        self.status_var.set("Searching...")
        result = RealtimeSearchEngine(user_input)
        self.update_output(f"Jarvis: {result}")
        TextToSpeech(result)
        self.status_var.set("Ready")

    def generate_image_action(self, prompt=None):
        if not prompt:
            prompt = self.input_field.get().strip()
        if not prompt or prompt == "(image prompt)":
            self.update_output("Jarvis: Please enter a valid description for the image.")
            return
        if "tony stark" in prompt.lower():
            self.update_output("Jarvis: Adjusting prompt to avoid copyrighted content.")
            prompt = "A superhero in a red and gold suit"
        self.update_output(f"User: Generate image of {prompt}")
        self.status_var.set("Generating Image...")
        success, image_paths, error_msg = GenerateImages(prompt)
        if success:
            self.update_output(f"Jarvis: Image generated for '{prompt}'!")
            self.display_image(image_paths)
        else:
            self.update_output(f"Jarvis: {error_msg}")
        self.status_var.set("Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()
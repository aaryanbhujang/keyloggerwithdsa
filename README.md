# Keylogger GUI Application

A graphical keylogger application developed in Python using the `tkinter` library. This app captures keystrokes and displays them in a scrollable log window, designed with a dark-themed modern UI for ease of use. 

## Features

- **Keystroke Capture**: Logs all keystrokes and displays them in real-time.
- **Timestamped Log**: Automatically adds timestamps after 30 seconds of inactivity.
- **User-Friendly GUI**: Built with a dark theme, providing a visually modern experience.
- **Clear Log Button**: Allows users to clear the log display with a single click.
- **Automatic Word Formation**: Groups letters into words for easier readability.
  
## Technologies Used

- **Python**: Main programming language
- **tkinter**: For GUI components
- **pynput**: For keyboard listener functionality
- **datetime**: For timestamping the log

## Prerequisites

- Python 3.x
- Required packages: `tkinter`, `pynput`

Install dependencies via pip:
```bash
pip install pynput

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
```
1. Setting Up the GUI
Main Window:

The code starts by creating the main window (root) with a dark theme and a title. DPI awareness is set for Windows systems to handle different display resolutions better.
Title and Subtitle:

Labels for the title (Keylogger) and a subtitle (Track those keystrokes.) are added to the top of the GUI window to guide the user.
Main Frame:

The main_frame divides the window into two primary areas: the log display area and the button area, creating a card-like appearance for each section.
Log Display:

A ScrolledText widget is used to display keystrokes as they are captured. This widget supports text wrapping and scrolling, making it ideal for a continuous log.
Button Area:

The "Clear Log" button, styled with a modern look, clears the displayed keystrokes when clicked.
2. Keylogger Functionalities
Starting the Keylogger:

The startKeylogger method initializes a keyboard listener using the pynput library, which runs in the background and listens for all keystrokes.
Each keystroke triggers the wordStacker function.
Keystroke Handling (wordStacker function):

This function processes each key pressed:
Backspace removes the last character from word_stack.
Space or Enter pushes the completed word (or sentence, in the case of Enter) to the log.
All other keystrokes are added to word_stack, forming a word one character at a time.
Displaying Keystrokes in Log (enqueueIntoLog function):

enqueueIntoLog takes completed words or lines and displays them in the log:
It checks if more than 30 seconds have passed since the last keystroke. If so, it adds a timestamp before displaying the next word.
The latest timestamp is updated to ensure only idle periods over 30 seconds trigger a new timestamp.
Clearing the Log (clearLog function):

When "Clear Log" is clicked, the log display is emptied, allowing for a fresh start without restarting the application.
3. Closing the Application
Stopping the Keylogger:
When the user closes the main window, the onClose method stops the pynput listener and safely closes the application, ensuring there’s no leftover process running in the background.

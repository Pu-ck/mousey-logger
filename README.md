# mousey-logger
Key(and mouse)logger

Python keylogger for Windows - detects and logs keyboard input (normal and special keys, along with the most common "ctrl + letter" hotkeys), mouse input (scrolls and clicks at [x, y] position), clipboard content (text and screenshots) and currently opened tabs (both system tabs as well as web browser tabs). All informations are stored in log.txt file (with date and time of creation and sending), screenshots are saved and then overwritten to screenshot.png file. Each log.txt file is sent to given e-mail address, when its character capacity is full (5000 characters by default). Each new taken screenshot is sent to given e-mail address. Capacity of log.txt files can be changed in config.ini file or in the code itself, desired e-mail address and password can be set in the code. Set hide_window to True in config.ini in order to hide console window.

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

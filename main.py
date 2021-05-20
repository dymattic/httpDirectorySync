import os.path
from pprint import pprint
from tkinter import *
import threading
from time import sleep
from random import randint
import re

import PySimpleGUI
import PySimpleGUI as sg

from httpDirectorySync import HttpDirectorySync

class Main:

    def __init__(self):
        # Window Column Definitions

        progress_bar = [
            [sg.ProgressBar(100, size=(40, 20), pad=(0, 0), key='Progress Bar'),
             sg.Text("  0%", size=(4, 1), key='Percent'), ],
        ]
        # Settings and Filetypes
        settings_controls_column = [

            [
                sg.Text('Comma separated list of file types'),
            ],
            [
                sg.In(default_text="pdf,jpeg,zip,java,jar,docx,rar,txt,rtf,tar", key="-FILETYPES-"),
            ],
            [
                sg.HSeparator(),
            ],

            [
                sg.Text('HTTP Auth Credentials'),
            ],
            [
                sg.Text("Username"),
                sg.In(size=(25, 1), enable_events=True, key="-HTTP User-"),
            ],
            [
                sg.Text("Password"),
                sg.In(size=(25, 1), enable_events=True, key="-HTTP Pass-", password_char="*"),
            ],
            [
                sg.HSeparator(),
            ],
            [
                sg.Text("Settings:")
            ],
            [
                sg.Text("Load from saved settings or save current.")
            ],
            [
                sg.Button(button_text="Load", enable_events=True, key="-SETTINGS LOAD-"),
                sg.Button(button_text="Save", enable_events=True, key="-SETTINGS SAVE-"),
            ],

        ]

        # URL Input and Remote Dir List
        web_url_column = [
            [
                sg.Text('HTTP Directory URL'),
                sg.In(size=(25, 1), enable_events=True, key="-URL-"),
                sg.Button(button_text="Search", enable_events=True, key="-URL Search-")
            ],
            [
                sg.Text("Remote: "),
                sg.Text(size=(40, 1), key="-Remote Text-"),
            ],
            [
                sg.Listbox(

                    values=[], enable_events=True, size=(40, 20), key="-Remote DIR LIST-"

                )

            ],

        ]

        # Local Directory search and list
        file_list_column = [

            [

                sg.Text("Folder"),

                sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),

                sg.FolderBrowse(),

            ],
            [

                sg.Listbox(

                    values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"

                )

            ],

        ]

        # Sync Button and output
        remote_sync_column = [
            [
                sg.Button("Sync", enable_events=True, key="-SYNC-"),
                sg.pin(sg.Column(progress_bar, key='Progress', visible=False))
            ],
            [sg.Text("Output:")],
            [sg.Output(size=(110, 20), font=('Helvetica 10'), key="-TOUT-")],
        ]

        # ----- Full layout -----



        layout = [

            [
                sg.Column(settings_controls_column),
                sg.VSeparator(),
                sg.Column(web_url_column),
                sg.VSeparator(),

                sg.Column(file_list_column),
            ],
            [
                sg.HSeparator(),
            ],
            [
                sg.Text(size=(15,0)),
                sg.Column(remote_sync_column),
            ],
        ]
        # Add Layout to window
        self.window = sg.Window("HTTP Directory Sync", layout)
        self.sync = HttpDirectorySync()
        self.downloading = False

    def download_file(self):
        while self.downloading:
            download_percent = 0
            while download_percent <= 100:
                download_percent = self.sync.get_percent()
                sleep(0.1)
                self.window.write_event_value('Next', download_percent)

    def sync_r(self, auth):
        self.downloading = True
        if not self.sync.sync_recurse(url_local=self.values["-URL-"], working_dir=self.values["-FOLDER-"], credentials=auth,
                                 filetypes=self.values["-FILETYPES-"]):
            pprint("Job finished with errors")
        else:
            pprint("Sync Successful")
        self.downloading = False

    def run(self):
        # Main
        if __name__ == '__main__':

            progress_bar = self.window['Progress Bar']
            percent = self.window['Percent']
            progress = self.window['Progress']

            try:
                # GUI Loop
                while True:

                    self.event, self.values = self.window.read()

                    if self.event == "Exit" or self.event == sg.WIN_CLOSED:
                        self.window.close()
                        break

                    # Save/Load Settings
                    if self.event == "-SETTINGS SAVE-":
                        authUser = self.values["-HTTP User-"]
                        authPass = self.values["-HTTP Pass-"]
                        url = self.values["-URL-"]
                        folder = self.values["-FOLDER-"]
                        ftypes = self.values["-FILETYPES-"]
                        sg.user_settings_set_entry("authUser", authUser)
                        sg.user_settings_set_entry("authPass", authPass)
                        sg.user_settings_set_entry("url", url)
                        sg.user_settings_set_entry("folder", folder)
                        sg.user_settings_set_entry("ftypes", ftypes)
                    elif self.event == "-SETTINGS LOAD-":
                        self.window["-HTTP User-"].update(sg.user_settings_get_entry('authUser'))
                        self.window["-HTTP Pass-"].update(sg.user_settings_get_entry('authPass'))
                        self.window["-URL-"].update(sg.user_settings_get_entry('url'))
                        self.window["-FOLDER-"].update(sg.user_settings_get_entry('folder'))
                        self.window["-FILETYPES-"].update(sg.user_settings_get_entry('ftypes'))

                    # Handle Local Directory
                    elif self.event == "-FOLDER-":

                        folder = self.values["-FOLDER-"]

                        try:

                            # Get list of files in folder

                            file_list = os.listdir(folder)

                        except:

                            file_list = []
                        filePatternArr = self.values["-FILETYPES-"].split(',')
                        type_pattern = ''
                        for ftype in filePatternArr:
                            type_pattern += ftype + '|'
                        type_pattern = type_pattern.strip('|')
                        fileEndingPattern = re.compile('\\.(' + type_pattern + ')$')
                        fnames = [

                            f

                            for f in file_list

                            if os.path.isfile(os.path.join(folder, f))

                               and fileEndingPattern.search(f) is not None

                        ]

                        self.window["-FILE LIST-"].update(fnames)

                    # Get Remote Contents when URl has been added and search was pressed
                    elif self.event == "-URL Search-":
                        if self.values["-URL-"] != "":
                            self.window["-Remote Text-"].update(self.values["-URL-"])
                            if self.values["-HTTP User-"] != "":
                                if self.values["-HTTP Pass-"] != "":
                                    auth = self.sync.gen_auth(username=self.values["-HTTP User-"], password=self.values["-HTTP Pass-"])
                                else:
                                    auth = self.sync.gen_auth(username=self.values["-HTTP User-"])
                            else:
                                auth = False
                            remote = self.sync.get_remote_listing(url_local=self.values["-URL-"], credentials=auth,
                                                             filetypes=self.values["-FILETYPES-"])
                            out = []
                            if ".." not in remote[1]:
                                out.append("../")
                            for folder in remote[1]:
                                out.append(folder[0] + "/")
                            for file in remote[0]:
                                out.append(file[0])

                            self.window["-Remote DIR LIST-"].update(out)

                    # Switch Remote directory after item has been clicked and is directory
                    elif self.event == "-Remote DIR LIST-":
                        url = self.values["-URL-"]
                        dir = self.values["-Remote DIR LIST-"][0]
                        #todo: fix switching directory if file is clicked
                        if dir.strip('/') == "..":
                            urlNew = re.sub('/[a-zA-z0-9\\-_+#]*$', '', url.strip('/'))
                        else:
                            urlNew = url.strip('/') + '/' + dir

                        if(re.search('\\..{1,6}$',urlNew)):
                            urlNew = url
                        else:
                            self.window["-URL-"].update(urlNew)
                        if self.values["-HTTP User-"] != "":
                            if self.values["-HTTP Pass-"] != "":
                                auth = self.sync.gen_auth(username=self.values["-HTTP User-"], password=self.values["-HTTP Pass-"])
                            else:
                                auth = self.sync.gen_auth(username=self.values["-HTTP User-"])
                        else:
                            auth = False
                        remote = self.sync.get_remote_listing(url_local=urlNew, credentials=auth,
                                                         filetypes=self.values["-FILETYPES-"])
                        out = []
                        if not ".." in remote[1]:
                            out.append("../")
                        for folder in remote[1]:
                            out.append(folder[0] + "/")
                        for file in remote[0]:
                            out.append(file[0])
                        self.window["-Remote Text-"].update(urlNew)
                        self.window["-Remote DIR LIST-"].update(out)
                    # Run sync
                    elif self.event == "-SYNC-":
                        if self.values["-URL-"] != "" and self.values["-FOLDER-"] != "":
                            if self.values["-HTTP User-"] != "":
                                if self.values["-HTTP Pass-"] != "":
                                    auth = self.sync.gen_auth(self.values["-HTTP User-"], self.values["-HTTP Pass-"])
                                else:
                                    auth = self.sync.gen_auth(self.values["-HTTP User-"])
                            else:
                                auth = False
                            count = 0
                            progress_bar.update(current_count=0, max=100)
                            progress.update(visible=True)
                            self.downloading = True
                            thread = threading.Thread(target=self.download_file, daemon=True)
                            thread.start()
                            thread2 = threading.Thread(target=self.sync_r, args=(auth,), daemon=True)
                            thread2.start()

                    elif self.event == 'Next':
                        count = self.values[self.event]
                        progress_bar.update(current_count=count)
                        percent.update(value=f'{count:>3d}%')
                        self.window.refresh()
                        if count == 100 and not self.downloading:
                            sleep(1)
                            progress.update(visible=False)
            except PySimpleGUI.ErrorElement as e:
                print(e)



main = Main()
main.run()

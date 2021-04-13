import os.path
from pprint import pprint
from tkinter import *

import PySimpleGUI as sg

from httpDirectorySync import HttpDirectorySync

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    sync = HttpDirectorySync()
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

    # For now will only show the name of the file that was chosen

    remote_sync_column = [
        [sg.Button("Sync", enable_events=True, key="-SYNC-")],
        [sg.HSeparator()],
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

            sg.VSeperator(),

            sg.Column(remote_sync_column),

        ]

    ]
    # Add Layout to window
    window = sg.Window("HTTP Directory Sync", layout)

    while True:

        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            window.close()
            break
        # Folder name was filled in, make a list of files in the folder
        if event == "-SETTINGS SAVE-":
            authUser = values["-HTTP User-"]
            authPass = values["-HTTP Pass-"]
            url = values["-URL-"]
            folder = values["-FOLDER-"]
            ftypes = values["-FILETYPES-"]
            sg.user_settings_set_entry("authUser", authUser)
            sg.user_settings_set_entry("authPass", authPass)
            sg.user_settings_set_entry("url", url)
            sg.user_settings_set_entry("folder", folder)
            sg.user_settings_set_entry("ftypes", ftypes)
        elif event == "-SETTINGS LOAD-":
            window["-HTTP User-"].update(sg.user_settings_get_entry('authUser'))
            window["-HTTP Pass-"].update(sg.user_settings_get_entry('authPass'))
            window["-URL-"].update(sg.user_settings_get_entry('url'))
            window["-FOLDER-"].update(sg.user_settings_get_entry('folder'))
            window["-FILETYPES-"].update(sg.user_settings_get_entry('ftypes'))
        elif event == "-FOLDER-":

            folder = values["-FOLDER-"]

            try:

                # Get list of files in folder

                file_list = os.listdir(folder)

            except:

                file_list = []
            filePatternArr = values["-FILETYPES-"].split(',')
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

            window["-FILE LIST-"].update(fnames)

        elif event == "-FILE LIST-":  # A file was chosen from the listbox

            try:

                filename = os.path.join(

                    values["-FOLDER-"], values["-FILE LIST-"][0]

                )

                window["-TOUT-"].update(filename)

            except:

                pass
        elif event == "-URL Search-":
            if values["-URL-"] != "":
                window["-Remote Text-"].update(values["-URL-"])
                if values["-HTTP User-"] != "":
                    if values["-HTTP Pass-"] != "":
                        auth = sync.gen_auth(username=values["-HTTP User-"], password=values["-HTTP Pass-"])
                    else:
                        auth = sync.gen_auth(username=values["-HTTP User-"])
                else:
                    auth = False
                remote = sync.get_remote_listing(url_local=values["-URL-"], credentials=auth, filetypes=values["-FILETYPES-"])
                out = []
                if ".." not in remote[1]:
                    out.append("../")
                for folder in remote[1]:
                    out.append(folder[0] + "/")
                for file in remote[0]:
                    out.append(file[0])

                window["-Remote DIR LIST-"].update(out)
        elif event == "-Remote DIR LIST-":
            url = values["-URL-"]
            dir = values["-Remote DIR LIST-"][0]
            if dir.strip('/') == "..":
                urlNew = re.sub('/[a-zA-z0-9\\-_+#]*$', '', url.strip('/'))
            else:
                urlNew = url.strip('/') + '/' + dir
            window["-URL-"].update(urlNew)
            if values["-HTTP User-"] != "":
                if values["-HTTP Pass-"] != "":
                    auth = sync.gen_auth(username=values["-HTTP User-"], password=values["-HTTP Pass-"])
                else:
                    auth = sync.gen_auth(username=values["-HTTP User-"])
            else:
                auth = False
            remote = sync.get_remote_listing(url_local=urlNew, credentials=auth, filetypes=values["-FILETYPES-"])
            out = []
            if not ".." in remote[1]:
                out.append("../")
            for folder in remote[1]:
                out.append(folder[0] + "/")
            for file in remote[0]:
                out.append(file[0])
            window["-Remote Text-"].update(urlNew)
            window["-Remote DIR LIST-"].update(out)
        elif event == "-SYNC-":
            if values["-URL-"] != "" and values["-FOLDER-"] != "":
                if values["-HTTP User-"] != "":
                    if values["-HTTP Pass-"] != "":
                        auth = sync.gen_auth(values["-HTTP User-"], values["-HTTP Pass-"])
                    else:
                        auth = sync.gen_auth(values["-HTTP User-"])
                else:
                    auth = False
                if not sync.sync_recurse(url_local=values["-URL-"], working_dir=values["-FOLDER-"], credentials=auth, filetypes=values["-FILETYPES-"]):
                    pprint("Job finished with errors")
                else:
                    pprint("Sync Successful")

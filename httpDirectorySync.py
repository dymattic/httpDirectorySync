import hashlib
import os
import os.path
from pathlib import Path
from pprint import pprint
import re

import bs4
import requests
from requests.auth import HTTPBasicAuth


class HttpDirectorySync:
    """
    @author: Dmitrij Pastian (dymattic)
    @name: Http Directory Sync
    @description: Python class for recursively syncing HTTP Directories to local directory
    """

    def __init__(self):
        self.download_percent = 0

    def get_percent(self):
        return self.download_percent

    def reset_percent(self):
        self.download_percent = 0
        return True

    def gen_auth(self, username=False, password=False):
        """
        @description: generate auth object to be passed to requests

        :param username: string
        :param password: string
        :return: HTTPBasicAuth Object
        """
        credentials = HTTPBasicAuth(username, password)
        return credentials

    def gen_file_hash(self, filename):
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()

    def downloadFile(self,credentials, remote_name, url_local, working_dir):
        if Path(working_dir + remote_name + '.temp').is_file():
            os.remove(working_dir + remote_name + '.temp')
        path = working_dir + remote_name + '.temp'
        with open(path, "wb") as f:
            print ("Downloading %s" % path)
            response = requests.get(url_local + remote_name, allow_redirects=True, auth=credentials, stream=True)
            total_length = response.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(100 * dl / total_length)
                    self.download_percent = done

    def http_get_data(self, url_local, credentials):
        if re.search('(/|\\\\)$', url_local) is None:
            url_local += "/"

        if not credentials:
            req = requests.get(url_local)
        else:
            req = requests.get(url_local, auth=credentials)
        data = bs4.BeautifulSoup(req.text, "html.parser")
        return data

    def get_remote_listing(self, url_local, credentials=False, recurse=False, filetypes=''):
        if not filetypes:
            file_ending_pattern = re.compile('\\.(pdf|jpeg|zip|java|jar|docx|rar|txt|rtf|tar)$')
        else:
            types = filetypes.split(',')
            type_pattern = ''
            for type in types:
                type_pattern += type + '|'
            type_pattern = type_pattern.strip('|')
            file_ending_pattern = re.compile('\\.(' + type_pattern + ')$')
        folder_link_pattern = re.compile('/$')
        files = []
        folders = []
        for link in self.http_get_data(url_local, credentials).find_all("a"):
            remote_name = link['href'].strip('/')
            if link["href"][0] in ['?', '..', '../', '.', './']:
                continue
            elif folder_link_pattern.search(link['href']) is not None and link['href'] not in url_local:
                if recurse:
                    folders.append(
                        [remote_name, self.get_remote_listing(url_local + remote_name, credentials, filetypes=filetypes)])
                else:
                    folders.append([remote_name, 'Folder'])
            elif file_ending_pattern.search(remote_name) is not None:
                files.append([remote_name, 'File'])
        return files, folders

    def sync_remote(self, url_local, working_dir, files, credentials):
        url_local = url_local.strip('/') + '/'
        working_dir = working_dir.strip('/').strip('\\') + '/'
        for file in files:
            remote_name = file[0]
            pprint("Downloading " + remote_name)
            if Path(working_dir + remote_name).is_file():
                existent_file_hash = self.gen_file_hash(working_dir + remote_name)
                try:
                    self.downloadFile(credentials, remote_name, url_local, working_dir)
                except OSError as e:
                    pprint(e)
                    return False
                new_file_hash = self.gen_file_hash(working_dir + remote_name + '.temp')

                if new_file_hash != existent_file_hash:
                    if Path(working_dir + 'original_' + remote_name).is_file():
                        os.remove(working_dir + 'original_' + remote_name)
                    os.rename(working_dir + remote_name + '.temp', working_dir + 'original_' + remote_name)
                    pprint("File \"" + remote_name + "\" containing changes...")
                    pprint("Saving as \"" + 'original_' + remote_name + "\"")
                else:
                    os.remove(working_dir + remote_name + '.temp')
            else:
                try:
                    self.downloadFile(credentials, remote_name, url_local, working_dir)
                except OSError as e:
                    pprint('Error while trying to create file: ' + working_dir + remote_name)
                    pprint(e)
                    return False
                os.rename(working_dir + remote_name + '.temp', working_dir + 'original_' + remote_name)
        return 'Files Synced'


    def sync_recurse(self, url_local, working_dir, credentials, filetypes=''):
        working_dir = working_dir.strip('/').strip('\\') + "/"
        url_local = url_local.strip('/') + "/"
        remote_data = self.get_remote_listing(url_local, credentials, filetypes=filetypes)
        if not self.sync_remote(url_local, working_dir, remote_data[0], credentials):
            return False

        for folder in remote_data[1]:
            new_url = url_local + folder[0]
            new_working_dir = working_dir + folder[0]
            pprint("Recursing to remote: " + new_url)
            if not os.path.exists(new_working_dir):
                os.makedirs(new_working_dir)
                pprint("Creating New Directory: ")
            pprint("Changing into Directory: " + new_working_dir)
            self.get_remote_listing(new_url, credentials=credentials, filetypes=filetypes)
            if not self.sync_recurse(new_url, new_working_dir, credentials, filetypes):
                return False
        return True

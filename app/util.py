import os
import re
import requests
import configparser

from enum import Enum, auto
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style


# NOTE: since util.py is imported everywhere I'm misusing
# it as a kind of global. see the bottom for some all-app
# variables and initializations. 

def install_path():
    #root path of install
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return path

def check_service(url):
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False
        
def print_welcome_message():
    console.print("\n" + "*" * 56, style=f"{app_color}")
    console.print("prompt-cli -- an Interactive Neural Search and Llama Chat", style=f"{app_color}")
    console.print("Type '/help' for list of available commands.", style=f"{app_color}")
    console.print("" + "*" * 56 + "\n", style=f"{app_color}")

def print_error(e):
    if config('ui','debug',bool):
        console.print(f"--the error shown is: {e}", style=f"{error_color}")
        import traceback
        console.print(f"--Traceback says: ", style=f"bold {error_color}")
        traceback.print_exc()
        console.print("\n")
    console.print("\n")

class ExtendedConfigParser(configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optionxform = str  # Preserve case in options
        self._comment_map = {}
        self._order_map = {}

    def read(self, filenames, encoding=None):
        if isinstance(filenames, str):
            filenames = [filenames]
        
        for filename in filenames:
            with open(filename, 'r', encoding=encoding) as f:
                self._read_file_with_comments(f, filename)
        
        return filenames

    def _read_file_with_comments(self, f, filename):
        self._comment_map[filename] = {}
        self._order_map[filename] = {}
        
        section = None
        comment_buffer = []
        line_number = 0

        content = f.read()
        f.seek(0)

        for line in f:
            line_number += 1
            stripped_line = line.strip()

            if stripped_line.startswith('#'):
                comment_buffer.append(line)
            elif stripped_line.startswith('[') and stripped_line.endswith(']'):
                section = stripped_line[1:-1]
                if section not in self._comment_map[filename]:
                    self._comment_map[filename][section] = {}
                    self._order_map[filename][section] = []
                if comment_buffer:
                    self._comment_map[filename][section]['__section__'] = comment_buffer
                    comment_buffer = []
            elif '=' in stripped_line:
                key, _ = stripped_line.split('=', 1)
                key = key.strip()
                if section:
                    if section not in self._order_map[filename]:
                        self._order_map[filename][section] = []
                    if comment_buffer:
                        self._comment_map[filename][section][key] = comment_buffer
                        comment_buffer = []
                    self._order_map[filename][section].append(key)
            elif not stripped_line:
                if comment_buffer:
                    comment_buffer.append(line)
                else:
                    comment_buffer.append('\n')

        f.seek(0)
        super().read_file(f)

    def merge_with_defaults(self, default_file, user_file):
        self.read(default_file)
        if os.path.exists(user_file):
            self.read(user_file)

        with open(user_file, 'w') as f:
            for section in self._sections:
                if section in self._comment_map[default_file] and '__section__' in self._comment_map[default_file][section]:
                    f.writelines(self._comment_map[default_file][section]['__section__'])
                f.write(f'[{section}]\n')

                for key in self._order_map[default_file][section]:
                    if key in self._comment_map[default_file][section]:
                        f.writelines(self._comment_map[default_file][section][key])
                    value = self[section][key]
                    f.write(f'{key} = {value}\n')

                if section in self._sections and self._sections[section]:
                    f.write('\n')

    def write(self, fileobject, space_around_delimiters=True):
        for section in self._sections:
            fileobject.write(f'[{section}]\n')
            for key in self._order_map.get(fileobject.name, {}).get(section, []):
                if key in self._comment_map.get(fileobject.name, {}).get(section, {}):
                    fileobject.writelines(self._comment_map[fileobject.name][section][key])
                value = self[section][key]
                if space_around_delimiters:
                    fileobject.write(f'{key} = {value}\n')
                else:
                    fileobject.write(f'{key}={value}\n')
            fileobject.write('\n')

def sync_comments_config():
    # this calls the class above to sync the comments in 
    # default.ini with user.ini since consoleparser() clears them
    # on set.
    user_config_path = 'user_config.ini'
    default_config_path = os.path.join('app', 'default.ini')

    config = ExtendedConfigParser()
    config.merge_with_defaults(default_config_path, user_config_path)


def config(section, key, value_type=str):
    # read from both default and user before pulling a value
    default_config_path = os.path.join('app', 'default.ini')
    user_config_path = 'user_config.ini'
    # create a ConfigParser instance
    config_join = configparser.ConfigParser()
    # read both configurations
    config_join.read([default_config_path, user_config_path])

    if value_type == int:
        return config_join.getint(section, key)
    elif value_type == float:
        return config_join.getfloat(section, key)
    elif value_type == bool:
        return config_join.getboolean(section, key)
    else:
        return config_join.get(section, key)

def set_config(section, key, value):
    user_config_path = 'user_config.ini'
    config = configparser.ConfigParser()
    
    # read the existing config file if it exists
    if os.path.exists(user_config_path):
        config.read(user_config_path)
    
    # ensure the section exists
    if section not in config:
        config[section] = {}
    
    # set the new value
    config[section][key] = str(value)
    
    # write the updated config back to the file
    with open(user_config_path, 'w') as configfile:
        config.write(configfile)

    # sync with default to bring back comments
    sync_comments_config()


##############################################
################FAKE GLOBALS##################
##############################################

#initialize rich console
console = Console()
#initialize prompt toolkit
session = PromptSession(history=InMemoryHistory())

# set some colors from config
app_color = config('ui','app_color')
llm_color = config('ui','llm_color')
search_color = config('ui','search_color')
error_color = config('ui','error_color')

# prompt style for prompt_toolkit
prompt_app_color = app_color.replace("_","")
prompt_llm_color = llm_color.replace("_","")
style_search = Style.from_dict({
    'prompt': f'ansi{prompt_app_color} bold',})
style_llm = Style.from_dict({
    'prompt': f'ansi{prompt_llm_color} bold',
})
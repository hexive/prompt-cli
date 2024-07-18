import os
import re
import requests
import configparser

from enum import Enum, auto
from rich.console import Console
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style

#initialize rich console
console = Console()

#initialize prompt toolkit
session = PromptSession(history=InMemoryHistory())

def print_config(config):
    for section in config.sections():
        print(f"[{section}]")
        for key, value in config.items(section):
            print(f"{key} = {value}")
        print()

# Define paths to the configuration files
default_config_path = os.path.join('app', 'default.ini')
user_config_path = 'user_config.ini'

# Create a ConfigParser instance
config_join = configparser.ConfigParser()

# Read both configurations
config_join.read([default_config_path, user_config_path])

#test
#print_config(config_join)

#initialize config settings
#user_config = configparser.ConfigParser()
#user_config.read('user_config.ini')

def config(section, key, value_type=str):
    if value_type == int:
        return config_join.getint(section, key)
    elif value_type == float:
        return config_join.getfloat(section, key)
    elif value_type == bool:
        return config_join.getboolean(section, key)
    else:
        return config_join.get(section, key)

app_color = config('ui','app_color')
llm_color = config('ui','llm_color')
search_color = config('ui','search_color')
error_color = config('ui','error_color')

#prompt style for prompt_toolkit
prompt_app_color = app_color.replace("_","")
prompt_llm_color = llm_color.replace("_","")
style_search = Style.from_dict({
    'prompt': f'ansi{prompt_app_color} bold',})
style_llm = Style.from_dict({
    'prompt': f'ansi{prompt_llm_color} bold',
})

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

def upgrade_config(config):
    default_config = configparser.ConfigParser()
    default_config.read('user_config.default.ini')
    
    for section in default_config.sections():
        if section not in config.sections():
            config[section] = {}
        for key, value in default_config[section].items():
            if key not in config[section]:
                config[section][key] = value
    
    with open('user_config.ini', 'w') as configfile:
        config.write(configfile)

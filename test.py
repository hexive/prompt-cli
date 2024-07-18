import os
import configparser

# Define paths to the configuration files
default_config_path = os.path.join('app', 'default.ini')
user_config_path = 'user_config.ini'

def upgrade_config():
    print(f"Reading default config from: {default_config_path}")
    print(f"User config path: {user_config_path}")

    # Check if default config file exists
    if not os.path.exists(default_config_path):
        print(f"Error: Default config file not found at {default_config_path}")
        return

    # Read the default and user config files
    default_config = configparser.ConfigParser()
    default_config.read(default_config_path)

    user_config = configparser.ConfigParser()
    user_config.read(user_config_path)

    print("Sections in default config:", default_config.sections())
    
    # If default config is empty, try to print its content
    if not default_config.sections():
        print("Default config appears to be empty. Content of the file:")
        try:
            with open(default_config_path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading default config: {e}")

    print("Sections in user config before update:", user_config.sections())

    # ... rest of the function remains the same ...

upgrade_config()
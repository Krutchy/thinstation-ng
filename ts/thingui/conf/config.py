import os
import sys
import yaml

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_main_config(path="thingui_config.yaml"):
    config_filepath = os.path.join(WORKING_DIR, path)

    if not os.path.isfile(config_filepath):
        raise FileNotFoundError(f"Main config file {config_filepath} not found.")
    else:
        with (open(config_filepath, "r")) as data:
            return yaml.safe_load(data)

def _load_packages(main_config_data):
    DEFAULT_CATEGORY = "Misc"

    PACKAGE_DIR = main_config_data.get("PACKAGE_DIR", None)
    if not PACKAGE_DIR: raise AttributeError(f"Main config file has no value for PACKAGE_DIR.")
    else:
        PACKAGE_DIR = os.path.join(WORKING_DIR, PACKAGE_DIR)
    CONFIGURATOR_FILENAME = main_config_data.get("CONFIGURATOR_FILENAME", None)
    if not CONFIGURATOR_FILENAME: raise AttributeError(f"Main config file has no value for CONFIGURATOR_FILENAME.")

    package_data = {}
    for folder in os.listdir(PACKAGE_DIR):
        path = os.path.join(PACKAGE_DIR, folder, CONFIGURATOR_FILENAME)
        if os.path.isfile(path):
            with open(path, "r") as f:
                configurator = yaml.safe_load(f)
                package = configurator.get("package", {})
                if package.get("visible", True):
                    package_data.setdefault(package.get("category", DEFAULT_CATEGORY), []).append(configurator)
    return package_data
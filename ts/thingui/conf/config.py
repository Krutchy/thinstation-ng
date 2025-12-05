import os
import yaml

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

def load_main_config(path="thingui_config.yaml"):
    """Load the main YAML configuration file."""
    config_filepath = os.path.join(WORKING_DIR, path)
    if not os.path.isfile(config_filepath):
        raise FileNotFoundError(f"Main config file {config_filepath} not found.")
    with open(config_filepath, "r") as f:
        return yaml.safe_load(f)

def load_packages(main_config_data):
    """
    Load all package configurators from PACKAGE_DIR, categorized by their 'category' field.
    Packages with 'visible: False' are skipped.
    """
    DEFAULT_CATEGORY = "Misc"

    package_dir = main_config_data.get("PACKAGE_DIR")
    if not package_dir:
        raise AttributeError("Main config file has no value for PACKAGE_DIR.")
    package_dir = os.path.join(WORKING_DIR, package_dir)

    configurator_filename = main_config_data.get("CONFIGURATOR_FILENAME")
    if not configurator_filename:
        raise AttributeError("Main config file has no value for CONFIGURATOR_FILENAME.")

    packages = {}
    for folder in os.listdir(package_dir):
        path = os.path.join(package_dir, folder, configurator_filename)
        if not os.path.isfile(path):
            continue

        with open(path, "r") as f:
            configurator = yaml.safe_load(f)
            package = configurator.get("package", {})
            if package.get("visible", True):
                category = package.get("category", DEFAULT_CATEGORY)
                packages.setdefault(category, []).append(configurator)

    return packages
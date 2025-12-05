import os
import yaml

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

def load_main_config(path):
    """Load a YAML configuration file for general config options."""
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
    DEFAULT_CATEGORY = main_config_data.get("DEFAULT_CATEGORY", "Misc")

    GENERAL_SESSION_FILEPATH = main_config_data.get("SESSION_CONFIGURATOR_FILEPATH", None)
    if GENERAL_SESSION_FILEPATH:
        path = os.path.join(WORKING_DIR, GENERAL_SESSION_FILEPATH)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Session config file {path} not found.")
        with open(path, "r") as f:
            general_session_options = yaml.safe_load(f).get("variables", [])

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
            if not package.get("visible", True):
                continue

            package_variables = configurator.get("variables", [])
            # Merge in general session variables if package uses sessions
            if package.get("has-sessions", False):
                package_names = {v.get("name") for v in package_variables}
                filtered_shared = [
                    v for v in general_session_options
                    if v.get("name") not in package_names
                ]
                package_variables = package_variables + filtered_shared

            configurator["variables"] = package_variables

            category = package.get("category", DEFAULT_CATEGORY)
            packages.setdefault(category, []).append(configurator)

    return packages
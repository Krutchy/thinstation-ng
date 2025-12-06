import os
import yaml

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

def load_yaml_file(path):
    """Load a YAML file from the working directory."""
    filepath = os.path.join(WORKING_DIR, path)
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r") as f:
        return yaml.safe_load(f)

def merge_session_options(package, options, general_session_options):
    """Merge package-specific session options with general session options."""
    global_options = [o for o in options if "SESSION" not in o.get("name", "").upper()]
    session_options = [o for o in options if "SESSION" in o.get("name", "").upper()]

    session_option_names = {o.get("name") for o in session_options}
    filtered_general = []

    for opt in general_session_options:
        name = opt.get("name")
        if isinstance(name, str) and "type" in name:
            opt["name"] = name.replace("type", package.get("name", "").upper())
        if name not in session_option_names:
            filtered_general.append(opt)

    return global_options, session_options + filtered_general


def load_packages(package_dir, configurator_filename, session_configurator_filepath, default_category):
    """Load all package configurators from the given package directory."""
    packages = {}

    package_dir_path = os.path.join(WORKING_DIR, package_dir)
    if not os.path.exists(package_dir_path):
        raise FileNotFoundError(f"No package directory found at {package_dir_path}")

    general_session_options = []
    if os.path.isfile(os.path.join(WORKING_DIR, session_configurator_filepath)):
        session_config = load_yaml_file(session_configurator_filepath)
        general_session_options = session_config.get("options", [])

    for folder in os.listdir(package_dir_path):
        config_path = os.path.join(package_dir_path, folder, configurator_filename)
        if not os.path.isfile(config_path):
            continue

        configurator = load_yaml_file(os.path.join(package_dir_path, folder, configurator_filename))
        package = configurator.get("package", {})

        if not package.get("visible", True):
            continue

        options = configurator.get("options", [])
        if package.get("has-sessions", False):
            options, session_options = merge_session_options(package, options, general_session_options)
            configurator["options"] = options
            configurator["session_options"] = session_options

        category = package.get("category", default_category)
        packages.setdefault(category, []).append(configurator)

    return packages

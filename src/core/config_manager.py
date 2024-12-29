from pathlib import Path
from typing import Optional, Iterator, List
from yaml import safe_load
import yaml


class ConfigManager:
    """
    A class to manage and validate YAML-based configuration for processing tags and properties.

    Attributes:
        _path (Path): The path to the YAML file.
        _yaml (dict): The loaded YAML content.
    """

    def __init__(self, yaml_path: Path):
        """
        Initialize the Config class.

        Args:
            yaml_path (Path): The path to the YAML configuration file.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
            yaml.YAMLError: If there is an error reading the YAML file.
        """
        self._path = yaml_path
        self._yaml = self._load_yaml(yaml_path)

    def get_next_tag(self) -> Iterator[tuple[Optional[str], Optional[list[dict]]]]:
        """
        Retrieve the next valid tag and its properties from the YAML configuration.

        Yields:
            tuple[Optional[str], Optional[list[dict]]]: The tag name and its properties.
        """
        if self._yaml.get("tags") is None:
            self._print_error("No tags found.")
            yield None, None

        for tag in self._yaml.get("tags", []):
            if self._validate_tag(tag):
                yield tag.get("tag"), self._validate_properties(tag)

    def _validate_tag(self, tag: dict) -> bool:
        """
        Validate the structure of a tag.

        Args:
            tag (dict): The tag to validate.

        Returns:
            bool: True if the tag is valid, False otherwise.
        """
        if not tag.get("tag"):
            self._print_error("No tag found.")
            return False

        if not isinstance(tag.get("properties"), list):
            self._print_error(f"Properties for tag {tag} must be a list.")
            return False

        if not all(isinstance(prop, dict) for prop in tag.get("properties")):
            self._print_error(f"Properties for tag {tag} must be a list of dictionaries.")
            return False

        return True

    def _validate_properties(self, tag: dict) -> list[dict]:
        """
        Validate the properties of a given tag.

        Args:
            tag (dict): A tag containing properties to validate.

        Returns:
            list[dict]: A list of valid properties.
        """
        properties: List[dict] = []
        for prop in tag.get("properties", []):
            action = prop.get("action")
            tag_name = tag.get("tag")
            if not action:
                self._print_error(f"No action defined for properties in tag: {tag_name}.")
                continue

            if action in ["rename", "remove"] and not prop.get("old"):
                self._print_error(f"Old property for action: {action} in tag: {tag_name} not found.")
                continue

            if action in ["rename", "add"] and not prop.get("new"):
                self._print_error(f"New property for action: {action} in tag: {tag_name} not found.")
                continue

            if prop.get("new") == prop.get("old"):
                self._print_warning(f"Old and new properties are the same for action: {action} in tag: {tag_name}.")
                continue

            properties.append(prop)

        return properties

    def _load_yaml(self, path: Path) -> dict:
        """
        Load the YAML file from the given path.

        Args:
            path (Path): The path to the YAML file.

        Returns:
            dict: The loaded YAML content.

        Raises:
            FileNotFoundError: If the file is not found.
            yaml.YAMLError: If there is an error parsing the YAML file.
            Exception: For any other errors during file reading.
        """
        try:
            with open(path, "r") as file:
                return safe_load(file)
        except FileNotFoundError:
            self._print_error(f"The file {path} was not found.")
            exit(-1)
        except yaml.YAMLError:
            self._print_error(f"The file {path} could not be read.")
            exit(-1)
        except Exception as e:
            self._print_error(f"An error occurred: {e}")
            exit(-1)

    @staticmethod
    def _print_error(msg):
        """
        Print an error message to the console.

        Args:
            msg (str): The error message to print.
        """
        print(f"[ERROR] - {msg}")

    @staticmethod
    def _print_warning(msg):
        """
        Print a warning message to the console.

        Args:
            msg (str): The warning message to print.
        """
        print(f"[WARNING] - {msg}")

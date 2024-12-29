import yaml


class PropertyChangeTracker:
    """
    A class to track changes and logs for YAML metadata (frontmatter) in files.

    Attributes:
        _filename (str): The name of the file being modified.
        _old_frontmatter (dict): The original YAML metadata before changes.
        _new_frontmatter (dict): The updated YAML metadata after changes.
        _changes (list): A list of changes, with each change represented as a dictionary.
        _logs (list): A list of log messages for problems or annotations.
    """

    def __init__(self, filename: str, old_frontmatter: dict, new_frontmatter: dict):
        """
        Initialize a PropertyChange instance.

        Args:
            filename (str): The name of the file being modified.
            old_frontmatter (dict): The original YAML metadata before changes.
            new_frontmatter (dict): The updated YAML metadata after changes.
        """
        self._filename = filename
        self._old_frontmatter = old_frontmatter
        self._new_frontmatter = new_frontmatter
        self._changes = []
        self._logs = []

    @property
    def filename(self) -> str:
        """
        Get the filename.

        Returns:
            str: The name of the file.
        """
        return self._filename

    @filename.setter
    def filename(self, value: str) -> None:
        """
        Set the filename.

        Args:
            value (str): The name of the file.

        Raises:
            ValueError: If the value is not a string.
        """
        if not isinstance(value, str):
            raise ValueError("Filename must be a string.")
        self._filename = value

    @property
    def old_frontmatter(self) -> dict:
        """
        Get the original frontmatter.

        Returns:
            dict: The original YAML metadata.
        """
        return self._old_frontmatter

    @old_frontmatter.setter
    def old_frontmatter(self, value: dict) -> None:
        """
        Set the original frontmatter.

        Args:
            value (dict): The original YAML metadata.

        Raises:
            ValueError: If the value is not a dictionary.
        """
        if not isinstance(value, dict):
            raise ValueError("Old frontmatter must be a dictionary.")
        self._old_frontmatter = value

    @property
    def new_frontmatter(self) -> dict:
        """
        Get the updated frontmatter.

        Returns:
            dict: The updated YAML metadata.
        """
        return self._new_frontmatter

    @new_frontmatter.setter
    def new_frontmatter(self, value: dict) -> None:
        """
        Set the updated frontmatter.

        Args:
            value (dict): The updated YAML metadata.

        Raises:
            ValueError: If the value is not a dictionary.
        """
        if not isinstance(value, dict):
            raise ValueError("New frontmatter must be a dictionary.")
        self._new_frontmatter = value

    def add_change(self, action, old_property=None, new_property=None, old_value=None, new_value=None) -> None:
        """
        Add a single change to the change tracker.

        Args:
            action (str): The type of action (e.g., "add", "remove", "rename").
            old_property (str, optional): The property name before the change.
            new_property (str, optional): The property name after the change.
            old_value (any, optional): The value of the property before the change.
            new_value (any, optional): The value of the property after the change.
        """
        change = {
            "action": action,
            "old_property": old_property,
            "new_property": new_property,
            "old_value": old_value,
            "new_value": new_value,
        }
        self._changes.append(change)

    def add_log(self, message) -> None:
        """
        Add a log entry to the log tracker.

        Args:
            message (str): The log message to add.
        """
        self._logs.append(message)

    def show_summary(self) -> None:
        """
        Display a summary of changes and logs in a structured format.
        """
        print("=" * 40)
        print(f"Summary for File: {self._filename}")
        print("=" * 40)

        # Old Frontmatter
        if self._old_frontmatter:
            print("\n[Old Frontmatter]")
            print(yaml.dump(self._old_frontmatter, default_flow_style=False, allow_unicode=True))
        else:
            print("\n[Old Frontmatter] None")

        # New Frontmatter
        if self._new_frontmatter:
            print("\n[New Frontmatter]")
            print(yaml.dump(self._new_frontmatter, default_flow_style=False, allow_unicode=True))
        else:
            print("\n[New Frontmatter] None")

        # Changes
        if self._changes:
            print("\n[Changes]")
            for change in self._changes:
                print(f"Action: {change.get('action')}")
                if change.get('old_property'):
                    print(f"  Old Property: {change.get('old_property')}")
                if change.get('new_property'):
                    print(f"  New Property: {change.get('new_property')}")
                if change.get('old_value') is not None:
                    print(f"  Old Value: {change.get('old_value')}")
                if change.get('new_value') is not None:
                    print(f"  New Value: {change.get('new_value')}")
                print("-" * 20)

        # Logs
        if self._logs:
            print("\n[Logs]")
            for log in self._logs:
                print(f" - {log}")

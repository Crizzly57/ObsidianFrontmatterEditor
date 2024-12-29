import shutil
from copy import deepcopy
from pathlib import Path
from typing import Union, Optional, List

from src.library.note import Notes, Note
from src.library.metadata import MetadataType

from src.core.config_manager import ConfigManager
from src.core.property_change_tracker import PropertyChangeTracker


class PropertyProcessor:
    """
    A class for renaming, adding, or removing YAML properties in a collection of notes.

    Attributes:
        _notes (Notes): The collection of notes to be processed.
        _config (ConfigManager): The configuration object for parsing the YAML file.
        _current_note (Optional[Note]): The note currently being processed.
        _all_changes (List[tuple[Path, List[PropertyChangeTracker]]]): A record of all changes made to the notes.
        _change_tracker (PropertyChangeTracker): Tracks changes for the currently processed note.
    """

    def __init__(self, vault_path: Path, yaml_path: Path):
        """
        Initialize the PropertyRenamer.

        Args:
            vault_path (Path): Path to the notes vault.
            yaml_path (Path): Path to the YAML configuration file.
        """
        self._vault_path = vault_path
        self._notes = Notes(vault_path)
        self._config = ConfigManager(yaml_path)
        self._current_note: Optional[Note] = None
        self._all_changes: List[PropertyChangeTracker] = []
        self._change_tracker: PropertyChangeTracker = PropertyChangeTracker("", {}, {})

    def run(self) -> None:
        """
        Execute the renaming, adding, and removing of properties based on the YAML configuration.
        """
        for tag, properties in self._config.get_next_tag():
            if not tag or not properties:
                continue

            notes = self._get_filtered_notes([("tags", tag, None)])
            if not notes:
                continue

            for note in notes.notes:
                self._current_note = note
                self._change_tracker = PropertyChangeTracker(str(note.path), {}, {})
                self._change_tracker.old_frontmatter = deepcopy(note.metadata.frontmatter.metadata)

                self._process_properties(properties)

                self._change_tracker.new_frontmatter = deepcopy(self._current_note.metadata.frontmatter.metadata)
                self._all_changes.append(self._change_tracker)

        self._finish()

    def _finish(self) -> None:
        """
        Finalize the processing by showing a summary of changes and updating the notes.
        Allows the user to cancel the operation with Ctrl+C.
        """
        for change in self._all_changes:
            change.show_summary()

        try:
            input("Press Enter to continue...")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return

        self._backup_vault()
        self._notes.update_content()
        self._notes.write()

        print("Changes saved successfully.")

    def _rename_property(self, old_property: str, new_property: str) -> None:
        """
        Rename a property in the current note's metadata.

        Args:
            old_property (str): The current property name to be renamed.
            new_property (str): The new name for the property.
        """
        if self._current_note.metadata.has(old_property):
            value = self._current_note.metadata.get(old_property)
            self._current_note.metadata.add(new_property, value, MetadataType.FRONTMATTER)
            self._current_note.metadata.remove(old_property)

            self._change_tracker.add_change(
                action="rename",
                old_property=old_property,
                new_property=new_property,
                old_value=value,
                new_value=value
            )
        else:
            self._change_tracker.add_log(f"Property '{old_property}' not found.")

    def _add_property(self, prop: str, value: str = "") -> None:
        """
        Add a property to the current note's metadata.

        Args:
            prop (str): The property name to add.
            value (str, optional): The value for the new property. Defaults to an empty string.
        """
        if not self._current_note.metadata.has(prop):
            self._current_note.metadata.add(prop, value, MetadataType.FRONTMATTER)

            self._change_tracker.add_change(
                action="add",
                new_property=prop,
                new_value=value
            )
        else:
            self._change_tracker.add_log(f"Property '{prop}' already exists.")

    def _remove_property(self, prop: str) -> None:
        """
        Remove a property from the current note's metadata.

        Args:
            prop (str): The property name to remove.
        """
        if self._current_note.metadata.has(prop):
            self._current_note.metadata.remove(prop)

            self._change_tracker.add_change(
                action="remove",
                old_property=prop
            )
        else:
            self._change_tracker.add_log(f"Property '{prop}' not found.")

    def _get_filtered_notes(
            self,
            meta_data: list[tuple[str, Union[list[str], str, None], Optional[MetadataType]]]
    ) -> Optional[Notes]:
        """
        Filter notes based on metadata.

        Args:
            meta_data (list): A list of metadata filters.

        Returns:
            Notes: A filtered collection of notes.
        """
        notes = self._notes
        notes.filter(has_meta=meta_data)
        return notes

    def _process_properties(self, properties: list[dict]) -> None:
        """
        Process a list of property changes for the current note.

        Args:
            properties (list): A list of property change configurations.
        """
        for prop in properties:
            action = prop.get("action")
            if action == "add":
                self._add_property(prop.get("new"), prop.get("default"))
            elif action == "rename":
                self._rename_property(prop.get("old"), prop.get("new"))
            elif action == "remove":
                self._remove_property(prop.get("old"))

    def _backup_vault(self) -> None:
        """
        Create a backup of the vault before making changes.
        """
        try:
            vault_backup_path = self._vault_path.parent / f"{self._vault_path.name}_backup.zip"
            shutil.make_archive(str(vault_backup_path).replace('.zip', ''), 'zip', self._vault_path)
            print(f"Backup created at {vault_backup_path}")
        except Exception as e:
            print(f"An error occurred while creating a backup: {e}")
            exit(-1)

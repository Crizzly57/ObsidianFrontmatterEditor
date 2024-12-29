from pathlib import Path
from core.property_processor import PropertyProcessor


def start() -> None:
    """
    Continuously prompts the user for a directory and configuration file path until valid inputs are provided.
    Once valid inputs are received, it initializes and runs the PropertyProcessor.
    """
    while True:
        directory_path = Path(input("Enter the path to the directory: "))
        if not directory_path.is_dir():
            print("The provided path to the directory is not valid. Please try again.")
            continue

        config_file_path = Path(input("Enter the path to the configuration file: "))
        if not config_file_path.is_file():
            print("The provided path to the configuration file is not valid. Please try again.")
            continue

        property_processor = PropertyProcessor(directory_path, config_file_path)
        property_processor.run()
        break


if __name__ == "__main__":
    start()

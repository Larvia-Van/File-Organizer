import argparse
import shutil
from pathlib import Path

#-----------------
# Viết code cho phép chạy nhiều option cùng lúc theo dạng: --option values --option values <=> -xy value (xy cùng nhận một value).
# Di dời class FileOrganizer thành một chức năng riêng thay vì để trong cli.py.
#------------------


class PathNotFound(Exception):
    pass



class FileOrganizer:
    def __init__(self, source_dirs=Path(""), target_dir=Path("")):

        self.paths = {
            "source_dirs": source_dirs,
            "target_dir": target_dir
        }
        
        self.pattern_extensions = {
            "text": (
                ".txt", ".log", ".md", ".markdown", ".rtf"
            ),

            "documents": (
                ".doc", ".docx", ".pdf", ".xps", ".oxps",
                ".djvu", ".epub", ".mobi", ".azw", ".azw3"
            ),

            "images": (
                ".jpg", ".jpeg", ".png", ".gif", ".webp",
                ".svg", ".tiff", ".tif", ".paint"
            ),

            "audio": (
                ".mp3", ".wav", ".m4a", ".flac", ".aac",
                ".wma", ".ogg", ".aiff", ".opus", ".mid"
            ),

            "applications": (
                ".exe", ".msi", ".app", ".apk", ".deb",
                ".rpm", ".dmg", ".pkg", ".jar", ".bat",
                ".cmd", ".com", ".scr"
            ),

            "videos": (
                ".mp4", ".avi", ".mkv", ".mov", ".wmv",
                    ".flv", ".webm", ".m4v", ".mpeg", ".mpg"
            ),

            "archives": (
                ".zip", ".rar", ".7z", ".tar", ".gz",
                ".bz2", ".xz", ".iso"
            ),
        }
        
        self._validate_paths()


    def get_file_extension(self):
        file_extensions = []

        for item in self.paths["target_dir"].iterdir():

            if item.is_file():
                file_extensions.append(item.suffix.lower())
            
        return set(file_extensions)


    def create_dirs(self, *args):
        target_dir = self.paths["target_dir"]
        created_dir_paths = []

        if not args:
            extensions = self.get_file_extension() 
        else:
            extensions = set(args)

        for key in self.pattern_extensions:
            matched_extensions = extensions.intersection(self.pattern_extensions[key])
   
            if matched_extensions:
                destination = target_dir / key.capitalize()
                destination.mkdir(
                    parents=True,
                    exist_ok=True
                    )

                extensions = extensions.difference(matched_extensions)
                created_dir_paths.append(destination)


        for extension in extensions:
            destination = target_dir / extension.upper()
            destination.mkdir(
                parents=True,
                exist_ok=True
                )
            
            created_dir_paths.append(destination)

        return {
            "paths": set(created_dir_paths),
            "exception_keys": extensions
            }


    def sort_files(self):
        target_dir = self.paths["target_dir"]
        created_dir = self.create_dirs()

        exception_keys = created_dir["exception_keys"]
        dir_paths = {path.name: path for path in created_dir["paths"]}


        for item in target_dir.iterdir():

            if item.suffix.lower() in exception_keys:
                shutil.move(
                    item,
                    dir_paths[item.suffix.upper()]
                )

            for key in self.pattern_extensions:
                if (
                    item.is_file()
                    and item.suffix.lower() in self.pattern_extensions[key]
                ):
                        shutil.move(
                            item,
                            dir_paths[key.capitalize()]
                        )

                        break
  
 
    def move_files(self, *args):
        source_dirs = self.paths["source_dirs"]
        target_dir = self.paths["target_dir"]
        
        if not args:
            extensions = set()
        else:
            extensions = set(args)

        for path in source_dirs:

            for item in path.iterdir():

                if not extensions:
                    if item.is_file():

                        shutil.move(
                            item,
                            target_dir
                        )   

                else:
                        if (
                            item.is_file()
                            and item.suffix in extensions
                        ):

                            shutil.move(
                                item,
                                target_dir
                            )


    def delete_files(self, *args):
        target_dir = self.paths["target_dir"]

        if not args:
            extensions = set()
        else:
            extensions = set(args)

        for item in target_dir.iterdir():
            if not extensions:
                if item.is_file():
                    item.unlink(missing_ok=True)

            else:
                if (
                    item.is_file
                    and item.suffix in extensions
                ):
                    item.unlink(missing_ok=True)


    def _validate_paths(self):

        for paths in self.paths.values():
            for path in [paths]:  

                if (
                    not path.exists()
                    or not path.is_dir()
                ):
                    raise PathNotFound(
                        f"Path not found or not a directory: {path}"
                    )


class BlankLineFormatter(argparse.HelpFormatter):
    def format_help(self):
        help_text = super().format_help()

        lines = help_text.splitlines()

        result = []

        for line in lines:
            if line.startswith("  -") and result:
                result.append("")

            result.append(line)

        return "\n".join(result)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Perform operations on files based on their extensions.",
        formatter_class=BlankLineFormatter
    )

#organize

    organize = parser.add_argument(  # noqa: F841
        "-o",
        "--organize",
        dest="organize",
        metavar="",
        nargs=1,  
        help="organize and group files into subfolders by file extension"
    )

#extension

    extensions = parser.add_argument(  # noqa: F841
        "-e",
        "--extension",
        dest="extensions",
        metavar="",
        nargs=1,
        help="list all file extensions in the folder"
    ) 

#create 

    create_dirs = parser.add_argument( # noqa: F841
        "-c",
        "--create",
        dest="create_dirs",
        metavar="",
        nargs="+",
        help="create folders by specified or auto-scanned file extensions."

    )

#move 

    move_files = parser.add_argument( # noqa: F841
        "-m",
        "--move",
        dest="move_files",
        metavar="",
        nargs="+",
        help="move files from source to destination by file extension."
    )

#delete

    delete_files = parser.add_argument( # noqa: F841
        "-d",
        "--delete",
        dest="delete_files",
        metavar="",
        nargs="+",
        help="delete files by specified extensions or all files in target directory."
    )


    return parser

def is_extension(value: str) -> bool:
    return value.startswith(".") and len(value) > 1 and "/" not in value and "\\" not in value


def classify_inputs(inputs: list[str]) -> dict:
    extensions = []
    paths = []

    for item in inputs:
        if is_extension(item):
            extensions.append(item)
        else:
            paths.append(Path(item))

    if not paths:
        raise ValueError("Target directory is required.")

    return {
        "extensions": extensions,
        "source_paths": paths[:-1] or [Path("")],
        "target_path": paths[-1],
    }


def main():
    parser = build_parser()
    args = parser.parse_args()
    
    for option,user_inputs in vars(args).items():
        if user_inputs is not None:

            user_inputs = classify_inputs(user_inputs)

            extensions = user_inputs["extensions"]
            source_paths = user_inputs["source_paths"]
            target_path = user_inputs["target_path"]

            organizer = FileOrganizer(source_dirs=source_paths, target_dir=target_path)

            if option == "organize":
                organizer.sort_files()

            if option == "extensions":
                organizer.get_file_extension()

            if option == "create_dirs":
                organizer.create_dirs(extensions)

            if option == "move_files":
                organizer.move_files(extensions)

            if option == "delete_files":
                organizer.delete_files(extensions)

if __name__ == "__main__":
    main()


     






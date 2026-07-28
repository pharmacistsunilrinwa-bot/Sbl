import os
import shutil
from typing import List

class FileManagerService:
    def __init__(self, base_dir: str = "user_data"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def list_files(self, sub_dir: str = "") -> List[str]:
        target_dir = os.path.join(self.base_dir, sub_dir)
        # Security check: Ensure we stay within base_dir
        if not os.path.abspath(target_dir).startswith(os.path.abspath(self.base_dir)):
            raise PermissionError("Access denied: Outside of user directory.")
        return os.listdir(target_dir)

    def create_directory(self, dir_name: str):
        path = os.path.join(self.base_dir, dir_name)
        os.makedirs(path, exist_ok=True)
        return f"Directory {dir_name} created."

    def delete_file(self, file_name: str):
        path = os.path.join(self.base_dir, file_name)
        if os.path.isfile(path):
            os.remove(path)
            return f"File {file_name} deleted."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Directory {file_name} deleted."
        return "File not found."

    def move_file(self, src: str, dst: str):
        shutil.move(os.path.join(self.base_dir, src), os.path.join(self.base_dir, dst))
        return f"Moved {src} to {dst}."

file_manager_service = FileManagerService()

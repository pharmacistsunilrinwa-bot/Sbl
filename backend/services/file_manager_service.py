import os
import shutil
from typing import List

class FileManagerService:
    def __init__(self, base_dir: str = "user_data"):
        self.base_dir = os.path.abspath(base_dir)
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _safe_path(self, path: str) -> str:
        # Join and resolve the absolute path
        # If path starts with /, os.path.join handles it correctly by starting from it
        # so we need to be careful. We strip leading slashes.
        safe_name = path.lstrip("/").lstrip("\\")
        target_path = os.path.abspath(os.path.join(self.base_dir, safe_name))
        
        if not target_path.startswith(self.base_dir):
            raise PermissionError("Access denied: Outside of user directory.")
        return target_path

    def list_files(self, sub_dir: str = "") -> List[str]:
        target_dir = self._safe_path(sub_dir)
        if not os.path.isdir(target_dir):
            return []
        return os.listdir(target_dir)

    def create_directory(self, dir_name: str):
        path = self._safe_path(dir_name)
        os.makedirs(path, exist_ok=True)
        return f"Directory {dir_name} created."

    def delete_file(self, file_name: str):
        path = self._safe_path(file_name)
        if os.path.isfile(path):
            os.remove(path)
            return f"File {file_name} deleted."
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return f"Directory {file_name} deleted."
        return "File not found."

    def move_file(self, src: str, dst: str):
        src_path = self._safe_path(src)
        dst_path = self._safe_path(dst)
        shutil.move(src_path, dst_path)
        return f"Moved {src} to {dst}."

file_manager_service = FileManagerService()

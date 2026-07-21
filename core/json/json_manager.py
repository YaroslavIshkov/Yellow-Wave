import json
from pathlib import Path


class JsonManager:
    def __init__(self):
        self.config_path = Path(__file__).parents[1] / "config"
        self.file_path = self.config_path / "arguments.json"
    
    def create_file(self, data: dict):
        try:
            if not self.config_path.exists():
                self.config_path.mkdir(parents=True)
            if not self.file_path.exists():
                with open(str(self.file_path), "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            print(e)
    
    def load_file(self) -> dict:
        try:
            with open(str(self.file_path), "r", encoding="utf-8") as f:
                return json.loads(f.read())
        except Exception as e:
            print(e)
    
    def save_file(self, data: dict):
        try:
            with open(str(self.file_path), "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(e)

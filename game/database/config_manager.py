from kivy.storage.jsonstore import JsonStore


class ConfigManager:
    """Manages application configuration using JsonStore"""

    def __init__(self, score_file="configs.json"):
        self._store = JsonStore(score_file, sort_keys=True)

    def exists(self, key):
        return self._store.exists(key)

    def delete(self, key):
        self._store.delete(key)

    def set(self, key, values):
        if isinstance(values, dict):
            self._store.put(key, **values)
        else:
            # Wrap single values in dictionary format
            data = {f"{key}_value": values}
            self._store.put(key, **data)

    def get(self, key):
        if self.exists(key):
            data = self._store.get(key)
            # Unwrap single values
            if f"{key}_value" in data:
                return data[f"{key}_value"]
            return data

        return None

    def get_all(self):
        return self._store
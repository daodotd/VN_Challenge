from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore


class ScoreManager:
    """Manages game scores and elapsed times"""
    def __init__(self, score_file="score.json"):
        self._store = JsonStore(score_file, sort_keys=True)

    def get_score(self, category, key):
        if self._store.exists(category):
            category_data = self._store.get(category)
            if key in category_data:
                return category_data[key]
        return None

    def save_score(self, category, key, score, elapsed_time):
        """Save score and update best score"""
        category_data = (
            self._store.get(category) if self._store.exists(category) else {}
        )

        # Initialize data structure for new key
        if key not in category_data:
            category_data[key] = {"last_score": {}, "best_score": {}}

        # Save current game score
        category_data[key]["last_score"] = {
            "score": score,
            "elapsed_time": elapsed_time,
            "timestamp": Clock.get_time(),
        }

        # Check and update best score
        best_score_data = category_data[key].get(
            "best_score", {"score": 0, "elapsed_time": float("inf")}
        )
        best_score = best_score_data.get("score", 0)
        best_time = best_score_data.get("elapsed_time", float("inf"))

        # Update if higher score or same score with better time
        if score > best_score or (score == best_score and elapsed_time < best_time):
            category_data[key]["best_score"] = {
                "score": score,
                "elapsed_time": elapsed_time,
                "timestamp": Clock.get_time(),
            }

        self._store.put(category, **category_data)
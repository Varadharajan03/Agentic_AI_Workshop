# validator.py
from typing import Any, Dict

class ResponseValidator:
    def validate_notification(self, data: Dict[str, Any]) -> bool:
        return all(k in data for k in ("student_id","status","message"))

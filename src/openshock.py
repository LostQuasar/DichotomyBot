from enum import Enum
import requests

class ControlType(Enum):
    VIBRATE = "Vibrate"
    SHOCK = "Shock"
    SOUND = "Sound"

class shock_api:
    def __init__(self, api_key, url: str = "https://api.shocklink.net/"):
        self.url = url
        self.headers = {
            "Content-type": "application/json",
            "accept": "application/json",
            "OpenShockToken": api_key,
        }
    
    def create_shocker(self, shocker_id):
        return self.shocker(self, shocker_id)

    class shocker:

        def __init__(self, parent, shocker_id: str):
            self.parent = parent
            self.shocker_id = shocker_id

        def control(self, type: ControlType, intensity: int, duration: int, author: str):
            return requests.post(
                self.parent.url + "2/shockers/control",
                json={
                    "shocks": [
                        {
                            "id": self.shocker_id,
                            "type": type.value,
                            "intensity": intensity,
                            "duration": duration,
                            "exclusive": True,
                        }
                    ],
                    "customName": author,
                },
                headers=self.parent.headers,
            )

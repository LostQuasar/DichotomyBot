from enum import Enum
import requests


class ControlType(Enum):
    VIBRATE = "Vibrate"
    SHOCK = "Shock"
    SOUND = "Sound"


class openshock_api:

    class shocker:
        def __init__(self, parent, shocker_id: str):
            self.parent = parent
            self.shocker_id = shocker_id

        async def control(
            self,
            type: ControlType,
            intensity: int,
            duration: int,
            author: str,
            exclusive: bool = True,
        ):
            """Send a control signal to the shocker

            Args:
                type (ControlType) Shock, Vibrate or Sound
                intensity (int): 1 - 100 percentage
                duration (int): 300 - 30 000 measured in ms
                author (str): Name to appear on the log

            Returns:
                Response: status of the post request
            """
            return requests.post(
                self.parent.url + "2/shockers/control",
                json={
                    "shocks": [
                        {
                            "id": self.shocker_id,
                            "type": type.value,
                            "intensity": intensity,
                            "duration": duration,
                            "exclusive": exclusive,
                        }
                    ],
                    "customName": author,
                },
                headers=self.parent.headers,
            )

    connected_shockers: list[shocker]

    def __init__(self, api_key, url: str = "https://api.shocklink.net/"):
        self.url = url
        self.headers = {
            "Content-type": "application/json",
            "accept": "application/json",
            "OpenShockToken": api_key,
        }
        self.connected_shockers = []

    def create_shocker(self, shocker_id):
        new_shocker = self.shocker(self, shocker_id)
        self.connected_shockers.append(new_shocker)
        return new_shocker

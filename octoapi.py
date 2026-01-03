from datetime import datetime, timedelta, timezone
import requests
import logging


class OctoApi:
    def __init__(self, api_key):
        self.api_root = "https://api.octopus.energy/v1"
        self.api_key = api_key
        self.auth = (api_key, "")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, url, params={}):
        print(params)
        response = requests.request(
            "GET",
            f"{self.api_root}/{url}",
            headers=self.headers,
            params=params,
            auth=self.auth,
        )
        return response.json()

    def to_z_time(self, t):
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def getConsumption(self, mpan, serial_number, day=-1):
        now_utc = datetime.now(timezone.utc)
        start_day = now_utc + timedelta(days=day)
        end_day = now_utc + timedelta(days=day + 1)
        period_from = start_day.replace(hour=0, minute=0, second=0, microsecond=0)
        period_to = end_day.replace(hour=0, minute=0, second=0, microsecond=0)
        params = {
            "period_from": self.to_z_time(period_from),
            "period_to": self.to_z_time(period_to),
            "order_by": "period",
        }
        url = f"electricity-meter-points/{mpan}/meters/{serial_number}/consumption/"
        return self._get(url, params)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api = OctoApi(os.getenv("OCTOPUS_API_KEY"))

    print(
        api.getConsumption(
            os.getenv("OCTOPUS_MPAN"), os.getenv("OCTOPUS_SERIAL_NUMBER"), day=-2
        )
    )

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GivEnergyApi:
    def __init__(self, api_key, inverter_serial_number):
        self.settings = None
        self.url_root = "https://api.givenergy.cloud/v1"
        self.api_key = api_key
        self.inverter_serial_number = inverter_serial_number
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _get(self, url, params={}):
        response = requests.request(
            "GET", f"{self.url_root}/{url}", headers=self.headers, params=params
        )
        return response.json()

    def _post(self, url, payload={}):
        response = requests.request(
            "POST", f"{self.url_root}/{url}", headers=self.headers, json=payload
        )
        logger.info(f"api responded with {response.status_code}, {response.json()}")
        response.raise_for_status()
        return response.json()

    def getCommunicationDevices(self):
        return self._get("communication-device")

    def getInverterEvents(self):
        params = {
            "cleared": "0",
            "start": "2025-09-01",
            "end": "2026-09-01",
            "page": "1",
            "pageSize": "30",
        }
        return self._get(
            f"inverter/{self.inverter_serial_number}/events", params=params
        )

    def getInverterHealthChecks(self):
        return self._get(f"inverter/{self.inverter_serial_number}/health")

    def getInverterSystemData(self):
        return self._get(f"inverter/{self.inverter_serial_number}/system-data/latest")

    def getInverterDataPoints(self):
        params = {"page": "1", "pageSize": "275"}
        return self._get(
            f"inverter/{self.inverter_serial_number}/data-points/2026-01-01",
            params=params,
        )

    def getInverterEnergyData(self):
        return self._get(f"inverter/{self.inverter_serial_number}/meter-data/latest")

    def getInverterSettings(self):
        return self._get(f"inverter/{self.inverter_serial_number}/settings")

    def getSettingId(self, name):
        if self.settings is None:
            settings_response = self.getInverterSettings()
            self.settings = settings_response.get("data", None)

        for setting in self.settings:
            if setting.get("name") == name:
                return setting.get("id")

        logger.info(f"setting id for {name} is {id}")
        return None

    def readInverterSetting(self, setting_name):
        id = self.getSettingId(setting_name)
        return self._post(f"inverter/{self.inverter_serial_number}/settings/{id}/read")

    def writeInverterSetting(self, setting_name, value):
        id = self.getSettingId(setting_name)
        logger.info(f"writing {value} to {setting_name} (id: {id})")
        payload = {"value": value, "context": "script"}
        resp = self._post(
            f"inverter/{self.inverter_serial_number}/settings/{id}/write", payload
        )

        return resp


def main():
    import os
    from dotenv import load_dotenv

    load_dotenv()
    giveapi = GivEnergyApi(
        os.getenv("GIVENERGY_API_KEY"), os.getenv("INVERTER_SERIAL_NUMBER")
    )

    # print(giveapi.getInverterHealthChecks())
    # print(giveapi.getInverterSystemData())
    # print(giveapi.getInverterEnergyData())
    # print(json.dumps(giveapi.getInverterSettings()))

    # print(f"""Discharge start: {giveapi.readInverterSetting("DC Discharge 1 Start Time")}
    # Discharge end: {giveapi.readInverterSetting("DC Discharge 1 End Time")}
    # Charge Start: {giveapi.readInverterSetting("AC Charge 1 Start Time")}
    # Charge End: {giveapi.readInverterSetting("AC Charge 1 End Time")}
    #          """)

    # print(giveapi.getCommunicationDevices())

    # print(giveapi.writeInverterSetting("AC Charge 1 End Time", "04:00"))
    # print(giveapi.readInverterSetting("AC Charge 1 End Time"))

    #      "validation": "Value must be one of: 0, 1, 2 (Load First, Battery First, Grid First)",
    print(giveapi.readInverterSetting("Export Power Priority"))
    # print(giveapi.readInverterSetting("Pause Battery"))

    # print(giveapi.getInverterEvents())
    # print(giveapi.getInverterEnergyData())
    # print(json.dumps(giveapi.getInverterDataPoints()))

    # Pause Battery Start Time - after it's fully charged
    # Pause Battery End Time - before peak load starts


if __name__ == "__main__":
    main()

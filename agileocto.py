from datetime import datetime, timedelta, timezone
import requests
import math
import logging

# battery capacity
BATTERY_CAPACITY_KWH = 9.5
# how fast can the battery be charged
BATTERY_MAX_CHARGE_SPEED_KWH = 3.5

logger = logging.getLogger(__name__)


class OctopusAgile:
    def __init__(
        self, product_code="AGILE-24-10-01", tariff_code="E-1R-AGILE-24-10-01-G", day=1
    ):
        self.product_code = product_code
        self.tariff_code = tariff_code
        self.hours_to_charge = self.charge_window_hours()
        self.data = self.get_input_data(day=day)

    def charge_window_hours(self):
        return math.ceil(BATTERY_CAPACITY_KWH / BATTERY_MAX_CHARGE_SPEED_KWH)

    def get_battery_charge_window(self):
        steps = self.hours_to_charge * 2
        min_sum = float("inf")
        min_window = None
        for i in range(len(self.data) - steps + 1):
            window = self.data[i : i + steps]
            total = sum(item["value_inc_vat"] for item in window)
            if total < min_sum:
                min_sum = total
                min_window = window

        return {
            "start_time": min_window[len(min_window) - 1]["valid_from"],
            "start_time_hour": self.utc_z_to_local_hour(
                min_window[len(min_window) - 1]["valid_from"]
            ),
            "end_time": min_window[0]["valid_to"],
            "end_time_hour": self.utc_z_to_local_hour(min_window[0]["valid_to"]),
            "data": min_window,
            "avg_cost_per_khw": min_sum / steps,
            "total_cost": min_sum / steps * BATTERY_CAPACITY_KWH,
        }

    def utc_z_to_local_hour(self, utc_z):
        dt_utc = datetime.strptime(utc_z, "%Y-%m-%dT%H:%M:%SZ")
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        dt_local = dt_utc.astimezone()
        return dt_local.strftime("%H:%M")

    def get_average_cost_per_kwh(self):
        return sum(item["value_inc_vat"] for item in self.data)/len(self.data)

    def get_negative_cost_items(self):
        return [i for i in self.data if i["value_inc_vat"] <= 0.0]

    def get_peak_time(self, slots=0):
        steps = self.hours_to_charge * 2 + slots
        max_sum = 0.0
        max_window = None
        for i in range(len(self.data) - steps + 1):
            window = self.data[i : i + steps]
            total = sum(item["value_inc_vat"] for item in window)
            if total > max_sum:
                max_sum = total
                max_window = window

        return {
            "start_time": max_window[len(max_window) - 1]["valid_from"],
            "start_time_hour": self.utc_z_to_local_hour(
                max_window[len(max_window) - 1]["valid_from"]
            ),
            "end_time": max_window[0]["valid_to"],
            "end_time_hour": self.utc_z_to_local_hour(max_window[0]["valid_to"]),
            "data": max_window,
            "avg_cost_per_khw": max_sum / steps,
            "total_cost": max_sum / steps * BATTERY_CAPACITY_KWH,
        }

    def to_z_time(self, t):
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_input_data(self, day=1):
        now_utc = datetime.now(timezone.utc)
        # Default: tomorrow 00:00 to tomorrow 23:59
        day = now_utc + timedelta(days=day)
        period_from = day.replace(hour=0, minute=0, second=0, microsecond=0)
        period_to = day.replace(hour=23, minute=59, second=59, microsecond=0)
        period_from_z = self.to_z_time(period_from)
        period_to_z = self.to_z_time(period_to)

        url = (
            f"https://api.octopus.energy/v1/products/{self.product_code}/"
            f"electricity-tariffs/{self.tariff_code}/standard-unit-rates/"
            f"?page_size=1500&period_from={period_from_z}&period_to={period_to_z}"
        )
        data = requests.get(url)
        data_json = data.json()
        return data_json.get("results", [])


def main():
    api = OctopusAgile(day=1)

    battery_charge_window = api.get_battery_charge_window()
    peak_time_window = api.get_peak_time()

    print(
        f"battery charge window: {battery_charge_window['start_time']} - {battery_charge_window['end_time']}"
    )
    print(
        f"battery charge cost: {battery_charge_window['total_cost']}p (@ {battery_charge_window['avg_cost_per_khw']} p/kWh)"
    )

    print(
        f"peak time window: {peak_time_window['start_time']} - {peak_time_window['end_time']}"
    )
    print(
        f"peak time cost: {peak_time_window['total_cost']}p (@ {peak_time_window['avg_cost_per_khw']} p/kWh)"
    )
    print(
        f"savings: {peak_time_window['total_cost'] - battery_charge_window['total_cost']}p"
    )


if __name__ == "__main__":
    main()

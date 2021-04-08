"""Constants for the Renault integration tests."""
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_BATTERY_CHARGING,
    DEVICE_CLASS_PLUG,
    DOMAIN as BINARY_SENSOR_DOMAIN,
)
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_KILOMETERS,
    PERCENTAGE,
    POWER_KILO_WATT,
    TEMP_CELSIUS,
    TIME_MINUTES,
    VOLUME_LITERS,
)

from custom_components.renault.const import (
    CONF_KAMEREON_ACCOUNT_ID,
    CONF_LOCALE,
    DEVICE_CLASS_CHARGE_MODE,
    DEVICE_CLASS_CHARGE_STATE,
    DEVICE_CLASS_PLUG_STATE,
    DOMAIN,
)

# Mock config data to be used across multiple tests
MOCK_CONFIG = {
    CONF_USERNAME: "email@test.com",
    CONF_PASSWORD: "test",
    CONF_KAMEREON_ACCOUNT_ID: "account_id_1",
    CONF_LOCALE: "fr_FR",
}

MOCK_VEHICLES = {
    "vehicle_ev": {
        "expected_device": {
            "identifiers": {(DOMAIN, "VF1AAAAA555777999")},
            "manufacturer": "Renault",
            "model": "Zoe",
            "name": "REG-NUMBER",
            "sw_version": "X102VE",
        },
        "endpoints_available": [True, True, True, True, False],
        "endpoints": {
            "cockpit": "cockpit_ev.json",
            "hvac_status": "hvac_status.json",
            "battery_status": "battery_status.json",
            "charge_mode": "charge_mode.json",
        },
        SENSOR_DOMAIN: [
            {
                "entity_id": "sensor.vf1aaaaa555777999_battery_autonomy",
                "unique_id": "vf1aaaaa555777999_battery_autonomy",
                "result": "141",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_battery_level",
                "unique_id": "vf1aaaaa555777999_battery_level",
                "result": "60",
                "unit": PERCENTAGE,
                "class": DEVICE_CLASS_BATTERY,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_battery_temperature",
                "unique_id": "vf1aaaaa555777999_battery_temperature",
                "result": "20",
                "unit": TEMP_CELSIUS,
                "class": DEVICE_CLASS_TEMPERATURE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_charge_mode",
                "unique_id": "vf1aaaaa555777999_charge_mode",
                "result": "always",
                "class": DEVICE_CLASS_CHARGE_MODE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_charge_state",
                "unique_id": "vf1aaaaa555777999_charge_state",
                "result": "charge_in_progress",
                "class": DEVICE_CLASS_CHARGE_STATE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_charging_power",
                "unique_id": "vf1aaaaa555777999_charging_power",
                "result": "27.0",
                "unit": POWER_KILO_WATT,
                "class": DEVICE_CLASS_ENERGY,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_charging_remaining_time",
                "unique_id": "vf1aaaaa555777999_charging_remaining_time",
                "result": "145",
                "unit": TIME_MINUTES,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_mileage",
                "unique_id": "vf1aaaaa555777999_mileage",
                "result": "49114",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_outside_temperature",
                "unique_id": "vf1aaaaa555777999_outside_temperature",
                "result": "8.0",
                "unit": TEMP_CELSIUS,
                "class": DEVICE_CLASS_TEMPERATURE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777999_plug_state",
                "unique_id": "vf1aaaaa555777999_plug_state",
                "result": "plugged",
                "class": DEVICE_CLASS_PLUG_STATE,
            },
        ],
        BINARY_SENSOR_DOMAIN: [
            {
                "entity_id": "binary_sensor.vf1aaaaa555777999_plugged_in",
                "unique_id": "vf1aaaaa555777999_plugged_in",
                "result": "on",
                "class": DEVICE_CLASS_PLUG,
            },
            {
                "entity_id": "binary_sensor.vf1aaaaa555777999_charging",
                "unique_id": "vf1aaaaa555777999_charging",
                "result": "on",
                "class": DEVICE_CLASS_BATTERY_CHARGING,
            },
        ],
    },
    "vehicle_phev": {
        "expected_device": {
            "identifiers": {(DOMAIN, "VF1AAAAA555777123")},
            "manufacturer": "Renault",
            "model": "Captur ii",
            "name": "REG-NUMBER",
            "sw_version": "XJB1SU",
        },
        "endpoints_available": [True, False, True, True, True],
        "endpoints": {
            "cockpit": "cockpit_fuel.json",
            "hvac_status": "hvac_status.json",
            "battery_status": "battery_status.json",
            "charge_mode": "charge_mode.json",
        },
        SENSOR_DOMAIN: [
            {
                "entity_id": "sensor.vf1aaaaa555777123_battery_autonomy",
                "unique_id": "vf1aaaaa555777123_battery_autonomy",
                "result": "141",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_battery_level",
                "unique_id": "vf1aaaaa555777123_battery_level",
                "result": "60",
                "unit": PERCENTAGE,
                "class": DEVICE_CLASS_BATTERY,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_battery_temperature",
                "unique_id": "vf1aaaaa555777123_battery_temperature",
                "result": "20",
                "unit": TEMP_CELSIUS,
                "class": DEVICE_CLASS_TEMPERATURE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_charge_mode",
                "unique_id": "vf1aaaaa555777123_charge_mode",
                "result": "always",
                "class": DEVICE_CLASS_CHARGE_MODE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_charge_state",
                "unique_id": "vf1aaaaa555777123_charge_state",
                "result": "charge_in_progress",
                "class": DEVICE_CLASS_CHARGE_STATE,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_charging_power",
                "unique_id": "vf1aaaaa555777123_charging_power",
                "result": "27.0",
                "unit": POWER_KILO_WATT,
                "class": DEVICE_CLASS_ENERGY,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_charging_remaining_time",
                "unique_id": "vf1aaaaa555777123_charging_remaining_time",
                "result": "145",
                "unit": TIME_MINUTES,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_fuel_autonomy",
                "unique_id": "vf1aaaaa555777123_fuel_autonomy",
                "result": "35",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_fuel_quantity",
                "unique_id": "vf1aaaaa555777123_fuel_quantity",
                "result": "3",
                "unit": VOLUME_LITERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_mileage",
                "unique_id": "vf1aaaaa555777123_mileage",
                "result": "5567",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_plug_state",
                "unique_id": "vf1aaaaa555777123_plug_state",
                "result": "plugged",
                "class": DEVICE_CLASS_PLUG_STATE,
            },
        ],
        BINARY_SENSOR_DOMAIN: [
            {
                "entity_id": "binary_sensor.vf1aaaaa555777123_plugged_in",
                "unique_id": "vf1aaaaa555777123_plugged_in",
                "result": "on",
                "class": DEVICE_CLASS_PLUG,
            },
            {
                "entity_id": "binary_sensor.vf1aaaaa555777123_charging",
                "unique_id": "vf1aaaaa555777123_charging",
                "result": "on",
                "class": DEVICE_CLASS_BATTERY_CHARGING,
            },
        ],
    },
    "vehicle_fuel": {
        "expected_device": {
            "identifiers": {(DOMAIN, "VF1AAAAA555777123")},
            "manufacturer": "Renault",
            "model": "Captur ii",
            "name": "REG-NUMBER",
            "sw_version": "XJB1SU",
        },
        "endpoints_available": [True, False, True],
        "endpoints": {
            "cockpit": "cockpit_fuel.json",
            "hvac_status": "hvac_status.json",
            "battery_status": "battery_status.json",
            "charge_mode": "charge_mode.json",
        },
        SENSOR_DOMAIN: [
            {
                "entity_id": "sensor.vf1aaaaa555777123_fuel_autonomy",
                "unique_id": "vf1aaaaa555777123_fuel_autonomy",
                "result": "35",
                "unit": LENGTH_KILOMETERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_fuel_quantity",
                "unique_id": "vf1aaaaa555777123_fuel_quantity",
                "result": "3",
                "unit": VOLUME_LITERS,
            },
            {
                "entity_id": "sensor.vf1aaaaa555777123_mileage",
                "unique_id": "vf1aaaaa555777123_mileage",
                "result": "5567",
                "unit": LENGTH_KILOMETERS,
            },
        ],
    },
}

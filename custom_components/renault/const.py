"""Constants for the Renault component."""
DOMAIN = "renault"

CONF_GIGYA_APIKEY = "gigya-api-key"
CONF_KAMEREON_APIKEY = "kamereon-api-key"
CONF_LOCALE = "locale"
CONF_KAMEREON_ACCOUNT_ID = "kamereon_account_id"

MODEL_SUPPORTS_LOCATION = ["X102VE"]
MODEL_USES_KWH = ["X102VE"]

REGEX_VIN = "(?i)^VF1[\\w]{14}$"

SUPPORTED_PLATFORMS = [
    "binary_sensor",
    "climate",
    "device_tracker",
    "sensor",
]

DEVICE_CLASS_PLUG_STATE = "renault__plug_state"
DEVICE_CLASS_CHARGE_STATE = "renault__charge_state"

"""Constants for the Renault component."""
DOMAIN = "renault"

CONF_GIGYA_APIKEY = "gigya-api-key"
CONF_KAMEREON_APIKEY = "kamereon-api-key"
CONF_LOCALE = "locale"
CONF_KAMEREON_ACCOUNT_ID = "kamereon_account_id"
CONF_DISTANCES_IN_MILES = "distances_in_miles"

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes
MIN_SCAN_INTERVAL = 60  # 1 minute

REGEX_VIN = "(?i)^VF1[\\w]{14}$"

SUPPORTED_PLATFORMS = [
    "binary_sensor",
    "device_tracker",
    "sensor",
]

DEVICE_CLASS_PLUG_STATE = "renault__plug_state"
DEVICE_CLASS_CHARGE_STATE = "renault__charge_state"
DEVICE_CLASS_CHARGE_MODE = "renault__charge_mode"

RENAULT_API_URL = "https://github.com/hacf-fr/renault-api/issues"

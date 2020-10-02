"""Constants for the Renault component."""
DOMAIN = "renault"

CONF_GIGYA_APIKEY = "gigya-api-key"
CONF_KAMEREON_APIKEY = "kamereon-api-key"
CONF_LOCALE = "locale"
CONF_KAMEREON_ACCOUNT_ID = "kamereon_account_id"

MODEL_SUPPORTS_LOCATION = ["X102VE"]

AVAILABLE_LOCALES = [
    "bg_BG",
    "cs_CZ",
    "da_DK",
    "de_DE",
    "de_AT",
    "de_CH",
    "en_GB",
    "en_IE",
    "es_ES",
    "es_MX",
    "fi_FI",
    "fr_FR",
    "fr_BE",
    "fr_CH",
    "fr_LU",
    "hr_HR",
    "hu_HU",
    "it_IT",
    "it_CH",
    "nl_NL",
    "nl_BE",
    "no_NO",
    "pl_PL",
    "pt_PT",
    "ro_RO",
    "ru_RU",
    "sk_SK",
    "sl_SI",
    "sv_SE",
]

REGEX_VIN = "(?i)^VF1[\\w]{14}$"

SUPPORTED_PLATFORMS = [
    "binary_sensor",
    "climate",
    "device_tracker",
    "sensor",
]

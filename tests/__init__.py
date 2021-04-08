"""Tests for the Renault integration."""
from datetime import timedelta
from unittest.mock import patch

from homeassistant.config_entries import CONN_CLASS_CLOUD_POLL
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import aiohttp_client
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from renault_api.kamereon import models, schemas
from renault_api.renault_vehicle import RenaultVehicle

from custom_components.renault.const import (
    CONF_KAMEREON_ACCOUNT_ID,
    CONF_LOCALE,
    DOMAIN,
)
from custom_components.renault.renault_vehicle import RenaultVehicleProxy

from .const import MOCK_VEHICLES


async def setup_renault_integration(hass):
    """Create the Renault integration."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source="user",
        data={
            CONF_LOCALE: "fr_FR",
            CONF_USERNAME: "email@test.com",
            CONF_PASSWORD: "test",
            CONF_KAMEREON_ACCOUNT_ID: "account_id_2",
        },
        unique_id="account_id_2",
        connection_class=CONN_CLASS_CLOUD_POLL,
        options={},
        entry_id="1",
    )
    config_entry.add_to_hass(hass)

    with patch(
        "custom_components.renault.RenaultHub.attempt_login", return_value=True
    ), patch("custom_components.renault.RenaultHub.async_initialise"):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    return config_entry


async def create_vehicle_proxy(hass, vehicle_type: str) -> RenaultVehicleProxy:
    """Create a vehicle proxy for testing."""
    mock_vehicle = MOCK_VEHICLES[vehicle_type]
    mock_get_cockpit = schemas.KamereonVehicleDataResponseSchema.loads(
        load_fixture(mock_vehicle["endpoints"]["cockpit"])
        if "cockpit" in mock_vehicle["endpoints"]
        else "{}"
    ).get_attributes(schemas.KamereonVehicleCockpitDataSchema)
    mock_get_hvac_status = schemas.KamereonVehicleDataResponseSchema.loads(
        load_fixture(mock_vehicle["endpoints"]["hvac_status"])
        if "hvac_status" in mock_vehicle["endpoints"]
        else "{}"
    ).get_attributes(schemas.KamereonVehicleHvacStatusDataSchema)
    mock_get_battery_status = schemas.KamereonVehicleDataResponseSchema.loads(
        load_fixture(mock_vehicle["endpoints"]["battery_status"])
        if "battery_status" in mock_vehicle["endpoints"]
        else "{}"
    ).get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema)
    mock_get_charge_mode = schemas.KamereonVehicleDataResponseSchema.loads(
        load_fixture(mock_vehicle["endpoints"]["charge_mode"])
        if "charge_mode" in mock_vehicle["endpoints"]
        else "{}"
    ).get_attributes(schemas.KamereonVehicleChargeModeDataSchema)
    mock_get_location = schemas.KamereonVehicleDataResponseSchema.loads(
        load_fixture(mock_vehicle["endpoints"]["location"])
        if "location" in mock_vehicle["endpoints"]
        else "{}"
    ).get_attributes(schemas.KamereonVehicleLocationDataSchema)

    vehicles_response: models.KamereonVehiclesResponse = (
        schemas.KamereonVehiclesResponseSchema.loads(
            load_fixture(f"{vehicle_type}.json")
        )
    )
    vehicle_details = vehicles_response.vehicleLinks[0].vehicleDetails
    vehicle = RenaultVehicle(
        vehicles_response.accountId,
        vehicle_details.vin,
        websession=aiohttp_client.async_get_clientsession(hass),
    )

    vehicle_proxy = RenaultVehicleProxy(
        hass, vehicle, vehicle_details, timedelta(seconds=300), False
    )
    with patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.endpoint_available",
        side_effect=mock_vehicle["endpoints_available"],
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_cockpit",
        return_value=mock_get_cockpit,
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_hvac_status",
        return_value=mock_get_hvac_status,
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_battery_status",
        return_value=mock_get_battery_status,
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_charge_mode",
        return_value=mock_get_charge_mode,
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_location",
        return_value=mock_get_location,
    ):
        await vehicle_proxy.async_initialise()
    return vehicle_proxy

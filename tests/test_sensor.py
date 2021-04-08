"""Tests for Renault sensors."""
from datetime import timedelta
from unittest.mock import PropertyMock, patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.helpers import aiohttp_client
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.common import (
    load_fixture,
    mock_device_registry,
    mock_registry,
)
from renault_api.kamereon import models, schemas
from renault_api.renault_vehicle import RenaultVehicle

from custom_components.renault.renault_vehicle import RenaultVehicleProxy
from tests.const import MOCK_VEHICLES

from . import setup_renault_integration


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensors(hass, vehicle_type):
    """Test for Renault sensors."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    mock_vehicle = MOCK_VEHICLES[vehicle_type]

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
        "custom_components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_details.vin: vehicle_proxy,
        },
    ), patch("custom_components.renault.SUPPORTED_PLATFORMS", [SENSOR_DOMAIN]), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.endpoint_available",
        side_effect=mock_vehicle["endpoints_available"],
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_cockpit",
        return_value=schemas.KamereonVehicleDataResponseSchema.loads(
            load_fixture(mock_vehicle["endpoints"]["cockpit"])
        ).get_attributes(schemas.KamereonVehicleCockpitDataSchema),
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_hvac_status",
        return_value=schemas.KamereonVehicleDataResponseSchema.loads(
            load_fixture(mock_vehicle["endpoints"]["hvac_status"])
        ).get_attributes(schemas.KamereonVehicleHvacStatusDataSchema),
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_battery_status",
        return_value=schemas.KamereonVehicleDataResponseSchema.loads(
            load_fixture(mock_vehicle["endpoints"]["battery_status"])
        ).get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
    ), patch(
        "custom_components.renault.renault_vehicle.RenaultVehicleProxy.get_charge_mode",
        return_value=schemas.KamereonVehicleDataResponseSchema.loads(
            load_fixture(mock_vehicle["endpoints"]["charge_mode"])
        ).get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
    ):
        await vehicle_proxy.async_initialise()
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    assert len(device_registry.devices) == 1
    expected_device = mock_vehicle["expected_device"]
    registry_entry = device_registry.async_get_device(expected_device["identifiers"])
    assert registry_entry is not None
    assert registry_entry.identifiers == expected_device["identifiers"]
    assert registry_entry.manufacturer == expected_device["manufacturer"]
    assert registry_entry.name == expected_device["name"]
    assert registry_entry.model == expected_device["model"]
    assert registry_entry.sw_version == expected_device["sw_version"]

    expected_entities = mock_vehicle[SENSOR_DOMAIN]
    assert len(entity_registry.entities) == len(expected_entities)
    for expected_entity in expected_entities:
        entity_id = expected_entity["entity_id"]
        registry_entry = entity_registry.entities.get(entity_id)
        assert registry_entry is not None
        assert registry_entry.unique_id == expected_entity["unique_id"]
        assert registry_entry.unit_of_measurement == expected_entity.get("unit")
        assert registry_entry.device_class == expected_entity.get("class")
        state = hass.states.get(entity_id)
        assert state.state == expected_entity["result"]

"""Tests for Renault sensors."""
from unittest.mock import PropertyMock, patch

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.common import (
    mock_device_registry,
    mock_registry,
)

from tests.const import MOCK_VEHICLES

from . import (
    create_unavailable_vehicle_proxy,
    create_vehicle_proxy,
    setup_renault_integration,
)


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensors(hass, vehicle_type):
    """Test for Renault sensors."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    vehicle_proxy = await create_vehicle_proxy(hass, vehicle_type)

    with patch(
        "custom_components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("custom_components.renault.SUPPORTED_PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    mock_vehicle = MOCK_VEHICLES[vehicle_type]
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


@pytest.mark.parametrize("vehicle_type", MOCK_VEHICLES.keys())
async def test_sensor_errors(hass, vehicle_type):
    """Test for Renault sensors with temporary failure."""
    await async_setup_component(hass, "persistent_notification", {})
    entity_registry = mock_registry(hass)
    device_registry = mock_device_registry(hass)

    vehicle_proxy = await create_unavailable_vehicle_proxy(hass, vehicle_type)

    with patch(
        "custom_components.renault.RenaultHub.vehicles",
        new_callable=PropertyMock,
        return_value={
            vehicle_proxy.details.vin: vehicle_proxy,
        },
    ), patch("custom_components.renault.SUPPORTED_PLATFORMS", [SENSOR_DOMAIN]):
        await setup_renault_integration(hass)
        await hass.async_block_till_done()

    mock_vehicle = MOCK_VEHICLES[vehicle_type]
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
        assert state.state == STATE_UNAVAILABLE

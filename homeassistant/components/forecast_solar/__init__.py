"""The Forecast.Solar integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, SupportsResponse

from .const import (
    CONF_DAMPING,
    CONF_DAMPING_EVENING,
    CONF_DAMPING_MORNING,
    CONF_MODULES_POWER,
    DOMAIN,
    LOGGER,
    SERVICE_NAME,
)
from .coordinator import ForecastSolarDataUpdateCoordinator
# from .services import async_setup_services, async_unload_services

PLATFORMS = [Platform.SENSOR]

type ForecastSolarConfigEntry = ConfigEntry[ForecastSolarDataUpdateCoordinator]

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entry."""

    if entry.version == 1:
        new_options = entry.options.copy()
        new_options |= {
            CONF_MODULES_POWER: new_options.pop("modules power"),
            CONF_DAMPING_MORNING: new_options.get(CONF_DAMPING, 0.0),
            CONF_DAMPING_EVENING: new_options.pop(CONF_DAMPING, 0.0),
        }

        hass.config_entries.async_update_entry(
            entry, data=entry.data, options=new_options, version=2
        )

    return True


# @callback
def async_setup_services(
    hass: HomeAssistant, coordinator: ForecastSolarDataUpdateCoordinator
) -> bool:
    hass.services.async_register(
        DOMAIN,
        SERVICE_NAME,
        coordinator.async_handle_get_prediction,
        supports_response=SupportsResponse.ONLY,
    )
    # https://developers.home-assistant.io/docs/dev_101_services/


async def async_setup_entry(
    hass: HomeAssistant, entry: ForecastSolarConfigEntry
) -> bool:
    """Set up Forecast.Solar from a config entry."""
    coordinator = ForecastSolarDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))
    async_setup_services(hass, coordinator)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

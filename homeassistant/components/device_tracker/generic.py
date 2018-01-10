"""
Support for OpenWRT (luci) routers.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/device_tracker.luci/
"""
import json
import logging
import re

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import CONF_URL, CONF_PASSWORD, CONF_USERNAME

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_URL): cv.string,
    vol.Optional(CONF_USERNAME): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string
})


def get_scanner(hass, config):
    """Validate the configuration and return a Luci scanner."""
    scanner = GenericDeviceScanner(config[DOMAIN])
    return scanner if scanner.success_init else None


class GenericDeviceScanner(DeviceScanner):
    """This class queries a wireless router running OpenWrt firmware."""

    def __init__(self, config):
        """Initialize the scanner."""
        self.url = config[CONF_URL]
        #self.username = config[CONF_USERNAME]
        #self.password = config[CONF_PASSWORD]
        self.last_results = {}
        self.success_init = True


    def scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        self._update_info()
        return self.last_results

    def get_device_name(self, device):
        return None

    def _update_info(self):
        """Ensure the information from the Luci router is up to date.
        Returns boolean if scanning successful.
        """
        if not self.success_init:
            return False

        try:
            result = requests.get(self.url, timeout=5 ).json()
        except Exception:
            _LOGGER.exception("Error while retrieve STA list")
            return False

        if result:
            self.last_results = []
            for device_entry in result:
                self.last_results.append(device_entry['mac'])
            return True
        return False
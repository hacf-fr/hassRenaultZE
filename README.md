# renault

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [Renault][renault]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show car charge and plug status as `True` or `False`.
`climate` | Control car HVAC.
`device_tracker` | Show car location.
`sensor` | Show various information about the car status.

![example][exampleimg]

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `renault`.
4. Download _all_ the files from the `custom_components/renault/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Renault"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/renault/translations/en.json
custom_components/renault/__init__.py
custom_components/renault/binary_sensor.py
custom_components/renault/climate.py
custom_components/renault/config_flow.py
custom_components/renault/const.py
custom_components/renault/device_tracker.json
custom_components/renault/manifest.json
custom_components/renault/pyzeproxy.py
custom_components/renault/pyzevehicleproxy.py
custom_components/renault/renaultentity.py
custom_components/renault/sensor.py
custom_components/renault/services.py
custom_components/renault/services.yaml
custom_components/renault/strings.json
```

## Configuration
Configuration is done in the UI, but some cases need [specific configuration](CONFIGURE.md).


## Logging
If you are having issues with the component, please enable debug logging in your `configuration.yaml`, for example:
```
logger:
  default: error
  logs:
    renault_api: debug
    custom_components.renault: debug
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[renault]: https://github.com/hacf-fr/hassRenaultZE
[commits-shield]: https://img.shields.io/github/commit-activity/y/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[commits]: https://github.com/hacf-fr/hassRenaultZE/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-epenet-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[releases]: https://github.com/hacf-fr/hassRenaultZE/releases

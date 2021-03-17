[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

_Component to integrate with [Renault][renault]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show car charge and plug status as `True` or `False`.
`device_tracker` | Show car location.
`sensor` | Show various information about the car status.

![example][exampleimg]

{% if not installed %}
## Installation

1. Click install.
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Renault".

{% endif %}


## Configuration is done in the UI

<!---->

***

[renault]: https://github.com/hacf-fr/hassRenaultZE
[commits-shield]: https://img.shields.io/github/commit-activity/y/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[commits]: https://github.com/hacf-fr/hassRenaultZE/commits/master
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license]: https://github.com//hacf-fr/hassRenaultZE/blob/main/LICENSE
[license-shield]: https://img.shields.io/github/license/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-epenet-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/hacf-fr/hassRenaultZE.svg?style=for-the-badge
[releases]: https://github.com/hacf-fr/hassRenaultZE/releases
[user_profile]: https://github.com/epenet

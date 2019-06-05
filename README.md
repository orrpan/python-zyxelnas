# Python API for ZyxelNAS [![Build Status](https://travis-ci.org/orrpan/python-zyxelnas.svg?branch=master)](https://travis-ci.org/orrpan/python-zyxelnas)

Based on [python-synology](https://github.com/StaticCube/python-synology) by [FG van Zeelst StaticCube](https://github.com/StaticCube/)

-----
## Installation
```sh
git clone https://github.com/orrpan/python-zyxelnas.git
cd python-zyxelnas
[sudo] pip install setup.py
```
-----
## Usage

### Module
------

You can import the module as `ZyxelNAS`.

```python

from ZyxelNAS import ZyxelNAS

print("Creating Valid API")
api = ZyxelNAS("192.168.1.10", "443", "admin", "superpassword", True)


print("=== Utilisation ===")
print("CPU Load:   " + str(api.utilisation.cpu_total_load))
print("Memory Use: " + str(api.utilisation.memory_real_usage))
print("Memory Size:" + str(api.utilisation.memory_size))
print("Net Up:     " + str(api.utilisation.network_up))
print("Net Down:   " + str(api.utilisation.network_down))
print("Status:     " + str(api.utilisation.system_status))
print("Fan Speed:  " + str(api.utilisation.system_status_fan) + " RPM")
print("CPU Temp:   " + str(api.utilisation.system_status_temp) + " °C")
print('\n')

print("=== Storage ===")
volumes = api.storage.volumes
for volume in volumes:
    print("ID:         " + str(volume))
    print("Status:     " + str(api.storage.volume_status(volume)))
    print("Device Type:" + str(api.storage.volume_device_type(volume)))
    print("VolSizeTot: " + str(api.storage.volume_size_total(volume)))
    print("VolSizeUsed:" + str(api.storage.volume_size_used(volume)))
    print("VolSizeUsed:" + str(api.storage.volume_percentage_used(volume)) + " %")
    print("DiskTempAvg:" + str(api.storage.volume_disk_temp_avg(volume)))
    print("DiskTempMax:" + str(api.storage.volume_disk_temp_max(volume)))
print('\n')

disks = api.storage.disks
for disk in disks:
    print("ID:         " + str(disk))
    print("Name:       " + str(api.storage.disk_name(disk)))
    print("Status:     " + str(api.storage.disk_status(disk)))
    print("Temp:       " + str(api.storage.disk_temp(disk)))
print('\n')


# Shutdown or reboot
api.shutdown
api.reboot

```

Turn on with wol
```python
from ZyxelNAS import ZyxelPowerOn

ZyxelPowerOn('000000000000')
```

## Credits / Special Thanks
- https://github.com/StaticCube (mirrored from)
- https://github.com/florianeinfalt
- https://github.com/tchellomello

LEVEL1_DEVICES = [
    {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "device_name": "Pico Safe 001",
        "model": "Raspberry Pi Pico 2W",
        "status": "online",
    },
    {
        "device_id": "pico-safe-002",
        "zone_id": "room-2",
        "device_name": "Pico Safe 002",
        "model": "Raspberry Pi Pico 2W",
        "status": "online",
    },
    {
        "device_id": "pico-safe-003",
        "zone_id": "room-3",
        "device_name": "Pico Safe 003",
        "model": "Raspberry Pi Pico 2W",
        "status": "online",
    },
    {
        "device_id": "pico-safe-004",
        "zone_id": "room-4",
        "device_name": "Pico Safe 004",
        "model": "Raspberry Pi Pico 2W",
        "status": "online",
    },
]

LEVEL1_DEVICE_IDS = tuple(device["device_id"] for device in LEVEL1_DEVICES)

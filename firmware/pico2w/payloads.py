def timestamp_from_localtime(local_time):
    year, month, day, hour, minute, second, _, _ = local_time
    if year < 2024:
        return None
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}+00:00".format(
        year,
        month,
        day,
        hour,
        minute,
        second,
    )


def reading_topic(zone_id, device_id, sensor_id):
    return "saferoom/{}/{}/sensors/{}/reading".format(zone_id, device_id, sensor_id)


def heartbeat_topic(zone_id, device_id):
    return "saferoom/{}/{}/status".format(zone_id, device_id)


def reading_payload(device_id, zone_id, sensor_id, value, unit, timestamp, seq):
    return {
        "device_id": device_id,
        "zone_id": zone_id,
        "sensor_id": sensor_id,
        "value": value,
        "unit": unit,
        "timestamp": timestamp,
        "seq": seq,
    }


def heartbeat_payload(device_id, zone_id, timestamp, uptime_ms, seq):
    return {
        "device_id": device_id,
        "zone_id": zone_id,
        "status": "online",
        "timestamp": timestamp,
        "uptime_ms": uptime_ms,
        "seq": seq,
    }

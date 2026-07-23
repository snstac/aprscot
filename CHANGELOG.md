## APRSCoT 8.2.0

- Add `KISSWorker`: read APRS from a local KISS-over-TCP TNC (e.g. Dire Wolf) instead of APRS-IS, enabling a fully-offline over-the-air RF → TAK gateway (`rtl_fm | direwolf → aprscot`).
- Select the input transport by config: set `KISS_HOST` (and optional `KISS_PORT`, default 8001) to use KISS; otherwise APRS-IS as before.
- Decodes KISS framing + AX.25 UI frames to TNC2, reusing the existing `aprslib`/CoT path (digipeater `*` "repeated" flags preserved).
- New constant `DEFAULT_KISS_PORT=8001`; new tests for the KISS/AX.25 decoder.

## APRSCoT 8.1.0

- Add `SensorWorker`: periodic `a-f-G-E-S-E` sensor CoT heartbeat every `SENSOR_KEEPALIVE_PERIOD` seconds (default 30).
- Position sourced from system gpsd → static `SENSOR_LAT`/`SENSOR_LON`/`SENSOR_HAE` config → null island fallback.
- Add `gen_sensor_cot()`: reusable CoT builder for sensor beacon events.
- New constants: `DEFAULT_SENSOR_KEEPALIVE_PERIOD=30`, `DEFAULT_SENSOR_LAT/LON/HAE=0.0`.

## APRSCOT 8.0.0

* Rewrite for 2024.
* Fixed #12 & #15: Add support for APRS-IS Passcodes ("passwords").

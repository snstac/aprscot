## APRSCoT 8.3.0

- **Runtime status surface.** aprscot now writes `/run/aprscot/status.json` via
  `pytak.StatusWriter`, so a management UI can tell a working gateway from a
  wedged one. Previously the only evidence aprscot was doing anything was CoT
  arriving at the far end, and every drop reason went to the journal or nowhere.
- Counters: `rx`, `emitted`, `no_position`, `unknown_format`, `parse_error`,
  `empty_frame`, `aprsis_keepalive`, `bad_ax25` (KISS). `aprsis_keepalive` is
  what distinguishes "connected, filter is quiet" from "connection is dead".
- Decode feed: every *parsed* frame is recorded with callsign, SSID, symbol,
  comment and path — not only the ones that plot. Most APRS traffic carries no
  position, so a plotted-only feed sits empty on a healthy receiver. A `placed`
  flag separates the two. `path` shows whether a frame arrived over RF or
  APRS-IS.
- Undecodable input is **not** counted as received, so a garbled RF feed cannot
  read as healthy traffic.
- Startup write before the first connect attempt (publishing `connected=false`)
  plus a 5s heartbeat, so "no status" now means aprscot is not running rather
  than aprscot is merely quiet.
- Positionless frames no longer log at WARNING; a healthy gateway filled the
  journal with warnings about ordinary APRS messages and telemetry.
- Degrades to a no-op on a pytak without `StatusWriter` (fleet is on 7.3.13)
  rather than failing to import.

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

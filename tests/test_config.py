"""Configuration tests: per-callsign sections (#16), APRS-IS settings (#13, #15)."""

import asyncio
from configparser import ConfigParser
from unittest.mock import AsyncMock, MagicMock, patch

import aprslib
import pytest

import aprscot
from aprscot.functions import aprs_to_cot_xml, aprsis_settings

INI = """
[aprscot]
COT_URL = udp://239.2.3.1:6969
COT_STALE = 3600

[W2GMD-9]
COT_TYPE = a-f-G-U-C
COT_STALE = 600
COT_NAME = Medic 52
COT_ICON = my/icon.png

[NB6F-2]
COT_NAME = Transport 2
"""


def _frame(call):
    return aprslib.parse(f"{call}>APRS,TCPIP*:!3745.60N/12229.85W_test")


@pytest.fixture
def parser():
    cp = ConfigParser()
    cp.optionxform = str
    cp.read_string(INI)
    return cp


def test_callsign_section_applies_via_sectionproxy(parser):
    """pytak.cli() hands over a SectionProxy, not the ConfigParser (#16)."""
    cot = aprs_to_cot_xml(_frame("W2GMD-9"), parser["aprscot"])
    assert cot.get("type") == "a-f-G-U-C"
    assert cot.get("stale") is not None
    detail = cot.find("detail")
    assert detail.find("usericon").get("iconsetpath") == "my/icon.png"


def test_callsign_name_override(parser):
    cot = aprs_to_cot_xml(_frame("NB6F-2"), parser["aprscot"])
    assert cot.find("detail/contact").get("callsign") == "Transport 2 (APRS)"
    # Unset keys fall back to the global defaults.
    assert cot.get("type") == aprscot.DEFAULT_COT_TYPE


def test_unlisted_callsign_uses_defaults(parser):
    cot = aprs_to_cot_xml(_frame("N0CALL"), parser["aprscot"])
    assert cot.get("type") == aprscot.DEFAULT_COT_TYPE
    assert cot.find("detail/contact").get("callsign") == "N0CALL (APRS)"


def test_global_icon_not_clobbered_by_callsign_section(parser):
    parser["aprscot"]["COT_ICON"] = "global/icon.png"
    cot = aprs_to_cot_xml(_frame("NB6F-2"), parser["aprscot"])
    assert cot.find("detail/usericon").get("iconsetpath") == "global/icon.png"


def test_plain_dict_config_still_works():
    cot = aprs_to_cot_xml(_frame("N0CALL"), {"COT_TYPE": "a-f-G"})
    assert cot.get("type") == "a-f-G"


# APRS-IS settings -------------------------------------------------------------


def test_aprsis_documented_keys_are_honoured():
    """APRSIS_HOST / APRSIS_PORT are the documented names (#13)."""
    s = aprsis_settings({"APRSIS_HOST": "aprs.example.com", "APRSIS_PORT": "10152"})
    assert (s["host"], s["port"]) == ("aprs.example.com", 10152)


def test_aprsis_legacy_keys_still_work():
    s = aprsis_settings({"APRS_HOST": "legacy.example.com", "APRS_PORT": "1"})
    assert (s["host"], s["port"]) == ("legacy.example.com", 1)


def test_aprsis_host_with_port():
    s = aprsis_settings({"APRSIS_HOST": "aprs.example.com:10152"})
    assert (s["host"], s["port"]) == ("aprs.example.com", 10152)


def test_aprsis_defaults():
    s = aprsis_settings({})
    assert s["host"] == aprscot.DEFAULT_APRSIS_HOST
    assert s["port"] == aprscot.DEFAULT_APRSIS_PORT


def test_aprsis_credentials_from_config_only():
    s = aprsis_settings({"APRSIS_CALLSIGN": "N0CALL-1", "APRSIS_PASSCODE": "12345"})
    assert (s["callsign"], s["passcode"]) == ("N0CALL-1", "12345")


def test_aprsis_empty_host_is_an_error():
    with pytest.raises(ValueError):
        aprsis_settings({"APRSIS_HOST": "noam..aprs2.net"})


def test_no_credentials_committed():
    """No real passcode is shipped; only the APRS-IS read-only marker."""
    assert aprscot.DEFAULT_APRSIS_PASSCODE == "-1"


def _run_worker(config):
    reader = MagicMock()
    reader.readline = AsyncMock(side_effect=asyncio.CancelledError)
    writer = MagicMock()
    writer.drain = AsyncMock()
    opener = AsyncMock(return_value=(reader, writer))
    worker = aprscot.APRSWorker(asyncio.Queue(), config)
    with patch("asyncio.open_connection", opener):
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(worker.run())
    return opener, writer


def test_worker_connects_to_configured_server_and_logs_in(caplog):
    cfg = {
        "APRSIS_HOST": "aprs.example.com",
        "APRSIS_PORT": "10152",
        "APRSIS_CALLSIGN": "N0CALL-1",
        "APRSIS_PASSCODE": "s3cret-pass",
        "APRSIS_FILTER": "r/1/2/3",
    }
    with caplog.at_level("DEBUG"):
        opener, writer = _run_worker(cfg)
    opener.assert_awaited_once_with("aprs.example.com", 10152)
    sent = writer.write.call_args[0][0].decode()
    assert sent.startswith("user N0CALL-1 pass s3cret-pass vers aprscot")
    assert "filter r/1/2/3" in sent
    assert "s3cret-pass" not in caplog.text

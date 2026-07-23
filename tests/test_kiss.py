#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tests for APRSCOT KISS/AX.25 decode (Dire Wolf RF input).

"""Tests for the KISS-over-TCP AX.25 -> TNC2 decoder used by KISSWorker."""

import unittest

from aprscot.classes import ax25_to_tnc2, kiss_unescape

FEND, FESC, TFEND, TFESC = 0xC0, 0xDB, 0xDC, 0xDD


def _enc_addr(call: str, ssid: int, last: bool, repeated: bool = False) -> bytes:
    out = bytes((ord(c) << 1) & 0xFE for c in call.ljust(6))
    ssid_byte = 0x60 | ((ssid & 0x0F) << 1)
    if repeated:
        ssid_byte |= 0x80
    if last:
        ssid_byte |= 0x01
    return out + bytes([ssid_byte])


def _ui_frame(src, ss, dest, ds, digis, info):
    frame = _enc_addr(dest, ds, False) + _enc_addr(src, ss, not digis)
    for n, (dc, dss, rpt) in enumerate(digis):
        frame += _enc_addr(dc, dss, n == len(digis) - 1, rpt)
    return frame + bytes([0x03, 0xF0]) + info.encode()


class KISSDecodeTestCase(unittest.TestCase):
    def test_ax25_to_tnc2_with_digis(self):
        info = "!3746.00N/12225.00W#Test de W2GMD"
        frame = _ui_frame(
            "W2GMD", 1, "APRS", 0,
            [("WIDE1", 1, True), ("WIDE2", 1, False)], info,
        )
        self.assertEqual(
            ax25_to_tnc2(frame),
            "W2GMD-1>APRS,WIDE1-1*,WIDE2-1:" + info,
        )

    def test_ax25_to_tnc2_no_digi(self):
        frame = _ui_frame("N0CALL", 0, "APRS", 0, [], ">status")
        self.assertEqual(ax25_to_tnc2(frame), "N0CALL>APRS:>status")

    def test_ax25_to_tnc2_short_frame_returns_none(self):
        self.assertIsNone(ax25_to_tnc2(b"\x00\x01\x02"))

    def test_kiss_unescape(self):
        # FESC TFEND -> FEND ; FESC TFESC -> FESC
        self.assertEqual(
            kiss_unescape(bytes([FESC, TFEND, 0x41, FESC, TFESC])),
            bytes([FEND, 0x41, FESC]),
        )


if __name__ == "__main__":
    unittest.main()

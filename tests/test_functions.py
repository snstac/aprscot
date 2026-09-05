#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Tests for APRS Cursor-on-Target Gateway.

"""Tests for APRSCOT: APRS to TAK Gateway."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

import aprslib
import aprscot.functions

# AE6DC-5>APDW15,TCPIP*,qAC,T2VAN:<IGATE,MSG_CNT=35,PKT_CNT=7,DIR_CNT=3,
# LOC_CNT=3,RF_CNT=58,UPL_CNT=56189,DNL_CNT=104937
# W6BSD-5>APDW15,TCPIP*,qAC,T2CAWEST:T#243,180,41856,487,0,0,00000000
# SUNSET>APRS,TCPIP*,qAC,T2SP:@145502z3745.60N/12229.85W_000/
# 000g000t060P000h99b00030W2GMD Outer Sunset, SF IGate/Digipeater
# http://w2gmd.org


class FunctionsTestCase(unittest.TestCase):
    def test_sensor_beacon_switch(self):
        """Receiver beacons default on and accept common false values."""
        enabled = aprscot.functions.sensor_beacon_enabled
        self.assertTrue(enabled({}))
        for value in ("0", "false", "False", "no", "off"):
            with self.subTest(value=value):
                self.assertFalse(enabled({"SENSOR_BEACON": value}))

    def test_create_tasks_can_omit_sensor_beacon(self):
        """Disabling the receiver beacon keeps APRS processing enabled."""
        clitool = SimpleNamespace(tx_queue=object())
        with patch.object(aprscot, "APRSWorker", return_value="aprs"), patch.object(
            aprscot, "SensorWorker", return_value="receiver"
        ) as sensor_worker:
            tasks = aprscot.functions.create_tasks({"SENSOR_BEACON": "0"}, clitool)
        self.assertEqual(tasks, {"aprs"})
        sensor_worker.assert_not_called()

    def test_aprs_to_cot_xml(self):
        """
        Tests that aprs_to_cot decodes an APRS Frame into a Cursor on Target
        message.
        """
        test_frame = (
            "SUNSET>APRS,TCPIP*,qAC,T2SP:@145502z3745.60N/12229.85W_000/"
            "000g000t060P000h99b00030W2GMD Outer Sunset, SF IGate/Digipeater "
            "http://w2gmd.org"
        )

        parsed_frame = aprslib.parse(test_frame)
        cot_frame = aprscot.functions.aprs_to_cot_xml(parsed_frame, {})

        self.assertEqual(cot_frame.get("type"), "a-f-G-I-U-T-r")
        self.assertEqual(cot_frame.get("uid"), "APRS.SUNSET")


if __name__ == "__main__":
    unittest.main()

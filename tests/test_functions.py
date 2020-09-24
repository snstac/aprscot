import unittest

import aprs
import aprscot.functions

# AE6DC-5>APDW15,TCPIP*,qAC,T2VAN:<IGATE,MSG_CNT=35,PKT_CNT=7,DIR_CNT=3,
# LOC_CNT=3,RF_CNT=58,UPL_CNT=56189,DNL_CNT=104937
# W6BSD-5>APDW15,TCPIP*,qAC,T2CAWEST:T#243,180,41856,487,0,0,00000000
# SUNSET>APRS,TCPIP*,qAC,T2SP:@145502z3745.60N/12229.85W_000/
# 000g000t060P000h99b00030W2GMD Outer Sunset, SF IGate/Digipeater
# http://w2gmd.org


class FunctionsTestCase(unittest.TestCase):

    def test_aprs_to_cot(self):
        """
        Tests that aprs_to_cot decodes an APRS Frame into a Cursor-on-Target
        message.
        """
        test_frame = (
            'SUNSET>APRS,TCPIP*,qAC,T2SP:@145502z3745.60N/12229.85W_000/'
            '000g000t060P000h99b00030W2GMD Outer Sunset, SF IGate/Digipeater '
            'http://w2gmd.org')
        parsed_frame = aprs.parse_frame(test_frame)
        cot_frame = aprscot.functions.aprs_to_cot(parsed_frame)
        self.assertEqual(cot_frame.event_type, 'a-f-G-E-V-C')
        self.assertEqual(cot_frame.uid, 'APRS.SUNSET')

    def test_decode_lat_lon(self):
        """
        Tests that the decode_lat_lon function decodes a valid lat & lon
        from APRS.
        """
        test_info = (
            '@145502z3745.60N/12229.85W_000/000g000t060P000h99b00030'
            'W2GMD Outer Sunset, SF IGate/Digipeater http://w2gmd.org')
        ll = aprscot.functions.decode_lat_lon(test_info)
        self.assertEqual(float(ll[0]), 37.76)
        self.assertEqual(str(ll[0]), '37.76')
        self.assertEqual(float(ll[1]), 122.4975)
        self.assertEqual(str(ll[1]), '122.4975')


if __name__ == '__main__':
    unittest.main()

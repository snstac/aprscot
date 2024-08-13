APRSCOT's configuration parameters can be set two ways:

1. In an INI-style configuration file. (ex. ``aprscot -c config.ini``)
2. As environment variables. (ex. ``export DEBUG=1;aprscot``)

APRSCOT has the following built-in configuration parameters:

APRSIS_FILTER = f/W6PW-10/50

* **`APRSIS_FILTER`**:
    * Default: ``m/50``

    [APRS-IS Server-side Filter](http://www.aprs-is.net/javAPRSFilter.aspx).

* **`COT_TYPE`**:
    * Default: ``a-f-G-I-U-T-r`` seconds

    COT Event type.
    
* **`COT_STALE`**:
    * Default: ``3600``

    COT Stale time.

* **`COT_NAME`**:
    * Default: unset
    
    COT Callsign.

* **`APRSIS_CALLSIGN`**:
    * Default: ``SUNSET``

    APRS-IS connection callsign.

* **`APRSIS_PASSWORD`**:
    * Default: ``-1``

    APRS-IS connection password.

* **`APRSIS_PORT`**:
    * Default: ``14580``

    APRS-IS port

* **`APRSIS_HOST`**:
    * Default: ``rotate.aprs.net``

    APRS-IS host.

Additional configuration parameters, including TAK Server configuration, are included in the [PyTAK Configuration](https://pytak.readthedocs.io/en/latest/configuration/) documentation.

## Transformations

`COT_NAME`, `COT_STALE` & `COT_STALE` can be set on a per-APRS callsign basis, for example:

```
[aprscot]
COT_URL = tcp://takserver.example.com:8088

[W2GMD-9]
COT_TYPE = a-f-G-U-C
COT_STALE = 600
COT_NAME = Medic 52

[NB6F-2]
COT_NAME = Transport 2
```

## Command-line

Command-line usage is available by running ``aprscot -h``.

```
usage: aprscot [-h] [-c CONFIG_FILE] [-p PREF_PACKAGE]

options:
  -h, --help            show this help message and exit
  -c CONFIG_FILE, --CONFIG_FILE CONFIG_FILE
                        Optional configuration file. Default: config.ini
  -p PREF_PACKAGE, --PREF_PACKAGE PREF_PACKAGE
                        Optional connection preferences package zip file (aka data package).
```

## Run as a service / Run forever

1. Add the text contents below a file named `/etc/systemd/system/aprscot.service`  
  You can use `nano` or `vi` editors: `sudo nano /etc/systemd/system/aprscot.service`
2. Reload systemctl: `sudo systemctl daemon-reload`
3. Enable APRSCOT: `sudo systemctl enable aprscot`
4. Start APRSCOT: `sudo systemctl start aprscot`

### `aprscot.service` Content
```ini
[Unit]
Description=APRSCOT - Display APRS in TAK
Documentation=https://aprscot.rtfd.io
Wants=network.target
After=network.target

[Service]
RuntimeDirectoryMode=0755
ExecStart=/usr/local/bin/aprscot -c /etc/aprscot.ini
SyslogIdentifier=aprscot
Type=simple
Restart=always
RestartSec=30
RestartPreventExitStatus=64
Nice=-5

[Install]
WantedBy=default.target
```

> Pay special attention to the `ExecStart` line above. You'll need to provide the full local filesystem path to both your aprscot executable & aprscot configuration files.
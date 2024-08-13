
To report bugs, please set the DEBUG=1 environment variable to collect logs:

```sh
DEBUG=1 aprscot
```

Or:

```sh linenums="1"
export DEBUG=1
aprscot
```

Or:

```sh linenums="1"
echo 'DEBUG=1' >> aprscot.ini
aprscot -c aprscot.ini
```

You can view systemd/systemctl/service logs via:

```journalctl -fu aprscot```

Please use GitHub issues for support requests. Please note that APRSCOT is free open source software and comes with no warranty. See LICENSE.
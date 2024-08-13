APRSCOT's functionality provided by a command-line program called `aprscot`.

There are several methods of installing APRSCOT. They are listed below, in order of complexity.

## Debian, Ubuntu, Raspberry Pi

Install APRSCOT, and prerequisite packages of [PyTAK](https://pytak.rtfd.io)

```sh linenums="1"
sudo apt update -qq
wget https://github.com/snstac/aprs-python/releases/latest/download/aprslib_latest_all.deb
sudo apt install -f ./aprslib_latest_all.deb
wget https://github.com/snstac/pytak/releases/latest/download/pytak_latest_all.deb
sudo apt install -f ./pytak_latest_all.deb
wget https://github.com/snstac/aprscot/releases/latest/download/aprscot_latest_all.deb
sudo apt install -f ./aprscot_latest_all.deb
```

## Windows, Linux

Install from the Python Package Index (PyPI) [Advanced Users]::

```sh
sudo python3 -m pip install aprscot
```

## Developers

PRs welcome!

```sh linenums="1"
git clone https://github.com/snstac/aprscot.git
cd aprscot/
python3 setup.py install
```

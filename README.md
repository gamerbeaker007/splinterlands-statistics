# Splinterlands Statistics

Main:
[![Flake8](https://gamerbeaker007.github.io/splinterlands-statistics/main/flake8-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/main/flake8/)
[![Tests](https://gamerbeaker007.github.io/splinterlands-statistics/main/junit-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/main/junit/)
[![Tests Coverage](https://gamerbeaker007.github.io/splinterlands-statistics/main/coverage-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/main/coverage/) | branch:
[![Flake8](https://gamerbeaker007.github.io/splinterlands-statistics/branch/flake8-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/branch/flake8/)
[![Tests](https://gamerbeaker007.github.io/splinterlands-statistics/branch/junit-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/branch/junit/)
[![Tests Coverage](https://gamerbeaker007.github.io/splinterlands-statistics/branch/coverage-badge.svg)](https://gamerbeaker007.github.io/splinterlands-statistics/branch/coverage/)

# Instructions

## With executable

* Download executable
* Unzip
* Run spl_statistics_tool_<x>.exe or spl_statistics_tool_<x>.sh
* Browse to http://127.0.0.1:8050
* In the config tab add the accounts you want to monitor
  Tip for windows: to see the console log of the program run this via and command prompt

## With Docker

docker pull gamerbeaker/splinterlands-statistics:latest

### Windows (docker):

<code>docker run --rm -it -v C:\Temp\:/app/store -p 8050:8050 --name splinterlands-statistics
gamerbeaker/splinterlands-statistics:latest</code>
For server mode
<code>docker run --rm -it -v C:\Temp\:/app/store -p 8050:8050 --name splinterlands-statistics
gamerbeaker/splinterlands-statistics:latest -s</code>

### Linux (docker):

<code>docker run --rm -it -v \tmp\:/app/store -p 8050:8050 --name splinterlands-statistics
gamerbeaker/splinterlands-statistics:latest</code>
For server mode
<code>docker run --rm -it -v \tmp\:/app/store -p 8050:8050 --name splinterlands-statistics
gamerbeaker/splinterlands-statistics:latest -s</code>

## With python development or local execution

Download sources and unpack.

Use python 3.8 or higher.
<code>pip install -r requirements.txt
python src/main.py</code>

When installing on a Windows machine and this error given:
<code>scrypt-1.2.1/libcperciva/crypto/crypto_aes.c(6): fatal error C1083: Cannot open include file: 'openssl/aes.h': No
such file or directory</code>
Then install [Win64 OpenSSL](https://slproweb.com/products/Win32OpenSSL.html) (not the light version)

# Result how to use

TODO

NOTE: Sometimes the clipboard icon is not shown when hive blog generated.
This might be caused by insecure connection http instead of https for example with home network local synology.  
For more information: https://community.plotly.com/t/dcc-clipboard-is-not-working-in-my-company-network/55899/13

# Splinterlands Statistics

.. image:: https://github.com/gamerbeaker007/splinterlands-statistics/workflows/main/badge.svg
:target: https://github.com/gamerbeaker007/splinterlands-statistics/actions?query=workflow%3Amain
:alt: build status

.. image:: https://results.pre-commit.ci/badge/github/gamerbeaker007/splinterlands-statistics/main.svg
:target: https://results.pre-commit.ci/latest/github/gamerbeaker007/splinterlands-statistics/main
:alt: pre-commit.ci status

![Flake8](https://img.shields.io/github/workflow/status/gamerbeaker007/splinterlands-statistics/Flake8/main?label=Flake8&logo=github&style=flat-square)

# Instructions

## With executable

* Download executable
* Unzip
* Run main.exe or main.sh
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


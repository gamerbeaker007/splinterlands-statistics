# splinterlands-battle-stats

# Instructions
## With windows executable
* Download windows executable
* Unzip
* Run main.exe
* Browse to http://127.0.0.1:8085 
* In the config tab add the accounts you want to monitor
Tip: to see the console log of the program run this via and command prompt

## With linux executable
* Download linux executable
* Unzip
* ./main.sh
* Browse to http://127.0.0.1:8085 
* In the config tab add the accounts you want to monitor

## With Docker 
<code>docker login ghcr.io --username your_github_username
docker pull ghcr.io/gamerbeaker007/splinterlands-stats-v2:latest</code>

### Windows (docker):
<code>docker run -p 8050:8050 -e "HOST=0.0.0.0" -it -v C:\Temp\:/app/store ghcr.io/gamerbeaker007/splinterlands-stats-v2:latest</code>

### Linux (docker):
<code>docker run -p 8050:8050 -e "HOST=0.0.0.0" -it -v \tmp\:/app/store ghcr.io/gamerbeaker007/splinterlands-stats-v2:latest</code>

## With python development or local execution
Download source and unpack. 
Modify config.properties with your desired information
Use python 3.8 or higher.
<code>pip install -r requirements.txt
python src/main.py</code>

# Result how to use
TODO


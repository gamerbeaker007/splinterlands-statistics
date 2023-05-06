# splinterlands-battle-stats

# Instructions
## With windows executable
* Download windows executable
* Unzip
* Edit config.properties add one or multiple users separated by , <br>Example <code>account_names=beaker007,beakerr</code>
* Run main.exe
Tip: to see the console log of the program run this via and command prompt

## With linux executable
* Download linux executable
* Unzip
* Edit config.properties add one or multiple users separated by , <br>Example <code>account_names=beaker007,beakerr</code>
* ./main.sh

## With Docker 
<code>docker login ghcr.io --username your_github_username
docker pull ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>

### Windows (docker):
<code>docker run -it -v C:\Temp\:/app/output -e "ACCOUNT_NAMES=spl_account_name,spl_name2" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>

### Linux (docker):
<code>docker run -it -v \tmp\:/app/output -e "ACCOUNT_NAMES=spl_account_name,spl_name2" -e "SKIP_ZEROS=True" ghcr.io/gamerbeaker007/splinterlands-stats:latest</code>

## With python development or local execution
Download source and unpack. 
Modify config.properties with your desired information
Use python 3.8 or higher.
<code>pip install -r requirements.txt
python src/main.py</code>

# Result 
The output is located per user in the output directory containing graphs and the post.txt.
With multiple users also combined_post.txt is created in the output directory.


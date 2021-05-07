![Logo](https://github.com/obheda12/GitDorker/blob/master/GitDorker.png)

# GitDorker
GitDorker is a tool that utilizes the GitHub Search API and an extensive list of GitHub dorks that I've compiled from various sources to provide an overview of sensitive information stored on github given a search query. 

The Primary purpose of GitDorker is to provide the user with a clean and tailored attack surface to begin harvesting sensitive information on GitHub. GitDorker can be used with additional tools such as GitRob or Trufflehog on interesting repos or users discovered from GitDorker to produce best results.

## In Depth How to Video and Use Cases
https://youtu.be/UwzB5a5GrZk

## Rate Limits
GitDorker utilizes the GitHub Search API and is limited to 30 requests per minute. In order to prevent rate limites a sleep function is built into GitDorker after every 30 requests to prevent search failures. Therefore, if one were to run use the alldorks.txt file with GitDorker, the process will take roughly 5 minutes to complete. 

## Requirements
** Python3

** GitHub Personal Access Token

** Install requirements inside of the requirements.txt file of this repo (pip3 install -r requirements.txt)

Please follow the guide below if you are unsure of how to create a personal access token:
https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

## Recommendations
It is recommended to provide GitDorker with at least two GitHub personal access tokens so that it may alternate between the two during the dorking process and reduce the likelihood of being rate limited. Using multiple tokens from separate GitHub accounts will provide the best results.

## Dorks
Within the dorks folder are a list of dorks. It is recommended to use the "alldorks.txt" file when mapping out your github secrets attack surface. The "alldorks.txt" is my collection of dorks that i've pulled from various resources, totalling to 239 individual dorks of sensitive github information.

## Usage
I've created a blog post with far more detail in how to use GitDorker and potential use cases here: https://medium.com/@obheda12/gitdorker-a-new-tool-for-manual-github-dorking-and-easy-bug-bounty-wins-92a0a0a6b8d5 

For a full detailed look of use cases and how to use GitDorker's most updated features please see the BlackHat Presentation below:
https://youtu.be/UwzB5a5GrZk

Help Output:

![Help](https://github.com/obheda12/GitDorker/blob/master/GitDorker%20Help.png)

## Docker

```bash

## Build Command
docker build -t gitdorker .

## Basic Run Command
docker run -it gitdorker

## Run Command
docker run -it -v $(pwd)/tf:/tf gitdorker -tf tf/TOKENSFILE -q tesla.com -d dorks/DORKFILE -o tesla

## Run Command
docker run -it -v $(pwd)/tf:/tf xshuden/gitdorker -tf tf/TOKENSFILE -q tesla.com -d dorks/DORKFILE -o tesla

```

## Screenshots
Below is an example of the results from running the query "tesla.com" with a small list of dorks.

The following command was run to query for "tesla.com" against a list of dorks:

`python3 GitDorker.py -tf TOKENSFILE -q tesla.com -d Dorks/DORKFILE -o tesla`

![Results](https://github.com/obheda12/GitDorker/blob/master/GitDorker%20Usage%20Example%20-%20Tesla.png)

Note: The more advanced queries you put (i.e incorporation of user, org, endpoint information, etc. the more succint results you will achieve)

## If you like GitDorker and want to see more cool tools!
<a href="https://www.buymeacoffee.com/obheda12" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

# Credits
Reference points for creating GitDorker and compiling dorks lists

- [@gwendallecoguic](https://github.com/gwen001) - special thank you to gwendall and his scripts that provided me with the framework for creating GitDorker.
- [@techgaun](https://github.com/techgaun) - His list of dorks provided a fantastic base for the dorks file
- [@Shashank-In](https://github.com/Shashank-In) - His list of Travis leaks helped add additional dorks
- [@Jhaddix](https://github.com/jhaddix) - Methodology and reference for dorks

# Disclaimer

This project is made for educational and ethical testing purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. Developers assume no liability and are not responsible for any misuse or damage caused by this tool.

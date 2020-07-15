# GitDorker
GitDorker is a tool that utilizes the GitHub Search API and an extensive list of GitHub dorks that I've compiled from various sources to provide an overview of sensitive information stored on github given a search query. 

The Primary purpose of GitDorker is to provide the user with a clean and tailored attack surface to begin harvesting sensitive information on GitHub. GitDorker can be used with additional tools such as GitRob or Trufflehog on interesting repos or users discovered from GitDorker to produce best results.

## Rate Limits & Runtime
GitDorker utilizes the GitHub Search API and is limited to 30 requests per minute. In order to prevent rate limites a sleep function is built into GitDorker after every 30 requests to prevent search failures. Therefore, if one were to run use the alldorks.txt file with GitDorker, the process will take roughly 5 minutes to complete. 

NOTE: Be careful of multithreading as it may accelerate rate limits. If experiencing issues with rate limits, reduce threads to 1.

## Dorks
Within the dorks folder are a list of dorks. It is recommended to use the "alldorks.txt" file when mapping out your github secrets attack surface. The "alldorks.txt" is my collection of dorks that i've pulled from various resources, totalling to 239 individual dorks of sensitive github information.

## Screenshots
Below is an example of the results from a query ran on "tesla.com" with a few dorks.

![Progress](https://github.com/obheda12/GitDorker/blob/master/GitDorker Usage.png)
![Results](https://github.com/obheda12/GitDorker/blob/master/GitDorker Results.png)


## Usage

``````````
usage: GitDorker.py [-h] [-d DORKS] [-t TOKEN] [-e THREADS] [-q QUERY] [-o ORG]

optional arguments:
  -h, --help            show this help message and exit
  -d DORKS, --dorks DORKS
                        dorks file (required)
  -t TOKEN, --token TOKEN
                        your github token (required)
  -e THREADS, --threads THREADS
                        maximum n threads, default 1
  -q QUERY, --query QUERY
                        query (required or -q)
  -o ORG, --org ORG     organization (required or -o)
``````````

# Credit

Reference points for creating GitDorker

- [@hisxo](https://github.com/hisxo)
- [@gwendallecoguic](https://github.com/gwen001)


# Disclaimer

This project is made for educational and ethical testing purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. Developers assume no liability and are not responsible for any misuse or damage caused by this tool.

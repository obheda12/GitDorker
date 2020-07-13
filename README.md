# GitDorker
GitDorker is a tool that utilizes the GitHub Search API and an extensive list of GitHub dorks that I've compiled from various sources to provide an overview of sensitive information stored on github given a search query. URLs for each dork are provided for the user to visit. This program serves to allow the user to enumerate their GitHub attack surface and utilize programs such as GitRob or Trufflehog on interesting repos or users discovered.

## Notes
GitDorker utilizes the GitHub Search API and is limited to 30 requests per minute. In order to prevent rate limites a sleep function is built into GitDorker after every 30 requests to prevent search failures. Therefore, if one were to run use the alldorks.txt file with GitDorker, the process will take roughly 5 minutes to complete.

This is an ongoing project I plan on building out to incorporate further functionality. Any suggestions are much appreciated. 

## Screenshots



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

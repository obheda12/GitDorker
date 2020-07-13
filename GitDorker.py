#!/usr/bin/python3

# Credits: Modified GitHub Dorker using GitAPI and JHaddix Github Dorks List. API Integration code borrowed and modified from Gwendal Le Coguic's scripts.
# Author: Omar Bheda
# Version: 1.1.2
print("""


  /$$$$$$  /$$   /$$           /$$$$$$$                      /$$                          
 /$$__  $$|__/  | $$          | $$__  $$                    | $$                          
| $$  \__/ /$$ /$$$$$$        | $$  \ $$  /$$$$$$   /$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$ 
| $$ /$$$$| $$|_  $$_/        | $$  | $$ /$$__  $$ /$$__  $$| $$  /$$/ /$$__  $$ /$$__  $$
| $$|_  $$| $$  | $$          | $$  | $$| $$  \ $$| $$  \__/| $$$$$$/ | $$$$$$$$| $$  \__/
| $$  \ $$| $$  | $$ /$$      | $$  | $$| $$  | $$| $$      | $$_  $$ | $$_____/| $$      
|  $$$$$$/| $$  |  $$$$/      | $$$$$$$/|  $$$$$$/| $$      | $$ \  $$|  $$$$$$$| $$      
 \______/ |__/   \___/        |_______/  \______/ |__/      |__/  \__/ \_______/|__/      


Find GitHub Secrets Utilizing GitHub Dorks. Simple to read and simple to chain into other
github credential harvesters such as trufflehog or gitrob.

**Potential Workflow**
Use GitDorker >> Find Juicy Users / Repos >> Run GitRob / TruffleHog on interesting Users / Repos >> $$$PROFIT$$$

EXAMPLE SYNTAX: python3 GitDorker.py -q QUERY -t TOKEN -d PATH/TO/DORKFILE -e 1

RATE LIMIT NOTE: GitHub rate limits searches to 30 dorks every 60 seconds. To avoid 
rate limits, ensure that each dork file fed to GitDorker consists of 30 lines or less. 
You may do a for loop to iterate dork files containing less than 30 requests each but you must 
include a sleep for 60 seconds between each run of GitDorker.

""")

#IMPORTS
import os
import sys
import json
import time
import re
import requests
import argparse
import random
from termcolor import colored
from multiprocessing.dummy import Pool

#API CONFIG
TOKENS_FILE = os.path.dirname(os.path.realpath(__file__)) + '/.tokens'
GITHUB_API_URL = 'https://api.github.com'

#PARSER CONFIG
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dorks", help="dorks file (required)")
parser.add_argument("-t", "--token", help="your github token (required)")
parser.add_argument("-e", "--threads", help="maximum n threads, default 1")
parser.add_argument("-q", "--query", help="query (required or -q)")
parser.add_argument("-o", "--org", help="organization (required or -o)")

parser.parse_args()
args = parser.parse_args()

#DECLARE LISTS
t_tokens = []
t_dorks = []
t_queries = []
t_orgs = []

#ARGUMENT LOGIC
if args.token:
    t_tokens = args.token.split(',')
else:
    if os.path.isfile(TOKENS_FILE):
        fp = open(TOKENS_FILE, 'r')
        for line in fp:
            r = re.search('^([a-f0-9]{40})$', line)
            if r:
                t_tokens.append(r.group(1))

if not len(t_tokens):
    parser.error('auth token is missing')

if args.query:
    t_queries = args.query.split(',')

if args.org:
    t_orgs = args.org.split(',')

if args.threads:
    threads = int(args.threads)
else:
    threads = 1

if not args.query and not args.org:
    parser.error('query or orgnanization missing')

if not args.dorks:
    parser.error('dorks file is missing')

fp = open(args.dorks, 'r')
for line in fp:
    t_dorks.append(line.strip())

#API SEARCH FUNCTION
def githubApiSearchCode(url):
    sys.stdout.write('progress: %d/%d\r' % (t_stats['n_current'], t_stats['n_total_urls']))
    sys.stdout.flush()
    t_stats['n_current'] = t_stats['n_current'] + 1
    i = t_stats['n_current'] % t_stats['l_tokens']
    headers = {"Authorization": "token " + t_tokens[i]}

    try:
        r = requests.get(url, headers=headers, timeout=5)
        json = r.json()
        if t_stats['n_current'] % 29 == 0:
            for remaining in range(65, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(colored("[#] (-_-)zzZZ sleeping to avoid rate limits |{:2d} seconds remaining.".format(remaining), "blue"))
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write(colored("\rContinue Dorking... ;)\n", "blue"))
            # sys.stdout.write(colored("Continue Dorking... ;)", "blue"))
        if 'documentation_url' in json:
            print(colored("[-] error occurred: %s" % json['documentation_url'], 'red'))
        else:
            t_results_urls[url] = json['total_count']

    except Exception as e:
        print(colored("[-] error occurred: %s" % e, 'red'))
        return 0

#URL ENCODING FUNCTION
def __urlencode(str):
    str = str.replace(':', '%3A');
    str = str.replace('"', '%22');
    str = str.replace(' ', '+');
    return str

#DECLARE DICTIONARIES
t_urls = {}
t_results = {}
t_results_urls = {}
t_stats = {
    'l_tokens': len(t_tokens),
    'n_current': 0,
    'n_total_urls': 0
}

#CREATE QUERIES
for query in t_queries:
    t_results[query] = []
    for dork in t_dorks:
        dork = "'{}'".format(query) + " " + dork
        url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
        t_results[query].append(url)
        t_urls[url] = 0

#CREATE ORGS
for org in t_orgs:
    t_results[org] = []
    for dork in t_dorks:
        dork = 'org:' + org + ' ' + dork
        url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
        t_results[org].append( url )
        t_urls[url] = 0

#STATS
t_stats['n_total_urls'] = len(t_urls)
print("-----------------------")
print("""
   ______       __    
  / __/ /____ _/ /____
 _\ \/ __/ _ `/ __(_-<
/___/\__/\_,_/\__/___/
**********************
""")
print("")
sys.stdout.write(colored('[#] %d orgs found.\n' % len(t_orgs), 'cyan'))
sys.stdout.write(colored('[#] %d dorks found.\n' % len(t_dorks), 'cyan'))
sys.stdout.write(colored('[#] %d queries ran.\n' % len(t_queries), 'cyan'))
sys.stdout.write(colored('[#] %d urls generated.\n' % len(t_urls), 'cyan'))
sys.stdout.write(colored('[#] running %d threads.\n' % threads, 'cyan'))
print("")
print("-----------------------")
print("")
#SLEEP
time.sleep(1)

#POOL FUNCTION TO RUN API SEARCH
pool = Pool(threads)
pool.map(githubApiSearchCode, t_urls)
pool.close()
pool.join()

#SET COUNT
count = 0

#SHOW RESULTS
print("")
print("""
   ___               ____    
  / _ \___ ___ __ __/ / /____
 / , _/ -_|_-</ // / / __(_-<
/_/|_|\__/___/\_,_/_/\__/___/
*****************************
""")
print("")
for query in t_queries:
    print("QUERY PROVIDED: " + '>>>>> %s\n' % query)
    for url in t_results[query]:
        if url in t_results_urls:
            url2 = '| DORK = ' + t_dorks[count] + ' | ' + url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            count = count + 1
            if t_results_urls[url] == 0:
                sys.stdout.write(colored('%s (%d)\n' % (url2, t_results_urls[url]), 'white'))
            else:
                sys.stdout.write(colored('%s (%d)\n' % (url2, t_results_urls[url]), 'green'))
        else:
            sys.stdout.write(colored('%s\n' % url2, 'red'))
            count = count - 1
            #Potentially code in removal from list to prevent query offset
    print('')

for org in t_orgs:
    print("QUERY PROVIDED: " + '>>>>> %s\n' % org)
    for url in t_results[org]:
        if url in t_results_urls:
            url2 = '| DORK = ' + t_dorks[count] + ' | ' + url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            count = count + 1
            if t_results_urls[url] == 0:
                sys.stdout.write(colored('%s (%d)\n' % (url2, t_results_urls[url]), 'white'))
            else:
                sys.stdout.write(colored('%s (%d)\n' % (url2, t_results_urls[url]), 'green'))
        else:
            sys.stdout.write(colored('%s\n' % url2, 'red'))
            count = count - 1
            #Potentially code in removal from list to prevent query offset
    print('')

#COMPLETION BANNER
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("")
print("             Dorking Complete! Visit your result queries to see if anything juicy returned :) ")
print("")
print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
print("")

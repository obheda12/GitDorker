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

EXAMPLE SYNTAX: python3 GitDorker.py -q DOMAIN -t TOKEN -d PATH/TO/DORKFILE -e 1

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
import argparse
import random
import re
import requests
import csv
from itertools import zip_longest
from itertools import cycle
from termcolor import colored
from multiprocessing.dummy import Pool
from beautifultable import BeautifulTable

#API CONFIG
# TOKENS_FILE = os.path.dirname(os.path.realpath(__file__))
GITHUB_API_URL = 'https://api.github.com'

#PARSER CONFIG
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dorks", help="dorks file (required)")
parser.add_argument("-t", "--token", help="your github token (required)")
parser.add_argument("-tf", "--tokenfile", help="file containing new line separated github tokens ")
parser.add_argument("-e", "--threads", help="maximum n threads, default 1")
parser.add_argument("-q", "--query", help="query (required or -q)")
parser.add_argument("-org", "--organization", help="organization (required or -org)")
parser.add_argument("-o", "--output", help="output to file name (required or -o)")

parser.parse_args()
args = parser.parse_args()

#DECLARE LISTS
t_tokens = []
t_dorks = []
t_queries = []
t_organizations = []

rows = []

#ARGUMENT LOGIC
if args.token:
    t_tokens = args.token.split(',')

if args.tokenfile:
    with open(args.tokenfile) as f:
        t_tokens = f.read().splitlines()

if not len(t_tokens):
    parser.error('auth token is missing')

if args.query:
    t_queries = args.query.split(',')

if args.organization:
    t_organizations = args.organization.split(',')

if args.threads:
    threads = int(args.threads)
else:
    threads = 1

if not args.query and not args.organization:
    parser.error('query or organization missing')

if not args.dorks:
    parser.error('dorks file is missing')

fp = open(args.dorks, 'r')
for line in fp:
    t_dorks.append(line.strip())

#TOKEN ROUND ROBIN
n = -1
def token_round_robin():
    global n
    n = n + 1
    if n == len(t_tokens):
        n = 0
    current_token = t_tokens[n]
    return current_token

#API SEARCH FUNCTION
def api_search(url):
    sys.stdout.write(colored('[#] Dorking Progress: %d/%d\r' % (t_stats['n_current'], t_stats['n_total_urls']), "blue"))
    sys.stdout.flush()
    t_stats['n_current'] = t_stats['n_current'] + 1
    # i = t_stats['n_current'] % t_stats['l_tokens']
    #TODO Implement Round Robin With Tokens
    headers = {"Authorization": "token " + token_round_robin()}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        json = r.json()

        if t_stats['n_current'] % 29 == 0:
            for remaining in range(67, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(colored("[#] (-_-)zzZZ sleeping to avoid rate limits |{:2d} seconds remaining.".format(remaining), "blue"))
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write(colored("[#] ٩(ˊᗜˋ*) Sleeping Finished! GitDorker Is Wide Awake. Continuing Dorking Process............ و\n", "green"))
        if 'documentation_url' in json:
            print(colored("[-] error occurred: %s" % json['documentation_url'], 'red'))
        else:
            t_results_urls[url] = json['total_count']

    except Exception as e:
        print(colored("[-] error occurred: %s" % e, 'red'))
        for remaining in range(67, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write(
                colored("[#] (-_-)zzZZ sleeping due to error |{:2d} seconds remaining.".format(remaining), "blue"))
            sys.stdout.flush()
            time.sleep(1)
            #TODO: Redo Sleeping Output to Console
            sys.stdout.write(colored("\r[#] Sleeping Finished! GitDorker is wide awake. Continuing... ٩(ˊᗜˋ*)و\n", "green"))
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
        #IF SUBDOMAIN IS ENTERED SURROUND QUERY IN QUOTES
        if ".com" in query:
            dork = "'{}'".format(query) + " " + dork
        else:
            dork = "{}".format(query) + " " + dork
        url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
        t_results[query].append(url)
        t_urls[url] = 0

#CREATE ORGS
for organization in t_organizations:
    t_results[organization] = []
    for dork in t_dorks:
        dork = 'org:' + organization + ' ' + dork
        url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
        t_results[organization].append( url )
        t_urls[url] = 0

#STATS
t_stats['n_total_urls'] = len(t_urls)
print("""
   ______       __    
  / __/ /____ _/ /____
 _\ \/ __/ _ `/ __(_-<
/___/\__/\_,_/\__/___/
**********************
""")
sys.stdout.write(colored('[#] %d organizations found.\n' % len(t_organizations), 'cyan'))
sys.stdout.write(colored('[#] %d dorks found.\n' % len(t_dorks), 'cyan'))
sys.stdout.write(colored('[#] %d queries ran.\n' % len(t_queries), 'cyan'))
sys.stdout.write(colored('[#] %d urls generated.\n' % len(t_urls), 'cyan'))
sys.stdout.write(colored('[#] running %d threads.\n' % threads, 'cyan'))
print("")
#SLEEP
time.sleep(1)

#POOL FUNCTION TO RUN API SEARCH
pool = Pool(threads)
pool.map(api_search, t_urls)
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

new_url_list = []
result_number_list = []
dork_name_list = []

#DEFINE CONDITIONAL OUTPUT MARKERS
sys.stdout.write(colored('[+] SUCCESS | RESULTS RETURNED ', 'green'))
print("")
normal = sys.stdout.write(colored('[#] NEUTRAL | NO RESULTS RETURNED', 'yellow'))
print("")
failure = sys.stdout.write(colored('[-] FAILURE | RATE LIMITS OR API FAILURE ', 'red'))
print("")

#RESULTS LOGIC FOR QUERIES
for query in t_queries:
    print("")
    sys.stdout.write(colored('QUERY PROVIDED: %s' % (query), 'cyan'))
    print("")

    for url in t_results[query]:

        if url in t_results_urls:
            new_url = url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            dork_name = t_dorks[count]
            dork_info = 'DORK = ' + dork_name + ' | '
            result_info = dork_info + new_url
            # new_url = '| DORK = ' + t_dorks[count] + ' | ' + url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            count = count + 1

            if t_results_urls[url] == 0:
                result_number = t_results_urls[url]
                normal = sys.stdout.write(colored('[#] ', 'yellow'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)

            else:
                result_number = t_results_urls[url]
                success = sys.stdout.write(colored('[+] ', 'green'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)

        else:
            failure = sys.stdout.write(colored('[-] ', 'red'))
            sys.stdout.write(colored('%s' % new_url, 'white'))
            count = count + 1
            # Potentially code in removal from list to prevent query offset
        print('')

#RESULTS LOGIC FOR ORGANIZATIONS
for organization in t_organizations:
    print("ORGANIZTION PROVIDED: " + '%s' % organization)
    print("")

    for url in t_results[organization]:

        if url in t_results_urls:
            new_url = url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            dork_name = t_dorks[count]
            dork_info = ' DORK = ' + dork_name + ' | '
            result_info = dork_info + new_url
            # new_url = '| DORK = ' + t_dorks[count] + ' | ' + url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            count = count + 1

            if t_results_urls[url] == 0:
                result_number = t_results_urls[url]
                normal = sys.stdout.write(colored('[#] ', 'yellow'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)

            else:
                result_number = t_results_urls[url]
                success = sys.stdout.write(colored('[+] ', 'green'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)

        else:
            failure = sys.stdout.write(colored('[-] ', 'red'))
            sys.stdout.write(colored('%s' % new_url, 'white'))
            count = count + 1
            # Potentially code in removal from list to prevent query offset
        print('')

#CSV OUTPUT TO FILE
if args.output:
    file_name = args.output
    rows = zip(dork_name_list, new_url_list, result_number_list)
    fields = ['DORK', 'URL', 'NUMBER OF RESULTS']
    #TODO: Make output argument specific
    with open(query + '.csv', "w") as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(fields)
        for row in rows:
            wr.writerow(row)
    csvfile.close()
    print("")
    sys.stdout.write(colored("Results have been outputted into the current working directory as " + file_name + ".csv", 'green'))
    print("")
    print("")





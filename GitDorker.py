#!/usr/bin/python3

# Credits: Modified GitHub Dorker using GitAPI and JHaddix Github Dorks List. API Integration code borrowed and modified from Gwendal Le Coguic's scripts.
# Author: Omar Bheda
# Version: 2.1.2
print("""


  /$$$$$$  /$$   /$$           /$$$$$$$                      /$$                          
 /$$__  $$|__/  | $$          | $$__  $$                    | $$                          
| $$  \__/ /$$ /$$$$$$        | $$  \ $$  /$$$$$$   /$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$ 
| $$ /$$$$| $$|_  $$_/        | $$  | $$ /$$__  $$ /$$__  $$| $$  /$$/ /$$__  $$ /$$__  $$
| $$|_  $$| $$  | $$          | $$  | $$| $$  \ $$| $$  \__/| $$$$$$/ | $$$$$$$$| $$  \__/
| $$  \ $$| $$  | $$ /$$      | $$  | $$| $$  | $$| $$      | $$_  $$ | $$_____/| $$      
|  $$$$$$/| $$  |  $$$$/      | $$$$$$$/|  $$$$$$/| $$      | $$ \  $$|  $$$$$$$| $$      
 \______/ |__/   \___/        |_______/  \______/ |__/      |__/  \__/ \_______/|__/      


Find GitHub secrets utilizing a vast list of GitHub dorks and the GitHub search api. The 
purpose of this tool is to enumerate interesting users,repos, and files to provide an 
easy to read overview of where a potential sensitive information exposure may reside.

HELP: python3 GitDorker.py -h
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

#API CONFIG
GITHUB_API_URL = 'https://api.github.com'

#PARSER CONFIG
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dorks", help="dorks file (required)")
parser.add_argument("-k", "--keyword", help="search on a keyword instead of a list of dorks")
parser.add_argument("-q", "--query", help="query (required or -q)")
parser.add_argument("-u", "--users", help="users to perform dork or keyword search on (comma separated).")
parser.add_argument("-uf", "--userfile", help="file containing new line separated users")
parser.add_argument("-org", "--organization", help="organization's GitHub name (required or -org if query not specified)")
parser.add_argument("-t", "--token", help="your github token (required if token file not specififed)")
parser.add_argument("-tf", "--tokenfile", help="file containing new line separated github tokens ")
parser.add_argument("-e", "--threads", help="maximum n threads, default 1")
parser.add_argument("-o", "--output", help="output to file name (required or -o)")
parser.parse_args()
args = parser.parse_args()

#DECLARE LISTS
t_tokens = []
t_dorks = []
t_queries = []
t_organizations = []
t_users = []
t_keywords = []
# rows = []

#TOKEN ARGUMENT LOGIC
if args.token:
    t_tokens = args.token.split(',')

if args.tokenfile:
    with open(args.tokenfile) as f:
        t_tokens = f.read().splitlines()

if not len(t_tokens):
    parser.error('auth token is missing')

#USER ARGUMENT LOGIC
if args.users:
    t_users = args.users.split(',')

if args.userfile:
    with open(args.userfile) as f:
        t_users = f.read().splitlines()

# if args.query and args.user:
#     parser.error('you cannot specify both a query and a user, please specify one or the other.')
#
# if args.query and args.userfile:
#     parser.error('you cannot specify both a query and a user, please specify one or the other.')

if args.query:
    t_queries = args.query.split(',')

if args.query and args.keyword:
    parser.error('you cannot specify both a query and a keyword, please specify one or the other.')

# if args.query and args.user:
#     parser.error('you cannot specify both a query and a user, please specify one or the other.')

if args.query and args.organization:
    parser.error('you cannot specify both a query and a organization, please specify one or the other.')

if args.organization:
    t_organizations = args.organization.split(',')

if args.threads:
    threads = int(args.threads)
else:
    threads = 1

if not args.query and not args.organization and not args.users and not args.userfile:
    parser.error('query or organization missing or users missing')

if args.dorks:
    fp = open(args.dorks, 'r')
    for line in fp:
        t_dorks.append(line.strip())

if args.keyword:
    t_keywords = args.keyword.split(',')

# if args.dorks and args.keyword:
#     parser.error('you cannot specify both dorks and keywords, please only specify one or the other.')

if not args.dorks and not args.keyword:
    parser.error('dorks file or keyword is missing')


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
    if args.dorks: #UNDO COMPLETE! :)
        if args.keyword:
            sys.stdout.write(colored('[#] Dorking with Keyword In Progress: %d/%d\r' % (t_stats['n_current'], t_stats['n_total_urls']),"blue"))
        else:
            sys.stdout.write(colored('[#] Dorking In Progress: %d/%d\r' % (t_stats['n_current'], t_stats['n_total_urls']),"blue"))
            sys.stdout.flush()
        # t_stats['n_current'] = t_stats['n_current'] + 1

        #TODO Implement Round Robin With Tokens
        # headers = {"Authorization": "token " + token_round_robin()}
    elif args.keyword and not args.dorks:
        sys.stdout.write(colored('[#] Keyword Search In Progress: %d/%d\r' % (t_stats['n_current'], t_stats['n_total_urls']), "blue"))
        sys.stdout.flush()

    t_stats['n_current'] = t_stats['n_current'] + 1
    headers = {"Authorization": "token " + token_round_robin()}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        json = r.json()

        if t_stats['n_current'] % 29 == 0:
            for remaining in range(67, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write(colored("[#] (-_-)zzZZ sleeping to avoid rate limits. GitDorker will resume soon | {:2d} seconds remaining.".format(remaining), "blue"))
                sys.stdout.flush()
                time.sleep(1)
            print("")
            sys.stdout.write(colored("\n[#] ٩(ˊᗜˋ*)و Sleeping Finished! GitDorker Is Wide Awake. Continuing Dorking Process............", "green"))

        if 'documentation_url' in json:
            print(colored("[-] error occurred: %s" % json['documentation_url'], 'red'))
        else:
            t_results_urls[url] = json['total_count']

    except Exception as e:
        print(colored("[-] error occurred: %s" % e, 'red'))
        # for remaining in range(67, 0, -1):
        #     sys.stdout.write("\r")
        #     sys.stdout.write(colored("[#] (-_-)zzZZ sleeping to avoid rate limits. GitDorker will resume soon | {:2d} seconds remaining.".format(remaining), "blue"))
        #     sys.stdout.flush()
        #     time.sleep(1)
        #     #TODO: Redo Sleeping Output to Console
        #     print("")
        #     sys.stdout.write(colored("\r[#] ٩(ˊᗜˋ*)و Sleeping Finished! GitDorker Is Wide Awake. Continuing Dorking Process............", "green"))
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

for user in t_users:
    t_results[user] = []
    if args.dorks:
        if args.keyword:
            for dork in t_dorks:
                for keyword in t_keywords:
                    keyword_dork = 'user:' + user + ' ' + keyword + ' ' + dork
                    print(dork)
                    url = 'https://api.github.com/search/code?q=' + __urlencode(keyword_dork)
                    t_results[user].append( url )
                    t_urls[url] = 0

    if not args.keyword:
        for dork in t_dorks:
            dork = 'user:' + user + ' ' + dork
            print(dork)
            url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
            t_results[user].append( url )
            t_urls[url] = 0

    if args.keyword and not args.dorks:
        for keyword in t_keywords:
            keyword = 'user:' + user + ' ' + keyword
            url = 'https://api.github.com/search/code?q=' + __urlencode(keyword)
            t_results[user].append(url)
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
sys.stdout.write(colored('[#] %d users found.\n' % len(t_users), 'cyan'))
sys.stdout.write(colored('[#] %d dorks found.\n' % len(t_dorks), 'cyan'))
sys.stdout.write(colored('[#] %d keywords found.\n' % len(t_keywords), 'cyan'))
sys.stdout.write(colored('[#] %d queries ran.\n' % len(t_queries), 'cyan'))
sys.stdout.write(colored('[#] %d urls generated.\n' % len(t_urls), 'cyan'))
sys.stdout.write(colored('[#] %d tokens being used.\n' % len(t_tokens), 'cyan'))
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
keyword_count = 0

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
keyword_name_list = []
user_list = []

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
    print("")

    for url in t_results[query]:

        if url in t_results_urls:
            new_url = url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            dork_name = t_dorks[count]
            dork_info = 'DORK = ' + dork_name + ' | '
            result_info = dork_info + new_url
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

#ADD KEYWORD TO OUTPUT TO BOTH DORKS AND ARGS
for user in t_users:
    print("")
    sys.stdout.write(colored('USER PROVIDED: %s' % (user), 'cyan'))
    print("")

    if args.keyword and not args.dorks:
        for url in t_results[user]:
            if url in t_results_urls:
                new_url = url.replace('https://api.github.com/search/code','https://github.com/search') + '&s=indexed&type=Code&o=desc'
                keyword_name = t_keywords[keyword_count]
                keyword_info = 'KEYWORD = ' + keyword_name + ' | '
                result_info = keyword_info + new_url
                if len(t_keywords) - 1 != keyword_count:
                    keyword_count = keyword_count + 1
                else:
                    keyword_count = 0

                if t_results_urls[url] == 0:
                    result_number = t_results_urls[url]
                    normal = sys.stdout.write(colored('[#] ', 'yellow'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    keyword_name_list.append(keyword_name)
                    user_list.append(user)

                else:
                    result_number = t_results_urls[url]
                    success = sys.stdout.write(colored('[+] ', 'green'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    keyword_name_list.append(keyword_name)
                    user_list.append(user)

            else:
                failure = sys.stdout.write(colored('[-] ', 'red'))
                sys.stdout.write(colored('%s' % new_url, 'white'))
                if len(t_keywords) - 1 != keyword_count:
                    keyword_count = keyword_count + 1
                else:
                    keyword_count = 0
                # Potentially code in removal from list to prevent query offset
            print('')


    elif args.dorks:
        for url in t_results[user]:
            if url in t_results_urls:
                new_url = url.replace('https://api.github.com/search/code', 'https://github.com/search') + '&s=indexed&type=Code&o=desc'
                dork_name = t_dorks[count]

                if args.keyword:
                    keyword_name = t_keywords[keyword_count]
                    dork_info = 'DORK = ' + dork_name + ' | KEYWORD = ' + keyword_name + ' | '
                    if len(t_keywords) - 1 != keyword_count:
                        keyword_count = keyword_count + 1
                    else:
                        keyword_count = 0
                        count = count + 1

                elif not args.keyword:
                    count = count + 1

                # if args.keyword:
                #     dork_info = 'DORK = '  + dork_name + ' | KEYWORD = ' + keyword_name + ' | '
                #     if len(t_keywords) - 1 != keyword_count:
                #         keyword_count = keyword_count + 1
                #     else:
                #         keyword_count = 0
                #         count = count + 1
                    dork_info = 'DORK = ' + dork_name + ' | '
                    result_info = dork_info + new_url
                    
                if len(t_dorks) == count:
                    count = 0


                if t_results_urls[url] == 0:
                    result_number = t_results_urls[url]
                    normal = sys.stdout.write(colored('[#] ', 'yellow'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    dork_name_list.append(dork_name)
                    if args.keyword:
                        keyword_name_list.append(keyword_name)
                    user_list.append(user)

                else:
                    result_number = t_results_urls[url]
                    success = sys.stdout.write(colored('[+] ', 'green'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    dork_name_list.append(dork_name)
                    if args.keyword:
                        keyword_name_list.append(keyword_name)
                    user_list.append(user)

            else:
                failure = sys.stdout.write(colored('[-] ', 'red'))
                sys.stdout.write(colored('%s' % new_url, 'white'))
                if args.keyword:
                    if len(t_keywords) - 1 != keyword_count:
                        keyword_count = keyword_count + 1
                count = count + 1
                if len(t_dorks) == count:
                    count = 0
                # Potentially code in removal from list to prevent query offset
            print('')


#RESULTS LOGIC FOR ORGANIZATIONS
for organization in t_organizations:
    print("ORGANIZATION PROVIDED: " + '%s' % organization)
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
    #FILE NAME USER INPUT
    file_name = args.output

    #DEFINE ROWS FOR KEYWORDS AND WITHOUT
    query_with_dorks_rows = zip(dork_name_list, new_url_list, result_number_list)
    user_with_keyword_only_rows = zip(user_list, keyword_name_list, new_url_list, result_number_list)
    user_with_keyword_and_dorks_rows = zip(user_list, dork_name_list, keyword_name_list, new_url_list, result_number_list)
    user_with_dorks_only_rows = zip(user_list, dork_name_list, new_url_list, result_number_list)

    #DEFINE FIELDS FOR KEYWORDS AND WITHOUT
    query_with_dorks_fields = ['DORK', 'URL', 'NUMBER OF RESULTS']
    user_with_keyword_only_fields = ['USER', 'KEYWORD', 'URL', 'NUMBER OF RESULTS']
    user_with_keyword_and_dorks_fields = ['USER', 'DORK', 'KEYWORD', 'URL', 'NUMBER OF RESULTS']
    user_with_dorks_only_fields = ['USER', 'DORK', 'URL', 'NUMBER OF RESULTS']

    #OUTPUT FOR ROWS WITH KEYWORDS AND DORKS
    with open(file_name + '.csv', "w") as csvfile:
        wr = csv.writer(csvfile)
        if args.query:
            wr.writerow(query_with_dorks_fields)
            for row in query_with_dorks_rows:
                wr.writerow(row)
        elif args.users or args.userfile:
            if args.keyword and args.dorks:
                wr.writerow(user_with_keyword_and_dorks_fields)
                for row in user_with_keyword_and_dorks_rows:
                    wr.writerow(row)
            elif args.keyword and not args.dorks:
                wr.writerow(user_with_keyword_only_fields)
                for row in user_with_keyword_only_rows:
                    wr.writerow(row)
            elif args.dorks and not args.keyword:
                wr.writerow(user_with_dorks_only_fields)
                for row in user_with_dorks_only_rows:
                    wr.writerow(row)

    # if args.keyword and args.dorks:
    #     with open(file_name + '.csv', "w") as csvfile:
    #         wr = csv.writer(csvfile)
    #         wr.writerow(all_fields)
    #         for row in all_rows:
    #             wr.writerow(row)
    #
    # #OUTPUT FOR ROWS WITH KEYWORDS ONLY
    # elif args.keywords and not args.dorks:
    #     with open(file_name + '.csv', "w") as csvfile:
    #         wr = csv.writer(csvfile)
    #         wr.writerow(keyword_only_fields)
    #         for row in keyword_only_rows:
    #             wr.writerow(row)
    #
    # #OUTPUT FOR ROWS WITHOUT KEYWORD FIELD
    # else:
    #     with open(file_name + '.csv', "w") as csvfile:
    #         wr = csv.writer(csvfile)
    #         wr.writerow(dork_only_fields)
    #         for row in dork_only_rows:
    #             wr.writerow(row)

    csvfile.close()
    print("")
    sys.stdout.write(colored("Results have been outputted into the current working directory as " + file_name + ".csv", 'green'))
    print("")
    print("")

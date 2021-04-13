#!/usr/bin/python3

# Credits: Modified GitHub Dorker using GitAPI and my personal compiled list of dorks across multiple resources. API Request structure modeled and modified and modified from Gwendal Le Coguic's scripts.
# Author: Omar Bheda
# Version: 1.1.3
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

# IMPORTS
import sys
import json
import time
import argparse
import random
import requests
import csv
from itertools import zip_longest
from termcolor import colored
from multiprocessing.dummy import Pool

# API CONFIG
GITHUB_API_URL = 'https://api.github.com'

# PARSER CONFIG
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dorks", help="dorks file (required)")
parser.add_argument("-k", "--keyword", help="search on a keyword instead of a list of dorks")
parser.add_argument("-q", "--query", help="query (required or -q)")
parser.add_argument("-qf", "--queryfile", help="query (required or -q)")
parser.add_argument("-ri", "--recentlyindexed", action='store_true', help="sort results of queries from most recent first")
parser.add_argument("-lb", "--limitbypass", action='store_true', help="increase requests per minute when using multiple tokens from UNIQUE accounts")
parser.add_argument("-pf", "--patternfilter", action='store_true', help="filter out noise/patterns for test/example keys")
parser.add_argument("-u", "--users", help="users to perform dork or keyword search on (comma separated).")
parser.add_argument("-uf", "--userfile", help="file containing new line separated users")
parser.add_argument("-org", "--organization",
                    help="organization's GitHub name (required or -org if query not specified)")
parser.add_argument("-t", "--token", help="your github token (required if token file not specififed)")
parser.add_argument("-tf", "--tokenfile", help="file containing new line separated github tokens ")
parser.add_argument("-e", "--threads", help="maximum n threads, default 1")
parser.add_argument("-p", "--positiveresults", action='store_true', help="display positive results only")
parser.add_argument("-o", "--output", help="output to file name (required or -o)")

parser.parse_args()
args = parser.parse_args()

# DECLARE LISTS
tokens_list = []
dorks_list = []
queries_list = []
organizations_list = []
users_list = []
keywords_list = []

# TOKEN ARGUMENT LOGIC
if args.token:
    tokens_list = args.token.split(',')

if args.tokenfile:
    with open(args.tokenfile) as f:
        tokens_list = [i.strip() for i in f.read().splitlines() if i.strip()]

# if not len(tokens_list):
#     parser.error('auth token is missing')

# USER ARGUMENT LOGIC
if args.users:
    users_list = args.users.split(',')

if args.userfile:
    with open(args.userfile) as f:
        users_list = [i.strip() for i in f.read().splitlines() if i.strip()]

if args.query:
    queries_list = args.query.split(',')

if args.queryfile:
    with open(args.queryfile) as f:
        queries_list = [i.strip() for i in f.read().splitlines() if i.strip()]

if args.patternfilter:
    patternfilter = " -fake -example -test -XXXX -1234 -ABCD"

# if args.query and args.keyword:
#     parser.error('you cannot specify both a query and a keyword, please specify one or the other.')
#
# if args.query and args.organization:
#     parser.error('you cannot specify both a query and a organization, please specify one or the other.')

if args.organization:
    organizations_list = args.organization.split(',')

if args.threads:
    threads = int(args.threads)
else:
    threads = 1

# if not args.query and not args.queryfile and not args.organization and not args.users and not args.userfile:
#     parser.error('query or organization missing or users missing')

if args.dorks:
    fp = open(args.dorks, 'r')
    for line in fp:
        dorks_list.append(line.strip())

if args.keyword:
    keywords_list = args.keyword.split(',')

if not args.dorks and not args.keyword:
    parser.error('dorks file or keyword is missing')

# NUMBER OF REQUESTS PER MINUTE (TOKENS MUST BE UNIQUE)
requests_per_minute = (len(tokens_list) * 30) - 1

# TOKEN ROUND ROBIN
n = -1


def token_round_robin():
    global n
    n = n + 1
    if n == len(tokens_list):
        n = 0
    current_token = tokens_list[n]
    return current_token


# API SEARCH FUNCTION
def api_search(url):
    if args.dorks:  # UNDO COMPLETE! :)
        if args.keyword:
            sys.stdout.write(colored(
                '\r[#] $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Dorking with Keyword In Progress $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ %d/%d\r' % (stats_dict['n_current'], stats_dict['n_total_urls']),
                "green"))
            sys.stdout.flush()
        else:
            sys.stdout.write(
                colored('\r[#] $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Dorking In Progress $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  %d/%d\r' % (stats_dict['n_current'], stats_dict['n_total_urls']), "green"))
            sys.stdout.flush()

    elif args.keyword and not args.dorks:
        sys.stdout.write(
            colored('\r[#] $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ Keyword Search In Progress $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ %d/%d\r' % (stats_dict['n_current'], stats_dict['n_total_urls']),
                    "green"))
        sys.stdout.flush()

    stats_dict['n_current'] = stats_dict['n_current'] + 1
    headers = {"Authorization": "token " + token_round_robin()}

    try:
        r = requests.get(url, headers=headers)
        json = r.json()
        if args.limitbypass:
            if stats_dict['n_current'] % requests_per_minute == 0:
                for remaining in range(63, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write(colored(
                        "\r[#] (-_-)zzZZzzZZzzZZzzZZ sleeping to avoid rate limits. GitDorker will resume soon (-_-)zzZZzzZZzzZZzzZZ | {:2d} seconds remaining.\r".format(
                            remaining), "blue"))
                    sys.stdout.flush()
                    time.sleep(1)
        else:
            if stats_dict['n_current'] % 29 == 0:
                for remaining in range(63, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write(colored(
                        "\r[#] (-_-)zzZZzzZZzzZZzzZZ sleeping to avoid rate limits. GitDorker will resume soon (-_-)zzZZzzZZzzZZzzZZ | {:2d} seconds remaining.\r".format(
                            remaining), "blue"))
                    sys.stdout.flush()
                    time.sleep(1)

        if 'documentation_url' in json:
            print(colored("[-] error occurred: %s" % json['documentation_url'], 'red'))
        else:
            url_results_dict[url] = json['total_count']

    except Exception as e:
        print(colored("[-] error occurred: %s" % e, 'red'))
        return 0


# URL ENCODING FUNCTION
def __urlencode(str):
    str = str.replace(':', '%3A');
    str = str.replace('"', '%22');
    str = str.replace(' ', '+');
    return str


# DECLARE DICTIONARIES
url_dict = {}
results_dict = {}
url_results_dict = {}
stats_dict = {
    'l_tokens': len(tokens_list),
    'n_current': 0,
    'n_total_urls': 0
}

# CREATE QUERIES
for query in queries_list:
    results_dict[query] = []
    for dork in dorks_list:
        if not args.patternfilter:
            if ":" in query:
                dork = "{}".format(query) + " " + dork
            else:
                dork = "{}".format(query) + " " + dork
            url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
            results_dict[query].append(url)
            url_dict[url] = 0
        else:
            if ":" in query:
                dork = "{}".format(query) + " " + dork + patternfilter
            else:
                dork = "{}".format(query) + " " + dork + patternfilter
            url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
            results_dict[query].append(url)
            url_dict[url] = 0



# CREATE ORGS
for organization in organizations_list:
    results_dict[organization] = []
    for dork in dorks_list:
        if not args.patternfilter:
            dork = 'org:' + organization + ' ' + dork
            url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
            results_dict[organization].append(url)
            url_dict[url] = 0
        else:
            dork = 'org:' + organization + ' ' + dork + patternfilter
            url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
            results_dict[organization].append(url)
            url_dict[url] = 0

#Create Users
for user in users_list:
    results_dict[user] = []
    if args.dorks:
        if args.keyword:
            for dork in dorks_list:
                for keyword in keywords_list:
                    if not args.patternfilter:
                        keyword_dork = 'user:' + user + ' ' + keyword + ' ' + dork
                        url = 'https://api.github.com/search/code?q=' + __urlencode(keyword_dork)
                        results_dict[user].append(url)
                        url_dict[url] = 0
                    else:
                        keyword_dork = 'user:' + user + ' ' + keyword + ' ' + dork + patternfilter
                        url = 'https://api.github.com/search/code?q=' + __urlencode(keyword_dork)
                        results_dict[user].append(url)
                        url_dict[url] = 0

    if not args.keyword:
        for dork in dorks_list:
            if not args.patternfilter:
                dork = 'user:' + user + ' ' + dork
                url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
                results_dict[user].append(url)
                url_dict[url] = 0
            else:
                dork = 'user:' + user + ' ' + dork + patternfilter
                url = 'https://api.github.com/search/code?q=' + __urlencode(dork)
                results_dict[user].append(url)
                url_dict[url] = 0

    if args.keyword and not args.dorks:
        for keyword in keywords_list:
            if not args.patternfilter:
                keyword = 'user:' + user + ' ' + keyword
                url = 'https://api.github.com/search/code?q=' + __urlencode(keyword)
                results_dict[user].append(url)
                url_dict[url] = 0
            else:
                keyword = 'user:' + user + ' ' + keyword + patternfilter
                url = 'https://api.github.com/search/code?q=' + __urlencode(keyword)
                results_dict[user].append(url)
                url_dict[url] = 0

# STATS
stats_dict['n_total_urls'] = len(url_dict)
print("""
   ______       __
  / __/ /____ _/ /____
 _\ \/ __/ _ `/ __(_-<
/___/\__/\_,_/\__/___/
**********************
""")
sys.stdout.write(colored('[#] %d organizations found.\n' % len(organizations_list), 'cyan'))
sys.stdout.write(colored('[#] %d users found.\n' % len(users_list), 'cyan'))
sys.stdout.write(colored('[#] %d dorks found.\n' % len(dorks_list), 'cyan'))
sys.stdout.write(colored('[#] %d keywords found.\n' % len(keywords_list), 'cyan'))
sys.stdout.write(colored('[#] %d queries ran.\n' % len(queries_list), 'cyan'))
sys.stdout.write(colored('[#] %d urls generated.\n' % len(url_dict), 'cyan'))
sys.stdout.write(colored('[#] %d tokens being used.\n' % len(tokens_list), 'cyan'))
sys.stdout.write(colored('[#] running %d threads.\n' % threads, 'cyan'))
if args.limitbypass:
    sys.stdout.write(colored('[#] %d requests per minute allowed\n' % requests_per_minute, 'cyan'))
else:
    sys.stdout.write(colored('[#] 29 requests per minute allowed\n', 'cyan'))
print("")
# SLEEP
time.sleep(1)

# POOL FUNCTION TO RUN API SEARCH
pool = Pool(threads)
pool.map(api_search, url_dict)
pool.close()
pool.join()

# SET COUNT
count = 0
keyword_count = 0

# SHOW RESULTS
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

# DEFINE CONDITIONAL OUTPUT MARKERS
sys.stdout.write(colored('[+] SUCCESS | RESULTS RETURNED ', 'green'))
print("")
normal = sys.stdout.write(colored('[#] NEUTRAL | NO RESULTS RETURNED', 'yellow'))
print("")
failure = sys.stdout.write(colored('[-] FAILURE | RATE LIMITS OR API FAILURE ', 'red'))
print("")

# RESULTS LOGIC FOR QUERIES
for query in queries_list:
    print("")
    sys.stdout.write(colored('QUERY PROVIDED: %s' % (query), 'cyan'))
    print("")
    print("")

    for url in results_dict[query]:

        if url in url_results_dict:
            if args.recentlyindexed:
                new_url = url.replace('https://api.github.com/search/code',
                                      'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            elif not args.recentlyindexed:
                new_url = url.replace('https://api.github.com/search/code',
                                      'https://github.com/search') + '&type=Code'
            dork_name = dorks_list[count]
            dork_info = 'DORK = ' + dork_name + ' | '
            result_info = dork_info + new_url
            if count < len(dorks_list)-1:
                count = count + 1
            else:
                count = 0

            if url_results_dict[url] == 0:
                if args.positiveresults == False:
                    result_number = url_results_dict[url]
                    normal = sys.stdout.write(colored('[#] ', 'yellow'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    dork_name_list.append(dork_name)
                    print('')

            else:
                result_number = url_results_dict[url]
                success = sys.stdout.write(colored('[+] ', 'green'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)
                print('')

        else:
            failure = sys.stdout.write(colored('[-] ', 'red'))
            sys.stdout.write(colored('%s' % new_url, 'white'))
            count = count + 1
            print('')


# ADD KEYWORD TO OUTPUT TO BOTH DORKS AND ARGS
for user in users_list:
    print("")
    sys.stdout.write(colored('USER PROVIDED: %s' % (user), 'cyan'))
    print("")

    if args.keyword and not args.dorks:
        for url in results_dict[user]:
            if url in url_results_dict:
                if args.recentlyindexed:
                    new_url = url.replace('https://api.github.com/search/code',
                                          'https://github.com/search') + '&s=indexed&type=Code&o=desc'
                elif not args.recentlyindexed:
                    new_url = url.replace('https://api.github.com/search/code',
                                          'https://github.com/search') + '&type=Code'

                keyword_name = keywords_list[keyword_count]
                keyword_info = 'KEYWORD = ' + keyword_name + ' | '
                result_info = keyword_info + new_url
                if len(keywords_list) - 1 != keyword_count:
                    keyword_count = keyword_count + 1
                else:
                    keyword_count = 0

                if url_results_dict[url] == 0:
                    if args.positiveresults == False:
                        result_number = url_results_dict[url]
                        normal = sys.stdout.write(colored('[#] ', 'yellow'))
                        sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                        sys.stdout.write(colored('%s' % (result_info), 'white'))
                        new_url_list.append(new_url)
                        result_number_list.append(result_number)
                        keyword_name_list.append(keyword_name)
                        user_list.append(user)
                        print('')

                else:
                    result_number = url_results_dict[url]
                    success = sys.stdout.write(colored('[+] ', 'green'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    keyword_name_list.append(keyword_name)
                    user_list.append(user)
                    print('')

            else:
                failure = sys.stdout.write(colored('[-] ', 'red'))
                keyword_name = keywords_list[keyword_count]
                sys.stdout.write(colored('No KEYWORD: %s found for %s' % (keyword_name, user), 'white'))
                if len(keywords_list) - 1 != keyword_count:
                    keyword_count = keyword_count + 1
                else:
                    keyword_count = 0
                # Potentially code in removal from list to prevent query offset
                print('')


    elif args.dorks:
        count = 0
        for url in results_dict[user]:
            if url in url_results_dict:
                if args.recentlyindexed:
                    new_url = url.replace('https://api.github.com/search/code',
                                          'https://github.com/search') + '&s=indexed&type=Code&o=desc'
                elif not args.recentlyindexed:
                    new_url = url.replace('https://api.github.com/search/code',
                                          'https://github.com/search') + '&type=Code'
                dork_name = dorks_list[count]

                if args.keyword:
                    keyword_name = keywords_list[keyword_count]
                    dork_info = 'DORK = ' + dork_name + ' | KEYWORD = ' + keyword_name + ' | '
                    result_info = dork_info + new_url
                    if len(keywords_list) - 1 != keyword_count:
                        keyword_count = keyword_count + 1
                    else:
                        keyword_count = 0
                        count = count + 1

                elif not args.keyword:
                    count = count + 1
                    dork_info = 'DORK = ' + dork_name + ' | '
                    result_info = dork_info + new_url

                if len(dorks_list) == count:
                    count = 0

                if url_results_dict[url] == 0:
                    if args.positiveresults == False:
                        result_number = url_results_dict[url]
                        normal = sys.stdout.write(colored('[#] ', 'yellow'))
                        sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                        sys.stdout.write(colored('%s' % (result_info), 'white'))
                        new_url_list.append(new_url)
                        result_number_list.append(result_number)
                        dork_name_list.append(dork_name)
                        if args.keyword:
                            keyword_name_list.append(keyword_name)
                        user_list.append(user)
                        print('')

                else:
                    result_number = url_results_dict[url]
                    success = sys.stdout.write(colored('[+] ', 'green'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    dork_name_list.append(dork_name)
                    if args.keyword:
                        keyword_name_list.append(keyword_name)
                    user_list.append(user)
                    print('')

            else:
                failure = sys.stdout.write(colored('[-] ', 'red'))
                sys.stdout.write(colored('%s' % new_url, 'white'))
                if args.keyword:
                    if len(keywords_list) - 1 != keyword_count:
                        keyword_count = keyword_count + 1
                count = count + 1
                if len(dorks_list) == count:
                    count = 0
                print('')

# RESULTS LOGIC FOR ORGANIZATIONS
for organization in organizations_list:
    print("ORGANIZATION PROVIDED: " + '%s' % organization)
    print("")
    for url in results_dict[organization]:

        if url in url_results_dict:
            if args.recentlyindexed:
                new_url = url.replace('https://api.github.com/search/code',
                                      'https://github.com/search') + '&s=indexed&type=Code&o=desc'
            elif not args.recentlyindexed:
                new_url = url.replace('https://api.github.com/search/code',
                                      'https://github.com/search') + '&type=Code'
            dork_name = dorks_list[count]
            dork_info = ' DORK = ' + dork_name + ' | '
            result_info = dork_info + new_url
            count = count + 1

            if url_results_dict[url] == 0:
                if args.positiveresults == False:
                    result_number = url_results_dict[url]
                    normal = sys.stdout.write(colored('[#] ', 'yellow'))
                    sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                    sys.stdout.write(colored('%s' % (result_info), 'white'))
                    new_url_list.append(new_url)
                    result_number_list.append(result_number)
                    dork_name_list.append(dork_name)
                    print('')

            else:
                result_number = url_results_dict[url]
                success = sys.stdout.write(colored('[+] ', 'green'))
                sys.stdout.write(colored('(%d) ' % (result_number), 'cyan'))
                sys.stdout.write(colored('%s' % (result_info), 'white'))
                new_url_list.append(new_url)
                result_number_list.append(result_number)
                dork_name_list.append(dork_name)
                print('')

        else:
            failure = sys.stdout.write(colored('[-] ', 'red'))
            sys.stdout.write(colored('%s' % new_url, 'white'))
            count = count + 1
            print('')

# CSV OUTPUT TO FILE
if args.output:
    # FILE NAME USER INPUT
    file_name = args.output

    # DEFINE ROWS FOR KEYWORDS AND WITHOUT
    query_with_dorks_rows = zip(dork_name_list, new_url_list, result_number_list)
    organization_with_dorks_row = zip(dork_name_list, new_url_list, result_number_list)
    user_with_keyword_only_rows = zip(user_list, keyword_name_list, new_url_list, result_number_list)
    user_with_keyword_and_dorks_rows = zip(user_list, dork_name_list, keyword_name_list, new_url_list,
                                           result_number_list)
    user_with_dorks_only_rows = zip(user_list, dork_name_list, new_url_list, result_number_list)

    # DEFINE FIELDS FOR KEYWORDS AND WITHOUT
    query_with_dorks_fields = ['DORK', 'URL', 'NUMBER OF RESULTS']
    organization_with_dorks_fields = ['DORK', 'URL', 'NUMBER OF RESULTS']
    user_with_keyword_only_fields = ['USER', 'KEYWORD', 'URL', 'NUMBER OF RESULTS']
    user_with_keyword_and_dorks_fields = ['USER', 'DORK', 'KEYWORD', 'URL', 'NUMBER OF RESULTS']
    user_with_dorks_only_fields = ['USER', 'DORK', 'URL', 'NUMBER OF RESULTS']

    # OUTPUT FOR ROWS WITH KEYWORDS AND DORKS
    with open(file_name + '_gh_dorks' + '.csv', "w") as csvfile:
        wr = csv.writer(csvfile)
        if args.query or args.queryfile:
            wr.writerow(query_with_dorks_fields)
            for row in query_with_dorks_rows:
                wr.writerow(row)
        if args.organization:
            wr.writerow(organization_with_dorks_fields)
            for row in organization_with_dorks_row:
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

    csvfile.close()
    print("")
    sys.stdout.write(
        colored("Results have been outputted into the current working directory as " + file_name + "_gitdorker",
                'green'))
    print("")
    print("")

#!/usr/bin/python

import sys
import getopt
import signal
import os
import random
import string
import time
import requests
import json
from itertools import product
from string import ascii_lowercase
from termcolor import colored

delay = 1 #Delay between requests (GoDaddy rate limit is 1 per sec)
errorDelay = 15 #Delay when rate limit is reached

def checkDomain(domain, apiKey, apiSecret):
    url = "https://api.godaddy.com/v1/domains/available?domain=" + str(domain) + "&checkType=FAST&forTransfer=false"
    payload = {}
    headers = {
    'accept': 'application/json',
    'Authorization': 'sso-key ' + apiKey + ':' + apiSecret
    }
    response = requests.request("GET", url, headers=headers, data = payload)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401 or response.status_code == 403:
        print(colored("API Error: Your API Key or Secret are invalid", 'red'))
        exit(0)
    elif response.status_code == 422:
        if mode == 'debug': print(colored(str(domain + " is not a valid domain, skipping"), 'red'))
        return "skip"
    elif response.status_code == 429:
        if mode == 'debug': print(colored("API Error: Too many requests, waiting 10 secs...", 'red'))
        print(response.json())
        time.sleep(response.json().retryAfterSec)
        return "retry"
    else:
        print(colored("API Error: " + str(response), 'red'))
        exit(0)

def checkDomainBulk(domains, apiKey, apiSecret):
    url = "https://api.godaddy.com/v1/domains/available?checkType=FAST"
    payload = json.dumps(domains)
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'sso-key ' + apiKey + ':' + apiSecret
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401 or response.status_code == 403:
        print(colored("API Error: Your API Key or Secret are invalid", 'red'))
        exit(0)
    elif response.status_code == 429:
        if mode == 'debug': print(colored("API Error: Too many requests, waiting 20 secs...", 'red'))
        time.sleep(20)
        return "retry"
    else:
        print(colored("API Error: " + str(response.json()), 'red'))
        exit(0)

def checkSingleDomain(domain, outFile, apiKey, apiSecret):
    full = domain
    # Query GoDaddy
    res = checkDomain(full, apiKey, apiSecret)
    if res is "retry":
        res = checkDomain(full, apiKey, apiSecret)
    elif res is "skip":
        return
    if 'code' in res:
        if 'UNSUPPORTED_TLD' in res['code']:
            print(colored(str(full + " is not a valid domain"), 'red'))
        else:
            if mode == 'debug': print(colored("Error: " + str(res), 'red'))
    else:
        if res["available"] is True:
            price = res["price"] / 1000000
            currency = "$"
            print(colored(str(full + " is available for: " + str(round(price, 2)) + " " + currency), 'green'))
        else:
            print(colored(str(full + " is not available"), 'red'))

def parseOneDomain(domain, tld, outFile, apiKey, apiSecret):
    full = str(domain) + "." + str(tld)
    # Query GoDaddy
    res = checkDomain(full, apiKey, apiSecret)
    if res is "retry":
        res = checkDomain(full, apiKey, apiSecret)
    elif res is "skip":
        return
    if 'code' in res:
        if 'UNSUPPORTED_TLD' in res['code']:
            if mode == 'debug': print(colored(str(full + " is not a valid domain"), 'red'))
        else:
            if mode == 'debug': print(colored("Error: " + str(res), 'red'))
    else:
        if res["available"] is True:
            price = res["price"] / 1000000
            currency = "$"
            if mode != "none": print(colored(str(full + " is available for: " + str(round(price, 2)) + " " + currency), 'green'))
            f = open(outFile, 'a')
            result = str(full + " - " + str(round(price, 2)) + " " + currency + "\n")
            f.write(result)
            f.close()
        else:
            if mode == "both" or mode == "debug": print(colored(str(full + " is not available"), 'red'))
    time.sleep(delay)

def parseMulipleDomains(full, outFile, apiKey, apiSecret):
    # Query GoDaddy
    res = checkDomainBulk(full, apiKey, apiSecret)
    if res is "retry":
        check = False
        result = ''
        while check == False:
            if mode == 'debug': print("Retrying")
            res = checkDomainBulk(full, apiKey, apiSecret)
            if res is not 'skip' or res is not 'retry':
                check = True
                result = res
            else:
                time.sleep(delay)
        for domain in result['domains']:
            #print("Domain: " + domain['domain'])
            if 'code' in domain:
                if 'UNSUPPORTED_TLD' in domain['code']:
                    if mode == 'debug': print(colored(str(domain['domain'] + " is not a valid domain"), 'red'))
                else:
                    if mode == 'debug': print(colored("Error: " + str(domain), 'red'))
            elif domain["available"] is True:
                price = domain["price"] / 1000000
                currency = "$"
                if mode != "none": print(colored(str(domain['domain'] + " is available for: " + str(round(price, 2)) + " " + currency), 'green'))
                f = open(outFile, 'a')
                result = str(domain['domain'] + " - " + str(round(price, 2)) + " " + currency + "\n")
                f.write(result)
                f.close()
            else:
                if mode == "both" or mode == "debug": print(colored(str(domain['domain'] + " is not available"), 'red'))

    elif res is "skip":
        time.sleep(delay)
        return
    else:
        #print(res)
        for domain in res['domains']:
            #print("Domain: " + domain['domain'])
            if 'code' in domain:
                if 'UNSUPPORTED_TLD' in domain['code']:
                    if mode == 'debug': print(colored(str(domain['domain'] + " is not a valid domain"), 'red'))
                else:
                    if mode == 'debug': print(colored("Error: " + str(domain), 'red'))
            elif domain["available"] is True:
                price = domain["price"] / 1000000
                currency = "$"
                if mode != "none": print(colored(str(domain['domain'] + " is available for: " + str(round(price, 2)) + " " + currency), 'green'))
                f = open(outFile, 'a')
                result = str(domain['domain'] + " - " + str(round(price, 2)) + " " + currency + "\n")
                f.write(result)
                f.close()
            else:
                if mode == "both" or mode == "debug": print(colored(str(domain['domain'] + " is not available"), 'red'))
        time.sleep(delay)
    
def run(domains, tlds, outFile, rand, bulk, apiKey, apiSecret):
    if mode == 'debug': print("Out file: " + str(outFile))
    print("Checking " + str(len(domains) * len(tlds)) + " domains...")
    if bulk: timeSec = ((len(domains) * len(tlds)) / 500 ) * 20
    else: timeSec = (len(domains) * len(tlds)) * (delay + 0.5)
    if timeSec > (60 * 60):
        estimate = str(round(((timeSec / 60) / 60),2)) + " hours"
    elif timeSec > 60:
        estimate = str(round((timeSec / 60), 2)) + " minutes"
    else:
        estimate = str(round(timeSec)) + " seconds"
    print("Estimated time: " + estimate)
    if mode == 'debug': print("TLDs: " + str(tlds))
    if group:
        if mode == "debug": print("Grouping TLDs")
        if bulk:
                if mode == 'debug': print("Bulk mode")
                data = []
                for domain in domains:
                   for tld in tlds:
                       data.append(domain + "." + tld)
                domains = data
                if len(domains) >= 499:
                    if mode == 'debug': print("More than 500, creating Chunks")
                    chunks = [domains[i * 499:(i + 1) * 499] for i in range((len(domains) + 499 - 1) // 499 )]
                    if mode == 'debug': print(str(len(chunks)) + " Chunks")
                    for chunk in chunks:
                        if mode == 'debug': print("Next Chunk")
                        parseMulipleDomains(chunk, outFile, apiKey, apiSecret)
                        if mode == 'debug': print("Waiting 10 sec...")
                        time.sleep(10)
                else:
                    parseMulipleDomains(domains, outFile, apiKey, apiSecret)
        else: 
            if mode == 'debug': print("Single mode")
            if rand:
                if mode == 'debug': print("Selecting in random order")
                size = len(domains)
                while size:
                    index = random.randrange(size)
                    domain = domains[index]
                    domains[index] = domains[size-1]
                    size = size - 1
                    for tld in tlds:
                        parseOneDomain(domain, tld, outFile, apiKey, apiSecret)
            else:
                for domain in domains:
                    for tld in tlds:
                        parseOneDomain(domain, tld, outFile, apiKey, apiSecret)
    else:
        if mode == 'debug': print("Bulk mode")
        for tld in tlds:
            if mode == 'debug': print("TLD: ." + str(tld))
            if bulk:
                if len(domains) >= 499:
                    if mode == 'debug': print("More than 500, creating Chunks")
                    chunks = [domains[i * 499:(i + 1) * 499] for i in range((len(domains) + 499 - 1) // 499 )]
                    if mode == 'debug': print(str(len(chunks)) + " Chunks")
                    for chunk in chunks:
                        full = []
                        for domain in chunk:
                                full.append(domain + "." + tld)
                        if mode == 'debug': print("Next Chunk")
                        parseMulipleDomains(full, outFile, apiKey, apiSecret)
                        if mode == 'debug': print("Waiting 10 sec...")
                        time.sleep(10)
                else:
                    full = []
                    for domain in domains:
                            full.append(domain + "." + tld)
                    parseMulipleDomains(full, outFile, apiKey, apiSecret)
            else: 
                if mode == 'debug': print("Single mode")
                if rand:
                    if mode == 'debug': print("Selecting in random order")
                    size = len(domains)
                    while size:
                        index = random.randrange(size)
                        domain = domains[index]
                        domains[index] = domains[size-1]
                        size = size - 1
                        parseOneDomain(domain, tld, outFile, apiKey, apiSecret)
                else:
                    for domain in domains:
                        parseOneDomain(domain, tld, outFile, apiKey, apiSecret)
    print("done")

def domainListFromFile(file):
    if os.path.exists(file):
        f = open(str(file), 'r')
        domains = f.read().splitlines()
        f.close()
        return domains
    else:
        print(colored(str("Error: " + file + " doesn't exist"), 'red'))
        exit(0)

def generateDomainList(length, characters):
    if length > 64:
        print("Error: Can't generate domains larger than 64 Characters")
        exit(2)
    domains = [''.join(x) for x in product(characters, repeat=length)]
    return domains

def getTldFromFile(file):
    if os.path.exists(file):
        f = open(str(file), 'r')
        tlds = f.read().splitlines()
        f.close()
        return tlds
    else:
        print(colored(str("Error: " + file + " doesn't exist"), 'red'))
        exit(0)


def signal_handler(sig, frame):
    print(' Stopping programm')
    exit(0)

def printHelp():
    print('dcheck - Mass Domain Availability Checker')
    print('2020 - Maximilian Schiller <schiller@mxis.ch>')
    print('Github: github.com/BetaHuhn/')
    print('Version: 1.0')
    print('--------------------------')
    print('*READ BEFORE RUNNING*')
    print('This Python Programm uses the GoDaddy API to check if a Domain is available.')
    print('You need to get your personal API Key and Secret on this page: https://developer.godaddy.com/keys')
    print('and specify them with the --key and --secret argument')
    print('--------------------------')
    print('By default the script generates permutation of 4 characters (a-z) as domains')
    print('You can also specify a list of domains in a file (one on each line) e.g -d domains.txt')
    print('You can either specify one tld e.g -t com or multiple by specifying a file (one tld per line)')
    print('--------------------------')
    print('Usage: decheck [options...]')
    print('-t, --tld <tld> Specify TLD without dot, if multiple: -t "com org" [default: com]')
    print('-l, --tldlist <file> List of TLDs in a file, one on each line')
    print('-d, --domain <domain> Check one domain')
    print('-m, --domainlist <file> List of Domains in a file, one per line')
    print('-f, --file <file> Name of the output file which contains all available domains [default: available.txt]')
    print('-n, --length <number> Length of generated Domain names [default: 4]')
    print('-c, --characters <string> used when generating domain names, e.g abcdefghijklmnopqrstuvwxyz0123456789 [default: a-z]')
    print('-o, --order <boolean> If set to true domain list will be reversed [default: false]')
    print('-g, --group <boolean> If set to true for every domain all TLDs are checked instead of all domains per TLD [default: false]')
    print('-r, --random <boolean> If set to true domain will be choosen randomly from domain list [default: false]')
    print('-k, --key GoDaddy API Key')
    print('-s, --secret GoDaddy API Secret')
    print('-p, --print Change what is shown')
    print('     both - prints both available and not available domains')
    print('     only - prints only available domains [default]')
    print("     none - doesn't print domains")
    print("     debug - prints debug information")
    print('-h, --help Will display this help page')

def main():
    signal.signal(signal.SIGINT, signal_handler)
    global mode
    global group
    #Enter your GoDaddy API Key and API Secret here:
    apiKey = "" 
    apiSecret = ""
    argv = sys.argv[1:]
    tldArg = ''
    tldFile = ''
    domainFile = ''
    outFile = ''
    options = ''
    length = ''
    reverse = False
    rand = False
    bulk = False
    group = False
    domain = ''
    mode = ''
    try:
        opts, args = getopt.getopt(argv,"t:d:l:n:c:f:r:b:s:k:o:p:m:g:",["tld=","domainlist=","tldlist=", "file=", "characters=", "length=", "random", "bulk", "key=", "secret=", "order", "domain=", "print=", "group"])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)
    if len(opts) == 0:
        printHelp()
        sys.exit(2)
    #print(opts)
    #go through command arguments
    for opt, arg in opts:
        if opt == '-h':
            printHelp()
            sys.exit()
        elif opt in ("-t", "--tld"):
            tldArg = arg
        elif opt in ("-m", "--domainlist"):
            domainFile = arg
        elif opt in ("-l", "--tldlist"):
            tldFile = arg
        elif opt in ("-f", "--file"):
            outFile = arg
        elif opt in ("-c", "--characters"):
            options = arg
        elif opt in ("-n", "--length"):
            length = arg
        elif opt in ("-r", "--random"):
            rand = arg
        elif opt in ("-o", "--order"):
            reverse = arg
        elif opt in ("-b", "--bulk"):
            bulk = arg
        elif opt in ("-k", "--key"):
            apiKey = arg
        elif opt in ("-s", "--secret"):
            apiSecret = arg
        elif opt in ("-d", "--domain"):
            domain = arg
        elif opt in ("-p", "--print"):
            mode = arg
        elif opt in ("-g", "--group"):
            group = arg
        else:
            print(colored("Error: Argument " + str(opt) + " doesn't exist", 'red'))
            printHelp()
            sys.exit(2)

    if mode != 'both' and mode != 'none' and mode != 'debug':
        mode = "only"
    #print(mode)

    if(len(apiKey) == 0 or len(apiSecret) == 0):
        apiKey = os.getenv('apiKey') 
        apiSecret = os.getenv('apiSecret')
        if(apiKey == None or apiSecret == None):
            apiKey = os.getenv('APIKEY') 
            apiSecret = os.getenv('APISECRET')
            if(apiKey == None or apiSecret == None):
                print(colored("Error: You need to specify your GoDaddy API Key and Secret with the --key and --secret argument", 'red'))
                exit(0)

        if mode == 'debug': print("API Key: " + apiKey + " API Secret: " + apiSecret)

    if outFile is '':
        outFile = 'available.txt'

    # Check only one domain
    if domain is not '':
        checkSingleDomain(domain, outFile, apiKey, apiSecret)
        exit(0)

    #Check if one tld specified, if not get tlds from file
    if tldArg is not '':
        tld = tldArg.split()     
    else:
        if tldFile is not '':
            if mode == 'debug': print("Loading TLDs from file: " + tldFile)
            tld = getTldFromFile(tldFile)
        else:
            tld = ['com']

    if rand == "true" or rand == "":
        rand = True
    else: 
        rand = False

    if bulk == "true" or bulk == "":
        bulk = True
    else:
        bulk = False

    if group == "true" or group == "":
        group = True
    else:
        group = False

    print("press ctrl+c at any time to stop")
    #Check if domain file is specified, if not generate domains
    if domainFile == '':
        if length is '':
            length = 4
        if options is '':
            options = ascii_lowercase
        if mode == 'debug': print("Generating domains with length " + str(length) + " and characters: " + options)
        domains = generateDomainList(int(length), options)
        if reverse == 'true' or reverse == '':
            if mode == 'debug': print("Running in reverse")
            domains.reverse()
        run(domains, tld, outFile, rand, bulk, apiKey, apiSecret)
    else:
        if mode == 'debug': print("Loading Domains from file: " + domainFile)
        domains = domainListFromFile(domainFile)
        if reverse == 'true' or reverse == '':
            if mode == 'debug': print("Running in reverse")
            domains.reverse()
        run(domains, tld, outFile, rand, bulk, apiKey, apiSecret)

if __name__ == '__main__':
    main()
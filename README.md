# dcheck
Mass Domain Availability Check Script

## Description

With this script you can check if a domain is available by either specifying a file which contains domain names, or by generating different domain names of various lenghts. You can also specify which TLDs to use. The Script can generate domain names with all combinations of characters (default is a-z) with a specified length. To check the availability it uses the GoDaddy API. The results will be saved to a file, or printed live to the shell.

## Features
- check if a single domain is available
- check if multiple domains in a file are available with specific TLD
- check if multiple domains in a file are available with multiple TLDs from file
- generate domain names with specific lengths and characters
- specify in which order the domain names are being checked (asc, desc, random)
- save available domains to file
- print only available domains or all domains to shell

## Example
### Generate domain names from aaa to zzz with .com and .net as TLDs
Command:
```shell
dcheck --tld "com net" --length 3 --print both
```
Output:
```shell
Checking 23762752 domains...
aaaa.com is not available
aaab.com is not available
aaac.com is not available
...
```
### Use wordlist for domains with .com and .net as TLDs
```shell
dcheck --tld "com net" --domainlist domains.txt --group
```
Output:
```shell
Checking 12 domains...
Estimated time: 18 seconds
stormyocean.com is not available
stormyocean.net is available for: 14.99 $
...
```
### Generate domain names with a-z and 0-9 and length 3 in random order with TLD .de
```shell
dcheck --tld de --length 3 --characters abcdefghijklmnopqrstuvwxyz0123456789 --random --print both
```
Output:
```shell
Checking 46656 domains...
Estimated time: 19.44 hours
gld.de is not available
z3d.de is not available
px9.de is not available
ci5.de is not available
2i6.de is available for: 7.99 $
ncw.de is not available
...
```

### Use file with domains and file with TLDs
```shell
dcheck --tldlist tlds.txt --domainlist domains.txt --print both --group
```
Output:
```shell
Checking 18 domains...
Estimated time: 27 seconds
windyweather.de is available for: 7.99 $
windyweather.com is not available
windyweather.net is not available
...
```

## Setup
Because with multiple different TLDs whois requests are often slow, this Python Programm uses the GoDaddy API to check if a Domain is available. In order to use the programm, you need to get your personal API Key and Secret on [this](https://developer.godaddy.com/keys) page (It's free).

- clone this repo:
```shell
git clone https://github.com/BetaHuhn/dcheck/
```
- cd into the folder
```shell
cd dcheck
```
- run the install command:
```shell
python3 setup.py install
```
- dcheck command is now available
- get your GoDaddy API Key and Secret [here](https://developer.godaddy.com/keys) and either set them as environment variables:
```shell
export APIKEY="YOUR KEY"
export APISECRET="YOUR SECRET"
```
or specify them each time you run the command with 
```shell
--key <YOUR KEY> and --secret <YOUR SECRET>
```

## Usage 
dcheck [options...]
```
-t, --tld <tld> Specify TLD without dot, if multiple: -t "com org" [default: com]
-l, --tldlist <file> List of TLDs in a file, one on each line
-d, --domain <domain> Check one domain
-m, --domainlist <file> List of Domains in a file, one per line
-f, --file <file> Name of the output file which contains all available domains [default: available.txt]
-n, --length <number> Length of generated Domain names [default: 4]
-c, --characters <string> used when generating domain names, e.g abcdefghijklmnopqrstuvwxyz0123456789 [default: a-z]
-o, --order <boolean> If set to true domain list will be reversed [default: false]
-g, --group <boolean> If set to true for every domain all TLDs are checked instead of all domains per TLD [default: false]
-r, --random <boolean> If set to true domain will be choosen randomly from domain list [default: false]
-k, --key GoDaddy API Key
-s, --secret GoDaddy API Secret
-p, --print Change what is shown
     both - prints both available and not available domains
     only - prints only available domains [default]
     none - doesn't print domains
     debug - prints debug information
-h, --help Will display this help page
```

## Authors
* **Maximilia Schiller** - *Initial work* - [BetaHuhn](https://github.com/BetaHuhn)

If you have any questions, noticed a bug or have a feature request, feel free to create an Issue or send me an [email](mailto:mail@betahuhn.de)

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

MIT © Maximilian Schiller


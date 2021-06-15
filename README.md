# Mr_URL
Mr.URL fetches known URLs for a given domain from Wayback Machine, Commoncrawl and OTX Alienvault. It also finds old versions of any given URL using WaybackMachine. Inspired by [GAU](https://github.com/lc/gau) and [Waybackurls](https://github.com/tomnomnom/waybackurls).

# Resources
- [Usage](#usage)
- [Installation](#installation)

## Usage:
Examples:

```bash
$ echo example.com | python3 Mr_URL.py
$ echo example.com | python3 Mr_URL.py -subs
$ cat live_subs.txt | python3 Mr_URL.py -q -t5
$ cat js_links.txt | python3 Mr_URL.py -v
```


| Flag | Description |
|------|-------------|
|-h, --help  |show this help message and exit|
|-subs       |Include Subdomains|
|-q          |Quick Mode (Uses Only WaybackMachine)|
|-v          |Get Old versions of a URL|
|-t          |Number of threads (Default : 10)|


## Installation:
```
$ git clone https://github.com/Sachin-v3rma/Mr_URL
$ cd Mr_URL && pip install -r requirements.txt
$ python3 Mr_URL.py -h
```

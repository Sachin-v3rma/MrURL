# MrURL
Mr.URL fetches known URLs for a given domain from Wayback Machine, Commoncrawl and OTX Alienvault. It also finds old versions of any given URL using WaybackMachine. Inspired by [GAU](https://github.com/lc/gau) and [Waybackurls](https://github.com/tomnomnom/waybackurls).

## Installation:
```
$ git clone https://github.com/Sachin-v3rma/MrURL
$ cd MrURL && pip install -r requirements.txt
$ python3 MrURL.py -h
```

## Usage:
Examples:

```bash
$ echo example.com | python3 MrURL.py
$ echo example.com | python3 MrURL.py -subs
$ cat live_subs.txt | python3 MrURL.py -q -t5
$ cat js_links.txt | python3 MrURL.py -v
```


| Flag | Description |
|------|-------------|
|-h, --help  |show this help message and exit|
|-subs       |Include Subdomains|
|-q          |Quick Mode (Uses Only WaybackMachine)|
|-v          |Get Old versions of a URL|
|-t          |Number of threads (Default : 10)|


<a href="https://www.buymeacoffee.com/sachinvm" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" height="41" width="174"></a>

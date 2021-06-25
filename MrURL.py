#!/bin/python3
# Waybackurls on steriods
# Inspired from Tomnomnom and GAU by Corben Leo
# Made with <3 by Sachin Verma ( @vm_sachin )

import asyncio
import aiohttp
import json
import re
import argparse
import sys
import random

async def fetch(session, url):  # Fetches a given URL
    try:
        async with session.get(url, allow_redirects=True, headers=headers) as response:
            html = await response.text()
            return html
    except (aiohttp.client_exceptions.ClientConnectorError,asyncio.exceptions.TimeoutError, ConnectionRefusedError):
        print(f'Request Timeout')

def counter():
    global count
    count += 1
    print(f'\r[*] Fetched data from {count}/{len(wb_urls)+len(cc_urls)} URLs (sources)', end ='', flush=True)
        
async def wayback(session, url):     # Wayback Machine Data
    if args.subs == True:
        pages = await fetch(session, f'https://web.archive.org/cdx/search/cdx?url=*.{url}/*&showNumPages=true')
        for i in range(int(pages)):
            wb_url = f'https://web.archive.org/cdx/search/cdx?url=*.{url}/*&output=txt&collapse=urlkey&fl=original&page={i}'
            wb_urls.append(wb_url)
        wb_url = f'https://web.archive.org/cdx/search/cdx?url=*.{url}/*&output=txt&collapse=urlkey&fl=original&page=/'
        wb_urls.append(wb_url)
    else:
        pages = await fetch(session, f'https://web.archive.org/cdx/search/cdx?url={url}/*&showNumPages=true')
        for i in range(int(pages)):
            wb_url = f'https://web.archive.org/cdx/search/cdx?url={url}/*&output=txt&collapse=urlkey&fl=original&page={i}'
            wb_urls.append(wb_url)
        wb_url = f'https://web.archive.org/cdx/search/cdx?url={url}/*&output=txt&collapse=urlkey&fl=original&page=/'
        wb_urls.append(wb_url)

async def alienvault(session, url): # OTX AlienVault Data
    if len(url.split('.')) == 2:
        mode = 'domain'
    else:
        mode = 'hostname'
        
    for i in range(100,2001,100):   # Finds approx. no. pages having data 
        otx_url = f'https://otx.alienvault.com/api/v1/indicators/{mode}/{url}/url_list/?limit=10000000&page={i}'
        html = await fetch(session, otx_url)
        page_no = 0
        if ': false,' in html:
            page_no = int(i)
            break
        elif i == 2000 and ': false' not in html:
            page_no = int(i)
        elif 'Invalid domain' in html:
            break
    if page_no != 0:
        for i in range(page_no-100,page_no,5):
            otx_url = f'https://otx.alienvault.com/api/v1/indicators/{mode}/{url}/url_list/?limit=10000000&page={i}'
            html = await fetch(session, otx_url)
            if ': false,' in html:
                page_no = int(i)
                break
        for i in range(page_no):    # Appends Found URLs to wb_urls to be fetched
            otx_url = f'https://otx.alienvault.com/api/v1/indicators/{mode}/{url}/url_list/?limit=10000000&page={i}'
            wb_urls.append(otx_url)

async def commoncrawl_api_url(session, url):    # CommonCrawl Data
    cc_api_url = 'http://index.commoncrawl.org/collinfo.json'
    html = await fetch(session, cc_api_url)
    json_html = json.loads(html)
    for i in json_html:
        if 'CC-MAIN-2018' in i['id']:
            break
        if args.subs == True:
            cc_api_urls.append(f"{i['cdx-api']}?url=*.{url}/*&output=json&fl=url&showNumPages=true")
        else:
            cc_api_urls.append(f"{i['cdx-api']}?url={url}/*&output=json&fl=url&showNumPages=true")

async def commoncrawl(sem, session, url):   # Parses the data of CommonCrawl
    async with sem:
        data = await fetch(session, url)
        if 'pages":' in data:
            json_data = json.loads(data)
            total_pages = json_data['pages']
            for i in range(total_pages):
                cc_urls.append(f'{url[:-29]}text&fl=url&pages={i}')
        else:
            pass

async def commoncrawl_parser(sem, session, url):
    async with sem:
        data = await fetch(session, url)
        if 'http://' and 'https://' in data:
            for i in data.split('\n'):
                output.add(i)
        #counter()

async def parser(session, url):     # Parses the data of Waybackmachine and Alienvault 
    data = await fetch(session, url)
    try:
        if re.findall(r'^http', data):
            print(data,end='')
        else:
            json_data = json.loads(data)
            for i in json_data['url_list']:
                print(i['url'])
        #counter()
    except json.decoder.JSONDecodeError:
        pass

async def get_versions(session, url):
    timestamp = f"https://web.archive.org/cdx/search/cdx/?url={url}&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest"
    async with session.get(timestamp, allow_redirects=True, headers=headers) as response:
        html = await response.json()
        if len(html) != 0:
            html.pop(0)
            for i in range(len(html)):
                print(f"https://web.archive.org/web/{html[i][0]}/{html[i][1]}")

async def start(urls:set, threads) -> None:
    sem = asyncio.Semaphore(2)
    connector = aiohttp.TCPConnector(limit_per_host=threads,ssl=False)
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(connector=connector,timeout=timeout) as session:
        tasks = []
        if args.versions == True:
            for url in urls:    # Find old versions
                tasks.append(get_versions(session=session, url=url))
        else:
            for url in urls:
                tasks.append(commoncrawl_api_url(session, url))
            await asyncio.gather(*tasks)
            tasks = []
            
            for url in urls:
                tasks.append(wayback(session=session, url=url))

            if args.quick == False:
                for url in urls:
                    tasks.append(alienvault(session=session, url=url))

                for url in cc_api_urls:
                    tasks.append(commoncrawl(sem, session=session, url=url))
            await asyncio.gather(*tasks)

            tasks = []
            for url in wb_urls:     # wayback + otx alienvault
                tasks.append(parser(session=session, url=url))
            for url in cc_urls:    # commoncrawl
                tasks.append(commoncrawl_parser(sem, session=session, url=url))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    user_agent_list = [
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
]
    # Arguments
    headers = {
    'User-Agent': random.choice(user_agent_list)
    }
    regex = re.compile(r"https?://")
    wb_urls = []
    cc_api_urls = []
    cc_urls = []
    count = 0
    output = set()
    help_msg = '''
This Program Scrapes archived URLs from WaybackMachine, OTX Alienvault and Commoncrawl data. It also finds the old versions of a URL/webpage from Waybackmachine. Takes Input from stdin.'''

    arg_parser = argparse.ArgumentParser(description=help_msg, formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('-subs', help='Include Subdomains', action='store_true',dest='subs')
    arg_parser.add_argument('-q', help='Quick Mode (Uses Only WaybackMachine)', action='store_true',dest='quick')
    arg_parser.add_argument('-v', help='Get Old versions of a URL', action='store_true',dest='versions')
    arg_parser.add_argument('-t', help='Number of threads (Default : 10)', type=int, default=10, dest='threads')
    args = arg_parser.parse_args()
    
    # Input
    threads = args.threads
    try:
        domains = sys.stdin.readlines()
        domains = set(map(str.strip, {regex.sub('',i) for i in domains}))
        asyncio.get_event_loop().run_until_complete(start(domains, threads))
        {print(i) for i in output if i}
    except KeyboardInterrupt:
        print(f'\n[-] Exiting')
        sys.exit()
    except UnicodeDecodeError:
        pass
    except Exception as err:
        print(f'\n[-] Error : {repr(err)}')
        sys.exit()

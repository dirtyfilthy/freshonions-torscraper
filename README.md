# Fresh Onions TOR Hidden Service Crawler

This is a copy of the source for the http://zlal32teyptf4tvi.onion hidden service, which implements a tor crawler and web site.

## Features

* Crawls the darknet looking for new hidden service
* Find hidden services from a number of clearnet sources
* Marks clone sites of the /r/darknet superlist
* Finds SSH fingerprints across hidden services
* Finds email addresses across hidden  services
* Finds bitcoin addresses across hidden services
* Shows incoming / outgoing links to onion domains
* Up-to-date alive / dead hidden service status
* Doesn't fuck around in general.

## Licence

This software is made available under the GNU Affero GPL 3 License.. What this means is that is you deploy this software as part of networked software that is available to the public, you must make the source code available (and any modifications).

From the GNU site:

    The GNU Affero General Public License is a modified version of the ordinary GNU GPL version 3. It has one added requirement: if you run a modified program on a server and let other users communicate with it there, your server must also allow them to download the source code corresponding to the modified version running there

## Dependencies

python
tor

### pip install:

scrapy
pony
py-crypto
py-pretty
possibly some others you will discover when shit errors out

## Install

Create mysql db from schema.sql

Edit lib/tor_db.py for your database setup

Edit etc/proxy for your TOR setup

script/push.sh someoniondirectory.onion 
script/push.sh anotheroniondirectory.onion

init/scraper_service.sh

Run init/isup_service.sh to keep site status up to date


## Infrastructure

Fresh Onions runs on two servers, a frontend host running the database and hidden service web site, and a backend host running the crawler. Probably most interesting to the reader is the setup for the backend. TOR as a client is COMPLETELY SINGLETHREADED. I know! It's 2017, and along with a complete lack of flying cars, TOR runs in a single thread. What this means is that if you try to run a crawler on a single TOR instance you will quickly find you are maxing out your CPU at 100%.

The solution to this problem is running multiple TOR instances and connecting to them through some kind of frontend that will round-robin your requests. The Fresh Onions crawler runs eight Tor instances.

Debian (and ubuntu) comes with a useful program "tor-instance-create" for quickly creating multiple instances of TOR. I used Squid as my frontend proxy, but unfortunately it can't connect to SOCKS directly, so I used "privoxy" as an intermediate proxy. You will need one privoxy instance for every TOR instance. There is a script in "scripts/create_privoxy.sh" to help with creating privoxy instances on debian systems. It also helps to replace /etc/privoxy/default.filter with an empty file, to reduce CPU load by removing unnecessary regexes.

Additionally, this resource https://www.howtoforge.com/ultimate-security-proxy-with-tor might be useful in setting up squid. If all you are doing is crawling and don't care about anonymity, I also recommend running TOR in tor2web mode (required recompilation) for increased speed

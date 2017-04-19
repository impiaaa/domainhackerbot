import os, urllib, sys, re
import random, time, whois
from mastodon import Mastodon

domainslist = urllib.urlopen("http://data.iana.org/TLD/tlds-alpha-by-domain.txt")
domains = filter(lambda a: not a.startswith('#'), [line.strip().lower() for line in domainslist])
domainslist.close()

mindomainlen = min(map(len, domains))
maxdomainlen = max(map(len, domains))

words = open("/usr/share/dict/words").readlines()

historyfilename = "history.txt"

if os.path.exists(historyfilename):
    history = set([s.strip() for s in open(historyfilename)])
else:
    history = set()

def googleCount(word):
    url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="+urllib.quote_plus(word)
    print url
    urldoc = urllib.urlopen(url)
    result = json.loads(urldoc.read())
    urldoc.close()
    return result["responseData"]["cursor"]["estimatedResultCount"]

def hostLookup(domain):
    exitCode = os.system("host -W 1 "+domain+"")
    if exitCode == 0:
        # If it has a host,
        # the website already exists.
        return False
    elif exitCode in (1, 256):
        return True
    else:
        raise Exception("invalid exit code "+str(exitCode))

mastodon = Mastodon(client_id='clientcred.txt', api_base_url='https://botsin.space')
mastodon.log_in(
    open('email.txt').read().strip(),
    open('password.txt').read().strip()
)

while True:
    random.shuffle(words)
    for word in words:
        random.shuffle(domains)
        word = word.strip()
        lword = re.sub("\\W", "", word.lower())
        for extension in domains:
            if lword.endswith(extension):
                domain = lword[:-len(extension)]+'.'+lword[-len(extension):]
                if domain in history: coninue
                history.add(domain)
                
                historyfile = open(historyfilename, 'w')
                historyfile.write(domain+'\n')
                historyfile.close()
                
                if whois.whois(domain).expiration_date is not None:
                    print "not", domain
                    continue
                print domain
                mastodon.toot(domain)
                time.sleep(10*60)
                break

import os, re, codecs
import random, time, whois
from mastodon import Mastodon

domainslist = open('tlds-alpha-by-domain.txt')
domains = list([line.strip().lower().decode('idna') for line in domainslist if not line.startswith("#")])
domainslist.close()

words = [s.strip() for s in codecs.open('/usr/share/dict/words', 'rU', 'utf-8') if not s.endswith(u"'s\n")]

historyfilename = 'history.txt'

if os.path.exists(historyfilename):
    history = set([s.strip() for s in open(historyfilename)])
else:
    history = set()

mastodon = Mastodon(client_id='clientcred.txt', api_base_url='https://botsin.space')
mastodon.log_in(
    open('email.txt').read().strip(),
    open('password.txt').read().strip()
)

while True:
    random.shuffle(words)
    for word in words:
        random.shuffle(domains)
        lword = re.sub(u"\\W", u"", word.lower())
        for extension in domains:
            if len(extension) < 2: continue
            if len(extension) >= len(lword): continue
            if lword.endswith(extension):
                domain = lword[:-len(extension)]+u"."+lword[-len(extension):]
                if domain in history: continue
                history.add(domain)
                
                historyfile = codecs.open(historyfilename, 'a', 'utf-8')
                historyfile.write(domain+u"\n")
                historyfile.close()
                
                try:
                    if whois.whois(domain).expiration_date is not None:
                        print u"not", domain
                        continue
                except Exception, e:
                    print domain, e
                    continue
                print domain
                mastodon.toot(domain)
                time.sleep(10*60)
                break

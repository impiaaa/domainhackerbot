import os, re, codecs, urllib
import random, time, whois, json
from mastodon import Mastodon
from mastodon.Mastodon import MastodonNetworkError
from wordfilter import Wordfilter

# open to configuration
testing = False
sleepDuration = 15*60
publicStatusFrequency = 4
skipDomains = [u"es", u"ng", u"ing"]
wordlist = '/usr/share/dict/words'
disallowedStatuses = set(['active',
                          'disallowed',
                          'claimed',
                          'reserved',
                          'dpml',
                          'invalid',
                          'registrar',
                          'zone',
                          'tld'])
mastodonUrl = 'https://botsin.space'

# these probably shouldn't change
tldsUrl = 'http://data.iana.org/TLD/tlds-alpha-by-domain.txt'
historyFilename = 'history.txt'
domainrEndpoint = 'https://domainr.p.mashape.com/v2/'


domainslist = urllib.urlopen(tldsUrl)
domains = list([line.strip().lower().decode('idna') for line in domainslist if not line.startswith("#")])
domainslist.close()

for extension in skipDomains:
    domains.remove(extension)

words = [s.strip() for s in codecs.open(wordlist, 'rU', 'utf-8') if not s.endswith(u"'s\n") and not s.startswith(u"#") and not s.isspace()]

# ASCII-only characters that are not allowed in a domain name (non-alphanumeric)
domainNameDisallowed = re.compile(u"[\x00-,.-/:-@[-`{-\x7f]", flags=re.UNICODE)


if os.path.exists(historyFilename):
    history = set([s.strip() for s in codecs.open(historyFilename, 'r', 'utf-8')])
else:
    history = set()

if not testing:
    mastodon = Mastodon(client_id='clientcred.txt', api_base_url=mastodonUrl)
    mastodon.log_in(
        open('email.txt').read().strip(),
        open('password.txt').read().strip(),
        scopes=['write']
    )

publicStatusCycle = 0

wordfilter = Wordfilter()

#mashapeKey = open('mashapekey.txt').read().strip()

def domainrStatus(domain):
    params = {'mashape-key': mashapeKey,
              'domain': domain}
    url = domainrEndpoint + 'status?' + urllib.urlencode(params)
    urldoc = urllib.urlopen(url)
    result = json.load(urldoc)
    urldoc.close()
    return result['status'][0]['status'].split()

while True:
    random.shuffle(words)
    for word in words:
        random.shuffle(domains)
        lword = domainNameDisallowed.sub(u"", word.lower())

        if wordfilter.blacklisted(lword):
            continue

        for extension in domains:
            if len(extension) < 2: continue
            if len(extension) >= len(lword): continue
            if lword.endswith(extension):
                domain = lword[:-len(extension)]+u"."+lword[-len(extension):]
                if domain in history: continue
                history.add(domain)

                historyfile = codecs.open(historyFilename, 'a', 'utf-8')
                historyfile.write(domain+u"\n")
                historyfile.close()

                try:
                    if whois.whois(domain).expiration_date is not None:
                        print "not", domain.encode('utf-8')
                        continue
                except Exception, e:
                    print e,

                publicStatusCycle += 1
                if publicStatusCycle == publicStatusFrequency:
                    publicStatusCycle = 0
                    visibility = 'public'
                else:
                    visibility = 'unlisted'

                print visibility, domain.encode('utf-8')

                for i in range(5):
                    try:
                        if not testing:
                            mastodon.status_post(domain, visibility=visibility)
                        break
                    except MastodonNetworkError, e:
                        if i >= 4:
                            raise
                        else:
                            print e
                            time.sleep(5)

                time.sleep(sleepDuration)
                break

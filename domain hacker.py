import os, csv, urllib, sys

domainslist = urllib.urlopen("http://data.iana.org/TLD/tlds-alpha-by-domain.txt")
domains = set(filter(lambda a: not a.startswith('#'), [line.strip().lower() for line in domainslist]))
domainslist.close()

mindomainlen = min(map(len, domains))
maxdomainlen = max(map(len, domains))

words = open("/usr/share/dict/words")

if os.path.exists(sys.argv[1]):
    lastfile = open(sys.argv[1])
    lastword = lastfile.readlines()[-1]
    lastword = lastword[:lastword.find(',')]
    lastfile.close()
    for word in words:
        if word.strip() == lastword: break

fout = open(sys.argv[1], 'w')
writer = csv.writer(fout)
for word in words:
    word = word.strip()
    lword = word.lower()
    for i in range(mindomainlen, min(len(word)-1, maxdomainlen)):
        if lword[-i:] in domains:
            row = []
            row.append(word)
            domain = lword[:-i]+'.'+word[-i:]
            row.append(domain)
            exitCode = os.system("host -W 1 "+domain+"")
            if exitCode == 0:
                # If it has a host,
                # the website already exists.
                #row.append("Taken")
                continue
            elif exitCode in (1, 256):
                #row.append("Available")
                pass
            else:
                raise Exception("invalid exit code "+str(exitCode))
            '''url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q="+urllib.quote_plus(word)
            print url
            urldoc = urllib.urlopen(url)
            result = json.loads(urldoc.read())
            urldoc.close()
            row.append(result["responseData"]["cursor"]["estimatedResultCount"])'''
            row.append(len(word))
            row.append(i)
            writer.writerow(row)
fout.close()
words.close()

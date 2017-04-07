import os, csv, urllib, sys
fin = open(sys.argv[1])
domains = list([line.strip().lower() for line in fin])
fin.close()
words = open("/usr/share/dict/cracklib-small")
fout = open(sys.argv[2], 'w', newline='')
writer = csv.writer(fout)
null = None
true = True
false = False
for word in words:
    word = word.strip().lower()
    for i in range(2, len(word)):
        if word[-i:] in domains:
            row = []
            row.append(word)
            domain = word[:-i]+'.'+word[-i:]
            row.append(domain)
            exitCode = os.system("host "+domain+"")
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
            result = eval(urldoc.read())
            urldoc.close()
            row.append(result["responseData"]["cursor"]["estimatedResultCount"])'''
            row.append(len(word))
            row.append(i)
            writer.writerow(row)
fout.close()
words.close()
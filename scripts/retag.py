import os
import sys

TAGS = '''mobile
android
side-channel
software-engineering
tool
framework
embedded
firmware
dynamic
static
rootkit
bootkit
vulnerabilit
fuzz
symbolic
defense
attack
detect
iot
operating-system
smartphone
kernel
forensic
web
trac
sgx
malware
cloud
sandbox
trusted
automatic
ndss
usenix
acm
ieee
network
virtual
obfuscat
acsac
''' + '\n'.join(str(i) for i in range(2000, 2021))

translations = {
    'obfuscat': 'obfuscation',
    'virtual': 'virtualization',
    'vulnerabilit': 'vulnerability',
    'trac': 'tracing',
    'forensic': 'forensics'
}

filename = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../bookshelf.tsv")
TITLE = 'Title\tLink\ttag00\ttag01\ttag02\ttag03\ttag04\ttag05\ttag06\ttag07\ttag08\ttag09\ttag10\ttag11\ttag12\ttag13\ttag14'


papers = dict()

if __name__ == "__main__":
    with open(filename, 'r') as f:
        log_content = f.read().strip().split('\n')[1:]
    for line in log_content:
        title = line.split('\t')[0]
        current_tags = line.split('\t')[2:]
        link = line.split('\t')[1]

        tag_list = TAGS.split('\n')
        mangled_title = title.lower().replace(' ', '-')
        for tag in tag_list:
            if tag in mangled_title and len(current_tags) < 5:
                if tag in translations:
                    tag = translations[tag]
                if tag in current_tags:
                    continue
                current_tags.append(tag)

        papers[title] = "{title}\t{link}\t{keywords}".format(
            title=title,
            link=link,
            keywords='\t'.join(sorted(current_tags))
        )

    with open(filename, 'w') as f:
        f.write(TITLE)
        f.write('\n')
        for title in sorted(papers):
            f.write(papers[title].strip())
            f.write('\n')



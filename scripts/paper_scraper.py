from IPython import embed
from bs4 import BeautifulSoup
import requests
import random
import time
import sys
import os
import html

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

ONLY_TITLE = False
papers = dict() # title -> data
TITLE = 'Title\tLink\ttag00\ttag01\ttag02\ttag03\ttag04\ttag05\ttag06\ttag07\ttag08\ttag09\ttag10\ttag11\ttag12\ttag13\ttag14'

query_template = "https://dblp.org/search/publ/api?q=year:{year}%20venue:{venue}&h={limit}&format=json"
acm_abstract_template = 'https://dl.acm.org/tab_abstract.cfm?id={doi_id}'
html_body_template = '''<html>
<body>
{content}
</body>
</html>'''
logfile_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../bookshelf.tsv")

user_agent_list = [
    #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

def generate_header():
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
    return headers


def search_per_venue(venue: str, year: str):
    r = requests.get(
        query_template.format(year=year, venue=venue, limit=1000),
        headers=generate_header()
    )
    if r.status_code != 200:
        raise Exception('Failed %d: %s' % (
            r.status_code, query_template.format(year=year, venue=venue, limit=1000)))
    res  = r.json()
    if 'hit' in res['result']['hits']:
        hits = res['result']['hits']['hit']
        return hits
    return []

def get_domain(url):
    domain_init_idx = url.find("://")+3
    domain = url[domain_init_idx:]
    domain_fin_idx = domain.find("/")
    return domain[:domain_fin_idx]

def find_paper_url_NDSS(soup):
    paper_url = None
    for a in soup.find_all("a"):
        if a.text == "Paper":
            paper_url = a.attrs['href']
    return paper_url

def find_paper_url_USENIX_SECURITY(soup):
    paper_url = None
    for a in soup.find_all("a"):
        if "PDF" in a.text:
            paper_url = a.attrs['href']
            break
    return paper_url

def avoid_broken_ndss_links(url):
    if 'wp.internetsociety.org/ndss/wp-content/uploads/sites' in url:
        splitted_url = url.split('/')
        paper = splitted_url[-1]
        month = splitted_url[-2]
        year  = splitted_url[-3]
        return '/'.join(['https://www.ndss-symposium.org/wp-content/uploads', year, month, paper])
    return url

def filter_per_keyword(hits, keywords):
    for hit in hits:
        # be gentle
        time.sleep(random.choice([1,2,2,3,3,3,4,4,5,6]))

        s = requests.Session()
        s.headers.update(generate_header())

        hit = hit['info']
        if 'ee' not in hit:
            print(bcolors.WARNING + "WARNING - no url for: " + hit["title"], bcolors.ENDC)
            continue
        
        title = hit['title']
        venue = hit['venue']
        year  = hit['year']
        url   = hit['ee']
        soup = None

        try:
            url = avoid_broken_ndss_links(url)
            r = s.get(url)
            if r.status_code != 200:
                raise Exception('Failed %d: %s' % (r.status_code,url))
            abstract = r.content
            if 'acm.org' in r.url.lower():
                doi_id = url.split('.')[-1].strip()
                r = s.get(acm_abstract_template.format(
                    doi_id=doi_id), headers={'referer':r.url})
                if r.status_code != 200:
                    raise Exception('Failed %d: %s' % (r.status_code,                   
                        acm_abstract_template.format(
                            doi_id=doi_id)))
                raw_abstract = r.content
                abstract = html_body_template.format(
                    content=raw_abstract.decode(encoding='ascii', errors='ignore')).encode()
        except ConnectionError:
            print(bcolors.FAIL + "ERROR - connection error on %s. URL: %s" % (title, url), bcolors.ENDC)
            continue

        keywords_ok = []
        for keyword in keywords:
            is_abstract_good = False
            if abstract is not None and b"%PDF" == abstract[:4]:
                with open("/tmp/tmp.pdf", "wb") as fout:
                    fout.write(abstract)
                is_abstract_good = os.system("pdfgrep --page-range=1 '{pattern}' /tmp/tmp.pdf > /dev/null".format(
                    pattern=keyword
                )) == 0

            elif abstract is not None:
                soup = BeautifulSoup(abstract, features="html.parser")
                abstract_ascii = str(soup.body.text).lower()
                if keyword.lower() in abstract_ascii:
                    is_abstract_good = True
            if keyword.lower() in title.lower() or (not ONLY_TITLE and is_abstract_good):
                keywords_ok.append(keyword)
        
        if len(keywords_ok) > 0:
            paper_url = None
            # if b"%PDF" == abstract[:4]:
            #     paper_url = url
            # elif soup and "ndss" in venue.lower():
            #     paper_url = find_paper_url_NDSS(soup)
            # elif soup and "usenix security" in venue.lower():
            #     paper_url = find_paper_url_USENIX_SECURITY(soup)

            # if paper_url is not None and "://" not in paper_url:
            #     paper_url = "http://" + get_domain(url) + paper_url

            val = {
                'title': title,
                'venue': venue,
                'year':  year,
                'paper': paper_url,
                'url': url,
                'tags': '\t'.join(sorted(keywords_ok))
            }
            yield val

def parse_log(filename):
    with open(filename, 'r') as f:
        log_content = f.read().strip().split('\n')[1:]
    for line in log_content:
        title = line.split('\t')[0]
        papers[title] = line

def write_log(filename):
    with open(filename, 'w') as f:
        f.write(TITLE)
        f.write('\n')
        for title in sorted(papers):
            f.write(papers[title].strip())
            f.write('\n')

def search(venue, year_min, year_max, keywords):
    # logfile = open(logfile_path, "a")
    parse_log(logfile_path)

    for year in range(year_min, year_max+1):
        year = str(year)
        
        # dirname = "./papers/%s" % venue.replace(" ", "-")+"_"+year
        # if not os.path.exists(dirname):
        #     os.mkdir(dirname)
        
        hits = search_per_venue(venue, year)
        for result in filter_per_keyword(hits, keywords):
            print("{}\n\tvenue: {}\n\tyear: {}".format(
                bcolors.OKGREEN + html.unescape(result["title"]) + bcolors.ENDC,
                venue, 
                year))
            log_title = "[{} {}] ".format(
                result['venue'], result['year']) + html.unescape(result["title"])
            
            if log_title in papers:
                old_tags = papers[log_title].split('\t')[2:]
                new_tags = result['tags'].split('\t')
                tags = '\t'.join(sorted(set(old_tags + new_tags)))
            else:
                tags = result['tags']

            papers[log_title] = "{title}\t{link}\t{keywords}".format(
                title=log_title,
                link=result['url'],
                keywords=tags
            )

            # if result["paper"] is not None:
            #     try:
            #         blob = requests.get(result["paper"], headers=generate_header()).content
            #     except:
            #         print("error during downloading pdf, url: %s" % result["paper"])
            #     with open(dirname+"/"+result["title"].replace(" ", "_").replace("/", "")+".pdf", "wb") as fout:
            #         fout.write(blob)
            # else:
            #     print("\tNO PDF!")
    write_log(logfile_path)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "USAGE: python3 %s venue year_min year_max keyword1 [keyword2 ...]" % sys.argv[0])
        exit(1)

    venue = sys.argv[1]
    year_min = int(sys.argv[2])
    year_max = int(sys.argv[3])
    keywords = sys.argv[4:]
    search(venue, year_min, year_max, keywords)

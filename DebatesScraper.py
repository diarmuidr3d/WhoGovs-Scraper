import datetime
import requests
from lxml import html
# from lxml.html import HtmlElement
from Objects import Debate

dail_debates_2016_jan_1 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016011300001?opendocument"
dail_debates_2016_jan_2 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016011300002?opendocument"
dail_debates_2016_jan_3 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016011300003?opendocument"
dail_debates_2016_jan13 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/takes/dail2016011300013?opendocument"
dail_debates_years = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/yearlist?readform&chamber=dail"
seanad_debates_years = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/yearlist?readform&chamber=seanad"
committee_debates_years = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/yearlist?readform&chamber=committees"

dail_debates_2016 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=dail&year=2016"
seanad_debat_2016 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=seanad&year=2016"
committee_debates_2016 = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/committeebasebyyear/2016?opendocument"

# Committee page by year has significantly different structure to the houses

domain = "http://oireachtasdebates.oireachtas.ie/"

xpath_days_for_year = "/html/body/div[1]/div/div/div[3]/div/table/tr/td[2]/a/@href"
xpath_headings_for_debate = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td/h3/text()"
xpath_page_content = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td"


def get_page(url):
    """
    :type url: str
    """
    content = requests.get(url).content
    return html.fromstring(content)


def get_debate_urls_for_year(house, year):
    """
    :type year: int
    :type house: str
    """
    url = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=" + \
          house + "&year=" + str(year)
    year_page = get_page(url)
    day_urls = year_page.xpath(xpath_days_for_year)
    for each in day_urls:
        get_debate_content(domain + str(each))


def get_debate_content(url):
    """
    :type url: str
    """
    xpath_heading_text = "text()"
    page_num = 3
    cut_off = url.find("0000")
    url = url[:cut_off]
    datestring = url[len(url)-8:]
    date = datetime.date(int(datestring[:4]), int(datestring[4:6]), int(datestring[6:]))
    reached_end = False
    current_proceeding = None
    while not reached_end:
        page = get_page(url + str(page_num).zfill(5))
        content = page.xpath(xpath_page_content)
        if len(content) == 0:
            reached_end = True
        else:
            content = content[0]
            for child in list(content):
                print(child)
                if type(child) is html.HtmlElement:
                    tag = child.tag
                    if tag == 'h3':
                        title = child.xpath(xpath_heading_text)[0]
                        current_proceeding = Debate(1, title, date)
                    elif tag == 'p':
                        identifier = "MemberID="
                        rep_url = str(child.xpath("a[1]/@href")[0])
                        rep_id = int(rep_url[rep_url.find(identifier)+len(identifier):])
#                         TODO: create the repspoke / repwrote items and add them to the proceeding



dail = "dail"
seanad = "seanad"
earliest_year = 1919

def begin_scrapng():
    current_year = datetime.datetime.now().year
    while current_year >= earliest_year:
        get_debate_urls_for_year(dail, current_year)
        get_debate_urls_for_year(seanad, current_year)
        current_year -= 1




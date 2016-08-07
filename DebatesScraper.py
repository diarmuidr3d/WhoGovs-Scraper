import datetime
from lxml import html
from Objects import Debate, Representative, RepSpoke
from Scraper import to_str, get_page, encode
# Committee page by year has significantly different structure to the houses

domain = "http://oireachtasdebates.oireachtas.ie/"

xpath_days_for_year = "/html/body/div[1]/div/div/div[3]/div/table/tr/td[2]/a/@href"
xpath_headings_for_debate = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td/h3/text()"
xpath_page_content = "/html/body/div[1]/div/div/div[3]/div/table[2]/tr/td"


def get_debate_urls_for_year(house, year):
    """
    :type year: int
    :type house: str
    """
    url = "http://oireachtasdebates.oireachtas.ie/debates%20authoring/debateswebpack.nsf/datelist?readform&chamber=" + \
          house + "&year=" + to_str(year)
    year_page = get_page(url)
    day_urls = year_page.xpath(xpath_days_for_year)
    for each in day_urls:
        get_debate_content(domain + to_str(each))


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
    proceeding_content_order = 0
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
                        title = to_str(child.xpath(xpath_heading_text)[0])
                        current_proceeding = Debate(1, title, date)
                        proceeding_content_order = 0
                    elif tag == 'h4':
                    #     TODO: Add sub proceedings to the proceeding to allow for individual questions
                    elif tag == 'p':
                        # question_number = child.xpath TODO: avoid including the description of a question in the debate
                        identifier = "MemberID="
                        rep_url = child.xpath("a[1]/@href")
                        if len(rep_url) is not 0:
                            rep_url = to_str(rep_url[0])
                            rep_id = to_str(rep_url[rep_url.find(identifier)+len(identifier):])
                            representative = Representative(rep_id)
                        text = to_str(child.xpath("text()"))
                        record = RepSpoke(rep_id + "_" + encode(title) + "_" + to_str(proceeding_content_order), representative, current_proceeding, text, proceeding_content_order,)
                        current_proceeding.add_proceeding_record(record)
                        proceeding_content_order += 1
#                         TODO: create the repspoke / repwrote items and add them to the proceeding

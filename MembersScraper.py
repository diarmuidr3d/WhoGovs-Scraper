import traceback
import urllib
import unicodedata
import requests
import sys

from Objects import Representative, RepInConstituency, Constituency, Party, House, export_graph
from lxml import html
from datetime import date as Date

dail_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=0'
seanad_members_url = 'http://www.oireachtas.ie/members-hist/default.asp?housetype=1'

house_instances_selector = "html body div#limiter div#container.container div.row div.col-xs-12 div.row div.col-md-9.col-xs-12.col-md-push-3.column-center2 div.column-center-inner div table tbody tr"


class MembersScraper:
    members_url = "http://www.oireachtas.ie/members-hist/default.asp?MemberID="
    xpath_name = "/html/body/div/div/div/div[1]/div[2]/div[1]/div/div[1]/div[6]/h3/text()"
    xpath_life = "/html/body/div/div/div/div[1]/div[2]/div[1]/div/div[1]/div[6]/p[1]/text()"
    xpath_profession = "//h5[text() = 'Profession: ']/span/text()"
    xpath_party = "//h5[text() = 'Party: ']/span/text()"
    xpath_all_house = "//b[text() = 'House: ']/a/text()"
    xpath_all_constituency = "//li[span/text() = 'Constituency']/a/text()"
    xpath_all_parties = "//li[span/text() = 'Party']/text()"

    def scrape_details(self, member_id):
        page = html.fromstring(requests.get(self.members_url + str(member_id)).content)
        member_name = page.xpath(self.xpath_name)
        if len(member_name) == 1:
            member_name = member_name[0]
            lifetime = page.xpath(self.xpath_life)
            if len(lifetime) == 1:
                lifetime = self.parse_lifetime(lifetime[0])
            else:
                lifetime = (None, None)
            professions = page.xpath(self.xpath_profession)
            if len(professions) == 1:
                professions = self.parse_professions(professions[0])
            else:
                professions = None
            party = page.xpath(self.xpath_party)
            if len(party) == 1:
                party = party[0]
            else:
                party = None
            all_houses = page.xpath(self.xpath_all_house)
            all_constituencies = page.xpath(self.xpath_all_constituency)
            all_parties = page.xpath(self.xpath_all_parties)
            representative = Representative(member_id, member_name, lifetime[0], lifetime[1], professions)
            for each in range(0, len(all_constituencies)):
                constituency_id = self.encode(self.to_str(all_constituencies[each]))
                constituency = Constituency(constituency_id, all_constituencies[each])
                organisations = []
                if len(all_parties) > each:
                    organisations.append(Party(self.encode(self.to_str(all_parties[each])), all_parties[each]))
                organisations.append(House(self.encode(self.to_str(all_houses[each])), all_houses[each]))
                rep_record = RepInConstituency(str(member_id)+"_"+constituency_id, constituency, representative, organisations)
                representative.add_rep_records(rep_record)
            print(member_name, ", ", lifetime, ", ", professions, ", ", party, ", ", all_houses, ", ", all_constituencies, ", ", all_parties)
            return True
        else:
            print("no data found for id: ", member_id)
            return False

    def parse_professions(self, professions):
        index = professions.find(',')
        if index == -1:
            return [professions.strip()]
        else:
            profession = professions[:index]
            profession.strip()
            professions = professions[index+1:]
            retVal = self.parse_professions(professions)
            retVal.append(profession)
            return retVal

    def parse_lifetime(self, lifetime):
        """
        Assuming it's in the form (DD/MM/YYYY - DD/MM/YYYY)
        :type lifetime: str
        """
        def parse_date(date):
            slash = date.find('/')
            dayval = date[:slash]
            day = int(dayval)
            my = date[slash+1:]
            secondslash = my.find('/')
            month = int(my[:secondslash])
            year = int(my[secondslash+1:])
            return Date(year, month, day)

        open_bracket = lifetime.find('(')
        close_bracket = lifetime.find(')')
        separator = lifetime.find('-')
        born = lifetime[open_bracket+1:separator]
        died = lifetime[separator+1:close_bracket]
        born = born.strip()
        died = died.strip()
        if born == '':
            born = None
        else:
            born = parse_date(born)
        if died == '':
            died = None
        else:
            died = parse_date(died)
        return born, died

    def to_str(self, to_convert):
        try:
            return str(to_convert)
        except UnicodeEncodeError:
            return unicodedata.normalize('NFKD', to_convert).encode('ascii', 'ignore')

    def encode(self, string):
        return urllib.quote(string, safe='')


rep_id = 1
scraper = MembersScraper()
false_count = 0
try:
    while false_count < 5:
        return_value = scraper.scrape_details(rep_id)
        if return_value:
            false_count = 0
        else:
            false_count += 1
        rep_id += 1
except (KeyboardInterrupt, SystemExit, Exception) as err:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("*** print_exception: ***")
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
    print("*** Exception over ***")
    export_graph("whogovs.n3")
export_graph("whogovs.n3")
import traceback
import urllib
import unicodedata

import re
import requests
import sys

from Objects import Representative, RepInConstituency, Constituency, Party, House, export_graph, Role
from lxml import html
from datetime import date as Date, date

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
    xpath_appointments = "/html/body/div/div/div/div[1]/div[2]/div[1]/div/div[1]/div[6]/p[3]"

    def scrape_details(self, member_id):
        print(member_id)
        content = requests.get(self.members_url + str(member_id)).content
        page = html.fromstring(content)
        member_name = page.xpath(self.xpath_name)
        if len(member_name) == 1:
            member_name = member_name[0]
            lifetime = page.xpath(self.xpath_life)
            if len(lifetime) == 1:
                lifetime = self.__parse_lifetime(lifetime[0])
            else:
                lifetime = (None, None)
            professions = page.xpath(self.xpath_profession)
            if len(professions) == 1:
                professions = self.__parse_professions(professions[0])
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
            all_appointments = page.xpath(self.xpath_appointments)
            representative = Representative(member_id, member_name, lifetime[0], lifetime[1], professions)
            if len(all_appointments) > 0:
                appointments = self.__parse_appointments(html.tostring(all_appointments[0]), representative)
            for each in range(0, len(all_constituencies)):
                constituency_id = self.__encode(self.__to_str(all_constituencies[each]))
                constituency = Constituency(constituency_id, all_constituencies[each])
                organisations = []
                if len(all_parties) > each:
                    organisations.append(Party(self.__encode(self.__to_str(all_parties[each])), all_parties[each]))
                organisations.append(House(self.__encode(self.__to_str(all_houses[each])), all_houses[each]))
                rep_record = RepInConstituency(str(member_id) + "_" + constituency_id, constituency, representative,
                                               organisations)
                representative.add_rep_records(rep_record)
            return True
        else:
            print("no data found for id: ", member_id)
            return False

    def __parse_appointments(self, details, representative):
        split_app = re.findall(r">[^<]*<", details)
        current_dail = ""
        return_values = {}
        role_id = 0
        for each in split_app:
            trimmed = each.replace('<', '').replace('>', '').strip()
            if '-' in trimmed:
                index = trimmed.find('-')
                if index != -1:
                    current_dail = trimmed[:index].strip()
                    trimmed = trimmed[index + 1:].strip()
            if current_dail not in return_values:
                return_values[current_dail] = []
            role = Role(str(representative.object_id) + "_role_" + str(role_id), representative, date(1916, 1, 1),
                        title=trimmed)
            return_values[current_dail].append(role)
            role_id += 1
        return return_values

    def __parse_professions(self, professions):
        index = professions.find(',')
        if index == -1:
            return [professions.strip()]
        else:
            profession = professions[:index]
            profession.strip()
            professions = professions[index + 1:]
            retVal = self.__parse_professions(professions)
            retVal.append(profession)
            return retVal

    def __parse_lifetime(self, lifetime):
        """
        Assuming it's in the form (DD/MM/YYYY - DD/MM/YYYY)
        :type lifetime: str
        """

        def parse_date(date):
            slash = date.find('/')
            dayval = date[:slash]
            day = int(dayval)
            my = date[slash + 1:]
            secondslash = my.find('/')
            month = int(my[:secondslash])
            year = int(my[secondslash + 1:])
            return Date(year, month, day)

        open_bracket = lifetime.find('(')
        close_bracket = lifetime.find(')')
        separator = lifetime.find('-')
        born = lifetime[open_bracket + 1:separator]
        died = lifetime[separator + 1:close_bracket]
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

    def __to_str(self, to_convert):
        try:
            return str(to_convert)
        except UnicodeEncodeError:
            return unicodedata.normalize('NFKD', to_convert).encode('ascii', 'ignore')

    def __encode(self, string):
        return urllib.quote(string, safe='')

def begin_scraping():
    # MembersScraper().scrape_details(6)
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
        print("*** print exception: ***")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        print("*** Exception over ***")
        export_graph("whogovs.n3")
    export_graph("whogovs.n3")

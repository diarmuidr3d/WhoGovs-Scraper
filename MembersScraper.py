import requests
from Objects import Representative, RepInConstituency, Constituency
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
            representative = Representative(member_name, lifetime[0], lifetime[1], professions)
            for each in all_constituencies:
                constituency = Constituency(each)
                # rep_in_constituency = RepInConstituency(constituency, representative, )
            print(member_name, ", ", lifetime, ", ", professions, ", ", party, ", ", all_houses, ", ", all_constituencies, ", ", all_parties)
            # self.scrape_details(member_id + 1)
        else:
            return 0

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


MembersScraper().scrape_details(12)
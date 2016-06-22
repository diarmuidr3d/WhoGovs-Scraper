from tribool import Tribool
from datetime import date


class Contactable:
    def __init__(self, name, email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type name: str
        """
        self.hasWebsite = website_id
        self.hasTwitterId = twitter_id
        self.hasFacebookId = facebook_id
        self.hasEmailAddress = email_address
        self.hasName = name


class Person(Contactable):
    def __init__(self, name, born_on=None, died_on=None, profession=None, candidate_in=None, email_address=None,
                 facebook_id=None,
                 twitter_id=None, website_id=None):
        """
        :type profession: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type candidate_in: ElectionRecord
        :type died_on: date
        :type born_on: date
        :type name: str
        """
        Contactable.__init__(self, name, email_address, facebook_id, twitter_id, website_id)
        self.hasProfession = profession
        self.wasBornOn = born_on
        self.diedOn = died_on
        self.candidateIn = candidate_in


class Representative(Person):
    def __init__(self, name, born_on=None, died_on=None, profession=None, candidate_in=None, email_address=None,
                 facebook_id=None,
                 twitter_id=None, website_id=None):
        """
        :type profession: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type candidate_in: ElectionRecord
        :type died_on: date
        :type born_on: date
        :type name: str
        """
        Person.__init__(self, name, born_on, died_on, profession, candidate_in, email_address, facebook_id, twitter_id,
                        website_id)


class Constituency:
    def __init__(self, name):
        """
        :type name: str
        """
        self.hasName = name


class Organisation:
    def __init__(self, name, belongs_to=None, has_belonging=None):
        """
        :type name: str
        :type has_belonging: [Organisation]
        :type belongs_to: [Organisation]
        """
        self.hasBelonging = has_belonging
        self.belongsTo = belongs_to
        self.hasName = name


class Party(Contactable, Organisation):
    def __init__(self, name, email_address=None, facebook_id=None, twitter_id=None, website_id=None, belongs_to=None,
                 has_belonging=None):
        Contactable.__init__(self, name, email_address, facebook_id, twitter_id, website_id)
        Organisation.__init__(self, name, belongs_to, has_belonging)


class Legislature(Organisation):
    def __init__(self, name, belongs_to=None, has_belonging=None):
        Organisation.__init__(self, name, belongs_to, has_belonging)


class Committee(Legislature):
    def __init__(self, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, name, belongs_to, has_belonging)


class House(Legislature):
    def __init__(self, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, name, belongs_to, has_belonging)


class Election:
    def __init__(self, election_date, election_parts=None):
        """
        :type election_date: date
        :type election_parts: ElectionRecord
        """
        self.electionParts = election_parts
        self.onDate = election_date


class ConstituencyRecord:
    def __init__(self, constituency):
        """
        :type constituency: Constituency
        """
        self.inConstituency = constituency


class ElectionRecord(ConstituencyRecord):
    def __init__(self, constituency, candidates, election):
        """
        :type election: Election
        :type candidates: [Person]
        """
        ConstituencyRecord.__init__(self, constituency)
        self.inElection = election
        self.hasCandidate = candidates


class TemporalRecord:
    def __init__(self, start_date, end_date=None, title=None):
        """
        :type title: str
        :type end_date: date
        :type start_date: date
        """
        self.startDate = start_date
        self.endDate = end_date
        self.title = title


class RepresentativeRecord:
    def __init__(self, representative):
        """
        :type representative: Representative
        """
        self.representative = representative


class OrganisationRecord:
    def __init__(self, organisations):
        """
        :type organisation: [Organisation]
        """
        self.inOrganisation = organisations


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord, OrganisationRecord):
    def __init__(self, constituency, representative, organisations, start_date=None, end_date=None, title=None):
        """
        :type constituency: Constituency
        :type representative: Representative
        """
        ConstituencyRecord.__init__(self, constituency)
        TemporalRecord.__init__(self, start_date, end_date, title)
        RepresentativeRecord.__init__(self, representative)
        OrganisationRecord.__init__(self, organisations)


class Proceeding(TemporalRecord):
    def __init__(self, start_date, end_date=None, title=None, proceeding_records=None):
        """
        :type proceeding_records: [ProceedingRecord]
        """
        TemporalRecord.__init__(self, start_date, end_date, title)
        self.hasProceedingRecords = proceeding_records


class Debate(Proceeding):
    def __init__(self, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, title, start_date, end_date, proceeding_records)


class Vote(Proceeding):
    def __init__(self, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, title, start_date, end_date, proceeding_records)


class ProceedingRecord:
    def __init__(self, proceeding):
        """
        :type proceeding: Proceeding
        """
        self.inProceeding = proceeding


class RepSpoke(ProceedingRecord, RepresentativeRecord):
    def __init__(self, representative, proceeding, content, order):
        """
        :type order: int
        :type content: str
        """
        ProceedingRecord.__init__(self, proceeding)
        RepresentativeRecord.__init__(self, representative)
        self.order = order
        self.content = content


class RepVoted(ProceedingRecord, RepresentativeRecord):
    def __init__(self, representative, proceeding, vote):
        """
        :type vote: VoteOption
        :type proceeding: Proceeding
        :type representative: Representative
        """
        ProceedingRecord.__init__(self, proceeding)
        RepresentativeRecord.__init__(self, representative)
        self.vote = vote


class Membership(RepresentativeRecord, TemporalRecord):
    def __init__(self, representative, member_of, start_date, end_date=None, title=None):
        """
        :type representative: Representative
        :type member_of: Organisation
        """
        RepresentativeRecord.__init__(self, representative)
        TemporalRecord.__init__(self, start_date, end_date, title)
        self.memberOf = member_of


class Role(RepresentativeRecord, TemporalRecord):
    def __init__(self, representative, start_date, end_date=None, title=None):
        RepresentativeRecord.__init__(self, representative)
        TemporalRecord.__init__(self, start_date, end_date, title)


class VoteOption:
    def __init__(self, vote):
        """
        :type vote: Tribool
        """
        self.vote = vote

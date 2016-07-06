from tribool import Tribool
from datetime import date
from rdflib import Graph, Namespace, URIRef, RDF, XSD, Literal
from rdflib.resource import Resource

WHOGOVSNS = Namespace("http://www.whogovs.com/ontology/")
OBJECTSNS = Namespace("http://www.whogovs.com/objects/")

graph = Graph()
graph.namespace_manager.bind("WHOGOVS", WHOGOVSNS)
graph.namespace_manager.bind("WGOBJ", OBJECTSNS)


class LinkedClass(Resource):
    def __init__(self, object_uri):
        uri = OBJECTSNS + str(object_uri)
        Resource.__init__(self, graph, URIRef(uri))
        resource_type = URIRef(WHOGOVSNS + self.__class__.__name__)
        self.add(RDF.type, resource_type)


class Contactable(LinkedClass):
    def __init__(self, unique_id, name, email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type unique_id: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type name: str
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))
        if website_id is not None:
            self.add(WHOGOVSNS.hasWebsite, Literal(website_id, datatype=XSD.string))
        if twitter_id is not None:
            self.add(WHOGOVSNS.hasTwitterId, Literal(twitter_id, datatype=XSD.string))
        if facebook_id is not None:
            self.add(WHOGOVSNS.hasFacebookId, Literal(facebook_id, datatype=XSD.string))
        if email_address is not None:
            self.add(WHOGOVSNS.hasEmailAddress, Literal(email_address, datatype=XSD.string))


class Person(Contactable):
    def __init__(self, unique_id, name, born_on=None, died_on=None, profession=None, election_record=None,
                 email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type unique_id: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type election_record: ElectionRecord
        :type died_on: date
        :type born_on: date
        :type name: str
        """
        Contactable.__init__(self, unique_id, name, email_address, facebook_id, twitter_id, website_id)
        if born_on is not None:
            self.add(WHOGOVSNS.bornOn, Literal(born_on, datatype=XSD.dateTime))
        if died_on is not None:
            self.add(WHOGOVSNS.diedOn, Literal(died_on, datatype=XSD.dateTime))
        if profession is not None:
            if type(profession) is list:
                for each in profession:
                    self.add(WHOGOVSNS.hasProfession, Literal(each, datatype=XSD.string))
            else:
                self.add(WHOGOVSNS.hasProfession, Literal(profession, datatype=XSD.string))
        if election_record is not None:
            if type(election_record) is list:
                for each in election_record:
                    self.add(WHOGOVSNS.candidateIn, each)
            else:
                self.add(WHOGOVSNS.candidateIn, election_record)


class Representative(Person):
    def __init__(self, unique_id, name, born_on=None, died_on=None, profession=None, election_record=None,
                 email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type unique_id: str
        :type profession: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type election_record: ElectionRecord
        :type died_on: date
        :type born_on: date
        :type name: str
        """
        Person.__init__(self, unique_id, name, born_on, died_on, profession, election_record, email_address,
                        facebook_id, twitter_id, website_id)


class Constituency(LinkedClass):
    def __init__(self, unique_id, name):
        """
        :type unique_id: str
        :type name: str
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))


class Organisation(LinkedClass):
    def __init__(self, unique_id, name, belongs_to=None, has_belonging=None):
        """
        :type unique_id: str
        :type name: str
        :type has_belonging: [Organisation]
        :type belongs_to: [Organisation]
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))
        if has_belonging is not None:
            if type(has_belonging) is list:
                for each in has_belonging:
                    self.add(WHOGOVSNS.hasBelonging, each)
            else:
                self.add(WHOGOVSNS.hasBelonging, has_belonging)
        if belongs_to is not None:
            if type(belongs_to) is list:
                for each in belongs_to:
                    self.add(WHOGOVSNS.belongsTo, each)
            else:
                self.add(WHOGOVSNS.belongsTo, belongs_to)


class Party(Contactable, Organisation):
    def __init__(self, unique_id, name, email_address=None, facebook_id=None, twitter_id=None, website_id=None,
                 belongs_to=None,
                 has_belonging=None):
        Contactable.__init__(self, unique_id, name, email_address, facebook_id, twitter_id, website_id)
        Organisation.__init__(self, unique_id, name, belongs_to, has_belonging)


class Legislature(Organisation):
    def __init__(self, unique_id, name, belongs_to=None, has_belonging=None):
        Organisation.__init__(self, unique_id, name, belongs_to, has_belonging)


class Committee(Legislature):
    def __init__(self, unique_id, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, unique_id, name, belongs_to, has_belonging)


class House(Legislature):
    def __init__(self, unique_id, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, unique_id, name, belongs_to, has_belonging)


class Election(LinkedClass):
    def __init__(self, unique_id, election_date, election_parts=None):
        """
        :type unique_id: str
        :type election_date: date
        :type election_parts: ElectionRecord
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.onDate, election_date)
        if election_parts is not None:
            if type(election_parts) is list:
                for each in election_parts:
                    self.add(WHOGOVSNS.electionParts, each)
            else:
                self.add(WHOGOVSNS.electionParts, election_parts)


class ConstituencyRecord(LinkedClass):
    def __init__(self, unique_id, constituency):
        """
        :type unique_id: str
        :type constituency: Constituency
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.inConstituency, constituency)


class ElectionRecord(ConstituencyRecord, LinkedClass):
    def __init__(self, unique_id, constituency, candidates, election):
        """
        :type unique_id: str
        :type election: Election
        :type candidates: [Person]
        """
        ConstituencyRecord.__init__(self, unique_id, constituency)
        if type(candidates) is list:
            for each in candidates:
                self.add(WHOGOVSNS.hasCandidate, each)
        else:
            self.add(WHOGOVSNS.hasCandidate, candidates)
        self.add(WHOGOVSNS.inElection, election)


class TemporalRecord(LinkedClass):
    def __init__(self, unique_id, start_date, end_date=None, title=None):
        """
        :type unique_id: str
        :type title: str
        :type end_date: date
        :type start_date: date
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.startDate, Literal(start_date, datatype=XSD.dateTime))
        if end_date is not None:
            self.add(WHOGOVSNS.endDate, Literal(end_date, datatype=XSD.dateTime))
        if title is not None:
            self.add(WHOGOVSNS.title, Literal(title, datatype=XSD.string))


class RepresentativeRecord(LinkedClass):
    def __init__(self, unique_id, representative):
        """
        :type unique_id: str
        :type representative: Representative
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.representative, representative)


class OrganisationRecord(LinkedClass):
    def __init__(self, unique_id, organisations):
        """
        :type unique_id: str
        :type organisations: [Organisation]
        """
        LinkedClass.__init__(self, unique_id)
        if type(organisations) is list:
            for each in organisations:
                self.add(WHOGOVSNS.inOrganisation, each)
        else:
            self.add(WHOGOVSNS.inOrganisation, organisations)


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord, OrganisationRecord):
    def __init__(self, unique_id, constituency, representative, organisations, start_date=None, end_date=None,
                 title=None):
        """
        :type unique_id: str
        :type constituency: Constituency
        :type representative: Representative
        """
        ConstituencyRecord.__init__(self, unique_id, constituency)
        TemporalRecord.__init__(self, unique_id, start_date, end_date, title)
        RepresentativeRecord.__init__(self, unique_id, representative)
        OrganisationRecord.__init__(self, unique_id, organisations)


class Proceeding(TemporalRecord):
    def __init__(self, unique_id, start_date, end_date=None, title=None, proceeding_records=None):
        """
        :type unique_id: str
        :type proceeding_records: [ProceedingRecord]
        """
        TemporalRecord.__init__(self, unique_id, start_date, end_date, title)
        if proceeding_records is not None:
            if type(proceeding_records) is list:
                for each in proceeding_records:
                    self.add(WHOGOVSNS.hasProceedingRecords, each)
            else:
                self.add(WHOGOVSNS.hasProceedingRecords, proceeding_records)


class Debate(Proceeding):
    def __init__(self, unique_id, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, unique_id, title, start_date, end_date, proceeding_records)


class Vote(Proceeding):
    def __init__(self, unique_id, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, unique_id, title, start_date, end_date, proceeding_records)


class ProceedingRecord(LinkedClass):
    def __init__(self, unique_id, proceeding):
        """
        :type unique_id: str
        :type proceeding: Proceeding
        """
        LinkedClass.__init__(self, unique_id)
        self.add(WHOGOVSNS.inProceeding, proceeding)


class RepSpoke(ProceedingRecord, RepresentativeRecord):
    def __init__(self, unique_id, representative, proceeding, content, order):
        """
        :type unique_id: str
        :type order: int
        :type content: str
        """
        ProceedingRecord.__init__(self, unique_id, proceeding)
        RepresentativeRecord.__init__(self, unique_id, representative)
        self.add(WHOGOVSNS.order, Literal(order, datatype=XSD.positiveInteger))
        self.add(WHOGOVSNS.content, Literal(content, datatype=XSD.string))


class RepVoted(ProceedingRecord, RepresentativeRecord):
    def __init__(self, unique_id, representative, proceeding, vote):
        """
        :type unique_id: str
        :type vote: VoteOption
        :type proceeding: Proceeding
        :type representative: Representative
        """
        ProceedingRecord.__init__(self, unique_id, proceeding)
        RepresentativeRecord.__init__(self, unique_id, representative)
        self.add(WHOGOVSNS.vote, vote)


class Membership(RepresentativeRecord, TemporalRecord):
    def __init__(self, unique_id, representative, member_of, start_date, end_date=None, title=None):
        """
        :type unique_id: str
        :type representative: Representative
        :type member_of: Organisation
        """
        RepresentativeRecord.__init__(self, unique_id, representative)
        TemporalRecord.__init__(self, unique_id, start_date, end_date, title)
        if type(member_of) is list:
            for each in member_of:
                self.add(WHOGOVSNS.memberOf, each)
        else:
            self.add(WHOGOVSNS.memberOf, member_of)


class Role(RepresentativeRecord, TemporalRecord):
    def __init__(self, unique_id, representative, start_date, end_date=None, title=None):
        RepresentativeRecord.__init__(self, unique_id, representative)
        TemporalRecord.__init__(self, unique_id, start_date, end_date, title)


class VoteOption(LinkedClass):
    def __init__(self, vote):
        """
        :type vote: Tribool
        """
        if vote.value is True:
            LinkedClass.__init__(self, "Yes")
        elif vote.value is False:
            LinkedClass.__init__(self, "No")
        else:
            LinkedClass.__init__(self, "Abstain")

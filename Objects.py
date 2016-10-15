from tribool import Tribool
from datetime import date
from rdflib import Graph, Namespace, URIRef, RDF, XSD, Literal
from rdflib.resource import Resource

WHOGOVSNS = Namespace("http://www.whogovs.com/ontology/")
OBJECTSNS = Namespace("http://www.whogovs.com/objects/")


class MyGraph(Graph):
    def __init__(self):
        super(MyGraph, self).__init__()
        self.namespace_manager.bind("WHOGOVS", WHOGOVSNS)
        self.namespace_manager.bind("WGOBJ", OBJECTSNS)

    def add(self, (s, p, o)):
        if (s, p, o) not in self:
            Graph.add(self, (s, p, o))

    def export(self, filename):
        if filename is not None:
            output_file = open(filename, "wb")
            Graph.serialize(self, destination=output_file, format='n3', auto_compact=True)


class LinkedClass(Resource):
    def __init__(self, graph, object_uri):
        self.object_id = object_uri
        class_name = self.__class__.__name__
        self.object_uri = OBJECTSNS + class_name + "/" + str(object_uri)
        Resource.__init__(self, graph, URIRef(self.object_uri))
        resource_type = URIRef(WHOGOVSNS + class_name)
        self.set(RDF.type, resource_type)


class Contactable(LinkedClass):
    def __init__(self, graph, unique_id, name=None, email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type unique_id: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type name: str
        """
        LinkedClass.__init__(self, graph, unique_id)
        if name is not None:
            self.set_name(name)
        if website_id is not None:
            self.add_website(website_id)
        if twitter_id is not None:
            self.add_twitter_handle(twitter_id)
        if facebook_id is not None:
            self.add_facebook_id(facebook_id)
        if email_address is not None:
            self.add_email_address(email_address)

    def set_name(self, name):
        self.set(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))

    def add_website(self, website):
        self.add(WHOGOVSNS.hasWebsite, Literal(website, datatype=XSD.string))

    def add_twitter_handle(self, handle):
        self.add(WHOGOVSNS.hasTwitterId, Literal(handle, datatype=XSD.string))

    def add_facebook_id(self, facebook_id):
        self.add(WHOGOVSNS.hasFacebookId, Literal(facebook_id, datatype=XSD.string))

    def add_email_address(self, email_address):
        self.add(WHOGOVSNS.hasEmailAddress, Literal(email_address, datatype=XSD.string))


class Person(Contactable):
    def __init__(self, graph, unique_id, name=None, born_on=None, died_on=None, profession=None, election_record=None,
                 email_address=None, facebook_id=None, twitter_id=None, website_id=None):
        """
        :type unique_id: str
        :type website_id: str
        :type twitter_id: str
        :type facebook_id: str
        :type email_address: str
        :type died_on: date
        :type born_on: date
        :type name: str
        """
        Contactable.__init__(self, graph, unique_id, name, email_address, facebook_id, twitter_id, website_id)
        if born_on is not None:
            self.add_birth_date(born_on)
        if died_on is not None:
            self.add_death_date(died_on)
        if profession is not None:
            if type(profession) is list:
                self.add_profession_list(profession)
            else:
                self.add_profession(profession)
        if election_record is not None:
            if type(election_record) is list:
                self.add_election_record_list(election_record)
            else:
                self.add_election_record(election_record)

    def add_birth_date(self, born_on):
        self.set(WHOGOVSNS.bornOn, Literal(born_on, datatype=XSD.dateTime))

    def add_death_date(self, died_on):
        self.set(WHOGOVSNS.diedOn, Literal(died_on, datatype=XSD.dateTime))

    def add_profession(self, profession):
        """
        :type profession: str
        """
        self.add(WHOGOVSNS.hasProfession, Literal(profession, datatype=XSD.string))

    def add_profession_list(self, professions):
        """
        This is a bulk method for add_profession, provide a list of professions to add
        :type professions: list
        """
        for each in professions:
            self.add_profession(each)

    def add_election_record(self, election_record):
        """
        :type election_record: ElectionRecord
        """
        self.add(WHOGOVSNS.candidateIn, election_record)

    def add_election_record_list(self, election_record_list):
        """
        Bulk addition of election records
        :type election_record_list: list
        """
        for each in election_record_list:
            self.add_election_record(each)


class Representative(Person):
    def __init__(self, graph, unique_id, name=None, born_on=None, died_on=None, profession=None, election_record=None,
                 email_address=None, facebook_id=None, twitter_id=None, website_id=None, has_rep_record=None):
        """
        :type has_rep_record: [RepInConstituency]
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
        Person.__init__(self, graph, unique_id, name, born_on, died_on, profession, election_record, email_address,
                        facebook_id, twitter_id, website_id)
        if has_rep_record is not None:
            if type(has_rep_record) is list:
                self.add_rep_records_list(has_rep_record)
            else:
                self.add_rep_records(has_rep_record)

    def add_rep_records(self, rep_records):
        self.add(WHOGOVSNS.hasRepRecord, rep_records)

    def add_rep_records_list(self, rep_records_list):
        for each in rep_records_list:
            self.add_rep_records(each)


class Constituency(LinkedClass):
    def __init__(self, graph, unique_id, name):
        """
        :type unique_id: str
        :type name: str
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))


class Organisation(LinkedClass):
    def __init__(self, graph, unique_id, name, belongs_to=None, has_belonging=None):
        """
        :type unique_id: str
        :type name: str
        :type has_belonging: [Organisation]
        :type belongs_to: [Organisation]
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.hasName, Literal(name, datatype=XSD.Name))
        if has_belonging is not None:
            if type(has_belonging) is list:
                self.add_belonging_organisation_list(has_belonging)
            else:
                self.add_belonging_organisation(has_belonging)
        if belongs_to is not None:
            if type(belongs_to) is list:
                self.add_belongs_to_organisation_list(belongs_to)
            else:
                self.add_belongs_to_organisation(belongs_to)

    def add_belonging_organisation(self, organisation):
        """
        :type organisation: Organisation
        """
        self.add(WHOGOVSNS.hasBelonging, organisation)

    def add_belonging_organisation_list(self, organisations):
        """
        :type organisations: list
        """
        for each in organisations:
            self.add_belonging_organisation(each)

    def add_belongs_to_organisation(self, organisation):
        """
        :type organisation: Organisation
        """
        self.add(WHOGOVSNS.belongsTo, organisation)

    def add_belongs_to_organisation_list(self, organisations):
        """
        :type organisations: list
        """
        for each in organisations:
            self.add_belongs_to_organisation(each)


class Party(Contactable, Organisation):
    def __init__(self, graph, unique_id, name, email_address=None, facebook_id=None, twitter_id=None, website_id=None,
                 belongs_to=None,
                 has_belonging=None):
        Contactable.__init__(self, graph, unique_id, name, email_address, facebook_id, twitter_id, website_id)
        Organisation.__init__(self, graph, unique_id, name, belongs_to, has_belonging)


class Legislature(Organisation):
    def __init__(self, graph, unique_id, name, belongs_to=None, has_belonging=None):
        Organisation.__init__(self, graph, unique_id, name, belongs_to, has_belonging)


class Committee(Legislature):
    def __init__(self, graph, unique_id, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, graph, unique_id, name, belongs_to, has_belonging)


class House(Legislature):
    def __init__(self, graph, unique_id, name, belongs_to=None, has_belonging=None):
        Legislature.__init__(self, graph, unique_id, name, belongs_to, has_belonging)


class Election(LinkedClass):
    def __init__(self, graph, unique_id, election_date, election_parts=None):
        """
        :type unique_id: str
        :type election_date: date
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.onDate, election_date)
        if election_parts is not None:
            if type(election_parts) is list:
                self.add_election_part(election_parts)
            else:
                self.add_election_parts_list(election_parts)

    def add_election_part(self, election_record):
        """
        :type election_record: ElectionRecord
        """
        self.add(WHOGOVSNS.electionParts, election_record)

    def add_election_parts_list(self, records):
        """
        :type records: list
        """
        for each in records:
            self.add_election_part(each)


class ConstituencyRecord(LinkedClass):
    def __init__(self, graph, unique_id, constituency):
        """
        :type unique_id: str
        :type constituency: Constituency
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.inConstituency, constituency)


class ElectionRecord(ConstituencyRecord, LinkedClass):
    def __init__(self, graph, unique_id, constituency, candidates, election):
        """
        :type unique_id: str
        :type election: Election
        :type candidates: [Person]
        """
        ConstituencyRecord.__init__(self, graph, unique_id, constituency)
        if type(candidates) is list:
            for each in candidates:
                self.add(WHOGOVSNS.hasCandidate, each)
        else:
            self.add(WHOGOVSNS.hasCandidate, candidates)
        self.set(WHOGOVSNS.inElection, election)


class TemporalRecord(LinkedClass):
    def __init__(self, graph, unique_id, start_date, end_date=None, title=None):
        """
        :type unique_id: str
        :type title: str
        :type end_date: date
        :type start_date: date
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.startDate, Literal(start_date, datatype=XSD.dateTime))
        if end_date is not None:
            self.add_end_date(end_date)
        if title is not None:
            self.add_title(title)

    def add_end_date(self, end_date):
        """
        :type end_date: date
        """
        self.set(WHOGOVSNS.endDate, Literal(end_date, datatype=XSD.dateTime))

    def add_title(self, title):
        """
        :type title: str
        """
        self.set(WHOGOVSNS.title, Literal(title, datatype=XSD.string))


class RepresentativeRecord(LinkedClass):
    def __init__(self, graph, unique_id, representative):
        """
        :type unique_id: str
        :type representative: Representative
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.set(WHOGOVSNS.representative, representative)


class OrganisationRecord(LinkedClass):
    def __init__(self, graph, unique_id, organisations):
        """
        :type unique_id: str
        :type organisations: [Organisation]
        """
        LinkedClass.__init__(self, graph, unique_id)
        if type(organisations) is list:
            for each in organisations:
                self.add(WHOGOVSNS.inOrganisation, each)
        else:
            self.add(WHOGOVSNS.inOrganisation, organisations)


class RepInConstituency(ConstituencyRecord, TemporalRecord, RepresentativeRecord, OrganisationRecord):
    def __init__(self, graph, unique_id, constituency, representative, organisations, start_date=None, end_date=None,
                 title=None):
        """
        :type unique_id: str
        :type constituency: Constituency
        :type representative: Representative
        """
        ConstituencyRecord.__init__(self, graph, unique_id, constituency)
        if start_date is not None or end_date is not None:
            TemporalRecord.__init__(self, graph, unique_id, start_date, end_date, title)
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        OrganisationRecord.__init__(self, graph, unique_id, organisations)


class Proceeding(TemporalRecord):
    def __init__(self, graph, unique_id, start_date, end_date=None, title=None, proceeding_records=None):
        """
        :type unique_id: str
        """
        TemporalRecord.__init__(self, graph, unique_id, start_date, end_date, title)
        if proceeding_records is not None:
            if type(proceeding_records) is list:
                self.add_proceeding_records_list(proceeding_records)
            else:
                self.add_proceeding_record(proceeding_records)

    def add_proceeding_record(self, record):
        """
        :type record: ProceedingRecord
        """
        self.add(WHOGOVSNS.hasProceedingRecords, record)

    def add_proceeding_records_list(self, records):
        """
        :type records: list
        """
        for each in records:
            self.add_proceeding_record(each)


class Debate(Proceeding):
    def __init__(self, graph, unique_id, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, graph, unique_id, start_date, end_date, title, proceeding_records)


class Vote(Proceeding):
    def __init__(self, graph, unique_id, title, start_date, end_date=None, proceeding_records=None):
        Proceeding.__init__(self, graph, unique_id, start_date, end_date, title, proceeding_records)


class ProceedingRecord(LinkedClass):
    def __init__(self, graph, unique_id, proceeding):
        """
        :type unique_id: str
        :type proceeding: Proceeding
        """
        LinkedClass.__init__(self, graph, unique_id)
        self.add(WHOGOVSNS.inProceeding, proceeding)


class RepSpoke(ProceedingRecord, RepresentativeRecord):
    def __init__(self, graph, unique_id, representative, proceeding, content_value, order):
        """
        :type unique_id: str
        :type order: int
        :type content_value: str
        """
        ProceedingRecord.__init__(self, graph, unique_id, proceeding)
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        self.add(WHOGOVSNS.order, Literal(order, datatype=XSD.positiveInteger))
        self.content = content_value

    @property
    def content(self):
        return self.objects(WHOGOVSNS.content).next()

    @content.setter
    def content(self, content_value):
        """
        :type content_value: str
        """
        self.set(WHOGOVSNS.content, Literal(content_value, datatype=XSD.string))


class RepWrote(ProceedingRecord, RepresentativeRecord):
    def __init__(self, graph, unique_id, representative, proceeding, content):
        """
        :type unique_id: str
        :type content: str
        """
        ProceedingRecord.__init__(self, graph, unique_id, proceeding)
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        self.add(WHOGOVSNS.content, Literal(content, datatype=XSD.string))


class RepVoted(ProceedingRecord, RepresentativeRecord):
    def __init__(self, graph, unique_id, representative, proceeding, vote):
        """
        :type unique_id: str
        :type vote: VoteOption
        :type proceeding: Proceeding
        :type representative: Representative
        """
        ProceedingRecord.__init__(self, graph, unique_id, proceeding)
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        self.add(WHOGOVSNS.vote, vote)


class Membership(RepresentativeRecord, TemporalRecord):
    def __init__(self, graph, unique_id, representative, member_of, start_date, end_date=None, title=None):
        """
        :type unique_id: str
        :type representative: Representative
        :type member_of: Organisation
        """
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        TemporalRecord.__init__(self, graph, unique_id, start_date, end_date, title)
        if type(member_of) is list:
            for each in member_of:
                self.add(WHOGOVSNS.memberOf, each)
        else:
            self.add(WHOGOVSNS.memberOf, member_of)


class Role(RepresentativeRecord, TemporalRecord):
    def __init__(self, graph, unique_id, representative, start_date, end_date=None, title=None):
        RepresentativeRecord.__init__(self, graph, unique_id, representative)
        TemporalRecord.__init__(self, graph, unique_id, start_date, end_date, title)


class VoteOption(LinkedClass):
    def __init__(self, graph, vote):
        """
        :type vote: Tribool
        """
        if vote.value is True:
            LinkedClass.__init__(self, graph, "Yes")
        elif vote.value is False:
            LinkedClass.__init__(self, graph, "No")
        else:
            LinkedClass.__init__(self, graph, "Abstain")

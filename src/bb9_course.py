import os
import zipfile

from lxml import etree

import elixer

class Blackboard9Course(object):
    def __init__(self, archive_filename):
        self.archive_filename = archive_filename

        try:
            self.zip = zipfile.ZipFile(self.archive_filename)
        except zipfile.error:
            raise zipfile.error(self.archive_filename)

        self.manifest = self.parse_manifest()

        self.forums = []

        self.convert_resources()

        self.sections = self.create_sections()

    def parse_manifest(self):
        # TODO: Improve this? I'm removing namespaces because I don't want to
        #       deal with them

        manifest_str = self.zip.read('imsmanifest.xml')

        namespace = 'xmlns:bb="http://www.blackboard.com/content-packaging/"'

        manifest_str = manifest_str.replace(namespace, '')
        manifest_str = manifest_str.replace('bb:', '').replace('xml:', '')

        return etree.fromstring(manifest_str)

    def convert_resources(self):
        for resource in self.manifest.iterfind('.//resource'):
            dat_name = resource.attrib['file']
            xml = etree.parse(self.zip.open(dat_name))

            type = resource.attrib['type']

            if type == 'course/x-bb-coursesetting':
                self.convert_course_settings(xml)
            elif type == 'resource/x-bb-discussionboard':
                self.forums.append(BlackBoard9DiscussionBoard(xml))
            else:
                pass

    def convert_course_settings(self, xml):
        self.fullname = xml.find('.//TITLE').attrib['value']
        self.shortname = self.fullname.replace(' ', '')

        category_elems = xml.findall('.//CLASSIFICATION')

        self.primary_category = category_elems[0].attrib['value']
        self.secondary_category = category_elems[1].attrib['value']

    def create_sections(self):
        # TODO
        section = {}

        section['number'] = 0
        section['summary'] = ''
        section['visible'] = 1
        section['id'] = abs(hash((section['number'], section['summary'])))

        return [section]


class BlackBoard9Resource(object):
    def __init__(self, xml):
        if self.__class__ == 'BlackBoard9Resource':
            raise NotImplementedError('Do not instantiate base class')

        self.xml = xml

        self._load()

        self.section_num = 0 # TODO: Temporary
        self.id = elixer.m_hash(self)
        self.section_id = elixer.m_hash(self)


class BlackBoard9DiscussionBoard(BlackBoard9Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.introduction = self.xml.find('.//TEXT').text


if __name__ == '__main__':
    course = Blackboard9Course('in.zip')

    elixer.create_moodle_zip(course, 'out.zip')

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

        self.questions = {}
        self.questions['essay'] = []
        self.questions['truefalse'] = []
        self.questions['shortanswer'] = []
        self.questions['multichoice'] = []
        self.questions['matching'] = []

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
            elif type == 'assessment/x-bb-qti-pool':
                self.convert_questions(xml)
            elif type == 'assessment/x-bb-qti-test':
                self.convert_questions(xml)
                # self.tests.append(BlackBoard9Test(xml))
            elif type == 'assessment/x-bb-qti-test':
                # TODO
                pass
            else:
                pass

    def convert_course_settings(self, xml):
        self.fullname = xml.find('.//TITLE').attrib['value']
        self.shortname = self.fullname.replace(' ', '')

        category_elems = xml.findall('.//CLASSIFICATION')

        self.primary_category = category_elems[0].attrib['value']
        self.secondary_category = category_elems[1].attrib['value']

    def convert_questions(self, xml):
        questions = xml.findall('.//item')

        for question in questions:
            question_type = question.find('.//bbmd_questiontype').text

            if question_type == 'Essay':
                self.questions['essay'].append(BlackBoard9EssayQuestion(xml))
            elif question_type == 'Short Response':
                self.questions['essay'].append(BlackBoard9ShortResponseQuestion(xml))
            elif question_type == 'Either/Or':
                self.questions['truefalse'].append(BlackBoard9EitherOrQuestion(xml))
            elif question_type == 'True/False':
                self.questions['truefalse'].append(BlackBoard9TrueFalseQuestion(xml))
            elif question_type == 'Multiple Choice':
                self.questions['multichoice'].append(BlackBoard9MultipleAnswerQuestion(xml))
            elif question_type == 'Multiple Answer':
                self.questions['multichoice'].append(BlackBoard9MultipleChoiceQuestion(xml))
            elif question_type == 'Opinion Scale':
                self.questions['multichoice'].append(BlackBoard9OpinionScaleQuestion(xml))
            elif question_type == 'Matching':
                self.questions['matching'].append(BlackBoard9MatchingQuestion(xml))
            elif question_type == 'Ordering':
                self.questions['matching'].append(BlackBoard9Ordering(xml))
            elif question_type == 'Fill in the Blank':
                self.questions['shortanswer'].append(BlackBoard9FillInTheBlankQuestion(xml))

    def create_sections(self):
        # TODO
        section = {}

        section['number'] = 0
        section['summary'] = ''
        section['visible'] = 1
        section['id'] = abs(hash((section['number'], section['summary'])))

        return [section]

class BlackBoard9ContentItem(object):
    def __init__(self, xml):
        if self.__class__ == 'BlackBoard9ContentItem':
            raise NotImplementedError('Do not instantiate base class')

        self.xml = xml

        self._load()

class BlackBoard9Resource(BlackBoard9ContentItem):
    def __init__(self, xml):
        if self.__class__ == 'BlackBoard9Resource':
            raise NotImplementedError('Do not instantiate base class')

        BlackBoard9ContentItem.__init__(self, xml)

        self.section_num = 0 # TODO: Temporary
        self.id = elixer.m_hash(self)
        self.section_id = elixer.m_hash(self)


class BlackBoard9DiscussionBoard(BlackBoard9Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.introduction = self.xml.find('.//TEXT').text


class BlackBoard9Question(BlackBoard9ContentItem):
    def __init__(self, xml):
        if self.__class__ == 'BlackBoard9Question':
            raise NotImplementedError('Do not instantiate base class')

        BlackBoard9ContentItem.__init__(self, xml)

class BlackBoard9EssayQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9ShortResponseQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9EitherOrQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9TrueFalseQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9MultipleAnswerQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9MultipleChoiceQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9OpinionScaleQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9MatchingQuestion(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9Ordering(BlackBoard9Question):
    def _load(self):
        pass

class BlackBoard9FillInTheBlankQuestion(BlackBoard9Question):
    def _load(self):
        pass


if __name__ == '__main__':
    course = Blackboard9Course('in.zip')

    elixer.create_moodle_zip(course, 'out.zip')

import os
import time
import zipfile

from lxml import etree

import elixer

class Course(object):
    def __init__(self, archive_filename):
        self.archive_filename = archive_filename

        self.timestamp = str(time.time()).split('.')[0]

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
                self.forums.append(DiscussionBoard(xml))
            elif type == 'assessment/x-bb-qti-pool':
                self.convert_questions(xml)
            elif type == 'assessment/x-bb-qti-test':
                self.convert_questions(xml)
                # self.tests.append(Test(xml))
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
                self.questions['essay'].append(EssayQuestion(xml))
            '''
            elif question_type == 'Short Response':
                self.questions['essay'].append(ShortResponseQuestion(xml))
            elif question_type == 'Either/Or':
                self.questions['truefalse'].append(EitherOrQuestion(xml))
            elif question_type == 'True/False':
                self.questions['truefalse'].append(TrueFalseQuestion(xml))
            elif question_type == 'Multiple Choice':
                self.questions['multichoice'].append(MultipleAnswerQuestion(xml))
            elif question_type == 'Multiple Answer':
                self.questions['multichoice'].append(MultipleChoiceQuestion(xml))
            elif question_type == 'Opinion Scale':
                self.questions['multichoice'].append(OpinionScaleQuestion(xml))
            elif question_type == 'Matching':
                self.questions['matching'].append(MatchingQuestion(xml))
            elif question_type == 'Ordering':
                self.questions['matching'].append(Ordering(xml))
            elif question_type == 'Fill in the Blank':
                self.questions['shortanswer'].append(FillInTheBlankQuestion(xml))
            '''

        self.quiz_category_id = elixer.m_hash(*tuple(self.questions)) # TODO
        self.quiz_category_stamp = elixer.generate_stamp()


    def create_sections(self):
        # TODO
        section = {}

        section['number'] = 0
        section['summary'] = ''
        section['visible'] = 1
        section['id'] = abs(hash((section['number'], section['summary'])))

        return [section]

class ContentItem(object):
    def __init__(self, xml):
        if self.__class__ == 'ContentItem':
            raise NotImplementedError('Do not instantiate base class')

        self.xml = xml

        self._load()

class Resource(ContentItem):
    def __init__(self, xml):
        if self.__class__ == 'Resource':
            raise NotImplementedError('Do not instantiate base class')

        ContentItem.__init__(self, xml)

        self.section_num = 0 # TODO: Temporary
        self.id = elixer.m_hash(self)
        self.section_id = elixer.m_hash(self)


class DiscussionBoard(Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.introduction = self.xml.find('.//TEXT').text


class Question(ContentItem):
    def __init__(self, xml):
        if self.__class__ == 'Question':
            raise NotImplementedError('Do not instantiate base class')

        ContentItem.__init__(self, xml)

        self.stamp = elixer.generate_stamp()
        self.id = elixer.m_hash(self)

class EssayQuestion(Question):
    def _load(self):
        e = self.xml.find('.//presentation').find('.//mat_formattedtext')

        self.name = self.text = e.text
        self.answer_id = elixer.m_hash(self)

class ShortResponseQuestion(Question):
    def _load(self):
        pass

class EitherOrQuestion(Question):
    def _load(self):
        pass

class TrueFalseQuestion(Question):
    def _load(self):
        pass

class MultipleAnswerQuestion(Question):
    def _load(self):
        pass

class MultipleChoiceQuestion(Question):
    def _load(self):
        pass

class OpinionScaleQuestion(Question):
    def _load(self):
        pass

class MatchingQuestion(Question):
    def _load(self):
        pass

class Ordering(Question):
    def _load(self):
        pass

class FillInTheBlankQuestion(Question):
    def _load(self):
        pass


if __name__ == '__main__':
    course = Course('in.zip')

    elixer.create_moodle_zip(course, 'out.zip')

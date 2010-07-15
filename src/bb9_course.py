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
                self.questions['essay'].append(EssayQuestion(question))
            elif question_type == 'Short Response':
                self.questions['essay'].append(ShortResponseQuestion(question))
            elif question_type == 'True/False':
                self.questions['truefalse'].append(TrueFalseQuestion(question))
            elif question_type == 'Either/Or':
                self.questions['multichoice'].append(EitherOrQuestion(question))
            '''
            elif question_type == 'Multiple Choice':
                self.questions['multichoice'].append(MultipleAnswerQuestion(question))
            elif question_type == 'Multiple Answer':
                self.questions['multichoice'].append(MultipleChoiceQuestion(question))
            elif question_type == 'Opinion Scale':
                self.questions['multichoice'].append(OpinionScaleQuestion(question))
            elif question_type == 'Matching':
                self.questions['matching'].append(MatchingQuestion(question))
            elif question_type == 'Ordering':
                self.questions['matching'].append(Ordering(question))
            elif question_type == 'Fill in the Blank':
                self.questions['shortanswer'].append(FillInTheBlankQuestion(question))
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
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.answer_id = elixer.m_hash(self)

class ShortResponseQuestion(EssayQuestion):
    pass

class TrueFalseQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        self.true_feedback = self.xml.find(query).text
        self.false_feedback = self.xml.find(query.replace('"c', '"inc')).text

        a = self.xml.find('.//respcondition[@title="correct"]//varequal').text

        self.true_points, self.false_points = (1, 0) if a == 'true' else (0, 1)

        self.true_answer_id = elixer.m_hash(self)
        self.false_answer_id = elixer.m_hash(self)

class EitherOrQuestion(Question):
    ans_types = {
        'yes_no': ('Yes', 'No'),
        'agree_disagree': ('Agree', 'Disagree'),
        'right_wrong': ('Right', 'Wrong'),
        'true_false': ('True', 'False')
    }

    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name
        self.single_answer = 1

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        cor_fb = self.xml.find(query).text
        incor_fb = self.xml.find(query.replace('"c', '"inc')).text

        a = self.xml.find('.//respcondition[@title="correct"]//varequal').text

        ans_type = a.split('.')[0]

        true_points, false_points = (1, 0) if a.endswith('true') else (0, 1)

        right_ans = {}
        right_ans['answer_text'] = self.ans_types[ans_type][0]
        right_ans['points'] = true_points
        right_ans['feedback'] = cor_fb if true_points == 1 else incor_fb
        right_ans['id'] = elixer.m_hash(right_ans) # Fix m_hash

        wrong_ans = {}
        wrong_ans['answer_text'] = self.ans_types[ans_type][1]
        wrong_ans['points'] = false_points
        wrong_ans['feedback'] = cor_fb if false_points == 1 else incor_fb
        wrong_ans['id'] = elixer.m_hash(wrong_ans) # Fix_mhash

        self.answers = (right_ans, wrong_ans)

        self.answer_string = ','.join([str(a['id']) for a in self.answers])

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

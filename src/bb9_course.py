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
        self.resources = []

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
            elif type == 'resource/x-bb-announcement':
                self.resources.append(Announcement(xml))
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
            elif question_type == 'Multiple Choice':
                self.questions['multichoice'].append(MultipleChoiceQuestion(question))
            elif question_type == 'Multiple Answer':
                self.questions['multichoice'].append(MultipleAnswerQuestion(question))
            elif question_type == 'Opinion Scale':
                self.questions['multichoice'].append(OpinionScaleQuestion(question))
            elif question_type == 'Matching':
                self.questions['matching'].append(MatchingQuestion(question))
            elif question_type == 'Ordering':
                self.questions['matching'].append(OrderingQuestion(question))
            elif question_type == 'Fill in the Blank':
                self.questions['shortanswer'].append(FillInTheBlankQuestion(question))

        self.quiz_category_id = elixer.m_hash(*tuple(self.questions)) # TODO
        self.quiz_category_stamp = elixer.generate_stamp()

    def create_sections(self):
        sections = [
            {'number': 0, 'summary': '<h2>Announcements</h2>'},
            {'number': 1, 'summary': '<h2>Forums</h2>'},
        ]

        for section in sections:
            section['visible'] = 1
            section['id'] = abs(hash((section['number'], section['summary'])))

        return sections


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

        self.id = elixer.m_hash(self)
        self.section_id = elixer.m_hash(self)


class DiscussionBoard(Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.introduction = self.xml.find('.//TEXT').text

        self.section_num = 1

class Announcement(Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.alltext = self.xml.find('.//TEXT').text
        self.type = 'html'
        self.reference = '2'

        self.section_num = 0

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

        self.true_answer_id = elixer.m_hash(self, self.true_points)
        self.false_answer_id = elixer.m_hash(self, self.false_points)


class MultipleChoiceQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        self.cor_fb = self.xml.find(query).text
        self.incor_fb = self.xml.find(query.replace('"c', '"inc')).text

        self.answers = []

        self.build_answers()

        self.answer_string = ','.join([str(a['id']) for a in self.answers])

    def build_answers(self):
        self.single_answer = 1

        answer_query = './/render_choice//response_label'

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer['ident'] = answer_elem.attrib['ident']
            answer['answer_text'] = answer_elem.find('.//mat_formattedtext').text

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//varequal'
        correct_ident = self.xml.find(query).text

        for answer in self.answers:
            if answer['ident'] == correct_ident:
                answer['points'] = 1
                answer['feedback'] = self.cor_fb
            else:
                answer['points'] = 0
                answer['feedback'] = self.incor_fb

            answer['id'] = elixer.m_hash(answer)


class EitherOrQuestion(MultipleChoiceQuestion):
    ans_types = {
        'yes_no': ('Yes', 'No'),
        'agree_disagree': ('Agree', 'Disagree'),
        'right_wrong': ('Right', 'Wrong'),
        'true_false': ('True', 'False')
    }

    def build_answers(self):
        self.single_answer = 1

        a = self.xml.find('.//respcondition[@title="correct"]//varequal').text

        ans_type = a.split('.')[0]

        true_points, false_points = (1, 0) if a.endswith('true') else (0, 1)

        right_ans = {}
        right_ans['answer_text'] = self.ans_types[ans_type][0]
        right_ans['points'] = true_points

        if true_points == 1:
            right_ans['feedback'] = self.cor_fb
        else:
            right_ans['feedback'] = self.incor_fb

        right_ans['id'] = elixer.m_hash(right_ans) # Fix m_hash

        wrong_ans = {}
        wrong_ans['answer_text'] = self.ans_types[ans_type][1]
        wrong_ans['points'] = false_points

        if false_points == 1:
            wrong_ans['feedback'] = self.cor_fb
        else:
            wrong_ans['feedback'] = self.incor_fb

        wrong_ans['id'] = elixer.m_hash(wrong_ans) # Fix_mhash

        self.answers = (right_ans, wrong_ans)

class MultipleAnswerQuestion(MultipleChoiceQuestion):
    def build_answers(self):
        self.single_answer = 0

        answer_query = './/render_choice//response_label'

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer['ident'] = answer_elem.attrib['ident']
            answer['answer_text'] = answer_elem.find('.//mat_formattedtext').text

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//and/varequal'
        correct_idents = [a.text for a in self.xml.findall(query)]

        for answer in self.answers:
            if answer['ident'] in correct_idents:
                answer['points'] = 1
                answer['feedback'] = self.cor_fb
            else:
                answer['points'] = 0
                answer['feedback'] = self.incor_fb

            answer['id'] = elixer.m_hash(answer)


class OpinionScaleQuestion(MultipleChoiceQuestion):
    pass


class MatchingQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        cor_fb = self.xml.find(query).text
        incor_fb = self.xml.find(query.replace('"c', '"inc')).text

        self.answers = []

        ident_query = './/flow[@class="RESPONSE_BLOCK"]//response_lid'
        text_query = './/flow[@class="RESPONSE_BLOCK"]//mat_formattedtext'

        idents = self.xml.findall(ident_query)
        texts = self.xml.findall(text_query)

        for n, i in enumerate(self.xml.findall(ident_query)):
            answer = {}
            answer['ident'] = idents[n].attrib['ident']
            answer['question_text'] = texts[n].text

            labels = idents[n].findall('.//response_label')

            answer['choice_idents'] = tuple([l.attrib['ident'] for l in labels])

            self.answers.append(answer)

        answer_query = './/flow[@class="RIGHT_MATCH_BLOCK"]//mat_formattedtext'

        answer_texts = [a.text for a in self.xml.findall(answer_query)]

        for match in self.xml.findall('.//varequal'):
            question_ident = match.attrib['respident']
            answer_ident = match.text

            for answer in self.answers:
                if answer['ident'] == question_ident:
                    i = answer['choice_idents'].index(answer_ident)

                    answer['answer_text'] = answer_texts[i]

                    break

        for answer in self.answers:
            answer['id'] = elixer.m_hash(answer)


class OrderingQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        cor_fb = self.xml.find(query).text
        incor_fb = self.xml.find(query.replace('"c', '"inc')).text

        self.answers = []

        answer_query = './/render_choice//response_label'

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer['ident'] = answer_elem.attrib['ident']
            answer['question_text'] = answer_elem.find('.//mat_formattedtext').text

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//varequal'
        ordered_ident_elems = self.xml.findall(query)

        for n, ordered_ident_elem in enumerate(ordered_ident_elems):
            for answer in self.answers:
                if answer['ident'] == ordered_ident_elem.text:
                    answer['answer_text'] = n + 1

                    break

        for answer in self.answers:
            answer['id'] = elixer.m_hash(answer)


class FillInTheBlankQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        cor_fb = self.xml.find(query).text
        incor_fb = self.xml.find(query.replace('"c', '"inc')).text

        self.answers = []

        for answer_text in [e.text for e in self.xml.findall('.//varequal')]:
            answer = {}
            answer['answer_text'] = answer_text
            answer['points'] = 1
            answer['id'] = elixer.m_hash(answer)

            self.answers.append(answer)


if __name__ == '__main__':
    course = Course('in.zip')

    elixer.create_moodle_zip(course, 'out.zip')

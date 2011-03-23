# Copyright 2011 Adam Zapletal
#
# This file is part of Reteach
# Reteach is free software licensed under the GPLv3. See LICENSE for details.

import os
import re
import time
import base64
import shutil
import urllib2
import zipfile
import subprocess

from lxml import etree

import utils

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
        self.labels = []
        self.quizzes = []
        self.resources = []

        self.questions = {}
        self.questions['essay'] = []
        self.questions['matching'] = []
        self.questions['truefalse'] = []
        self.questions['shortanswer'] = []
        self.questions['multichoice'] = []

        self.convert_resources()

        self.sections = self.create_default_sections()
        self.sections += self.create_content_areas()

        self.quiz_category_stamp = utils.generate_stamp()
        self.quiz_category_id = utils.m_hash(self.quiz_category_stamp)

        self.has_questions = any(self.questions.values())

        self.zip.close()

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

            # TODO: Replace with a check in self.zip.namelist?
            try:
                xml = etree.parse(self.zip.open(dat_name))
            except KeyError:
                continue

            res_num = dat_name.replace('res', '').replace('.dat', '')

            res_type = resource.attrib['type']

            if res_type == 'course/x-bb-coursesetting':
                self.convert_course_settings(xml)
            elif res_type == 'resource/x-bb-discussionboard':
                self.forums.append(DiscussionBoard(xml, res_num))
            elif res_type == 'resource/x-bb-announcement':
                self.resources.append(Announcement(xml, res_num))
            elif res_type == 'resource/x-bb-staffinfo':
                self.resources.append(StaffInfo(xml, res_num))
            elif res_type == 'assessment/x-bb-qti-test':
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes.append(Test(xml, quiz_questions, res_num))
            elif res_type == 'assessment/x-bb-qti-survey':
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes.append(Survey(xml, quiz_questions, res_num))
            elif res_type == 'assessment/x-bb-qti-pool':
                quiz_questions = self.convert_questions(xml, res_num)
                self.quizzes.append(Pool(xml, quiz_questions, res_num))
            elif res_type == 'resource/x-bb-document':
                document = Document(xml, res_num)

                if not document.ignore:
                    self.resources.append(document)

                if document.make_label:
                    self.labels.append(Label(document.name, res_num))

    def convert_course_settings(self, xml):
        self.fullname = xml.find('.//TITLE').attrib['value']
        self.shortname = xml.find('.//COURSEID').attrib['value']

        category_elems = xml.findall('.//CLASSIFICATION')

        self.primary_category = category_elems[0].attrib['value']

        # TODO: Could be better
        try:
            self.secondary_category = category_elems[1].attrib['value']
        except IndexError:
            self.secondary_category = ''

    def convert_questions(self, xml, res_num):
        questions = xml.findall('.//item')

        old_question_ids = [q.id for q in sum(self.questions.values(), [])]

        # TODO: PEP8

        for question in questions:
            question_type = question.find('.//bbmd_questiontype').text

            if question_type == 'Essay':
                self.questions['essay'].append(EssayQuestion(question, res_num))
            elif question_type == 'Short Response':
                self.questions['essay'].append(ShortResponseQuestion(question, res_num))
            elif question_type == 'True/False':
                self.questions['truefalse'].append(TrueFalseQuestion(question, res_num))
            elif question_type == 'Either/Or':
                self.questions['multichoice'].append(EitherOrQuestion(question, res_num))
            elif question_type == 'Multiple Choice':
                self.questions['multichoice'].append(MultipleChoiceQuestion(question, res_num))
            elif question_type == 'Multiple Answer':
                self.questions['multichoice'].append(MultipleAnswerQuestion(question, res_num))
            elif question_type == 'Opinion Scale':
                self.questions['multichoice'].append(OpinionScaleQuestion(question, res_num))
            elif question_type == 'Matching':
                self.questions['matching'].append(MatchingQuestion(question, res_num))
            elif question_type == 'Ordering':
                self.questions['matching'].append(OrderingQuestion(question, res_num))
            elif question_type == 'Fill in the Blank':
                self.questions['shortanswer'].append(FillInTheBlankQuestion(question, res_num))

        all_questions = sum(self.questions.values(), [])

        all_question_ids = [q.id for q in all_questions]

        new_question_ids = [q for q in all_question_ids if q not in old_question_ids]

        quiz_questions = [q for q in all_questions if q.id in new_question_ids]

        return quiz_questions

    def create_default_sections(self):
        sections = [
            {'number': 0, 'summary': ''},
            {'number': 1, 'summary': '<h2>Announcements</h2>'},
            {'number': 2, 'summary': '<h2>Forums</h2>'},
            {'number': 3, 'summary': '<h2>Quizzes</h2>'},
            {'number': 4, 'summary': '<h2>Contacts</h2>'},
        ]

        # TODO: Questionable
        sections[1]['mods'] = [r for r in self.resources if isinstance(r, Announcement)]
        sections[2]['mods'] = self.forums
        sections[3]['mods'] = self.quizzes
        sections[4]['mods'] = [r for r in self.resources if isinstance(r, StaffInfo)]

        for section in sections:
            section['visible'] = 1
            section['id'] = abs(hash((section['number'], section['summary'])))

        return sections

    def create_content_areas(self):
        sections = []

        res_nums_to_assets = {}

        for asset in self.resources + self.labels:
            res_nums_to_assets[asset.res_num] = asset

        for content_area in self.manifest.find('.//organization').iterchildren():
            if len(content_area.getchildren()) < 2:
                continue

            section_num = len(self.sections) + len(sections)

            # Avoiding staffinfo
            try:
                dat_name = content_area.attrib['identifierref'] + '.dat'
            except KeyError:
                continue

            res_xml = etree.parse(self.zip.open(dat_name))

            if not res_xml.find('.//TARGETTYPE').attrib['value'] == 'CONTENT':
                continue

            title = content_area.getchildren()[0].text

            section = {}
            section['number'] = section_num
            section['summary'] = '<h2>' + title + '</h2>'
            section['visible'] = 1
            section['id'] = abs(hash((section['number'], section['summary'])))
            section['mods'] = []

            sections.append(section)

            def recurse(elem, indent):
                children = elem.getchildren()

                for child in children:
                    if not child.tag == 'item':
                        continue

                    res_num = child.attrib['identifierref'].replace('res', '')

                    # TODO: Hackish
                    try:
                        res_nums_to_assets[res_num].indent = indent
                        res_nums_to_assets[res_num].section_num = section_num
                    except KeyError:
                        continue

                    section['mods'].append(res_nums_to_assets[res_num])

                    inner_children = child.getchildren()

                    if len(inner_children) > 1:
                        recurse(child, indent + 1)

            recurse(content_area.getchildren()[1], 0)

        return sections


class ContentItem(object):
    def __init__(self, xml):
        if self.__class__ == 'ContentItem':
            raise NotImplementedError('Do not instantiate base class')

        self.xml = xml

        self._load()


class Resource(ContentItem):
    def __init__(self, xml, res_num):
        if self.__class__ == 'Resource':
            raise NotImplementedError('Do not instantiate base class')

        self.res_num = res_num
        self.indent = 0

        ContentItem.__init__(self, xml)

        self.id = utils.m_hash(self)
        self.section_id = utils.m_hash(self)


class DiscussionBoard(Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.introduction = self.xml.find('.//TEXT').text

        self.type = 'forum'


class Announcement(Resource):
    def _load(self):
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.alltext = self.xml.find('.//TEXT').text
        self.res_type = 'html'
        self.reference = '2' # TODO

        self.type = 'resource'


class StaffInfo(Resource):
    def _load(self):
        parts = ('FORMALTITLE', 'GIVEN', 'FAMILY')
        data_parts = [self.xml.find('.//%s' % p).attrib['value'] for p in parts]

        self.name = ' '.join([p for p in data_parts if p])

        email = self.xml.find('.//EMAIL').attrib['value']
        phone = self.xml.find('.//PHONE').attrib['value']
        hours = self.xml.find('.//HOURS').attrib['value']
        address = self.xml.find('.//ADDRESS').attrib['value']
        homepage = self.xml.find('.//HOMEPAGE').attrib['value']
        image = self.xml.find('.//IMAGE').attrib['value']
        notes = self.xml.find('.//TEXT').text or ''

        if image:
            image = utils.fix_filename(image, self.res_num)

        self.res_type = 'html'

        self.alltext =  '''
            <table border = "0" width = "50%%">
              <tr>
                <td colspan = "2"><h3>%s</h3></td>
              </tr>

              <tr>
                <td>
                  <ul>
                    <li><b>Email</b>: %s</li>
                    <li><b>Work Phone</b>: %s</li>
                    <li><b>Office Location</b>: %s</li>
                    <li><b>Office Hours</b>: %s</li>
                    <li><b>Personal Link</b>: %s</li>
                  </ul>
                </td>
        ''' % (self.name, email, phone, hours, address, homepage)

        if image:
            self.alltext += '''
                <td>
                  <img src = "$@FILEPHP@$/%s" alt="" width="150" height="150"/>
                </td>
            ''' % image

        self.alltext += '''
              </tr>
              <tr>
                <td colspan = "2">%s</td>
              </tr>
            </table>
        ''' % notes

        formal_title = self.xml.find('.//FORMALTITLE')

        self.type = 'resource'


class Document(Resource):
    def _load(self):
        self.content_id = self.xml.getroot().attrib['id']
        self.name = self.xml.find('.//TITLE').attrib['value']
        self.alltext = self.xml.find('.//TEXT').text
        self.ignore = False
        self.make_label = False

        if not self.alltext:
            self.alltext = ''

        while '@X@EmbeddedFile.location@X@' in self.alltext:
            self.alltext = self.handle_embedded_file(self.alltext)

        content_handler = self.xml.find('.//CONTENTHANDLER').attrib['value']

        ignored_handlers = (
            'resource/x-bb-module-page',
            'resource/x-bb-courselink'
        )

        folder_handlers = ('resource/x-bb-folder', 'resource/x-bb-lesson')

        if content_handler == 'resource/x-bb-externallink':
            self.res_type = 'file'
            self.reference = self.xml.find('.//URL').attrib['value']
        elif content_handler in ignored_handlers:
            self.ignore = True
        elif content_handler in folder_handlers:
            self.ignore = True
            self.make_label = True

            if self.xml.find('.//PARENTID').attrib['value'] == '{unset id}':
                self.make_label = False
        else:
            self.res_type = 'html'

        for file_elem in self.xml.findall('.//FILE'):
            self.handle_file(file_elem)

        self.type = 'resource'

    def handle_file(self, file_elem):
        orig_name = file_elem.find('.//NAME').text

        fixed_name = utils.fix_filename(orig_name, self.res_num)

        fname = urllib2.quote(fixed_name.encode('utf-8'))

        link_name = file_elem.find('.//LINKNAME').attrib['value']

        f_link = '<a href = "$@FILEPHP@$/%s" title = %s>' % ((fname,) * 2)
        f_link = 'Attached File: ' + f_link + '%s</a>' % link_name

        self.alltext = '<br /><br />'.join([self.alltext, f_link])

    def handle_embedded_file(self, text):
        before, rest = text.split('@X@EmbeddedFile.location@X@', 1)

        filename, after = rest.split('"', 1)

        after = '"' + after

        filename = utils.fix_filename(filename, self.res_num)

        return before + '$@FILEPHP@$/' + filename + after


class Label(Resource):
    def __init__(self, name, res_num):
        self.name = self.content = name
        self.res_num = res_num

        self.id = utils.m_hash(self)
        self.section_id = utils.m_hash(self)

        self.type = 'label'


class Test(Resource):
    def __init__(self, xml, quiz_questions, res_num):
        Resource.__init__(self, xml, res_num)

        self.questions = quiz_questions
        self.question_string = ','.join([str(q.id) for q in self.questions])
        self.feedback_id = utils.m_hash(self)


    def _load(self):
        self.name = self.xml.find('.//assessment').attrib['title']

        self.stamp = utils.generate_stamp()

        self.category_id = utils.m_hash(self.name, self.stamp)

        query = './/presentation_material//mat_formattedtext'
        description = self.xml.find(query).text

        query = './/rubric[@view="All"]//mat_formattedtext'
        instructions = self.xml.find(query).text

        description = '' if not description else description
        instructions = '' if not instructions else instructions

        self.intro = description + '<br /><br />' + instructions

        self.intro = '' if self.intro == '<br /><br />' else self.intro

        self.type = 'quiz'


class Survey(Test):
    pass


class Pool(Test):
    pass


class Question(ContentItem):
    def __init__(self, xml, res_num):
        if self.__class__ == 'Question':
            raise NotImplementedError('Do not instantiate base class')

        ContentItem.__init__(self, xml)

        if not self.name:
            self.name = '________'

        self.name = re.sub(r'<.*?>', '', self.name).strip()
        self.res_num = res_num

        query = './/flow[@class="FILE_BLOCK"]//matapplication'

        for elem in self.xml.findall(query):
            self.image = utils.fix_filename(elem.attrib['label'], res_num)

        self.stamp = utils.generate_stamp()
        self.id = utils.m_hash(self)


class EssayQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name
        self.answer_id = utils.m_hash(self)


class ShortResponseQuestion(EssayQuestion):
    pass


class TrueFalseQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        true_fb_el = self.xml.find(query)
        false_fb_el = self.xml.find(query.replace('"c', '"inc'))

        self.true_feedback = true_fb_el.text if true_fb_el is not None else ''
        self.false_feedback = false_fb_el.text if false_fb_el is not None else ''

        answer_query = './/respcondition[@title="correct"]//varequal'

        answer_elem = self.xml.find(answer_query)

        if answer_elem is not None:
            a = answer_elem.text

            self.true_points, self.false_points = (1, 0) if a == 'true' else (0, 1)

            self.true_answer_id = utils.m_hash(self, self.true_points)
            self.false_answer_id = utils.m_hash(self, self.false_points)
        else:
            # Survey
            # TODO: Make this multichoice
            self.true_points, self.false_points = (1, 0)

            self.true_answer_id = utils.m_hash(self, self.true_points)
            self.false_answer_id = utils.m_hash(self, self.false_points)


class MultipleChoiceQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        query = './/itemfeedback[@ident="correct"]//mat_formattedtext'

        try:
            self.cor_fb = self.xml.find(query).text
            self.incor_fb = self.xml.find(query.replace('"c', '"inc')).text
        except AttributeError:
            # Survey
            self.cor_fb = ''
            self.incor_fb = ''

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

            # Filter out blank choices
            if not answer['answer_text']:
                continue

            self.answers.append(answer)

        query = './/respcondition[@title="correct"]//varequal'

        correct_elem = self.xml.find(query)

        if correct_elem is not None:
            correct_ident = correct_elem.text

            for answer in self.answers:
                if answer['ident'] == correct_ident:
                    answer['points'] = 1
                    answer['feedback'] = self.cor_fb
                else:
                    answer['points'] = 0
                    answer['feedback'] = self.incor_fb

                answer['id'] = utils.m_hash(answer)
        else:
            for answer in self.answers:
                answer['points'] = 1
                answer['feedback'] = self.cor_fb
                answer['id'] = utils.m_hash(answer)


class EitherOrQuestion(MultipleChoiceQuestion):
    ans_types = {
        'yes_no': ('Yes', 'No'),
        'agree_disagree': ('Agree', 'Disagree'),
        'right_wrong': ('Right', 'Wrong'),
        'true_false': ('True', 'False')
    }

    def build_answers(self):
        self.single_answer = 1

        answer_query = './/respcondition[@title="correct"]//varequal'
        answer_elem = self.xml.find(answer_query)

        if answer_elem is not None:
            answer = answer_elem.text

            ans_type = answer.split('.')[0]

            true_points, false_points = (1, 0) if answer.endswith('true') else (0, 1)

            right_ans = {}
            right_ans['answer_text'] = self.ans_types[ans_type][0]
            right_ans['points'] = true_points

            if true_points == 1:
                right_ans['feedback'] = self.cor_fb
            else:
                right_ans['feedback'] = self.incor_fb

            right_ans['id'] = utils.m_hash(right_ans) # Fix m_hash

            wrong_ans = {}
            wrong_ans['answer_text'] = self.ans_types[ans_type][1]
            wrong_ans['points'] = false_points

            if false_points == 1:
                wrong_ans['feedback'] = self.cor_fb
            else:
                wrong_ans['feedback'] = self.incor_fb

            wrong_ans['id'] = utils.m_hash(wrong_ans) # Fix_mhash
        else:
            # TODO: Improve
            # Survey
            right_ans = {}
            right_ans['answer_text'] = 'Agree'
            right_ans['points'] = 1
            right_ans['feedback'] = ''
            right_ans['id'] = utils.m_hash(right_ans) # Fix m_hash

            wrong_ans = {}
            wrong_ans['answer_text'] = 'Disagree'
            wrong_ans['points'] = 0
            wrong_ans['feedback'] = ''
            wrong_ans['id'] = utils.m_hash(wrong_ans) # Fix_mhash

        self.answers = (right_ans, wrong_ans)

class MultipleAnswerQuestion(MultipleChoiceQuestion):
    def build_answers(self):
        self.single_answer = 0

        answer_query = './/render_choice//response_label'

        for answer_elem in self.xml.findall(answer_query):
            answer = {}
            answer['ident'] = answer_elem.attrib['ident']
            answer['answer_text'] = answer_elem.find('.//mat_formattedtext').text

            # Filter out blank choices
            if not answer['answer_text']:
                continue

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

            answer['id'] = utils.m_hash(answer)


class OpinionScaleQuestion(MultipleChoiceQuestion):
    pass


class MatchingQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

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
            answer['id'] = utils.m_hash(answer)


class OrderingQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

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
            answer['id'] = utils.m_hash(answer)


class FillInTheBlankQuestion(Question):
    def _load(self):
        self.name = self.xml.find('.//presentation//mat_formattedtext').text
        self.text = self.name

        self.answers = []

        for answer_text in [e.text for e in self.xml.findall('.//varequal')]:
            answer = {}
            answer['answer_text'] = answer_text
            answer['points'] = 1
            answer['id'] = utils.m_hash(answer)

            self.answers.append(answer)


def create_moodle_zip(blackboard_zip_fname, out_name):
    try:
        shutil.rmtree('elixer_tmp')
        shutil.rmtree('course_files')
    except OSError:
        pass

    course = Course(blackboard_zip_fname)

    moodle_zip = zipfile.ZipFile(out_name, 'w')

    moodle_xml_str = utils.convert(course).encode('utf-8')

    moodle_zip.writestr('moodle.xml', moodle_xml_str)

    err_fh = open(os.path.devnull, 'w')

    command = ('unzip %s -d elixer_tmp' % blackboard_zip_fname).split(' ')
    subprocess.Popen(command, stdout=err_fh, stderr=err_fh).communicate()

    skip_parent = False

    for root, dirs, files in os.walk('elixer_tmp'):
        if not skip_parent:
            skip_parent = True
            continue

        for bb_fname in files:
            moodle_fname = bb_fname

            if bb_fname.startswith('!'):
                if '.' in bb_fname:
                    ext, fname = [s[::-1] for s in bb_fname[1:][::-1].split('.', 1)]
                    moodle_fname = (base64.b16decode(fname.upper()) + '.' + ext)
                else:
                    ext, fname = '', bb_fname[1:]
                    moodle_fname = (base64.b16decode(fname.upper()))

                moodle_fname = urllib2.unquote(moodle_fname)

            res_num = root.split(os.sep, 1)[1].split(os.sep)[0].replace('res', '')

            fixed_filename = utils.fix_filename(moodle_fname, res_num)

            bb_fname = os.path.join(root, bb_fname)

            moodle_fname = os.path.join('course_files', fixed_filename)

            moodle_zip.write(bb_fname, moodle_fname)

    shutil.rmtree('elixer_tmp')

    moodle_zip.close()

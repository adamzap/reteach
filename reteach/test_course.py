# Copyright 2011 Adam Zapletal
#
# This file is part of Reteach
# Reteach is free software licensed under the GPLv3. See LICENSE for details.

import time
import random

from utils import m_hash, generate_stamp, create_moodle_zip

class TestCourse(object):
    def __init__(self):
        raise NotImplementedError('Do not instantiate base class')

    def add_course_settings(self):
        self.fullname = self.shortname = random.randrange(0, 1000)

    def add_date(self):
        self.timestamp = str(time.time()).split('.')[0]

    def add_sections(self):
        self.sections = []

        for n in xrange(5):
            section = {}

            section['number'] = n
            section['summary'] = '<h2>Test Section #%s</h2>' % (n + 1)
            section['visible'] = 1
            section['id'] = m_hash(section['number'], section['summary'])

            self.sections.append(section)

    def add_forums(self):
        self.forums = []

        for n in xrange(4):
            forum = {}

            forum['name'] = 'Forum #%s' % (n + 1)
            forum['introduction'] = 'Forum #%s introduction' % (n + 1)
            forum['id'] = m_hash(forum['name'], forum['introduction'])
            forum['section_num'] = n
            forum['section_id'] = m_hash(forum['id'], forum['section_num'])

            self.forums.append(forum)

    def add_labels(self):
        self.labels = []

        for n in xrange(4):
            label = {}

            label['name'] = 'Label #%s' % (n + 1)
            label['content'] = '<i>Label #%s</i>' % (n + 1)
            label['id'] = m_hash(label['name'], label['content'])
            label['section_num'] = n
            label['section_id'] = m_hash(label['id'], label['section_num'])

            self.labels.append(label)

    def add_resources(self):
        text_res = {}
        text_res['name'] = 'Text Page Resource'
        text_res['type'] = 'text'
        text_res['reference'] = '2'
        text_res['summary'] = 'Text Page Resource Summary'
        text_res['alltext'] = 'Blah Blah Blah Blah'
        text_res['id'] = m_hash(text_res['name'], text_res['alltext'])
        text_res['section_num'] = 4
        text_res['section_id'] = m_hash(text_res['id'], text_res['section_num'])

        html_res = {}
        html_res['name'] = 'Web Page Resource'
        html_res['type'] = 'html'
        html_res['reference'] = '2'
        html_res['summary'] = 'Web Page Resource Summary'
        html_res['alltext'] = '<h2>Blah Blah Blah Blah</h2>'
        html_res['id'] = m_hash(html_res['name'], html_res['alltext'])
        html_res['section_num'] = 4
        html_res['section_id'] = m_hash(html_res['id'], html_res['section_num'])

        link_res = {}
        link_res['name'] = 'Link Resource'
        link_res['type'] = 'file'
        link_res['reference'] = 'http://cnn.com'
        link_res['summary'] = 'Link Resource Summary'
        link_res['alltext'] = ''
        link_res['id'] = m_hash(link_res['name'], link_res['reference'])
        link_res['section_num'] = 4
        link_res['section_id'] = m_hash(link_res['id'], link_res['section_num'])

        file_res = {}
        file_res['name'] = 'File Resource'
        file_res['type'] = 'file'
        file_res['reference'] = 'moodle.xml'
        file_res['summary'] = 'File Resource Summary'
        file_res['alltext'] = ''
        file_res['id'] = m_hash(file_res['name'], file_res['reference'])
        file_res['section_num'] = 4
        file_res['section_id'] = m_hash(file_res['id'], file_res['section_num'])

        self.resources = [text_res, html_res, link_res, file_res]

    def add_questions_container(self):
        self.questions = {}

        self.quiz_category_id = 22345678
        self.quiz_category_stamp = generate_stamp()

    def add_questions_essay(self):
        essay_questions = []

        for n in xrange(2):
            essay_question = {}

            essay_question['name'] = 'Essay Question #%s' % (n + 1)
            essay_question['text'] = 'Text for essay question #%s' % (n + 1)
            essay_question['stamp'] = generate_stamp()
            essay_question['id'] = m_hash(essay_question)
            essay_question['feedback'] = 'Feedback for Essay Question #%s' % (n + 1)
            essay_question['answer_id'] = m_hash(essay_question)

            essay_questions.append(essay_question)

        self.questions['essay'] = essay_questions

    def add_questions_truefalse(self):
        truefalse_questions = []

        for n in xrange(2):
            tf_question = {}

            tf_question['name'] = 'True/False Question #%s' % (n + 1)
            tf_question['text'] = 'Text for truefalse question #%s' % (n + 1)
            tf_question['stamp'] = generate_stamp()
            tf_question['id'] = m_hash(tf_question)
            tf_question['general_feedback'] = 'Gen feedback for tf #%s' % (n + 1)

            tf_question['true_answer_id'] = m_hash(tf_question)
            tf_question['true_points'] = n
            tf_question['true_feedback'] = '#%s true feedback' % (n + 1)

            tf_question['false_answer_id'] = m_hash(tf_question)
            tf_question['false_points'] = -n + 1
            tf_question['false_feedback'] = '#%s false feedback' % (n + 1)

            truefalse_questions.append(tf_question)

        self.questions['truefalse'] = truefalse_questions

    def add_questions_shortanswer(self):
        shortanswer_questions = []

        for n in xrange(2):
            sa_question = {}

            sa_question['name'] = 'Shortanswer Question #%s' % (n + 1)
            sa_question['text'] = 'Text for shortanswer question #%s' % (n + 1)
            sa_question['stamp'] = generate_stamp()
            sa_question['id'] = m_hash(sa_question)
            sa_question['general_feedback'] = 'Gen feedback for sa #%s' % (n + 1)

            answers = []

            for i in xrange(4):
                answer = {}

                answer['answer_text'] = 'Answer %s text for sa #%s' % (i, n)
                answer['points'] = 1 if i == 1 else 0
                answer['feedback'] = 'Answer %s feedback for sa #%s' % (i, n)
                answer['id'] = m_hash(answer)

                answers.append(answer)

            sa_question['answers'] = answers

            sa_question['answer_string'] = ','.join(str(a['id']) for a in answers)

            shortanswer_questions.append(sa_question)

        self.questions['shortanswer'] = shortanswer_questions

    def add_questions_multichoice(self):
        multichoice_questions = []

        for n in xrange(2):
            mc_question = {}

            mc_question['name'] = 'Multichoice Question #%s' % (n + 1)
            mc_question['text'] = 'Text for multichoice question #%s' % (n + 1)
            mc_question['stamp'] = generate_stamp()
            mc_question['single_answer'] = n
            mc_question['id'] = m_hash(mc_question)
            mc_question['general_feedback'] = 'Gen feedback for mc #%s' % (n + 1)
            mc_question['correct_feedback'] = 'Correct feedback for mc #%s' % (n + 1)
            mc_question['partially_correct_feedback'] = 'Partial feedback for mc #%s' % (n + 1)
            mc_question['incorrect_feecback'] = 'Incorrect feedback for mc #%s' % (n + 1)

            answers = []

            for i in xrange(4):
                answer = {}

                answer['answer_text'] = 'Answer %s text for mc #%s' % (i, n)
                answer['points'] = 1 if i == 1 else 0
                answer['feedback'] = 'Answer %s feedback for mc #%s' % (i, n)
                answer['id'] = m_hash(answer)

                answers.append(answer)

            mc_question['answers'] = answers

            mc_question['answer_string'] = ','.join(str(a['id']) for a in answers)

            multichoice_questions.append(mc_question)

        self.questions['multichoice'] = multichoice_questions

    def add_questions_matching(self):
        matching_questions = []

        for n in xrange(2):
            ma_question = {}

            ma_question['name'] = 'Matching Question #%s' % (n + 1)
            ma_question['text'] = 'Text for matching question #%s' % (n + 1)
            ma_question['stamp'] = generate_stamp()
            ma_question['id'] = m_hash(ma_question)
            ma_question['general_feedback'] = 'Gen feedback for ma #%s' % (n + 1)

            answers = []

            for i in xrange(4):
                answer = {}

                answer['question_text'] = 'Question %s text for mc #%s' % (i, n)
                answer['answer_text'] = 'Question %s text for mc #%s' % (i, n)
                answer['id'] = m_hash(answer)

                answers.append(answer)

            ma_question['answers'] = answers

            matching_questions.append(ma_question)

        self.questions['matching'] = matching_questions


    """
    def add_quizzes(self):
        all_qs = []

        [all_qs.extend(l) for l in self.questions.itervalues()]

        self.quizzes = []

        quiz = {}

        quiz['name'] = 'Question Container'
        quiz['intro'] = ''
        quiz['question_string'] = ','.join([str(s['id']) for s in all_qs])
        quiz['id'] = m_hash(quiz)
        quiz['section_num'] = 4
        quiz['section_id'] = m_hash(quiz)
        quiz['feedback_id'] = m_hash(quiz)
        #quiz['questions'] = all_qs

        self.quizzes.append(quiz)
    """


class FullTestCourse(TestCourse):
    def __init__(self):
        methods = [m for m in dir(self.__class__) if not m.startswith('__')]

        [getattr(self, method)() for method in methods]

class QuizTestCourse(TestCourse):
    def __init__(self):
        add_course_settings()
        add_sections()
        add_questions_container()
        add_quizzes()


if __name__ == '__main__':
    course = FullTestCourse()

    create_moodle_zip(course, 'out.zip')

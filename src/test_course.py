import time

import elixer

from elixer import m_hash

class TestCourse(object):
    def __init__(self):
        raise NotImplementedError('Do not instantiate base class')

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

class FullTestCourse(TestCourse):
    def __init__(self):
        methods = [m for m in dir(self.__class__) if not m.startswith('__')]

        [getattr(self, method)() for method in methods]

course = FullTestCourse()

elixer.create_moodle_zip(course, 'out.zip')

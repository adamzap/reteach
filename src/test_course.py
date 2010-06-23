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

        for n in xrange(4):
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

class FullTestCourse(TestCourse):
    def __init__(self):
        methods = [m for m in dir(self.__class__) if not m.startswith('__')]

        [getattr(self, method)() for method in methods]

course = FullTestCourse()

elixer.create_moodle_zip(course, 'out.zip')

import time

import elixer

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
            section['id'] = abs(hash((section['number'], section['summary'])))

            self.sections.append(section)

class FullTestCourse(TestCourse):
    def __init__(self):
        methods = [m for m in dir(self.__class__) if not m.startswith('__')]

        [getattr(self, method)() for method in methods]

course = FullTestCourse()

elixer.create_moodle_zip(course, 'out.zip')

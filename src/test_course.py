import elixer

class TestCourse(object):
    def __init__(self):
        raise NotImplementedError('Do not instantiate base class')

    def add_sections(self):
        self.sections = []

        for n in xrange(4):
            section = {}

            section.id = n + 1
            section.number = n
            section.visible = 1

            self.sections.append(section)

class FullTestCourse(TestCourse):
    def __init__(self):
        methods = [m for m in dir(self.__class__) if not m.startswith('__')]

        [getattr(self, method) for method in methods]

course = FullTestCourse()

elixer.create_moodle_zip(course, 'out.zip')

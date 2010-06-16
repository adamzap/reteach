import sys
import zipfile

course = object()

def create_moodle_zip(course, out_name):
    moodle_zip = zipfile.ZipFile(out_name, 'w')

    moodle_zip.write('moodle.xml.template', 'moodle.xml')

    moodle_zip.close()

create_moodle_zip(course, 'out.zip')

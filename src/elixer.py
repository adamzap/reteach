import sys
import string
import jinja2
import random
import zipfile
import datetime

def m_hash(obj):
    if isinstance(obj, dict):
        return abs(hash(tuple(obj)))
    else:
        return abs(hash(tuple(obj.__dict__.values())))

def generate_stamp():
    chars = string.ascii_letters + string.digits

    host_part = 'unknownhost'
    date_part = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join([random.choice(chars) for n in xrange(6)])

    return '+'.join([host_part, date_part, random_part])

def create_moodle_zip(course, out_name):
    xml_template = jinja2.Template(open('moodle.xml.template', 'r').read())

    moodle_xml_str = xml_template.render(course=course)

    moodle_zip = zipfile.ZipFile(out_name, 'w')

    moodle_zip.writestr('moodle.xml', moodle_xml_str)

    moodle_zip.close()

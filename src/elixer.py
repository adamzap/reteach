import sys
import string
import jinja2
import random
import zipfile
import datetime

def m_hash(*args):
    # TODO: Refactor?

    if len(args) > 1:
        the_hash = abs(hash(args))
    elif isinstance(args[0], dict):
        the_hash = abs(hash(tuple(args[0].values())))
    else:
        the_hash = abs(hash(args[0]))

    return int(str(the_hash))

def generate_stamp():
    chars = string.ascii_letters + string.digits

    host_part = 'unknownhost'
    date_part = datetime.datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join([random.choice(chars) for n in xrange(6)])

    return '+'.join([host_part, date_part, random_part])

def fix_filename(filename, res_num):
    '''In:  internet.mp3, Out: internet_res_num.mp3'''

    filename = filename.replace(' ', '_')

    if not res_num:
        return filename

    if '.' not in filename:
        return filename + '_' + res_num

    ext, name = filename[::-1].split('.', 1)

    return (ext + '.' + res_num[::-1] + '_' + name)[::-1]

def create_moodle_zip(course, out_name):
    xml_template = jinja2.Template(open('moodle.xml.template', 'r').read())

    moodle_xml_str = xml_template.render(course=course)

    moodle_zip = zipfile.ZipFile(out_name, 'w')

    moodle_zip.writestr('moodle.xml', moodle_xml_str)

    moodle_zip.close()

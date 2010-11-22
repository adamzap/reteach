import sys
import optparse

def _parse_args():
    parser = optparse.OptionParser(
        usage='%prog export.zip [output.zip]',
        description='Blackboard 9 to Moodle 1.9 converter',
        version='1.0',
    )

    (options, args) = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    for arg in args:
        if not arg.endswith('.zip'):
            print 'Error: %s\n Please provide a valid zip file' % arg

    in_zip_name = args[0]

    if len(args) > 1:
        out_zip_name = args[1]
    else:
        out_zip_name = in_zip_name.replace('.zip', '_converted.zip')

    return in_zip_name, out_zip_name

def main():
    blackboard_zip_name, moodle_zip_name = _parse_args()

    import bb9_course

    bb9_course.create_moodle_zip(blackboard_zip_name, moodle_zip_name)

if __name__ == '__main__':
    main()

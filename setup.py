from setuptools import setup

setup(
    name='reteach',
    version='1.0.0',
    description='Convert Blackboard (TM) 9 courses into Moodle 1.9 courses',
    packages=['reteach'],
    package_data={'reteach': ['moodle.xml.template']},
    include_package_data=True,
    zip_safe=False,
    author='Adam Zapletal',
    author_email='adamzap@gmail.com',
    url='http://reteach.org/',
    license='GPL v3',
    platforms=['any'],
    keywords=['blackboard', 'moodle', 'convert', 'lms'],
    install_requires=['lxml', 'jinja2'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License (GPL)'
    ],
    long_description='Convert Blackboard (TM) 9 courses into Moodle 1.9 courses',
    entry_points={
        "console_scripts": [
            "reteach = reteach.main:main",
        ]
    },
)

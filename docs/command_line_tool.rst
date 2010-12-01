Using The Command Line Tool
===========================

Converting a Single Course
--------------------------

The reteach command line tool takes at least one argument, the path to
a Blackboard 9 export zip file. If this is the only argument present,
``_converted`` will be added to the original filename before the ``.zip``
extension.

The following command will convert a Blackboard 9 export zip named ``bb9.zip``
to a Moodle 1.9 archive called ``bb9_converted.zip``::

    $ reteach bb9.zip

In addition, you may provide the ``-o`` option along with a name for the
converted zip file.

The following command will convert a Blackboard 9 export zip named ``bb9.zip``
to a Moodle 1.9 archive called ``moodle19.zip``::

    $ reteach -o moodle19.zip bb9.zip

Converting a Directory of Courses
---------------------------------

If the ``-f`` flag is provided, reteach will attempt to convert every zip file
in the provided folder.

A new folder will be created with the same name of the specified folder, and
``_converted`` will be appended its name. Also, each converted course will have
``_converted`` appended to its filename before the ``.zip`` extension.

The following command will convert all zips in a folder called
``bb9_exports_converted`` to Moodle 1.9 zips::

    $ reteach -f bb9_exports

Basic Usage
===========

Using The Command Line Tool
---------------------------

The reteach command line tool takes at least one argument, the path to
a Blackboard 9 export zip file.

As an optional second argument, you may provide the name of the output zip
file. If no second argument is present, ``_converted`` will be added to the
original filename before the ``.zip`` extension.

This will convert a Blackboard 9 export zip named ``bb9.zip`` to a Moodle 1.9
archive called ``moodle19.zip``::

    $ reteach bb9.zip moodle19.zip

This will convert a Blackboard 9 export zip named ``bb9.zip`` to a Moodle 1.9
archive called ``bb9_converted.zip``::

    $ reteach bb9.zip

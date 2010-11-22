Course Object Specification
===========================

Before converting a Blackboard archive into a Moodle archive, Reteach converts
course data into an intermediary format. This aids in portability and makes
Reteach a more easily extensible tool than it would be otherwise.

This format is represented internally as a Python object.

Below are the required properties needed to create a new input plugin for
Reteach that will convert to a Moodle 1.9 course archive.

Read This First
---------------

A property called `id` will appear frequently in this specification. An
object's `id` must be an integer that is unique to that piece of course
content.

For instance, a forum's id will be used multiple content items: the course
section where the forum exists and in the forum's settings. The `id` property
must be consistent throughout.

This is an annotated list of properties. For a more raw view of this object's
structure, see :ref:`raw_course_object_spec`.

General Properties
------------------

- archive_filename - Filename of the zip that is being converted
- timestamp - Unix timestamp of when the archive was created
- fullname - The course's long name. Example: Intro to Biology
- shortname - The course's short name. Example: BIOL101
- has_questions - Bool specifying whether or not this course has quiz questions
- quiz_category_stamp - an arbitrary Moodle Stamp
- quiz_category_id - an arbitrary numerical identifier

Content Containers
------------------

These properties are Python lists of content on the course object

- forums - see :ref:`forums`
- labels - see :ref:`labels`
- quizzes - see :ref:`quizzes`
- resources - see :ref:`resources`
- questions - see :ref:`questions`
- sections - see :ref:`sections`

.. _forums:

Forums
******

- id
- name
- introduction

.. _labels:

Labels
******

- id
- name
- content

.. _quizzes:

Quizzes
*******

- id
- name
- intro
- question_string
- section_id
- stamp
- res_num
- feedback_id
- questions

  - id

.. _resources:

Resources
*********

- id
- name
- res_type
- reference
- summary
- alltext

.. _sections:

Sections
********

- id
- number
- summary
- visible
- mods

  - id
  - type
  - indent

.. _questions:

Questions
---------

There are five question types:

- essay
- truefalse
- shortanswer
- multichoice
- matching
- stamp

Questions is a dictionary on the course object. The keys are the above question
type names, and the values are lists of question objects.

Some properties are shared between all question types. There are as follows:

- id
- name
- res_num
- text
- image

Essay
*****

  - answer_id
  - feedback

Truefalse
*********

  - general_feedback
  - true_answer_id
  - false_answer_id
  - true_points
  - true_feedback
  - false_points
  - false_feedback

Shortanswer
***********

  - general_feedback
  - answer_string
  - answers

    - id
    - answer_text
    - points
    - feedback

Multichoice
***********

  - general_feedback
  - answer_string
  - single_answer
  - correct_feedback
  - partially_correct_feedback
  - incorrect_feedback
  - answers

    - id
    - answer_text
    - points
    - feedback

Matching
********

  - general_feedback
  - answers

    - id
    - question_text
    - answer_text

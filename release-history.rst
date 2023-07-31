.. _release_history:

Release and Version History
==============================================================================


Backlog (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.8.1 (2023-07-31)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``waiter.Waiter`` for retry and long polling pattern
- add ``iterable.group_by`` function
- add ``aws.aws_s3_uri.py`` module
- add ``aws.aws_dynamodb_export_to_s3.py`` module


0.7.1 (2023-05-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``hashes.Hashes.of_folder`` and ``hashes.Hashes.of_paths``.
- add ``git_cli.locate_dir_repo``.

**Minor Improvements**

- add edge case handling for ``better_pathlib.temp_cwd``.

**Bugfixes**

**Miscellaneous**


0.6.1 (2023-05-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``build_dist`` module to build the source distribution of Python.


0.5.3 (2023-05-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Minor Improvements**

- allow mini string template in ``nest_logger.NestedLogger.pretty_log``, ``nest_logger.NestedLogger.start_and_end``.


0.5.2 (2023-05-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Miscellaneous**

- add ``get_names`` method for most of enum class in ``better_enum`` module
- add ``error_emoji`` argument to ``nest_logger.NestedLogger.start_and_end`` decorator.


0.5.1 (2023-05-05)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``better_pathlib``
- add ``dataclass_dataframe``
- add ``pytest_cov_helper``
- add ``better_enum``
- add ``runtime``
- add ``os_platform``
- add ``git_cli``

**Minor Improvements**

- improve code coverage test


0.4.1 (2023-02-25)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``nested_logger.block``

**Miscellaneous**

- add more jupyter notebook examples


0.3.2 (2023-02-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- by default, ``nest_logger.py`` no longer create the default logger.


0.3.1 (2023-02-06)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- ``nest_logger.py`` new features:
    - allow to customize pipe character
    - ``nested()`` context manager is now smarter
    - ``disabled()`` context manager can temporarily disable the logger


0.2.1 (2023-02-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``nest_logger.py``


0.1.1 (2023-02-04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- First release
- add ``binarysearch.py``
- add ``hashes.py``
- add ``iterable.py``
- add ``rnd.py``
- add ``timer.py``

===========================================
Linter for Zalando's RESTful API Guidelines
===========================================

.. image:: https://travis-ci.org/zalando-incubator/restful-api-guidelines-linter.svg?branch=master
   :target: https://travis-ci.org/zalando-incubator/restful-api-guidelines-linter
   :alt: Build Status

.. image:: https://coveralls.io/repos/zalando-incubator/restful-api-guidelines-linter/badge.svg
   :target: https://coveralls.io/r/zalando-incubator/restful-api-guidelines-linter
   :alt: Code Coverage

.. image:: https://img.shields.io/pypi/dw/restful-api-guidelines-linter.svg
   :target: https://pypi.python.org/pypi/restful-api-guidelines-linter/
   :alt: PyPI Downloads

.. image:: https://img.shields.io/pypi/v/restful-api-guidelines-linter.svg
   :target: https://pypi.python.org/pypi/restful-api-guidelines-linter/
   :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/l/restful-api-guidelines-linter.svg
   :target: https://pypi.python.org/pypi/restful-api-guidelines-linter/
   :alt: License


This is a very basic linter to check whether a given Swagger specification (YAML file)
complies with `Zalando's RESTful API Guidelines`_.

Usage:

.. code-block:: bash

    $ sudo pip3 install -U restful-api-guidelines-linter
    $ restful-api-guidelines-linter my-swagger-spec.yaml -v

The following guidelines are currently checked:

* `Must: Always Return JSON Objects As Top-Level Data Structures To Support Extensibility <https://zalando.github.io/restful-api-guidelines/compatibility/Compatibility.html#must-always-return-json-objects-as-toplevel-data-structures-to-support-extensibility>`_
* `Must: Avoid Trailing Slashes <https://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-avoid-trailing-slashes>`_
* `Must: Do Not Use URI Versioning <https://zalando.github.io/restful-api-guidelines/compatibility/Compatibility.html#must-do-not-use-uri-versioning>`_
* `Must: Pluralize Resource Names <https://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-pluralize-resource-names>`_
* `Must: Property names must be snake_case (and never camelCase). <http://zalando.github.io/restful-api-guidelines/json-guidelines/JsonGuidelines.html#must-property-names-must-be-snakecase-and-never-camelcase>`_
* `Must: Use HTTP Methods Correctly <http://zalando.github.io/restful-api-guidelines/http/Http.html#must-use-http-methods-correctly>`_
* `Must: Use lowercase separate words with hyphens for Path Segments <http://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-use-lowercase-separate-words-with-hyphens-for-path-segments>`_
* `Must: Use snake_case (never camelCase) for Query Parameters <http://zalando.github.io/restful-api-guidelines/naming/Naming.html#must-use-snakecase-never-camelcase-for-query-parameters>`_


Running Unit Tests
==================

.. code-block:: bash

    $ sudo pip3 install -U tox
    $ tox

.. _Zalando's RESTful API Guidelines: http://zalando.github.io/restful-api-guidelines/

python-resuds
=============

[![Build Status](https://travis-ci.org/AppsFuel/python-resuds.png?branch=master)](https://travis-ci.org/AppsFuel/python-resuds)

[![Coverage Status](https://coveralls.io/repos/AppsFuel/python-resuds/badge.png?branch=master)](https://coveralls.io/r/AppsFuel/python-resuds)

suds wrapper (for amobee)

== TODO ==
* Problem on receive resposneError in ResudsClientTestCase.testResponseErrorOnCreate. In the Envelope there're a faultcode field in with there's a text. Suds try to convert the string to int raising a ValueError.
# smartmeter-greenbutton
Python code to read smart-meter data from utility company

## Description

This code is meant to be a framework to extract smart-meter data using the
[Green Button](https://www.greenbuttondata.org) API.  Unfortuanately at the
moment there does not seem to be any documentation on subscribing to the
stream as a 'Third Party', so this code uses the Residential
'Download my Data' button instead.

Currently only Portland General Electric is supported, and they do not provide
an easy link to get the data, so screen scraping is used to scrape the relevant
links.  Because PGE's site is entirely AJAX based, `selenium` and `phantomjs`
are used to parse the relevant web pages.

I will be happy to work with anyone interested to help add additional providers.

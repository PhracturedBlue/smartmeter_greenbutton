# smartmeter-greenbutton
Python code to read smart-meter data from utility company

## Description

This code is meant to be a framework to extract smart-meter data using the
[Green Button](https://www.greenbuttondata.org) API.  Unfortuanately at the
moment there does not seem to be any documentation on subscribing to the
stream as a 'Third Party', so this code uses the Residential
'Download my Data' button instead.

Currently only Portland General Electric is supported.  Access is done via OAuth2,
which requires a bit of manual configuration to setup, but is simple and reliable
once that is complete.  Full instructions for filling out the fields in config.yaml
can be found in the header in `smartmeter_greenbutton/utilities/portland_general_electric.py`

I will be happy to work with anyone interested to help add additional providers.

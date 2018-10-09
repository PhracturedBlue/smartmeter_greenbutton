"""Load GreenButton data from utility's web-site"""

import argparse
import logging
from smartmeter_greenbutton.parser import parse_data


def fetch_data(module, conf, start_date=None):
    """Dynamically load requested utility module"""
    mod = __import__('smartmeter_greenbutton.utilities.' +
                     module, fromlist=['fetch_data'])
    mod_fetch_data = getattr(mod, 'fetch_data')
    zipdata = mod_fetch_data(conf, start_date)
    return zipdata


def main():
    """Main routine example"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", help="User Name", required=False)
    parser.add_argument("--password", help="Password", required=False)
    parser.add_argument("--file",
                        help="Zip File to read rather than reading from web",
                        required=False)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if not args.file:
        zipdata = fetch_data(
            "portland_general_electric",
            {'username': args.username, 'password': args.password})
    else:
        with open(args.file, "rb") as stream:
            zipdata = stream.read()
    # with open("dump", "wb") as stream:
    #     stream.write(zipdata)
    usage = parse_data(zipdata)
    for (start, duration, value, kwh) in usage:
        print("{} ({}): {} --> {}".format(
            start.strftime('%Y-%m-%d %H:%M:%S'), duration, value, kwh))


if __name__ == '__main__':
    main()

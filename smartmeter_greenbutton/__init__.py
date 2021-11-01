"""Load GreenButton data from utility's web-site"""

import argparse
import logging
import yaml
from smartmeter_greenbutton.parser import parse_data


def fetch_data(conf, start_date=None):
    """Dynamically load requested utility module"""
    if start_date:
        start_date = datetime.datetime.strprime(start_date, '%Y-%m-%d')
    if 'module' not in conf:
        logging.error("'module' is a required field in the config file")
        raise ValueError
    mod = __import__(f'smartmeter_greenbutton.utilities.{conf["module"]}', fromlist=['fetch_data'])
    mod_fetch_data = getattr(mod, 'fetch_data')
    zipdata = mod_fetch_data(conf, start_date)
    return zipdata


def main():
    """Main routine example"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", help="Config File", required=True)
    parser.add_argument("--start-date", help="Start-date as YYYY-MM-DD)")
    parser.add_argument("--file",
                        help="Zip File to read rather than reading from web",
                        required=False)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    if not args.file:
        with open(args.config_file) as _fh:
            try:
                conf = yaml.safe_load(_fh)
            except yaml.YAMLError as _e:
                logging.error("Failed to parse config file: %s", _e)
                raise
        breakpoint()
        zipdata = fetch_data(conf, args.start_date)
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

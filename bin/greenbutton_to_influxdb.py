#!/usr/bin/env python3
"""Fetch GreenButton data and store it in influxdb"""

import argparse
import subprocess
import json
import datetime
import logging
import re
import time

import yaml

from smartmeter_greenbutton import fetch_data
from smartmeter_greenbutton.parser import parse_data

def main():
    """Main routine"""
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Config-file", required=True)
    parser.add_argument("-t", "--test", help="test-mode.  Don't update influxdb",
                        action='store_true')
    args = parser.parse_args()

    with open(args.config, "r") as stream:
        conf = yaml.load(stream)

    last_time = _get_last_influx_entry(conf)

    #filename = sys.argv[1]
    #with open(filename, "rb") as fh:
    #    zipdata = fh.read()
    zipdata = fetch_data(conf['utility']['provider'], conf['utility'], last_time)
    usage = parse_data(zipdata)
    epoch = datetime.datetime.utcfromtimestamp(0)
    for (start, _duration, value, kwh) in usage:
        orig_start = start
        start += datetime.timedelta(hours=time.altzone/3600)
        if args.test:
            print("{} ({}) > {}: {} {}kwh".format(start, orig_start, last_time, value, kwh))
            continue
        if not last_time or orig_start > last_time:
            influx_str = conf['influxdb']['values']
            influx_str = re.sub(':VALUE:', str(value), influx_str)
            influx_str = re.sub(':KWH:', str(kwh/1000), influx_str)
            result = subprocess.run(
                [
                    'curl', '-s', '-i',
                    '-XPOST',
                    conf['influxdb']['url'] + '/write?db=' + conf['influxdb']['database'],
                    '-u', conf['influxdb']['userpass'],
                    '--data-binary',
                    "{},{} {} {}".format(
                        conf['influxdb']['series'],
                        conf['influxdb']['tags'],
                        influx_str,
                        int((start - epoch).total_seconds() * 1e9))
                ],
                stdout=subprocess.PIPE)
            logging.info(result.stdout)

def _get_last_influx_entry(conf):
    last_time = None
    try:
        result = subprocess.run(
            [
                'curl', '-G', '-s',
                conf['influxdb']['url'] + '/query',
                '-u', conf['influxdb']['userpass'],
                '--data-urlencode', 'db=' + conf['influxdb']['database'],
                '--data-urlencode', 'epoch=s',
                '--data-urlencode', "q=SELECT * FROM {} WHERE {} order by DESC limit 1".format(
                    conf['influxdb']['series'],
                    conf['influxdb']['filter'])
            ],
            stdout=subprocess.PIPE)

        res = json.loads(result.stdout)['results'][0]['series'][0]
        idx = res['columns'].index('time')
        last_time = datetime.datetime.utcfromtimestamp(
            res['values'][0][idx]) - datetime.timedelta(hours=time.altzone/3600)
        logging.info("Querying data starting from: " + last_time.strftime("%Y-%m-%d"))
    except Exception:  # pylint: disable=broad-except
        logging.warning("Failed to determine last_date")
    return last_time

main()

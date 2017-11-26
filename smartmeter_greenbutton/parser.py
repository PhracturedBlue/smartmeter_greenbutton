"""Parse GreenButton XML (within zipfile)"""

import datetime
import io
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

def parse_data(zipdata):
    """Main parser routine"""
    usage = []
    zipfh = io.BytesIO(zipdata)

    with ZipFile(zipfh) as stream:
        data = stream.read(stream.infolist()[0]).decode("utf-8")
        data = re.sub(' xmlns="[^"]+"', '', data)
        root = ET.fromstring(data)
        last_date = datetime.date.today()
        kwh = 0
        for child in root.findall("./entry"):
            if child.find("./title").text != "Energy Usage":
                print("Skipping: {}".format(child.find("./title").text))
                continue
            for reading in child.findall("./content/IntervalBlock/IntervalReading"):
                value = float(reading.find("./value").text)
                start = int(reading.find("./timePeriod/start").text)
                duration = float(reading.find("./timePeriod/duration").text)
                start = datetime.datetime.utcfromtimestamp(start)
                if start.date() != last_date:
                    last_date = start.date()
                    kwh = 0
                    usage.append((start, 0.0, 0.0, 0.0))
                kwh += value / duration * 3600
                end = start + datetime.timedelta(seconds=duration)
                if end.date() != start.date():
                    end = start.replace(hour=23, minute=59, second=59, microsecond=0)
                usage.append((end, duration, value, kwh))
    return usage

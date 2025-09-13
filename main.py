import argparse
import logging
import os
from dataclasses import dataclass
from datetime import datetime

from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

BACKGROUND_COLOR = "#0f0f0f"


@dataclass
class Floor_Data:
    name: str
    summary: int
    data: list[str]


def makeLogger(logFile):
    formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)-8s %(message)s',
                                  datefmt='%Y-%-m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logFile)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def set_data(data: list[Floor_Data], file: str):
    with open(file, 'r') as f:
        content = f.read()
    for line in content.split("\n"):
        line_split = line.split(",")
        floor: int = 0
        if not line_split[0][:1].lower() == 'b':
            floor = int(line_split[0][:1])
        data[floor].summary += 1
        data[floor].data.append(f"{line_split[0]} - {line_split[1]} {line_split[2]}")


@app.route('/', methods=['GET', 'POST'])
def update_file():
    if request.method == 'GET':
        data = []
        for i in range(10):
            if i == 0:
                data.append(Floor_Data(name='Basement', summary=0, data=[]))
            else:
                data.append(Floor_Data(name=f'Floor {i}', summary=0, data=[]))
        set_data(data, "alarms.txt")

        latest_alarm_date = None
        days_since = "NaN"

        try:
            with open("alarms.txt", 'r') as f:
                for line in f:
                    if not line.strip(): continue

                    # get dates
                    parts = line.split(',')
                    date_str = parts[1].strip()
                    current_alarm_date = datetime.strptime(date_str,'%Y-%m-%d').date()

                    # check if this alarm is the latest, if so update latest_alarm_date
                    if latest_alarm_date is None or current_alarm_date > latest_alarm_date: latest_alarm_date = current_alarm_date

            if latest_alarm_date:
                # get date difference
                today = datetime.now().date()
                difference = today - latest_alarm_date
                days_since = difference.days

        except (FileNotFoundError,IndexError):
            days_since = "Error reading file or file not found" # yeah ehren look at my planning for not having a file

        return render_template('fire.html', color=BACKGROUND_COLOR, floor_data=data, days_since=days_since)


if __name__ == '__main__':
    logger = "fire.log"

    # from waitress import serve
    # serve(app,host='0.0.0.0',port=8080)
    # gunicorn -w 4 'web_printer:app' -b '0.0.0.0:8080'
    app.run(host='0.0.0.0', port=5000, debug=False)
import argparse
import logging
import os
from dataclasses import dataclass
import datetime

from flask import Flask, request, redirect, url_for, render_template
app = Flask(__name__)

BACKGROUND_COLOR="#0f0f0f"

@dataclass
class Floor_Data:
    name: str
    summary: int
    alarms_str: str
    arrow: str

@dataclass
class Archive_Page:
    name: str
    url: str

def makeLogger(logFile):
    formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(logFile)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

def get_archive_pages():
    archive = []
    for filename in os.listdir('archive'):
        archive.append(Archive_Page(name=filename, url=url_for('archive_alarms', filename=filename)))
    return archive

def set_data(data:list, file: str):
    with open(file,'r') as f:
        content = f.read()
    now = datetime.datetime.now()
    days = 100000
    total = 0
    for line in content.split("\n"):
        if line == '':
           continue
        line_split = line.split(",")
        floor: int = 0
        if line_split[0].lower()[0] == 'o':
            floor = 10
            line_split[0] = line_split[0][1:]
        elif not line_split[0][:1].lower() == 'b':
            floor = int(line_split[0][:1])
        data[floor].summary += 1
        total += 1
        data[floor].alarms_str += f"{line_split[0]} - {line_split[1]} {line_split[2]}<br>"
        date = datetime.datetime.strptime(line_split[1], '%Y-%m-%d')
        days = min(days, (now-date).days)
    if days == 100000:
        return 'N/A', total
    return days, total

@app.route('/', methods=['GET', 'POST'])
def default_route():
    return redirect(url_for('current_alarms'))

@app.route('/alarms')
def current_alarms():
    try:
        data = []
        for i in range(10):
            if i == 0:
                data.append(Floor_Data(name='Basement', summary=0, alarms_str='', arrow=f'ArrowBasement'))
            else:
                data.append(Floor_Data(name=f'Floor {i}', summary=0, alarms_str='', arrow=f'ArrowFloor {i}'))
        data.append(Floor_Data(name='Other', summary=0, alarms_str='', arrow='ArrowOther'))
        days, total = set_data(data, 'alarms')
        archive = get_archive_pages()
        return render_template('fire.html', color=BACKGROUND_COLOR, floor_data=data, days=days, total=total, archive=archive)
    except Exception as e:
        print(e)
        return redirect(url_for('current_alarms'))

@app.route('/archive/<filename>')
def archive_alarms(filename):
    try:
        data = []
        for i in range(10):
            if i == 0:
                data.append(Floor_Data(name='Basement', summary=0, alarms_str='', arrow=f'ArrowBasement'))
            else:
                data.append(Floor_Data(name=f'Floor {i}', summary=0, alarms_str='', arrow=f'ArrowFloor {i}'))
        data.append(Floor_Data(name='Other', summary=0, alarms_str='', arrow='ArrowOther'))
        days, total = set_data(data, f'archive/{filename}')
        archive = get_archive_pages()
        return render_template('fire.html', color=BACKGROUND_COLOR, floor_data=data, days=days, total=total, archive=archive)
    except Exception as e:
        return redirect(url_for('current_alarms'))

if __name__ == '__main__':
    logger = "fire.log"


    # from waitress import serve
    # serve(app,host='0.0.0.0',port=8080)
    # gunicorn -w 4 'web_printer:app' -b '0.0.0.0:8080'
    app.run(host='0.0.0.0', port=5001,debug=False)

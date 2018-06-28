from pymongo import MongoClient
from flask import Flask, render_template, request, url_for, redirect
import csv
import json
import configparser
#file level variable block starts

config = configparser.ConfigParser()
config.read("perf/perf.ini")

hostip = str(config.get("MONGO", "hostip"))
port = int(config.get("MONGO", "port"))
print ("Mongo connected to host " + hostip + " on port " + str(port))
CLIENT = MongoClient(hostip, port)  #the mongo db is on same machine on aws. hence passing localhost.
MONGO_PERF_DB = CLIENT.perf_db
MONGO_PERF_COLLECTION= MONGO_PERF_DB.perf_coll
IS_DEV_MODE = True

#file level variable block ends

app = Flask(__name__)

def perf_csv_parser(filename, release, build, collection, date):
    reader = csv.DictReader(open(filename))
    query = {'Release': release, 'Build': build, 'date': date}
    result = {}
    for row in reader:
        key = row.pop('sampler_label')
        result[key] = row
    query['Result'] = result

    top_three_report_error_percent = {}
    exp1 = dict(sorted(result.items(), key=lambda x: float(x[1]['aggregate_report_90%_line']), reverse=True)[:3])
    for k, v in exp1.items():
        top_three_report_error_percent[k] = str(v['aggregate_report_error%'])

    highlights = {'aggregate_report_count': result['TOTAL']['aggregate_report_count'],
                  'average': result['TOTAL']['average'],
                  'aggregate_report_median': result['TOTAL']['aggregate_report_median'],
                  'aggregate_report_90_percent_line': result['TOTAL']['aggregate_report_90%_line'],
                  'aggregate_report_error_percent': str(result['TOTAL']['aggregate_report_error%']),
                  'aggregate_report_rate': str(round(float(result['TOTAL']['aggregate_report_rate']), 2)),
                  'top_three_report_error_percent': top_three_report_error_percent}
    query['Highlights'] = highlights
    collection.insert_one(query)
    return True

@app.route("/")
def root():
    return render_template("index.html", title="jMeter Report")

@app.route("/index")
def index():
    return root()

@app.route("/uploadcsv")
def importperfresult():
    return render_template('import_perf_result.html', title="Import Perf Results", is_dev_mode=IS_DEV_MODE)

@app.route('/importPerfResult', methods = ['POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        perf_csv_parser(f.filename, request.form['release'], request.form['build'],
                        MONGO_PERF_COLLECTION, request.form['date'])
        return 'Data imported into Mongo DB'

@app.route("/perfcompareui", methods=['POST', 'GET'])
def perf_compare_ui():
    release_list = ['--None--']
    if request.method == 'GET':
        try:
            releases = (MONGO_PERF_COLLECTION.find({}, {'Release': 1}))
            for key, value in enumerate(releases):
                release_list.append(value['Release'])
            print(release_list)
        except Exception as e:
            return "Error occured while fetching data for releases .Error is "+e.__str__()
        return render_template('perf_compare_ui.html', data=release_list, title='Perf Compare Result', is_dev_mode=IS_DEV_MODE)
    else:
        formdata = request.form
        base_rel = formdata['base_rel']
        curr_rel = formdata['curr_rel']
        perfreporturl = url_for('perf_compare', baseline_release=base_rel, current_release=curr_rel)
        if not IS_DEV_MODE:
            perfreporturl = "/ms-perfcompare" + perfreporturl
        return redirect(perfreporturl)


@app.route("/perfcompare/<baseline_release>/<current_release>")
def perf_compare(baseline_release, current_release):
    '''
    This service to get perf results comparison between baselne and current release
    :param baseline_release:
    :param current_release:
    :return:
    '''
    try:
        modules_base = MONGO_PERF_COLLECTION.find_one({'Release': baseline_release})['Result']
    except Exception as e:
        return "Error occured while fetching data for baseline release " +baseline_release + " .Error is "+e.__str__()
    try:
        modules_current = MONGO_PERF_COLLECTION.find_one({'Release': current_release})['Result']
    except Exception as e:
        return "Error occured while fetching data for baseline release " +current_release + " .Error is "+e.__str__()

    perfcompareui = url_for('perf_compare_ui')
    if not IS_DEV_MODE:
        perfcompareui = "/ms-perfcompare" + perfcompareui
    return render_template('index_sort.html', title='Sorted Perf Report', modules_base=modules_base, modules_current=modules_current,baseline=baseline_release,current=current_release, backurl=perfcompareui)


@app.route("/perfcompare/result/json", methods=['POST'])
def perf_compare_json_report():
    '''
    This API is used to return perf compare result in JSON format
    {"success": "true", "data": {"perf": {"Current_Release": "4.0.0_42", "Baseline_Release": "2.5.0", "result": [["Modules", "Baseline Release Value (2.5.0)", "Current Release Value (4.0.0_42)", "Precent Change", "Status"], ["Search Item to trace", 49.0, 45.0, -8.16326530612245, "Pass"]]}}, "error": {}}
    :return:
    '''
    req_data = request.get_json()
    errordata = {}
    if None == req_data:
        errordata["statuscode"] = 404
        errordata["errormsg"] = "NULL request."
        return builderrorresponse(errordata)

    if None == req_data['data']['baseline_release']:
        errordata["statuscode"] = 404
        errordata["errormsg"] = "baseline_release not found in request."
        return builderrorresponse(errordata)

    if None == req_data['data']['current_release']:
        errordata["statuscode"] = 404
        errordata["errormsg"] = "current_release not found in request."
        return builderrorresponse(errordata)

    baseline_release = req_data['data']['baseline_release']
    current_release = req_data['data']['current_release']
    try:
        modules_base = MONGO_PERF_COLLECTION.find_one({'Release': baseline_release})['Result']
    except Exception as e:
        errordata["statuscode"] = 404
        errordata["errormsg"] = "Error occured while fetching data for baseline release " + baseline_release + " .Error is " + e.__str__()
        return builderrorresponse(errordata)
    try:
        modules_current = MONGO_PERF_COLLECTION.find_one({'Release': current_release})['Result']
    except Exception as e:
        errordata["statuscode"] = 400
        errordata["errormsg"] = "Error occured while fetching data for baseline release " + current_release + " .Error is " + e.__str__()
        return builderrorresponse(errordata)

    returndata = {}
    data={}
    data['Current_Release'] = current_release
    data['Baseline_Release'] = baseline_release
    data['result'] = [['Modules', 'Baseline Release Value (' + baseline_release + ')', 'Current Release Value (' + current_release + ')', 'Precent Change', 'Status']]
    returndata['perf'] = data
    all_base_items = modules_base.items()

    for baseline_item in all_base_items:
        module_name = baseline_item[0]
        baseline_module_data = baseline_item[1]
        current_module_data = modules_current[module_name]
        baseline_release_value = float(baseline_module_data['aggregate_report_90%_line'])
        current_release_value = float(current_module_data['aggregate_report_90%_line'])
        percent_deviation = ((current_release_value - baseline_release_value)/baseline_release_value) * 100
        if current_release_value < (1.05 * baseline_release_value):
            status = "Pass"
        else:
            status = "Fail"
        data['result'] += [[module_name, baseline_release_value, current_release_value, percent_deviation, status]]
    return getsuccessresponse(returndata)

def getsuccessresponse(data):
    returndata = {}
    returndata["success"] = "true"
    returndata["data"] = data
    returndata["error"] = {}
    return json.dumps(returndata)


def builderrorresponse(data):
    returndata = {}
    returndata["success"] = "false"
    returndata["data"] = {}
    returndata["error"] = data
    return json.dumps(returndata)

if __name__ == "__main__":
    app.run("0.0.0.0", 5002, debug=True)

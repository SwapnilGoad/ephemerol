from zipfile import ZipFile
from Models import ScanItem, ScanResult, ScanStats
import csv

rulebase = []
scan_results = []


def load_rules(rules_csv):
    global rulebase
    rulebase = []
    with open(rules_csv, 'rU') as csvfile:
        rulereader = csv.DictReader(csvfile, delimiter=',')
        for row in rulereader:
            rulebase.append(ScanItem(app_type=row['app_type'],
                                 file_type=row['file_type'],
                                 file_category=row['file_category'],
                                 file_name=row['file_name'],
                                 refactor_rating=row['refactor_rating'],
                                 description=row['description'],
                                 text_pattern=row['text_pattern']
                                 ))


def config_scan(file_path_list):
    configrules = []
    global scan_results

    for rule in rulebase:
        if (rule.file_type == "config") and (rule.app_type == "java"):
            configrules.append(rule)

    for path in file_path_list:
        if path.endswith('/'):
            path = path[:-1]
        file_name = path.split('/')[-1]
        for configrule in configrules:
            if file_name == configrule.file_name:
                scan_results.append(ScanResult(scan_item=configrule, flagged_file_id=file_name))


def source_scan(zfile):
    for fname in zfile.namelist():
        if fname.endswith('.java'):
            java_file_scan(zfile.open(fname).readlines(), fname)
        elif fname.endswith('.xml'):
            xml_file_scan(zfile.open(fname).readlines(), fname)


def xml_file_scan(file_lines, filename):
    xmlrules = []
    global scan_results
    for rule in rulebase:
        if (rule.file_type == "config") and (rule.file_name == "*.xml") and (rule.text_pattern != "NONE"):
            xmlrules.append(rule)

    for line in file_lines:
        for rule in xmlrules:
            if (rule.text_pattern in line):
                scan_results.append(ScanResult(scan_item=rule, flagged_file_id=filename))


def java_file_scan(file_lines, filename):
    javarules = []
    global scan_results
    for rule in rulebase:
        if (rule.file_type == "java") \
                and (rule.app_type == "java") \
                and (rule.file_name == "*.java") \
                and (rule.text_pattern != "NONE"):
            javarules.append(rule)

    for line in file_lines:
        for rule in javarules:
            if (rule.text_pattern in line):
                scan_results.append(ScanResult(scan_item=rule, flagged_file_id=filename))


def scan_archive(file_name):
    global scan_results
    scan_results = []
    with ZipFile(file_name, 'r') as zfile:
        config_scan(zfile.namelist())
        source_scan(zfile)

    return scan_results, ScanStats(scan_results)

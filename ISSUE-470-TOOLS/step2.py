#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This program  modifying the standard name table files. It must
be run as second step, i.e. after executing step1.py.

In the xml files each standard name table entry (element <entry>) must have
tags <canonical_units> and <description>. For entries where either of these, 
or both, are missing this program will add empty such tags.

The intention is to be as non-intrusive as possible wrt the original file formatting.
"""


import re
from datetime import datetime, UTC
from pathlib import Path


MY_PATH = "../"
BASE_PATH = MY_PATH + "Data/cf-standard-names/"


def extract_entries(xml_raw):
    """
    The total length of the xml string will change so have to make changes beginning
    at the end and then moving forward to the start.
    """
    found_entries = list(re.finditer(r'<entry id=\".+?\">.+?</entry>', xml_raw, re.S))
    found_entries.reverse()
    for found in found_entries:
        entry = found.group()
        e = re.search(r'(?<=\").+?(?=\")', entry)
        std_name = e.group()
        start, stop = found.span()
        entry_lines = entry.split("\n")
        indent = len(entry_lines[1]) - len(entry_lines[1].lstrip())
        if len(entry_lines) == 2:
            indent = indent + 3
        modified = False
        for i, tag in enumerate(["canonical_units", "description"]):
            if not re.search(rf"(?<=\<{tag}>).*?", entry, re.S):
                if not modified:
                    print(f"   --- {std_name}:", end ="")
                print(f"      {tag}", end="")
                modified = True
                entry_lines.insert(i + 1, f"{' '*indent}<{tag}></{tag}>")
        if modified:
            print()
            entry = "\n".join(entry_lines)
            xml_raw = xml_raw[0: start] + entry + xml_raw[stop:]
    return xml_raw


def update_last_modified(xml_raw):
    time_stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    pat = r"<last_modified>.+?Z</last_modified>"
    new = r"<last_modified>" + time_stamp + r"</last_modified>"
    xml_raw = re.sub(pat, new, xml_raw)
    return xml_raw


def do_the_work(version):
    xml_file = f"{BASE_PATH}{version}/src/cf-standard-name-table.xml"
    with open(xml_file, "r") as fh:
        xml_raw = fh.read()
    print(xml_file)

    xml_raw = extract_entries(xml_raw)
    xml_raw = update_last_modified(xml_raw)

    with open(xml_file, "w") as fh:
           fh.write(xml_raw)
    

if __name__ == "__main__":
    for version in range(1, 100):
        try:
            if version != 38:
                print("\n")
                do_the_work(version)
        except:
            break

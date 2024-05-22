#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
This is the first of several programs for modifying the standard name table files.
It implements changes to the XML file format agreed on by hte CF Committee,
for an overview see
https://github.com/cf-convention/cf-convention.github.io/issues/457

Briefly:
* Update link to online XSD schema file
* New tags: <conventions>, <first_published>, and <last_modified> (changed meaning)
* Allow aliased standard name to point to two alternatives
* Specific fixes to three versions
* Currently, https://github.com/cf-convention/discuss/issues/273 are not handled,
  but probably it should be fixed here. 

The intention is to be as non-intrusive as possible wrt the original file formatting.
"""


import re
from datetime import datetime, UTC
from pathlib import Path


MY_PATH = "../"
BASE_PATH = MY_PATH + "Data/cf-standard-names/"
NEW_XSD = "https://cfconventions.org/Data/schema-files/cf-standard-name-table-2.0.xsd"


def handle_input_file(xml_file):
    """
    This program is the first one modifying the standard name table files,
    hence we are starting from scratch and need to use the original file.
    IF there is an "__ORIGINAL" file available, then read from that one,
    else read the usual file and immediately save it as an "__ORIGINAL" file.
    """
    xml_original = xml_file.replace("-table", "-table__ORIGINAL")

    my_file = Path(xml_original)
    if my_file.is_file():
        # there is already a backup file: read this one
        with open(xml_file, "r") as fh:
            xml_raw = fh.read()
        print(f"READING SAVED ORIGINAL FILE:  {xml_original}")
    else:
        # there is no backup: read the normal file
        with open(xml_file, "r") as fh:
            xml_raw = fh.read()
        # then save a backup copy before start modifications
        with open(xml_original, "w") as fh:
            fh.write(xml_raw)
        print(f"READING NORMAL FILE, AND CREATING A BACKUP:  {xml_file}")
    return xml_raw


def fix_xml_header(xml_raw):
    if xml_raw[:6] != "<?xml ":
        xml_raw = '<?xml version="1.0"?>\n' + xml_raw
        print("   --- added tag '<?xml ...>")
    return xml_raw


def update_xsd_link(xml_raw):
    for old_xsd in ["CFStandardNameTable-1.0.xsd", 
                    "CFStandardNameTable-1.1.xsd", 
                    "cf-standard-name-table-1.1.xsd"]:
        if old_xsd in xml_raw: 
            xml_raw = xml_raw.replace(old_xsd, NEW_XSD)
            print(f"   --- changed xsd link:   {old_xsd}  -->  {NEW_XSD}")
    return xml_raw


def fix_v1_datetime(xml_raw):
    """
    In version 1 add missing a `last_modified` tag after the `version_number` tag.
    The actual date is taken from the originally published html table.
    """
    txt1 = ">1</version_number>\n"
    txt2 = txt1 + "  <last_modified>2002-04-02T12:00:00Z</last_modified>\n"
    xml_raw = xml_raw.replace(txt1, txt2)
    print("   --- added <last_modified> tag in version 1")
    return xml_raw


def fix_v12_duplicate_entry(xml_raw):
    """In version 12 delete a duplicate standard name entry."""
    pat = r'\n *<entry id="sea_surface_height_above_reference_ellipsoid">.+?</entry> *?(?=\n)'
    xml_raw = re.sub(pat, "", xml_raw, 1, re.S)
    print("   --- removed first instance of exact duplicates of 'sea_surface_height_above_reference_ellipsoid' in version 12")
    return xml_raw


def fix_v71_datetime(xml_raw):
    """In version 71 update the `last_modified` dateTime payload to include seconds."""
    if "2020-02-04T12:00Z" in xml_raw:
        xml_raw = xml_raw.replace("2020-02-04T12:00Z", "2020-02-04T12:00:00Z")
        print("   --- modified <last_modified> to include seconds in version 71")
    return xml_raw


def change_to_first_published_tag(xml_raw):
    xml_raw = xml_raw.replace("last_modified", "first_published")
    print("   --- changed 'last_modified'  -->  'first_published'")
    return xml_raw


def add_last_modified_tag(xml_raw):
    time_stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    modified = "last_modified"
    modified_start = "<" + modified + ">"
    modified_end = modified_start.replace("<", "</")
    modified_element = modified_start + time_stamp + modified_end
    inst_text = "<institution>"
    n = len( inst_text)
    inst = re.search(("\n( *)" + inst_text), xml_raw)
    spaces = inst.group()[1: -n]
    position = inst.span()[0]
    xml_raw = xml_raw[:position] + "\n" + spaces + modified_element + xml_raw[position:]
    print("   --- added new tag 'last_modified'")
    return xml_raw


def add_conventions(xml_raw):
    pat = r"\n +?<version_number>\d+?</version_number>"
    old_elem = re.search(pat, xml_raw)
    old_elem = old_elem.group()
    version = re.search(r"\d{1,3}", old_elem)
    version = version.group()
    new_elem = old_elem + "\n  <conventions>CF-StandardNameTable-" + version + "</conventions>"
    xml_raw = xml_raw.replace(old_elem, new_elem)
    return xml_raw


def find_duplicate_aliases(xml_raw):
    pat = (r' +?<alias id=".+?</alias> *?\n')
    alias_dict = {}
    for found in re.finditer(pat, xml_raw, re.S):
        res = re.search(r'(?<=").+?(?=">)', found.group())
        res = res.group()
        if res in alias_dict:
            alias_dict[res] += 1
        else:
            alias_dict[res] = 1
    for k in list(alias_dict):
        if alias_dict[k] == 1:
            _ = alias_dict.pop(k, 0)
    # _ = [print(f'     {k}: {v}') for k,v in alias_dict.items()]
    return list(alias_dict.keys())


def fix_duplicate_aliases(xml_raw, std_name):
    pat = (r' +?<alias id="' + std_name + r'".+?</alias> *?\n')
    result = [r for r in re.finditer(pat, xml_raw, re.S)]
    if len(result) > 1:
        collected_entries = []
        for k, r in enumerate(result):
            lines = r.group().splitlines()
            for s in lines:
                if "<entry_id>" in s and s not in collected_entries:
                    collected_entries.append(s)
        new_alias = []
        for line in result[0].group().splitlines():
            if "entry_id" in line:
                new_alias.extend(collected_entries)
            elif line:
                new_alias.append(line)
        _ = [print(f'   {line}') for line in new_alias]
        result_0 = "\n".join(new_alias)
        for r in reversed(result[1:]):
            span = r.span()
            xml_raw = xml_raw[: span[0]] + xml_raw[span[1]: ]
        span = result[0].span()
        xml_raw = xml_raw[: span[0]] + "\n" + "\n".join(new_alias) + "\n" + xml_raw[span[1]: ]
    else:
        xml_raw = ""
    return xml_raw


def do_the_work(version):
    xml_file = f"{BASE_PATH}{version}/src/cf-standard-name-table.xml"
    xml_raw = handle_input_file(xml_file)

    xml_raw = fix_xml_header(xml_raw)
    xml_raw = update_xsd_link(xml_raw)

    if version == 1:
        xml_raw = fix_v1_datetime(xml_raw)
    elif version == 12:
        xml_raw = fix_v12_duplicate_entry(xml_raw)
    elif version == 71:
        xml_raw = fix_v71_datetime(xml_raw)

    xml_raw = change_to_first_published_tag(xml_raw)
    
    xml_raw = add_last_modified_tag(xml_raw)

    xml_raw = add_conventions(xml_raw)

    duplicate_aliases = find_duplicate_aliases(xml_raw)
    for std_name in duplicate_aliases:
        result = fix_duplicate_aliases(xml_raw, std_name)
        if result:
            xml_raw = result
        else:
            print("    No change")


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

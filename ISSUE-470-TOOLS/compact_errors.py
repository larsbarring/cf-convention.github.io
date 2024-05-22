import re
import argparse


def do_the_work(file_name):
    with open(file_name, "r") as fh:
        in_text = fh.readlines()
    
    err_dict = {}
    for line in in_text:
        line = line.strip()
        if line:
            if line.startswith("../"):
                version = re.search(r"(?<=names/)\d{1,2}(?=/src)", line)
                version = version.group()
            else:
                line = re.sub(r"Line \d+? :  ", "", line)
                if line in err_dict.keys():
                    err_dict[line].append(version)
                else:
                    err_dict[line] = [version]
    out_dict = {}
    for line, version_list in err_dict.items():
        v0 = int(version_list[0])
        version_string = ", ".join(version_list)
        text = f"{version_string} | {line}"
        if v0 in out_dict:
            out_dict[v0].append(text)
        else:
            out_dict[v0] = [text]
    for v0 in range(1, 84):
        text_list = out_dict.pop(v0, "")
        for text in text_list:
            print(text)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="compact_errors",
        description=("\nCompact error lists to show in which version each error occur.")
    )
    parser.add_argument("filename", type=str, metavar="FILENAME",
                        help="Name of error file to process.")
    args = parser.parse_args()

    do_the_work(args.filename)

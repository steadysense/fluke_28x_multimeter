import csv
import sys
import collections

def write_csv(data, head=False, out=None, keys=None):
    """
    writes data as csv
    :param data: dict or list of dicts
    :param head: write csv header or not
    :param out: output to write to, default: sys.stdout
    :param keys: explicit keys to print
    :return: 
    """
    if hasattr(data, "items"):
        data = [data]

    if keys is None:
        keys = set()
        for d in data:
            [keys.add(k) for k in d.keys()]

    writer = csv.DictWriter(out or sys.stdout, keys)
    if head is True:
        writer.writeheader()
    writer.writerows(data)

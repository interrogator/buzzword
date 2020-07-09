#!/usr/bin/env python3

# helper script for making corpus from OCR updates

# python manage.py dumpdata compare.OCRUpdate > ocr.json
# python manage.py dumpdata compare.PDF > pdf.json

import os
import json

with open("ocr.json", "r") as fo:
    ocrs = json.load(fo)

with open("pdf.json", "r") as fo:
    pdfs = json.load(fo)

out_dir = "swiss-law/txt"
os.makedirs(out_dir, exist_ok=True)

for ocr in ocrs:

    # skip other corpora
    if ocr["fields"]["slug"] != "swiss-law":
        continue

    # skip anything but latest timestamp
    same_ocr = [i for i in ocrs if i["fields"]["pdf"] == ocr["fields"]["pdf"]]
    timestamps = sorted([i["fields"]["timestamp"] for i in same_ocr])
    latest = timestamps[-1]
    if ocr["fields"]["timestamp"] != latest:
        continue

    # find correct pdf
    try:
        same_pdf = next(i for i in pdfs if i["fields"]["num"] == ocr["fields"]["pdf"])
    except StopIteration:
        print(f"No OCR for: {ocr['fields']['pdf']}")

    # make name and save
    new_name = same_pdf["fields"]["path"].replace(".pdf", ".txt")
    new_name = os.path.basename(new_name)
    print(f"Doing {new_name}")
    with open(os.path.join(out_dir, new_name), "w") as fo:
        fo.write(ocr["fields"]["text"].strip() + "\n")

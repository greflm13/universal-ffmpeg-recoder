#!/usr/bin/env python3

import os
import json
import datetime
from subprocess import Popen, PIPE
from genson import SchemaBuilder, TypedSchemaStrategy


class CustomDateTime(TypedSchemaStrategy):
    """
    Strategy for date-time formatted strings
    """

    JS_TYPE = "string"
    PYTHON_TYPE = (str,)

    def __init__(self, node_class):
        super().__init__(node_class)
        self.format = "date-time"

    @classmethod
    def match_object(cls, obj):
        try:
            date_time_obj = datetime.datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f%z")
            return isinstance(date_time_obj, datetime.datetime)
        except (TypeError, ValueError) as e:
            return False

    def to_schema(self):
        schema = super().to_schema()
        schema["type"] = self.JS_TYPE
        schema["format"] = self.format
        return schema


class CustomSchemaBuilder(SchemaBuilder):
    """Detects & labels date-time formatted strings"""

    EXTRA_STRATEGIES = (CustomDateTime,)


def generate_filelist(searchpath):
    filelist = []
    with Popen(
        [
            "sudo", "find", searchpath,
            "-name", "*.mkv", "-or",
            "-name", "*.mp4", "-or",
            "-name", "*.avi", "-or",
            "-name", "*.webm", "-or",
            "-name", "*.flv", "-or",
            "-name", "*.mov"
        ],
        stdout=PIPE, stderr=PIPE
    ) as find:
        out, err = find.communicate()
        if err:
            print(f"Error finding files: {err.decode('utf-8')}")
        filelist = out.decode("utf-8").split("\n")
    return filelist


def main():
    searchpath = os.getcwd()
    filelist_path = os.path.join(os.getcwd(), f"{searchpath.replace('/', '_')}-filelist.json")
    builder = CustomSchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}, "$schema": "http://json-schema.org/draft/2020-12/schema"})

    if os.path.exists(filelist_path):
        print(f"Loading file list from {filelist_path}")
        with open(filelist_path, "r", encoding="utf-8") as f:
            filelist = json.loads(f.read())
    else:
        print("Generating file list...")
        filelist = generate_filelist(searchpath)
        with open(filelist_path, "w", encoding="utf-8") as f:
            json.dump(filelist, f)

    print("Generating JSON schema...")
    objects = []
    for file in filelist:
        if not file:
            continue
        print(f"Checking file {file}...")
        p = Popen(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-print_format", "json", os.path.realpath(file)],
            stdout=PIPE, stderr=PIPE
        )
        ffprobe, err = p.communicate()
        if err:
            print(f"Error processing file {file}: {err.decode('utf-8')}")
            continue
        obj = json.loads(ffprobe.decode("utf-8"))
        builder.add_object(obj)
        objects.append(obj)

    print("Writing JSON schema...")
    with open("schema.json", "w", encoding="utf-8") as f:
        f.write(builder.to_json(indent=2))

    print("Writing full JSON...")
    with open("possible.json", "w", encoding="utf-8") as f:
        json.dump(objects, f, indent=2)

    print("Done!")


if __name__ == "__main__":
    main()

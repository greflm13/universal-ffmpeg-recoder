#!/usr/bin/env python3

import os
import json
import datetime

from subprocess import Popen, PIPE

from genson import SchemaBuilder, TypedSchemaStrategy


class CustomDateTime(TypedSchemaStrategy):
    """
    strategy for date-time formatted strings
    """

    JS_TYPE = "string"
    PYTHON_TYPE = (str, type(""))

    # create a new instance variable
    def __init__(self, node_class):
        super().__init__(node_class)
        self.format = "date-time"

    @classmethod
    def match_object(cls, obj):
        super().match_object(obj)
        try:
            date_time_obj = datetime.datetime.strptime(obj, "%Y-%m-%dT%H:%M:%S.%f%z")
            if isinstance(date_time_obj, datetime.datetime):
                return True
            else:
                return False
        except (TypeError, ValueError) as exception:
            print(exception)
            return False

    def to_schema(self):
        schema = super().to_schema()
        schema["type"] = self.JS_TYPE
        schema["format"] = self.format
        return schema


class CustomSchemaBuilder(SchemaBuilder):
    """detects & labels date-time formatted strings"""

    EXTRA_STRATEGIES = (CustomDateTime,)


def generate_filelist(searchpath):
    filelist = []
    with Popen(
        [
            "sudo",
            "find",
            searchpath,
            "-name",
            "*.mkv",
            "-or",
            "-name",
            "*.mp4",
            "-or",
            "-name",
            "*.avi",
            "-or",
            "-name",
            "*.webm",
            "-or",
            "-name",
            "*.flv",
            "-or",
            "-name",
            "*.mov",
        ],
        stdout=PIPE,
        stderr=PIPE,
    ) as find:
        out, err = find.communicate()
        if err:
            print(f"Error finding files: {err.decode('utf-8')}")
        filelist = out.decode("utf-8").split("\n")
    return filelist


def main():
    objects = []
    searchpath = "/"
    filelist_path = os.path.join(os.getcwd(), f"{searchpath.replace('/', '_')}-filelist.json")
    # searchpath = os.getcwd()
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
            f.write(json.dumps(filelist))
    print("Generating JSON schema...")
    for file in filelist:
        print(f"Checking file {file}...")
        p = Popen(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-output_format", "json", os.path.realpath(file)],
            stdout=PIPE,
            stderr=PIPE,
        )
        ffprobe, err = p.communicate()
        obj = json.loads(ffprobe.decode("utf-8"))
        if "format" in obj.keys():
            builder.add_object(obj)
            objects.append(obj)
            print("Writing Object...")
            with open("objects/" + str(hash(obj["format"]["filename"].replace("/", "_"))) + ".json", "w", encoding="utf-8") as f:
                f.write(json.dumps(obj, indent=2))
    print("Writing JSON schema...")
    with open("schema.json", "w", encoding="utf-8") as f:
        f.write(builder.to_json(indent=2))
    print("Writing full JSON...")
    with open("possible.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(objects, indent=2))
    print("Done!")


if __name__ == "__main__":
    main()

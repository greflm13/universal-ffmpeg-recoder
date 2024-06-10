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
    def match_object(self, obj):
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


def main():
    filelist = []
    # searchpath = "/"
    searchpath = os.getcwd()
    builder = CustomSchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})
    print(f"Checking if file {os.getcwd()}/{searchpath.replace('/', '_')}-filelist.json exists")
    if os.path.exists(os.getcwd() + "/" + searchpath.replace("/", "_") + "-filelist.json"):
        with open(os.getcwd() + "/" + searchpath.replace("/", "_") + "-filelist.json", "r", encoding="utf-8") as f:
            filelist = json.loads(f.read())
    else:
        print("Generating file list...")
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
            try:
                files = out.decode("utf-8")
            except:
                print(err)
            for file in files.split("\n"):
                filelist.append(file)
            with open(os.getcwd() + "/" + searchpath.replace("/", "_") + "-filelist.json", "w", encoding="utf-8") as f:
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
        builder.add_object(obj)
    print("Writing JSON schema...")
    with open("schema.json", "w", encoding="utf-8") as f:
        f.write(builder.to_json(indent=2))
    print("Done!")


if __name__ == "__main__":
    main()

# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import shutil
import sys
import tempfile

import ifcopenshell

try:
    import ifcopenshell.express
except:
    pass  # They are using an old version of IfcOpenShell. Gracefully degrade for now.
import behave.formatter.pretty  # Needed for pyinstaller to package it
from bimtester.ifc import IfcStore
from bimtester.ifc import init_ifcstore
from distutils.dir_util import copy_tree

# TODO: refactor when this isn't super experimental
from logging import StreamHandler

import behave.formatter.pretty  # Needed for pyinstaller to package it
from behave.__main__ import main as behave_main

from bimtester.ifc import IfcStore


class TestRunner:
    def __init__(self, ifc_path, schema_path=None, ifc=None):

        # can't load the IFC file if the schema is not loaded before
        if schema_path:
            schema = ifcopenshell.express.parse(schema_path)
            ifcopenshell.register_schema(schema)

        if IfcStore.file is None:
            print("Main IfcStore class variable file was not set. Need to parse the Ifc here.")
            status = init_ifcstore(ifc_path, "IfcBuildingElement")
            print("IfcStore initialisation finished with: {}".format(status))

        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            self.base_path = sys._MEIPASS
        except Exception:
            self.base_path = os.path.dirname(os.path.realpath(__file__))

        self.locale_path = os.path.join(self.base_path, "locale")

    def run(self, args):
        return self.test_feature(args)

    def test_feature(self, args):
        # tmpdir = tempfile.mkdtemp()
        tmpdir = os.path.join(tempfile.gettempdir(), "bimtesterfc")
        # delete tmpdir, if it exists
        if os.path.isdir(tmpdir):
            try:
                shutil.rmtree(tmpdir)
            except OSError as e:
                print("Error deleteing directory: %s - %s." % (e.filename, e.strerror))
                exit()
            os.mkdir(tmpdir)
        features_path = os.path.join(tmpdir, "features")
        steps_path = os.path.join(features_path, "steps")
        report_json = os.path.join(tmpdir, "report.json")
        shutil.copytree(os.path.join(self.base_path, "features"), features_path)
        if os.path.isfile(args["feature"]):
            shutil.copy(args["feature"], features_path)
        elif os.path.isdir(args["feature"]):
            copy_tree(args["feature"], features_path)
        if args["steps"]:
            if os.path.isfile(args["steps"]):
                shutil.copy(args["steps"], steps_path)
            elif os.path.isdir(args["steps"]):
                copy_tree(args["steps"], steps_path)
        args = self.get_behave_args(args, features_path, report_json)

        print(json.dumps(sys.path, indent=4))

        print("The behave args in run")
        print(json.dumps(args, indent=4))
        behave_main(args)
        return report_json  # is returned even if not created, (args["console"] == False)

    def get_behave_args(self, args, features_path, report_json):
        behave_args = [features_path]
        #behave_args.extend(["--define", "localedir={}".format(self.locale_path)])
        if args["advanced_arguments"]:
            behave_args.extend(args["advanced_arguments"].split())
        if args["ifc"]:
            behave_args.extend(["--define", "ifc={}".format(args["ifc"])])
        if args["path"]:
            behave_args.extend(["--define", "path={}".format(args["path"])])
        if args["lang"]:
            behave_args.extend(["--lang={}".format(args["lang"])])
        if not args["console"]:
            # https://github.com/behave/behave/issues/346
            behave_args.extend(["--no-capture", "--format", "json.pretty", "--outfile", report_json])
        return behave_args

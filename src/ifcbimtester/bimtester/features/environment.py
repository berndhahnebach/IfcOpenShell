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

import os
from behave.model import Scenario

from bimtester.ifc import IfcStore
from bimtester.lang import switch_locale
from logfile import append_logfile
from logfile import create_logfile
from zoom_smart_view import add_smartview
from zoom_smart_view import create_zoom_set_of_smartviews


this_path = os.path.dirname(os.path.realpath(__file__))


def before_all(context):

    userdata = context.config.userdata
    context.locale_dir = userdata.get("localedir")

    if context.config.lang:
        switch_locale(context.locale_dir, context.config.lang)

    # continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = False
    # for some Scenarios True would be better, may be dependend on the Scenario name as a workaround

    # context.ifc_path = userdata.get("ifc", "")
    context.ifcfile_basename = os.path.basename(
        os.path.splitext(userdata["ifc"])[0]
    )
    context.outpath = os.path.join(this_path, "..")
    context.create_log = True
    context.create_smartview = True

    if context.create_log is True:
        # set up log file
        context.thelogfile = os.path.join(
            context.outpath,
            context.ifcfile_basename + ".log"
        )
        create_logfile(
            context.thelogfile,
            context.ifcfile_basename,
        )

    # we have to use a dict to preserve the contents
    # https://stackoverflow.com/a/67606164
    context.skip_all_other_features = {"skip": False}

    # elements count container
    context.elecount_data = []


def after_all(context):
    import json
    # print(json.dumps(context.elecount_data, indent=4, ensure_ascii=False))
    import yaml
    yf = open(os.path.join(context.outpath, "elecount.yaml"), "w", encoding="utf-8")
    # yaml schreibt strings ohne quotes, heisst 1.0.0 wird dann als float wieder eingelesen
    # daher alle werte mit quote schreiben ... default_style='"'
    # https://stackoverflow.com/a/69850618
    yaml.safe_dump(context.elecount_data, yf, default_flow_style=False, allow_unicode=True, default_style='"')
    yaml.safe_dump(context.elecount_data, yf, default_flow_style=False, allow_unicode=True)
    yf.close()
    print("---E N D E---")


def before_feature(context, feature):

    print("Start feature: {}".format(feature.name))

    # https://github.com/IfcOpenShell/IfcOpenShell/issues/1910#issuecomment-989732600
    # messages language, parsed by behaves lang argument
    print("Messages language: {}".format(context.config.lang))
    # features file language, set in feature files first line
    # html report will use this too
    print("Features language: {}".format(context.feature.language))

    # if messages lang is not set use features lang
    if context.config.lang == "" or context.config.lang is None:
        context.config.lang = context.feature.language
        print("Switch messages language to: {}".format(context.config.lang))
        switch_locale(context.locale_dir, context.config.lang)

    # TODO: refactor zoom smart view support into a decoupled module
    if context.create_smartview is True:
        smartview_name = context.ifcfile_basename + "_" + feature.name
        context.smview_file = os.path.join(
            context.outpath,
            smartview_name + ".bcsv"
        )
        # print("SmartView file: {}".format(context.smview_file))
        create_zoom_set_of_smartviews(
            context.smview_file,
            smartview_name,
        )

    # print(context.skip_all_other_features)
    if context.skip_all_other_features["skip"] is True:
        feature.skip("Due to a failing feature all other features are skipped.")
        return
        # https://stackoverflow.com/a/42721605


def after_feature(context, feature):
    print("After feature: {} --> {}".format(feature.name, feature.status))
    # print(str(feature.status))
    # print(context.skip_all_other_features)
    # TODO: mit userdata bei start bimtester uebergeben
    #
    # Wenn allplan feature nicht erfuellt ist, sofort abbruch
    #
    features_to_continue = [
        "681_Weitere",
        # "682_Modellpruefungen_FBJ_Weitere_allplan",
        "683_Modellpruefungen_FBJ_Weitere_bimtester",
        "684_Modellpruefungen_FBJ_Geomqualitaet_bimtester",
        "686_Modellpruefungen_TRW_Weitere_bimtester",
        "891_Projektpruefungen_Allg",
        # "892_Projektpruefungen_TRW_allplan",
        "893_Projektpruefungen_TRW_bimtester",
        # "899_Projektpruefungen_Name",
    ]
    if str(feature.status) == "Status.failed" and feature.name not in features_to_continue:
        # print("set to skip all other features")
        context.skip_all_other_features["skip"] = True
    # print(context.skip_all_other_features)


# workaround to finish specific scenarios
finish_scenario = [
    "Geometrieabmessungen Mauerwerk",
    "Geometriefehler",
    "Geometriequalität",
    "Regextests",
]
def before_scenario(context, scenario):
    # print(scenario.name)
    if scenario.name in finish_scenario:
        Scenario.continue_after_failed_step = True
    context.open_step_counter = 0


def after_scenario(context, scenario):
    # print(scenario.name)
    if scenario.name in finish_scenario:
        Scenario.continue_after_failed_step = False
    context.open_step_counter = 0


def before_step(context, step):
    # print("{}".format(step.name))
    context.open_step_counter += 1

def after_step(context, step):

    if step.status == "failed" and context.create_log is True:
        append_logfile(context, step)

    # Workaround: introduce a open_step_counter
    # only if the counter of not finished steps is 1 create a smart view
    # see https://github.com/behave/behave/issues/992
    # the German step starts, calls the english step
    # the English starts, fails, closes,
    # than the German fails and closes
    # thus both steps fail, thus both are in the smart view file
    if (
        step.status == "failed"
        and context.create_smartview is True
        and hasattr(context, "falseguids")
        and context.open_step_counter == 1
    ):
        # print("\nDBG: {}, {}\n".format(step.name, context.open_step_counter))
        # print(context.falseguids)
        add_smartview(
            context.smview_file,
            step.name,
            context.falseguids
        )

    # elecount
    if hasattr(context, "elemcount"):
        count = context.elemcount
    else:
        count = None
    context.elecount_data.append([step.name, count])
    # zuordnung step json und step elecount anstatt ueber name auch mit location moeglich
    # siehe json und dort den location string
    # damit keine umlaute etc ... 
    # print(step.location)

    context.open_step_counter -= 1
    print("Finished step: {}".format(step.name))

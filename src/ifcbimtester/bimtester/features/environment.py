import os

from behave.model import Scenario

from logfile import create_logfile
from logfile import append_logfile
from zoom_smart_view import create_zoom_set_of_smartviews
from zoom_smart_view import add_smartview

from bimtester.ifc import IfcStore
from bimtester.lang import switch_locale


this_path = os.path.dirname(os.path.realpath(__file__))


def before_all(context):
    userdata = context.config.userdata
    context.ifcbasename = os.path.basename(
        os.path.splitext(userdata["ifc"])[0]
    )

    if context.config.lang:
        switch_locale(userdata.get("localedir"), context.config.lang)

    continue_after_failed = userdata.getbool("runner.continue_after_failed_step", True)
    Scenario.continue_after_failed_step = continue_after_failed

    # TODO: refactor smart view support into a decoupled module
    # context.ifc_path = userdata.get("ifc", "")
    # context.ifc_basename = os.path.basename(
    #     os.path.splitext(context.ifc_path)[0]
    # )

    context.outpath = os.path.join(this_path, "..")

    # set up log file
    context.thelogfile = os.path.join(
        context.outpath,
        context.ifcbasename + ".log"
    )
    create_logfile(
        context.thelogfile,
        context.ifcbasename,
    )


def before_feature(context, feature):
    print("Start feature: {}".format(feature.name))

    # set up smart view file
    smartview_name = context.ifcbasename + "_" + feature.name
    context.smview_file = os.path.join(
        context.outpath,
        smartview_name + ".bcsv"
    )
    # print("SmartView file: {}".format(context.smview_file))
    create_zoom_set_of_smartviews(
        context.smview_file,
        smartview_name,
    )


def after_step(context, step):

    if step.status == "failed":

        # append log file
        append_logfile(context, step)

        # extend smart view
        if hasattr(context, "falseguids"):
            # print(context.falseguids)

            add_smartview(
                context.smview_file,
                step.name,
                context.falseguids
            )
    print("Finished step: {}".format(step.name))

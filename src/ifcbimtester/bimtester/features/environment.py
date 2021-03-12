import os

from behave.model import Scenario

from logfile import create_logfile
from logfile import append_logfile
from zoom_smart_view import append_zoom_smartview
from zoom_smart_view import create_zoom_smartview


this_path = os.path.dirname(os.path.realpath(__file__))


def before_all(context):

    # get from userdata
    userdata = context.config.userdata
    context.localedir = userdata.get("localedir")
    context.ifcfile = userdata["ifcfile"]
    context.ifcbasename = os.path.basename(
        os.path.splitext(context.ifcfile)[0]
    )

    # do not break after a failed scenario
    # https://community.osarch.org/discussion/comment/3328/#Comment_3328
    continue_after_failed = userdata.getbool(
        "runner.continue_after_failed_step", True
    )
    Scenario.continue_after_failed_step = continue_after_failed

    # keep out path
    context.outpath = os.path.join(this_path, "..")

    # since bimtesterfc directory in tmp is removed on every run
    # neither log file nor sm file does need to be explicit removed first

    # set up log file
    context.thelogfile = os.path.join(
        context.outpath,
        context.ifcbasename + ".log"
    )
    create_logfile(
        context.thelogfile,
        context.ifcbasename,
    )

    # set up failure information file
    context.thefailurefile = os.path.join(
        "//fbj.local", "dats", "Daten FBJ", "04 Briefkasten", "BHA", "BIMTesting", "failure.txt"
    )
    failurefile = open(context.thefailurefile, "a")
    failurefile.close()

    create_logfile(
        context.thelogfile,
        context.ifcbasename,
    )


    # there might be a better way to skip after a failure of a certain scenario
    # set skip_all_bimtesting to False
    context.skip_all_bimtesting = False


def after_all(context):
    pass
    # print(context.__dir__())


def before_feature(context, feature):
    print("Start feature: {}".format(feature.name))

    # set up smart view file
    smartview_name = context.ifcbasename + "_" + feature.name
    context.smview_file = os.path.join(
        context.outpath,
        smartview_name + ".bcsv"
    )
    # print("SmartView file: {}".format(context.smview_file))
    create_zoom_smartview(
        context.smview_file,
        smartview_name,
    )


def after_feature(context, feature):
    if feature.name == "Basisdaten" and feature.status == "failed":
        failurefile = open(context.thefailurefile, "a")
        failurefile.write("{}\n".format(context.ifcbasename))
        failurefile.close()
    print("Finished feature: {}".format(feature.name))


"""
# in den steps das skip implementiert, ifc exporter allplan und ifc schema type
# https://behave.readthedocs.io/en/stable/new_and_noteworthy_v1.2.5.html?highlight=skip#exclude-feature-scenario-at-runtime
def before_scenario(context, scenario):
    # some how the variable context.skip_all_bimtesting does not keep its value ... 
    # the scope of the context scenario is only the scenario
    # https://behave.readthedocs.io/en/stable/context_attributes.html?highlight=after_all#user-attributes
    # print(context.skip_all_bimtesting)
    # if context.skip_all_bimtesting is True:
    #     scenario.skip()
    print(scenario.continue_after_failed_step)

def after_scenario(context, scenario):
    if scenario.name == "Bereitstellen von IFC-Daten":
        if scenario.status == "failed":
            print("Found failed Szenario: 'Bereitstellen von IFC-Daten', all other should be skiped")
            context.skip_all_bimtesting = True
            scenario.continue_after_failed_step = False
"""


def after_step(context, step):

    if step.status == "failed":

        # append log file
        append_logfile(context, step)

        # extend smart view
        if hasattr(context, "falseguids"):
            # print(context.falseguids)

            append_zoom_smartview(
                context.smview_file,
                step.name,
                context.falseguids
            )

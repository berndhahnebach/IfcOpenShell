from behave import step

import ifcdata_methods as idm
from utils import switch_locale


the_lang = "de"


@given('Die IFC-Datei wurde durch einen Startparameter zur Verfügung gestellt')
def step_impl(context):
    switch_locale(context.localedir, the_lang)
    idm.provide_ifcfile_by_argument(context)


@step('Die IFC-Daten müssen das "{schema}" Schema benutzen')
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    idm.has_ifcdata_specific_schema(context, schema)


# TODO use language system
from utils import IfcFile
@step('Die IFC-Datei wurde mit dem neuen Allplan Exporter erstellt. Das heisst der data header description hot folgenden Inhalt: "{target_header_file_description}"')
def step_impl(context, target_header_file_description):

    actual_header_file_description = str(IfcFile.get().wrapped_data.header.file_description.description)
    if actual_header_file_description == target_header_file_description:
        passed = True
    else:
        passed = False
    # print(len(actual_header_file_description))
    # print(actual_header_file_description)
    # print(len(target_header_file_description))
    # print(target_header_file_description)

    if passed is False:
        # -- SKIP: Remaining steps in current feature.
        context.feature.skip("Alter Allplan IFC-Exporter, Abbruch.")

    assert  passed , (
        "Die IFC-Datei wurde nicht mit dem neuen Allplan Exporter erstellt. File description header IST: {} != {}: File description header SOLL."
        .format(actual_header_file_description, target_header_file_description)
    )

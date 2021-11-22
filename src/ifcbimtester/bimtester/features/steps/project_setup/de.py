from behave import step


@step('Die IFC-Daten müssen das "{schema}" Schema benutzen')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('Die Globale Identifikationskennung (Globally Unique Identifier = GUID) des Projektes ist "{guid}"')
def step_impl(context, guid):
    context.execute_steps(f'* The project must have an identifier of "{guid}"')


@step('Der Name, die Abkürzung oder die Kurzkennung des Projektes ist "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')


# TODO use language system
@step('Die IFC-Datei wurde mit dem neuen Allplan Exporter erstellt. Das heisst der data header description hot folgenden Inhalt: "{target_header_file_description}"')
def step_impl(context, target_header_file_description):
    return
    actual_header_file_description = str(IfcStore.file.wrapped_data.header.file_description.description)
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

    assert passed, (
        "Die IFC-Datei wurde nicht mit dem neuen Allplan Exporter erstellt. File description header IST: {} != {}: File description header SOLL."
        .format(actual_header_file_description, target_header_file_description)
    )

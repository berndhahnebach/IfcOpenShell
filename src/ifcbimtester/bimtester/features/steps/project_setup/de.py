from behave import step


@step('Die IFC-Daten müssen das "{schema}" Schema benutzen')
def step_impl(context, schema):
    context.execute_steps(f'* IFC data must use the "{schema}" schema')


@step('Die IFC-Daten haben genau "{unit_count}" Einheit(en) des Einheitentypes "{unit_type}"')
def step_impl(context, unit_count, unit_type):
    context.execute_steps(f'* The ifc data uses exact "{unit_count}" units of unit type "{unit_type}"')

@step('Eine "{unit_type}" hat den Typ "{ifc_type}" und den Namen "{unit_name}"')
def step_impl(context, unit_type, ifc_type, unit_name):
    context.execute_steps(f'* A "{unit_type}" is of type "{ifc_type}" and is named "{unit_name}"')

@step('Eine "{unit_type}" mit dem Namen "{unit_name}" hat den Prefix ""')
def step_impl(context, unit_type, unit_name, unit_prefix):
    context.execute_steps(f'* A "{unit_type}" named "{unit_name}" uses the prefix "{unit_prefix}"')

@step('Die Globale Identifikationskennung (Globally Unique Identifier = GUID) des Projektes ist "{guid}"')
def step_impl(context, guid):
    context.execute_steps(f'* The project must have an identifier of "{guid}"')


@step('Der Name, die Abkürzung oder die Kurzkennung des Projektes ist "{value}"')
def step_impl(context, value):
    context.execute_steps(f'* The project name, code, or short identifier must be "{value}"')



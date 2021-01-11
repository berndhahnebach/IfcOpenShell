from behave import step

import ifcdata_methods as idm
from utils import switch_locale


the_lang = "it"


@step("The IFC file "{file}" must be provided")
def step_impl(context, schema):
    switch_locale(context.localedir, the_lang)
    idm.has_ifcdata_schema(context, schema)

from behave import step

from utils import assert_attribute
from utils import IfcFile
from utils import switch_locale


the_lang = "it"


"""
# TODO the next line needs translation
@step("The project must have an identifier of {guid}")
def step_impl(context, guid):
    switch_locale(context.localedir, the_lang)
    assert_attribute(IfcFile.get().by_type("IfcProject")[0], "GlobalId", guid)
"""


@step('Il nome del progetto, codice o identificatore breve deve essere "{value}"')
def step_impl(context, value):
    switch_locale(context.localedir, the_lang)
    assert_attribute(IfcFile.get().by_type("IfcProject")[0], "Name", value)

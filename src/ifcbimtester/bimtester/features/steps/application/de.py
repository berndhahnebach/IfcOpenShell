from behave import step
import ifcopenshell.util.element as eleutils

from behave import step
from behave import use_step_matcher

from bimtester import util
from bimtester.ifc import IfcStore
from bimtester.lang import _


@step('Die IFC-Datei wurde mit dem neuen Allplan Exporter erstellt. Das heisst der data header description hot folgenden Inhalt: "{target_header_file_description}"')
def step_impl(context, target_header_file_description):
    context.execute_steps(f'* The ifc file has been exported with the new Allplan ifc exporter. This means the ifc file data header description is as follows: "{target_header_file_description}"')

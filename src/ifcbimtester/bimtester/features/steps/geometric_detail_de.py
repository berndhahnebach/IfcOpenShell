from behave import step

import geometric_detail_methods as gdm
from utils import switch_locale


the_lang = "de"


@step("Alle {ifc_class} Bauteile müssen eine geometrische Repräsentation der Klasse {representation_class} verwenden")
def step_impl(context, ifc_class, representation_class):
    switch_locale(context.localedir, the_lang)
    gdm.eleclass_has_geometric_representation_of_specific_class(
        context,
        ifc_class,
        representation_class
    )


@step("Alle {ifc_class} Bauteile müssen geometrische Repräsentationen ohne Fehler haben")
def step_impl(context, ifc_class):
    switch_locale(context.localedir, the_lang)
    gdm.eleclass_has_geometric_representation_without_errors(context, ifc_class)

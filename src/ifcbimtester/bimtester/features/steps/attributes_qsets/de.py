from behave import step


@step('Alle "{ifc_class}" Bauteile haben den Geometriewert QuantitySet.Quantity "{aqset}.{aquantity}" angehängt')
def step_impl(context, ifc_class, aqset, aquantity):
    context.execute_steps(f'* All "{ifc_class}" elements have a "{aqset}.{aquantity}" quantity')


@step('Alle "{ifc_class}" Bauteile aus dem Material "{material}" haben ausschliesslich eine "{geometryproperty}" der Werte "{valuerange}" Meter')
def step_impl(context, ifc_class, material, geometryproperty, valuerange):
    context.execute_steps(f'* All "{ifc_class}" elements made from material "{material}" do only have the "{geometryproperty}" value range "{valuerange}" meter')


@step('Alle "{ifc_classes_string}" Bauteile haben mindestens ein Quantity in einem Mengen-PSet exportiert (IFC-Export mit Mengen)')
def step_impl(context, ifc_classes_string):
    context.execute_steps(f'* All "{ifc_classes_string}" elements have at least one quantity in a quantity pset exported (IFC-export with quantities)')

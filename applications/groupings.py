def by_wmclass_group(a, b):
    return a.get_class_group_name() == b.get_class_group_name()

def by_wmclass_instance(a, b):
    return a.get_class_instance_name() == b.get_class_instance_name()

def by_icon_name(a, b):
    return a.get_icon_name() == b.get_icon_name() and a.has_icon_name() and b.has_icon_name()
import CosNaming


_MAX_NAMES = 1000


def _str2nc(name):
    return [CosNaming.NameComponent(id=name, kind='')]


def _nc2str(nc):
    return nc[0].id


class NameService():

    def __init__(self, orb, namespace='TaskContexts'):
        self.orb = orb
        self.namespace = namespace
        root_context = self.orb.resolve_initial_references(
            'NameService')._narrow(CosNaming.NamingContext)
        self.context = root_context.resolve(_str2nc(namespace))

    def names(self):
        blist, _ = self.context.list(_MAX_NAMES)
        return [_nc2str(binding.binding_name) for binding in blist]

    def get(self, name):
        return self.context.resolve(_str2nc(name))

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
        self.context = self._resolve_context(self.namespace)

    def _resolve_context(self, namespace):
        context = None
        try:
            root_context = self.orb.resolve_initial_references(
                'NameService')._narrow(CosNaming.NamingContext)
            context = root_context.resolve(_str2nc(namespace))
        except CosNaming.NamingContext.NotFound:
            pass
        return context

    def names(self):
        if not self.context:
            self.context = self._resolve_context(self.namespace)
        if not self.context:
            return []
        blist, _ = self.context.list(_MAX_NAMES)
        return [_nc2str(binding.binding_name) for binding in blist]

    def get(self, name):
        if not self.context:
            self.context = self._resolve_context(self.namespace)
        if not self.context:
            return None
        return self.context.resolve(_str2nc(name))

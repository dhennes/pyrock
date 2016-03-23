import sys

from omniORB import CORBA
import CosNaming

import RTT
import RTT__POA


orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
poa = orb.resolve_initial_references("RootPOA")


class TaskContext(RTT__POA.corba.CTaskContext):

    def getName(self):
        print 'getName triggered'
        return 'hello'

tc = TaskContext()
poa.activate_object(tc)

# bind task to context
root_context = orb.resolve_initial_references(
    'NameService')._narrow(CosNaming.NamingContext)
context = root_context.resolve([CosNaming.NameComponent("TaskContexts", "")])
try:
    context.bind([CosNaming.NameComponent('test', '')], tc._this())
except CosNaming.NamingContext.AlreadyBound:
    context.rebind([CosNaming.NameComponent('test', '')], tc._this())

print orb.object_to_string(tc._this())

poa._get_the_POAManager().activate()
orb.run()

#poaManager = poa._get_the_POAManager()
# poaManager.activate()

#RTT.corba.CConnPolicy(type=CData, init=False, lock_policy=CLockFree, pull=False, size=1, transport=1, data_size=1, name_id='test')

# http://www.orocos.org/stable/documentation/rtt/v2.x/api/html/DataFlowI_8cpp_source.html

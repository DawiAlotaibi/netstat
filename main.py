import NetworkHelper
import sys
# TODO:
#   Add a user friendly interface to use the networkHelper package.
nw_helper = NetworkHelper.NetWorkHelper()
# for k, v in nw_helper.getProcesses(args=["n"]).items():
#     print(f"Process {v} PID {k}")

if len(sys.argv) <= 1:
    # print(nw_helper.getProcesses(args=["-n","-pid"]))
    print(nw_helper.getNameById("7332"))
    print(nw_helper.getBandwidthById("7332"))
else:  # just add args later
    for arg in sys.argv[1:]:
        print(arg)
nw_helper.getNames()
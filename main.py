import NetworkHelper
import sys
# TODO:
#   Add a user friendly interface to use the networkHelper package.
nw_helper = NetworkHelper.NetWorkHelper()
# for k, v in nw_helper.getProcesses(args=["n"]).items():
#     print(f"Process {v} PID {k}")

if len(sys.argv) <= 1:
    #print(nw_helper.getProcesses())
    # print(nw_helper.getNameById(5540))
    print(nw_helper.getBandwidthById(20128,interval=15,args=["-b"],elapsed=True))
    #print(nw_helper.getAllBandwidth(interval=1,print_output=False))
    # print(nw_helper.getProcesses(args=["-n","-pid"]))
    #
else:  # just add args later
    for arg in sys.argv[1:]:
        print(arg)






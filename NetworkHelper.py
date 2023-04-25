"""


This program is a Python script that helps in getting information about network usage for processes running on the
system. It uses the subprocess and psutil modules to run commands and interact with the system respectively.

"""

import concurrent.futures
import json
import subprocess
import time

import psutil

"""

The program defines a custom exception class, TooManyArgsError and insufficientArgsError, which can be raised when 
the number of arguments passed to a method is not as expected. 

"""


class TooManyArgsError(Exception):
    pass


class insufficientArgsError(Exception):
    pass


# TODO:
#   Make The programing more generic and dynamic.
#   getBandwidth() Method to calculate for multiply PID's and sort them by highest usage.
class NetWorkHelper:
    """

    The program defines a NetWorkHelper class with several methods for getting network-related information.

    """

    def __init__(self):
        netstatOutput = "no"
        process_name = ""

    # TODO:
    #   Return different outputs for different args for the netstat command.
    @staticmethod
    def netstat():
        """

        This method gets the result of running the netstat command and returns it as a string.

        :return: A string containing the output of the netstat command.

        """

        returnString = ""
        # this is the executable command for the netstat.
        # The args -no are used to show the PID and to stop the run.
        process = subprocess.Popen(['netstat', '-no'], stdout=subprocess.PIPE)
        while True:
            output = process.stdout.readline()
            if output == b'' and process.poll() is not None:
                break
            returnString = returnString + output.decode("UTF-8").strip() + "\n"
        return returnString.strip()

    @staticmethod
    def getNames(pidList, nameList=None):
        """

        This method takes a list of process ids and returns a dictionary containing the names of the corresponding processes.

        :param nameList: (dict) An optional dictionary to store the list in.
        :param pidList: (list) A list of process ids to retrieve names for.
        :return: A dictionary with the process ids as keys and the corresponding process names as values.

        """
        if nameList is None:
            nameList = {}
        for pid in pidList:
            try:
                process = psutil.Process(int(pid))
                process_name = process.name()
                nameList[pid] = process_name
            except Exception as e:
                print(f"Something went wrong: {e} check netstat output.")

        return nameList

    @staticmethod
    def getNameById(pid):
        """

        This method takes a process id and returns the name of the corresponding process.

        :param pid: (int) The process id to retrieve the name for.

        :return: The name of the process as a string.

        """
        try:
            process = psutil.Process(int(pid))
            return process.name()
        except Exception as e:
            print(f"Something went wrong: {e} check process Id.")

    # TODO:
    #   Sort and filter processes.
    def getProcesses(self, netstatOutput="no", args=None):
        """

        This method gets the process ids and/or names and ids or the normal netstat output if there are no arguments.

        :param netstatOutput: (str): Optional output of previews netstat command.
        :param args: (list) A list of arguments that could be either:
            -name or -n: to show the PID and the names of the processes.
            -PID: to show just the PID of the processes.

        :return : (str) returns the normal netstat command if there are no arguments.


        """

        returnMsg = ""
        if args is None:
            args = []
        if not isinstance(args, list):
            raise TypeError("args must be a list")
        if netstatOutput == "no":
            netstatOutput = self.netstat()
        if not args:
            # TODO:
            #   Return netstatoutput when arg is "-o" or "-output" other idk what to return.
            return netstatOutput

        else:
            pidList = []
            nameList = {}
            for line in netstatOutput.splitlines():
                if line.startswith("TCP") or line.startswith("UDP"):
                    words = line.split()
                    pidList.append(words[-1])
            if len(args) > 1:
                for arg in args:
                    if arg == "-name" or arg == "-n":
                        returnMsg = returnMsg + f" for the argument, {arg}:\n" \
                                    + json.dumps(self.getNames(pidList, nameList)) + "\n\n"
                    elif arg == "-pid":
                        returnMsg = returnMsg + f" for the argument, {arg}:\n" + \
                                    ", ".join(pidList) + "\n\n"
                if returnMsg == "no":
                    return None
                else:
                    return returnMsg
            else:
                if "-name" in args or "-n" in args:
                    return self.getNames(pidList, nameList)
                elif "-pid" in args:
                    return pidList
                else:
                    print(
                        "Invalid argument. Please use one of the following: -name/-n, -pid.")

    @staticmethod
    def calcBandwidthInterval(pid, interval):
        """

        This method takes a process id and returns the total bytes sent and received by the process over an elapsed time.

        :param pid: (int) The process id to calculate it's bandwidth.

        :param interval: (int) The interval or the time to elapse

        :return : (int) The elapsed time for the calculation, (int) The total bytes sent in the interval, (int) the
        total bytes received in the interval.


        """
        try:
            process = psutil.Process(int(pid))

            start_io_counters = psutil.net_io_counters()
            start_time = time.time()

            # Wait for some time to elapse
            time.sleep(interval)

            end_io_counters = psutil.net_io_counters()
            end_time = time.time()

            elapsed_time = end_time - start_time
            total_bytes_sent = end_io_counters.bytes_sent - start_io_counters.bytes_sent
            total_bytes_received = end_io_counters.bytes_recv - start_io_counters.bytes_recv
            return elapsed_time, total_bytes_sent, total_bytes_received
        except ValueError:
            print("The PID Must Be an integer.")

    # TODO:
    #   Return the calculations instead of just printing it.
    #   Return Total bytes sent and received in interval or per second.
    def getBandwidthById(self, pid, interval=10, elapsed=True, args=None, print_output=True):
        """

        This method gets the bandwidth for a single pid and optionally prints it or just returns is.

        :param pid: (int) The process id to calculate it's bandwidth.
        :param interval: (int) The interval or the time to elapse.
        :param elapsed: (bool) True if you want elapsed, false if second by second.
        :param args: (list) A list of arguments that could be either:
            -byte or -b: to show the results in bytes/s.
            -kilobyte or -k: to show the results in kilobyte/s.
            -megabyte or -m: to show the results in megabyte/s.
            -gigabyte or -g to show the results in gigabyte/s.
        :param print_output: (bool) True if you want to print the output, false if not.

        :return : (int) The pid , (int) The total bytes sent in a second, (int) the
        total bytes received in a second.


        """
        if args is None:
            args = ["-byte"]
        if not isinstance(args, list):
            raise TypeError("args must be a list")
        returnMessage = ""
        totalMessage = ""
        if elapsed:
            if "-byte" in args or "-b" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                bytes_per_second_sent = total_bytes_sent / elapsed_time
                bytes_per_second_received = total_bytes_received / elapsed_time

                total_bytes_sent = (
                    f'{total_bytes_sent:.3f}' if f'{total_bytes_sent:.3f}' != '0.000' else total_bytes_sent)
                total_bytes_received = (
                    f'{total_bytes_received:.3f}' if f'{total_bytes_received:.3f}' != '0.000' else total_bytes_received)
                bytes_per_second_sent = (
                    f'{bytes_per_second_sent:.3f}' if f'{bytes_per_second_sent:.3f}' != '0.000' else bytes_per_second_sent)
                bytes_per_second_received = (
                    f'{bytes_per_second_received:.3f}' if f'{bytes_per_second_received:.3f}' != '0.000' else bytes_per_second_received)

                if print_output:
                    print(
                        f"Process {pid} sent {bytes_per_second_sent} bytes/s and received {bytes_per_second_received} bytes/s. With a Total of {total_bytes_sent} bytes sent, and "
                        f" {total_bytes_received} bytes received, over approximately {interval} seconds.")
                return pid, total_bytes_sent, total_bytes_received
            elif "-kilobyte" in args or "-k" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                kilobytes_sent = total_bytes_sent / 1024
                kilobytes_received = total_bytes_received / 1024
                kilobytes_per_second_sent = kilobytes_sent / elapsed_time
                kilobytes_per_second_received = kilobytes_received / elapsed_time

                kilobytes_sent = (
                    f'{kilobytes_sent:.3f}' if f'{kilobytes_sent:.3f}' != '0.000' else kilobytes_sent)
                kilobytes_received = (
                    f'{kilobytes_received:.3f}' if f'{kilobytes_received:.3f}' != '0.000' else kilobytes_received)
                kilobytes_per_second_sent = (
                    f'{kilobytes_per_second_sent:.3f}' if f'{kilobytes_per_second_sent:.3f}' != '0.000' else kilobytes_per_second_sent)
                kilobytes_per_second_received = (
                    f'{kilobytes_per_second_received:.3f}' if f'{kilobytes_per_second_received:.3f}' != '0.000' else kilobytes_per_second_received)

                if print_output:
                    print(
                        f"Process {pid} sent {kilobytes_per_second_sent} KB/s and received {kilobytes_per_second_received} KB/s. With a Total of {kilobytes_sent} KB sent, and "
                        f" {kilobytes_received} KB received, over approximately {interval} seconds.")
                return pid, kilobytes_sent, kilobytes_received

            elif "-megabyte" in args or "-m" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                megabytes_sent = total_bytes_sent / (1024 * 1024)
                megabytes_received = total_bytes_received / (1024 * 1024)
                megabytes_per_second_sent = megabytes_sent / elapsed_time
                megabytes_per_second_received = megabytes_received / elapsed_time

                megabytes_sent = (
                    f'{megabytes_sent:.3f}' if f'{megabytes_sent:.3f}' != '0.000' else megabytes_sent)
                megabytes_received = (
                    f'{megabytes_received:.3f}' if f'{megabytes_received:.3f}' != '0.000' else megabytes_received)
                megabytes_per_second_sent = (
                    f'{megabytes_per_second_sent:.3f}' if f'{megabytes_per_second_sent:.3f}' != '0.000' else megabytes_per_second_sent)
                megabytes_per_second_received = (
                    f'{megabytes_per_second_received:.3f}' if f'{megabytes_per_second_received:.3f}' != '0.000' else megabytes_per_second_received)

                if print_output:
                    print(
                        f"Process {pid} sent {megabytes_per_second_sent} MB/s and received {megabytes_per_second_received} MB/s. With a Total of {megabytes_sent} MB sent, and"
                        f" {megabytes_received} MB received, over approximately {interval} seconds.")
                return pid, megabytes_sent, megabytes_received

            elif "-gigabyte" in args or "-g" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                gigabytes_sent = total_bytes_sent / (1024 * 1024 * 1024)
                gigabytes_received = total_bytes_received / (1024 * 1024 * 1024)
                gigabytes_per_second_sent = gigabytes_sent / elapsed_time
                gigabytes_per_second_received = gigabytes_received / elapsed_time

                gigabytes_sent = (
                    f'{gigabytes_sent:.3f}' if f'{gigabytes_sent:.3f}' != '0.000' else gigabytes_sent)
                gigabytes_received = (
                    f'{gigabytes_received:.3f}' if f'{gigabytes_received:.3f}' != '0.000' else gigabytes_received)
                gigabytes_per_second_sent = (
                    f'{gigabytes_per_second_sent:.3f}' if f'{gigabytes_per_second_sent:.3f}' != '0.000' else gigabytes_per_second_sent)
                gigabytes_per_second_received = (
                    f'{gigabytes_per_second_received:.3f}' if f'{gigabytes_per_second_received:.3f}' != '0.000' else gigabytes_per_second_received)

                if print_output:
                    print(
                        f"Process {pid} sent {gigabytes_per_second_sent} GB/s and received {gigabytes_per_second_received} GB/s. With a Total of {gigabytes_sent} GB sent, and "
                        f" {gigabytes_received} GB received, over approximately {interval} seconds.")
                return pid, gigabytes_sent, gigabytes_received

            else:
                print(
                    "Invalid argument. Please use one of the following: -byte/-b, -kilobyte/-k, -megabyte/-m, "
                    "-gigabyte/-g.")

        elif not elapsed:
            total_bytes_sent, total_bytes_received = 0, 0
            for i in range(interval):
                elapsed_time,bytes_sent, bytes_received = self.calcBandwidthInterval(pid,1)
                total_bytes_sent += bytes_sent
                total_bytes_received += bytes_received
                elapsed_time = i + 1
                bytes_per_second_sent = total_bytes_sent / elapsed_time
                bytes_per_second_received = total_bytes_received / elapsed_time
                if "-byte" in args or "-b" in args:
                    bytes_per_second_sent = (
                        f'{bytes_per_second_sent:.3f}' if f'{bytes_per_second_sent:.3f}' != '0.000' else bytes_per_second_sent)
                    bytes_per_second_received = (
                        f'{bytes_per_second_received:.3f}' if f'{bytes_per_second_received:.3f}' != '0.000' else bytes_per_second_received)

                    if print_output:
                        print(
                            f"Process {pid} sent {bytes_per_second_sent} bytes/s and received {bytes_per_second_received} bytes/s. {elapsed_time} seconds elapsed.")
                    returnMessage = returnMessage + f"Process {pid} sent {bytes_per_second_sent} bytes/s and received {bytes_per_second_received} bytes/s. {elapsed_time} seconds elapsed.\n"
                    totalMessage = f"With a Total of {total_bytes_sent} Bytes sent, and  {total_bytes_received} Bytes received, over approximately {interval} seconds. "
                elif "-kilobyte" in args or "-k" in args:
                    kilobytes_sent = total_bytes_sent / 1024
                    kilobytes_received = total_bytes_received / 1024
                    kilobytes_per_second_sent = kilobytes_sent / elapsed_time
                    kilobytes_per_second_received = kilobytes_received / elapsed_time

                    kilobytes_per_second_sent = (
                        f'{kilobytes_per_second_sent:.3f}' if f'{kilobytes_per_second_sent:.3f}' != '0.000' else kilobytes_per_second_sent)
                    kilobytes_per_second_received = (
                        f'{kilobytes_per_second_received:.3f}' if f'{kilobytes_per_second_received:.3f}' != '0.000' else kilobytes_per_second_received)

                    print(
                        f"Process {pid} sent {kilobytes_per_second_sent} KB/s and received {kilobytes_per_second_received} KB/s. {elapsed_time} seconds elapsed.")
                    returnMessage = returnMessage + f"Process {pid} sent {kilobytes_per_second_sent} KB/s and received {kilobytes_per_second_received} KB/s. {elapsed_time} seconds elapsed.\n"

                elif "-megabyte" in args or "-m" in args:
                    megabytes_sent = total_bytes_sent / (1024 * 1024)
                    megabytes_received = total_bytes_received / (1024 * 1024)
                    megabytes_per_second_sent = megabytes_sent / elapsed_time
                    megabytes_per_second_received = megabytes_received / elapsed_time

                    megabytes_per_second_sent = (
                        f'{megabytes_per_second_sent:.3f}' if f'{megabytes_per_second_sent:.3f}' != '0.000' else megabytes_per_second_sent)
                    megabytes_per_second_received = (
                        f'{megabytes_per_second_received:.3f}' if f'{megabytes_per_second_received:.3f}' != '0.000' else megabytes_per_second_received)

                    print(
                        f"Process {pid} sent {megabytes_per_second_sent} MB/s and received {megabytes_per_second_received} MB/s. {elapsed_time} seconds elapsed.")
                    returnMessage = returnMessage + f"Process {pid} sent {megabytes_per_second_sent} MB/s and received {megabytes_per_second_received} MB/s. {elapsed_time} seconds elapsed.\n"

                elif "-gigabyte" in args or "-g" in args:
                    gigabytes_sent = total_bytes_sent / (1024 * 1024 * 1024)
                    gigabytes_received = total_bytes_received / (1024 * 1024 * 1024)
                    gigabytes_per_second_sent = gigabytes_sent / elapsed_time
                    gigabytes_per_second_received = gigabytes_received / elapsed_time

                    gigabytes_per_second_sent = (
                        f'{gigabytes_per_second_sent:.3f}' if f'{gigabytes_per_second_sent:.3f}' != '0.000' else gigabytes_per_second_sent)
                    gigabytes_per_second_received = (
                        f'{gigabytes_per_second_received:.3f}' if f'{gigabytes_per_second_received:.3f}' != '0.000' else gigabytes_per_second_received)

                    print(
                        f"Process {pid} sent {gigabytes_per_second_sent} GB/s and received {gigabytes_per_second_received} GB/s. {elapsed_time} seconds elapsed.")
                    returnMessage = returnMessage + f"Process {pid} sent {gigabytes_per_second_sent} GB/s and received {gigabytes_per_second_received} GB/s. {elapsed_time} seconds elapsed.\n"

                else:
                    print(
                        "Invalid argument. Please use one of the following: -byte/-b, -kilobyte/-k, -megabyte/-m, "
                        "-gigabyte/-g.")
            return returnMessage + "\n" + totalMessage


    def getAllBandwidth(self, pids=None, interval=10, elapsed=True, args=None, print_output=True, threading=True,
                        max_workers=100):
        """

        This method gets the bandwidth for a list of pids using multi-threading.


        :param pid: (int) The process id to calculate it's bandwidth.
        :param interval: (int) The interval or the time to elapse.
        :param elapsed: (bool) True if you want elapsed, false if second by second.
        :param args: (list) A list of arguments that could be either:
            -byte or -b: to show the results in bytes/s.
            -kilobyte or -k: to show the results in kilobyte/s.
            -megabyte or -m: to show the results in megabyte/s.
            -gigabyte or -g to show the results in gigabyte/s.
        :param print_output: (bool) True if you want to print the output, false if not.
        :param threading: (bool) True if you want to use multi-threading, false if not.
        :param max_workers: (int) The maximum number of threads that can be used to execute the given calls.

        :return : (list) The pid, total_bytes_sent, total_bytes_received for each PID passed.


        """
        if pids is None or pids == []:
            pids = self.getProcesses(args=["-pid"])
        if args is None:
            args = ["-byte"]
        bandwidthList = []
        if threading:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_id = {executor.submit(self.getBandwidthById, pid, interval, elapsed, args, print_output): pid
                                for
                                pid in
                                pids}
                for future in concurrent.futures.as_completed(future_to_id):
                    pid = future_to_id[future]
                    try:
                        bandwidth = future.result()
                        # process the bandwidth information
                        bandwidthList.append(bandwidth)
                    except Exception as e:
                        print(f"Error fetching bandwidth for PID {pid}: {e}")
        else:
            for pid in pids:
                bandwidthList.append(self.getBandwidthById(pid, interval, elapsed, args, print_output))

        return bandwidthList

"""


This program is a Python script that helps in getting information about network usage for processes running on the
system. It uses the subprocess and psutil modules to run commands and interact with the system respectively.

"""

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

    @staticmethod
    def calcBandwidth(pid):
        """

        This method takes a process id and returns the total bytes sent and received by the process in a second.

        :param pid: (int) The process id to calculate it's bandwidth.

        :return : (int) The elapsed time for the calculation, (int) The total bytes sent in a second, (int) the
        total bytes received in a second.


        """
        try:
            process = psutil.Process(int(pid))

            start_io_counters = psutil.net_io_counters()
            # Wait for some time to elapse

            end_io_counters = psutil.net_io_counters()

            total_bytes_sent = end_io_counters.bytes_sent - start_io_counters.bytes_sent
            total_bytes_received = end_io_counters.bytes_recv - start_io_counters.bytes_recv
            return total_bytes_sent, total_bytes_received
        except ValueError:
            print("The PID Must Be an integer.")

    # TODO:
    #   Return the calculations instead of just printing it.
    #   Return Total bytes sent and received in interval or per second.
    def getBandwidthById(self, pid, interval=10, elapsed=True, args=None):
        """

        This method takes a process id, an interval, a boolean value indicating whether or not to return the elapsed
        time, and a list of arguments. It calculates the bandwidth usage for the specified process during the
        specified interval and returns the result as a formatted string.

        :param pid: (int) The process id to calculate it's bandwidth.
        :param interval: (int) The interval or the time to elapse.
        :param elapsed: (bool) True if you want elapsed, false if second by second.
        :param args: (list) A list of arguments that could be either:
            -byte or -b: to show the results in bytes/s.
            -kilobyte or -k: to show the results in kilobyte/s.
            -megabyte or -m: to show the results in megabyte/s.
            -gigabyte or -g to show the results in gigabyte/s.

        :return : (int) The elapsed time for the calculation, (int) The total bytes sent in a second, (int) the
        total bytes received in a second.


        """
        if args is None:
            args = ["-byte"]
        if not isinstance(args, list):
            raise TypeError("args must be a list")
        if elapsed:
            if "-byte" in args or "-b" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                bytes_per_second_sent = total_bytes_sent / elapsed_time
                bytes_per_second_received = total_bytes_received / elapsed_time
                print(
                    f"Process {pid} sent {bytes_per_second_sent:.2f} bytes/s and received {bytes_per_second_received:.2f} bytes/s. Over {interval} seconds.")
            elif "-kilobyte" in args or "-k" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                kilobytes_sent = total_bytes_sent / 1024
                kilobytes_received = total_bytes_received / 1024
                kilobytes_per_second_sent = kilobytes_sent / elapsed_time
                kilobytes_per_second_received = kilobytes_received / elapsed_time
                print(
                    f"Process {pid} sent {kilobytes_per_second_sent:.2f} KB/s and received {kilobytes_per_second_received:.2f} KB/s. Over {interval} seconds.")
            elif "-megabyte" in args or "-m" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                megabytes_sent = total_bytes_sent / (1024 * 1024)
                megabytes_received = total_bytes_received / (1024 * 1024)
                megabytes_per_second_sent = megabytes_sent / elapsed_time
                megabytes_per_second_received = megabytes_received / elapsed_time
                print(
                    f"Process {pid} sent {megabytes_per_second_sent:.2f} MB/s and received {megabytes_per_second_received:.2f} MB/s. Over {interval} seconds.")
            elif "-gigabyte" in args or "-g" in args:
                elapsed_time, total_bytes_sent, total_bytes_received = self.calcBandwidthInterval(pid, interval)
                gigabytes_sent = total_bytes_sent / (1024 * 1024 * 1024)
                gigabytes_received = total_bytes_received / (1024 * 1024 * 1024)
                gigabytes_per_second_sent = gigabytes_sent / elapsed_time
                gigabytes_per_second_received = gigabytes_received / elapsed_time
                gigabytes_per_second_sent = (
                    gigabytes_per_second_sent if f'{gigabytes_per_second_sent:.3f}' != '0.000' else gigabytes_per_second_sent)
                print(
                    f"Process {pid} sent {gigabytes_per_second_sent} GB/s and received {gigabytes_per_second_received:.2f} GB/s. Over {interval} seconds.")
            else:
                print(
                    "Invalid argument. Please use one of the following: -byte/-b, -kilobyte/-k, -megabyte/-m, "
                    "-gigabyte/-g.")
        elif not elapsed:
            total_bytes_sent, total_bytes_received = 0, 0
            for i in range(interval):
                time.sleep(1)
                bytes_sent, bytes_received = self.calcBandwidth(pid)
                total_bytes_sent += bytes_sent
                total_bytes_received += bytes_received
                elapsed_time = i + 1
                bytes_per_second_sent = total_bytes_sent / elapsed_time
                bytes_per_second_received = total_bytes_received / elapsed_time
                if "-byte" in args or "-b" in args:
                    bytes_per_second_sent = (
                        bytes_per_second_sent if f'{bytes_per_second_sent:.3f}' != '0.000' else bytes_per_second_sent)
                    bytes_per_second_received = (
                        bytes_per_second_received if f'{bytes_per_second_received:.3f}' != '0.000' else bytes_per_second_received)

                    print(
                        f"Process {pid} sent {bytes_per_second_sent} bytes/s and received {bytes_per_second_received} bytes/s. {elapsed_time} seconds elapsed.")
                elif "-kilobyte" in args or "-k" in args:
                    kilobytes_sent = total_bytes_sent / 1024
                    kilobytes_received = total_bytes_received / 1024
                    kilobytes_per_second_sent = kilobytes_sent / elapsed_time
                    kilobytes_per_second_received = kilobytes_received / elapsed_time
                    kilobytes_per_second_sent = (
                        kilobytes_per_second_sent if f'{kilobytes_per_second_sent:.3f}' != '0.000' else kilobytes_per_second_sent)
                    kilobytes_per_second_received = (
                        kilobytes_per_second_received if f'{kilobytes_per_second_received:.3f}' != '0.000' else kilobytes_per_second_received)
                    print(
                        f"Process {pid} sent {kilobytes_per_second_sent} KB/s and received {kilobytes_per_second_received} KB/s. {elapsed_time} seconds elapsed.")
                elif "-megabyte" in args or "-m" in args:
                    megabytes_sent = total_bytes_sent / (1024 * 1024)
                    megabytes_received = total_bytes_received / (1024 * 1024)
                    megabytes_per_second_sent = megabytes_sent / elapsed_time
                    megabytes_per_second_received = megabytes_received / elapsed_time
                    megabytes_per_second_sent = (
                        megabytes_per_second_sent if f'{megabytes_per_second_sent:.3f}' != '0.000' else megabytes_per_second_sent)
                    megabytes_per_second_received = (
                        megabytes_per_second_received if f'{megabytes_per_second_received:.3f}' != '0.000' else megabytes_per_second_received)
                    print(
                        f"Process {pid} sent {megabytes_per_second_sent} MB/s and received {megabytes_per_second_received} MB/s. {elapsed_time} seconds elapsed.")
                elif "-gigabyte" in args or "-g" in args:
                    gigabytes_sent = total_bytes_sent / (1024 * 1024 * 1024)
                    gigabytes_received = total_bytes_received / (1024 * 1024 * 1024)
                    gigabytes_per_second_sent = gigabytes_sent / elapsed_time
                    gigabytes_per_second_received = gigabytes_received / elapsed_time
                    gigabytes_per_second_sent = (
                        gigabytes_per_second_sent if f'{gigabytes_per_second_sent:.3f}' != '0.000' else gigabytes_per_second_sent)
                    gigabytes_per_second_received = (
                        gigabytes_per_second_received if f'{gigabytes_per_second_received:.3f}' != '0.000' else gigabytes_per_second_received)
                    print(
                        f"Process {pid} sent {gigabytes_per_second_sent} GB/s and received {gigabytes_per_second_received} GB/s. {elapsed_time} seconds elapsed.")
                else:

                    print(
                        "Invalid argument. Please use one of the following: -byte/-b, -kilobyte/-k, -megabyte/-m, "
                        "-gigabyte/-g.")
            print()

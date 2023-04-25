# NetworkHelper

NetworkHelper is a Python class designed to provide information about network usage for processes running on a system. The class contains several functions, including Netstat, PID and name retrieval, and bandwidth calculation for individual or multiple processes over a desired time frame.

## Functions

### Netstat
The Netstat function generates a report of network connections and their corresponding states.

### Get PIDs and Names
This function retrieves the process IDs and names of processes currently running on the system and utilizing the network.

### Calculate Bandwidth
The Calculate Bandwidth function can calculate the bandwidth usage for a single process or multiple processes running over a desired time frame. It can calculate bandwidth usage on a second-by-second basis or over a longer time period. It is important to note that the accuracy of the bandwidth calculation may be subject to error and improvements are currently being made.

## Requirements
NetworkHelper requires the psutil library, specifically version 5.9.5.

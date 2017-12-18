import os
import inspect
import time
import datetime
import pytz


class Logger():

    def __init__(self, dir):
        self.dir = dir

        if not os.path.exists(dir):
            os.makedirs(dir)

        self.log_file = open(dir + os.sep + "events.log", "a+")
        self.log_file.close()

    def error(self, s):
        self.log_file = open(self.dir + os.sep + "events.log", "a+")

        self.log_file.write(
            "[" + self.timestamp() + "] (Error) " + str(inspect.stack()[1][1]).split("/")[-1] + "::" +
            inspect.stack()[1][3] + "." + str(inspect.stack()[1][2]) + ": " + str(
                s) + "\n")
        self.log_file.close()

    def debug(self, s):
        self.log_file = open(self.dir + os.sep + "events.log", "a+")

        self.log_file.write(
            "[" + self.timestamp() + "] (Debug) " + str(inspect.stack()[1][1]).split("/")[-1] + "::" +
            inspect.stack()[1][3] + "." + str(inspect.stack()[1][2]) + ": " + str(
                s) + "\n")
        self.log_file.close()

    def success(self, s):
        self.log_file = open(self.dir + os.sep + "events.log", "a+")

        self.log_file.write(
            "[" + self.timestamp() + "] (Success) " + str(inspect.stack()[1][1]).split("/")[-1] + "::" +
            inspect.stack()[1][3] + "." + str(inspect.stack()[1][2]) + ": " + str(
                s) + "\n")
        self.log_file.close()

    def timestamp(self):
        ts = time.time()
        return str(datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S %d-%m-%Y'))

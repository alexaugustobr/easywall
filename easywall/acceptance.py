"""
this module exports a class for checking the user acceptance of a process using a acceptance file
"""
from copy import deepcopy
from logging import info
from time import sleep

from easywall.config import Config
from easywall.utility import (create_file_if_not_exists, delete_file_if_exists,
                              write_into_file)


class Acceptance(object):
    """
    the Acceptance class exports functions to check the user acceptance.

    the functions have to be executed in the following order:
    1. init class
    2. execute "start"
    3. execute "wait"
    4. execute "status"

    the functions can be executed as often as you want
    since they check the internal status of the class
    """

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.filename = ".acceptance"
        self.enabled = self.cfg.get_value("ACCEPTANCE", "enabled")
        self.duration = self.cfg.get_value("ACCEPTANCE", "duration")

        self.mystatus = "ready"
        if not self.enabled:
            self.mystatus = "disabled"

        info("Acceptance Library initialized. \n Enabled: {} \n Filename: {}".format(
            self.enabled, self.filename))

    def start(self) -> None:
        """
        the start of the acceptance process is triggered by this function
        the function checks the internal status of the class.
        the internal status can be ready, accepted or not accepted.
        if the status is disabled the function does nothing
        """
        if self.mystatus in ["ready", "accepted", "not accepted"]:
            create_file_if_not_exists(self.filename)
            write_into_file(self.filename, "false")
            self.mystatus = "started"
        info("Acceptance Process has been started.")

    def wait(self) -> None:
        """
        this function executes a sleep for the configured duration.
        the sleep is only executed when the start function was triggered before
        and not if the status is disabled.
        """
        if self.mystatus == "started":
            seconds = deepcopy(self.duration)
            info("acceptance wait process started. waiting for {} seconds".format(seconds))
            self.mystatus = "waiting"

            while seconds > 0:
                sleep(1)
                seconds = seconds - 1

            self.mystatus = "waited"

        info("acceptance wait process finished")

    def status(self) -> str:
        """
        this function returns the current status of the acceptance process.
        this is useful for calls of external software.
        when the status is waited the file content is read and the final acceptance status is
        determined here. the temporary file is also deleted in this function.

        possible status values:
        - ready
        - disabled
        - started
        - waiting
        - waited
        - accepted
        - not accepted
        """

        if self.mystatus == "waited":
            with open(self.filename, 'r') as tmpfile:
                content = tmpfile.read()
                content = content.replace("\n", "")
                content = content.replace("\t", "")

                if content.lower() == "true":
                    info("acceptance result: Accepted")
                    self.mystatus = "accepted"
                else:
                    info("acceptance result: Not Accepted (file content: {})".format(content))
                    self.mystatus = "not accepted"

            delete_file_if_exists(self.filename)

        return self.mystatus

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017, NewAE Technology Inc
# All rights reserved.
#
#=================================================

from subprocess import Popen, PIPE

class STLinkProgrammer(object):

    stexe = r"..\stlink_cli\ST-LINK_CLI.exe"

    def get_exitcode_stdout_stderr(self, args):
        """
        Execute the external command and get its exitcode, stdout and stderr.
        """
        proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
        out, err = proc.communicate()
        exitcode = proc.returncode
        return exitcode, out, err

    def check_device(self):
        exitcode, out, err = self.get_exitcode_stdout_stderr([self.stexe, "-TVolt"])

        if exitcode != 0:
            raise IOError("Error on STLink:\n%s"%out)

        for item in out.split("\n"):
            if "Device family" in item:
                item = item.replace("Device family :", "")
                return item        
        

    def program(self, fname):
        exitcode, out, err = self.get_exitcode_stdout_stderr([self.stexe, "-P", fname, "-V"])

        if exitcode != 0:
            raise IOError("Error on STLink:\n%s"%out)

if __name__ == "__main__":

    st = STLinkProgrammer()
    print st.check_device()
    st.program(r"..\fw_build\fw\GCC_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex")

        
        

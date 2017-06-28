
from shutil import copyfile
from subprocess import Popen, PIPE
import itertools

def get_exitcode_stdout_stderr(args):
    """
    Execute the external command and get its exitcode, stdout and stderr.
    """
    proc = Popen(args, stdout=PIPE, stderr=PIPE, shell=True)
    out, err = proc.communicate()
    exitcode = proc.returncode
    #
    return exitcode, out, err

with open("iar/STM32FX.ewp.template", "r") as f:
    template_orig = f.read()

rootfwdir = "C:\\chipwhisperer\\hardware\\victims\\firmware\\"

opt1 = ["OPT=s", "OPT=0"]
opt2 = ["", "MBEDTLS_AES_ROM_TABLES=1"]

other_options = [opt1, opt2]


#The following settings taken from IAR:
# For optimization level = high, balanced option (turns on most optimizations):
#  $CC_ALLOW_LIST$ = 11111110
#  $CC_OPT_LEVEL$ = 3
#  $CC_OPT_LEVEL_SLAVE$ = 3
#
# For optimization level = none:
#  $CC_ALLOW_LIST$ = 00000000
#  $CC_OPT_LEVEL$ = 0
#  $CC_OPT_LEVEL_SLAVE$ = 0


for platform in ["stm32f0", "stm32f1", "stm32f2"]:

    template = template_orig[:]
    template = template.replace("$FWROOTDIR$", rootfwdir)
    template = template.replace("$stm32f$", platform)
    template = template.replace("$STM32F$", platform.upper())

    #The following is a bit of a hack to support various targets
    if "stm32f0" in platform:
        template = template.replace("$CHIPNAME1$", "STM32F071RB	ST STM32F071RB")
        template = template.replace("$LINKERSCRIPT$", "stm32f071xB.icf")
        template = template.replace("$STM32FULLPN$", "STM32F071RBTX")
    elif "stm32f1" in platform:
        template = template.replace("$CHIPNAME1$", "STM32F100RB	ST STM32F100RB")
        template = template.replace("$LINKERSCRIPT$", "stm32f100xB.icf")
        template = template.replace("$STM32FULLPN$", "STM32F100xB")
    elif "stm32f2" in platform:
        template = template.replace("$CHIPNAME1$", "STM32F205RE	ST STM32F205RE")
        template = template.replace("$LINKERSCRIPT$", "stm32f205xE.icf")
        template = template.replace("$STM32FULLPN$", "STM32F205RETx")
    else:
        raise ValueError("Error: Bad Things...")

    template_stage_2 = template[:]

    for option in list(itertools.product(*other_options)):
        optstr = " ".join(option)

        template = template_stage_2[:]

        if "MBEDTLS_AES_ROM_TABLES" in optstr:
            template = template.replace("$EXTRADEFINES$", "MBEDTLS_AES_ROM_TABLES=1")
        else:
            template = template.replace("$EXTRADEFINES$", "")

        if "OPT=s" in optstr:
            template = template.replace("$CC_ALLOW_LIST$", "11111110")
            template = template.replace("$CC_OPT_LEVEL$", "3")
            template = template.replace("$CC_OPT_LEVEL_SLAVE$", "3")
        elif "OPT=0" in optstr:
            template = template.replace("$CC_ALLOW_LIST$", "00000000")
            template = template.replace("$CC_OPT_LEVEL$", "0")
            template = template.replace("$CC_OPT_LEVEL_SLAVE$", "0")
        else:
            raise ValueError("Error: Bad Things...")


        with open("iar/STM32FAutoBuild.ewp", "w") as newfile:
            newfile.write(template)


        exitcode, out, err = get_exitcode_stdout_stderr(["E:/IAR Systems/Embedded Workbench 8.0/common/bin/IarBuild.exe", "iar/STM32FAutoBuild.ewp", "-build", "Debug", "-log", "all"])
        print out
        print err
        print exitcode

        print "*** Build command: "
        print "   " + platform + " " + optstr

        if exitcode != 0:
            print "**************Build FAILED****************"
        else:
            hexname = "IAR_AES_CW308_" + platform.upper() + "_CRYPTO_TARGET=MBEDTLS_" + optstr.replace(" ", "_") + ".hex"

            print "   Copying to file " + hexname
            copyfile("iar/Debug/Exe/STM32FBUILD.hex", "fw/" + hexname)
        




            

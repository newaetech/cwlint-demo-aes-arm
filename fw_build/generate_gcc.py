import itertools

platforms = ["CW308_STM32F0", "CW308_STM32F1", "CW308_STM32F2"]
crypto_targets = ["MBEDTLS"]

opt1 = ["OPT=s", "OPT=0"]
opt2 = ["", "MBEDTLS_AES_ROM_TABLES=1"]

batch_file = ""

other_options = [opt1, opt2]

for platform in platforms:
    makestr = "PLATFORM=" + platform + " "

    for target in crypto_targets:
        makestr += "CRYPTO_TARGET=" + target + " "

        for option in list(itertools.product(*other_options)):
            makestr_with_option = makestr + " ".join(option)

            batch_file += "make " + makestr_with_option + "\n"
            batch_file += "mv simpleserial-aes-" + platform + ".hex fw/GCC_AES_" + makestr_with_option.replace("PLATFORM=", "").replace(" ", "_") + ".hex\n"

with open("aes_gcc_build.bat", "w") as f:
    f.write(batch_file)
        

            



# ChipWhisperer Lint Demos #

The following codebase shows several demos of the CW-Lint tool (see http://github.com/newaetech/ChipWhisperer-Lint). This tool is designed to make it easier for finding cryptographic leakage on embedded systems, be it a hardware or software solution. We have currently targeted implementations of AES - these demos all use AES-128 ECB, but other lengths and modes can be selected (or added if not supported yet).

This tool has many use-cases, but the most powerful is to work as a "lint" style tool to catch leakage accidentally introduced in software or hardware implementations of cryptography. This can be setup to automatically run a given library across a wide variety of hardware targets for example, as leakage can vary widely between different devices. The setup is roughly like this:

![ChipWhisperer-Lint Super-Cool Demo Figure](/doc/cwlint_arch.png)

### Test Vector Leakage Assessment (TVLA) ###

CW-Lint builds primarily on work done to develop TVLA. The TVLA setup provides a method to find statistical differences in power traces between two "known" conditions. For example this could be used to prove that the power traces look different (with a defined level of statistical significance) when a byte of a secret key is 0x00 compared to 0x1F. This comparison is done using the Welch's t-test (note this can also be converted into a SNR number).

This is a very powerful test as it doesn't rely on us to know how to break the encryption, but instead provides proof that it *might* be breakable.

###### References ######

[A testing methodology for side-channel resistance validation: Paper](http://csrc.nist.gov/news_events/non-invasive-attack-testing-workshop/papers/08_Goodwill.pdf)

[Is your design leaking keys? Efficient testing for sidechannel leakage: Presentation](https://www.rsaconference.com/writable/presentations/file_upload/asec-r35b.pdf)

[Welch's T-Test](https://en.wikipedia.org/wiki/Welch%27s_t-test)

### ISO/IEC ###

The ISO/IEC 17825:2016 standard (Testing methods for the mitigation of non-invasive attack classes against cryptographic modules) defines a number of tests performed with TVLA in order to quantify if a given device is breakable or not.

The CW-Lint provides a "ISO/IEC 17825:2016 Mode" that performs a specific subset of tests given in that document. Note a number of additional tests that will help you track down where and why cryptographic leakage is occurring are available too, but these use modified versions of the T-Test. 


## ChipWhisperer Lint Detection on mbed TLS Library ##

This demo is designed to run AES using the mbed TLS library against a number of ARM targets. This demonstrates the power of automated analysis in determining where leakage exists, and why testing against ALL possible variants is useful for detecting leakage that might go unnoticed on specific builds/variants.

The setup involves (a) building possible variants of the library with different compilers, library options, and compiler flags, (b) running the target code on different physical architectures, and (c) performing automated side-channel analysis of the resulting power traces.

These are provided by:

 (a) A special build script (would be specific to your build environment).
 (b) The ChipWhisperer-Capture software connected to a ChipWhisperer-Lite + UFO Board, run in a basic script.
 (c) The ChipWhisperer-Lint software.

### (a) Build Process ###

The target is the mbed TLS library. The automated test script performs the following actions:

1. Perform "git pull" to get latest code from public repository.
2. For each variant:
   * Autogenerate makefile to build binary (based on settings below).   
   * Build binary for target device.   
   * Program target device.   
   * Record power traces while performing AES operation.

A total of 24 variants are possible, with the following combinations:

* Compiler: IAR, GCC
* Compiler settings: Optimization -Os / -O0
   * For IAR: -O0 = None, -0s = High / Balanced
* AES Configuration: MBEDTLS_AES_ROM_TABLES defined/not defined (changes if ROM tables or SRAM tables used)
* Targets: STM32F100, ST32F205, STM32F071

Note 4 variants will fail to build: the STM32F1 device does not have enough SRAM for SRAM tables. Thus any variants with the STM32F100 without MBEDTLS_AES_ROM_TABLES are not possible.

The system will generate 20 HEX-files as a result of the build process, which have names similar to the following:

	HEX Size  Filename
	43,306    GCC_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex
	65,536    GCC_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	28,321    GCC_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=s_.hex
	52,674    GCC_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex
	69,128    GCC_AES_CW308_STM32F1_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	51,329    GCC_AES_CW308_STM32F1_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex
	37,506    GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex
	62,145    GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	24,120    GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=s_.hex
	49,995    GCC_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex
	27,432    IAR_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex
	49,903    IAR_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	21,095    IAR_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=s_.hex
	44,008    IAR_AES_CW308_STM32F0_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex
	51,957    IAR_AES_CW308_STM32F1_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	42,126    IAR_AES_CW308_STM32F1_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex
	26,757    IAR_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_.hex
	49,633    IAR_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=0_MBEDTLS_AES_ROM_TABLES=1.hex
	18,477    IAR_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=s_.hex
	41,607    IAR_AES_CW308_STM32F2_CRYPTO_TARGET=MBEDTLS_OPT=s_MBEDTLS_AES_ROM_TABLES=1.hex


### (b) Physical Setup ###

This requires a ChipWhisperer for performing power analysis, and a suitable target board. This is designed to run on a CW308 UFO board with the STM32Fx targets. Switching between STM32F devices does require physically switching the target boards (or having multiple ChipWhisperer-Capture + target setups).

## Example Output ##
See [/doc/all-boards-output-example.html] for the result of running the tool. Here's a little sneak peak:
![ChipWhisperer-Lint Output Example](/doc/snipper_image.png)

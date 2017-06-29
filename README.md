# Side-Channel Lint Detection on mbed TLS Library #


This demo is designed to run AES using the mbed TLS library against a number of ARM targets. This demonstrates the power of automated analysis in determining where leakage exists, and why testing against ALL possible variants is useful for detecting leakage that might go unnoticed on specific builds/variants.

The setup involves (a) building possible variants of the library with different compilers, library options, and compiler flags, (b) running the target code on different physical architectures, and (c) performing automated side-channel analysis of the resulting power traces.

These are provided by:

 (a) A special build script (would be specific to your build environment).
 (b) The ChipWhisperer-Capture software connected to a ChipWhisperer-Lite + UFO Board, run in a basic script.
 (c) The SideChannel-Lint software.

## (a) Build Process ##

The target is the mbed TLS library. The automated test script performs the following actions:

1. Perform "git pull" to get latest code from public repository.
2. For each variant:
   a. Autogenerate makefile to build binary (based on settings below).
   b. Build binary for target device.
   c. Program target device.
   d. Record power traces while performing AES AES.

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


## (b) Physical Setup ##

TODO

## (c) Side-Channel Lint Setup ##

TODO
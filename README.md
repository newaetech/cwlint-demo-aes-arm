This demo is designed to run AES using the mbed TLS library against a number of ARM targets. This demonstrates the power of automated analysis in determining where leakage exists.

The target is the mbed TLS library. The automated test script performs the following actions:

1. Perform "git pull" to get latest code from public repository.
2. For each variant:
   a. Autogenerate makefile to build binary (based on settings below).
   b. Build binary for target device.
   c. Program target device.
   d. Record power traces while performing AES AES.

A total of 24 variants are tested, with the following combinations:

* Compiler settings: Optimization -Os / -O0 (size/OFF)
* AES Configuration: MBEDTLS_AES_ROM_TABLES defined/not defined (changes if ROM tables or SRAM tables used)
* Compiler: IAR, GCC
* Targets: STM32F100, ST32F205, STM32F051

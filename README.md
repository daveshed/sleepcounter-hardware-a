# sleepcounter-hardware-a

A python package that defines hardware specific (concretions) code and specifies non-hardware specific dependencies.

## Hardware Required

* An led matrix display based on the Maxim 7219.
* A stepper-motor driven rack-and-pinion

## Development

Given that this package depends on hardware-specific packages, it's not possible to install it and run tests on an x86 development machine.

TODO: provide a docker development environment/tox
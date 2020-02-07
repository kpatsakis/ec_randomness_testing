# Elliptic curves randomness evaluation

This is a Python script to generate a set of raw files that can be used to assess the randomness of the points of elliptic curves.

The curves that are being used in the current version are: Ed25519, P192, P224, P256, P521, P384, secp192k1, secp224k1, and secp256k1.

## Dependencies

The main dependencies are
* [fastecdsa](https://github.com/AntonKueltz/fastecdsa)
* [gmpy2](https://github.com/BrianGladman/gmpy2)
* [bitarray](https://github.com/ilanschnell/bitarray)
You may use, e.g. pip to install the dependencies with:
```
pip3 install fastecdsa gmpy2 bitarray
```

## Platform

The code has been tested on Linux-based systems with Python 3.7.5

## Code dependencies

The code for ED25519 is derived from the [original code](https://ed25519.cr.yp.to/python/ed25519.py) with minor changes. These changes are mainly for compatibility with Python 3, using the native Python *pow* function for modular exponentiation, and gmpy2 for modular inversion.

## Usage

Just run the Python script and define how many tests you want to perform, the default is 1000.
```
python3 CurveTester.py -t 10000
```

A curve like Ed25519 produces in general 255 bits long output. However, this length does not fit properly in bytes. Therefore, the script will increase a bit the tests that will be performed so that the output fits exactly in bytes.

# Elliptic curves randomness evaluation

This is a Python script to generate a set of raw files that can be used to assess the randomness of the points of elliptic curves.

The curves that are being used in the current version are:

* ED25519
* P-256
* P-384
* P-521

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

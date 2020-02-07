#!/usr/bin/env python3
from random import randrange
from fastecdsa import curve
from fastecdsa.curve import P192, P224, P256, P521, P384, secp192k1, secp224k1, secp256k1
from fastecdsa.point import Point
from ed25519 import *
from multiprocessing import Pool
from bitarray import bitarray
import argparse


def padnum(x, L):
    # gets a number, converts it to binary, pads it with zeros to fit a length and returns the *binary* format, which essentially is bitarray
    tmp = bin(x)[2:]
    tmp = (L - len(tmp)) * "0" + tmp
    return tmp[:L]


def FixTests(tests, L):
    # fixes the number of tests so that the end result of bits is multiple of 8 and we can also get their quartiles
    while (tests * L) % 8 > 0 or ((tests * L) // 4) % 8 > 0:
        tests += 1
    return tests


def rnd_multpoint25519(UB):
    r = randrange(UB)
    pnt = scalarmult(B, r)[0]
    return pnt


def TestCurve25519(TESTS):
    TESTS = FixTests(TESTS, 255)
    prefix = "ED25519"
    p = 2**255 - 19
    pl = Pool(8)
    lst = [p] * TESTS
    points = pl.map(rnd_multpoint25519, lst)
    allbits = bitarray()
    for pnt in points:
        allbits += bitarray(padnum(pnt, 255))
    filesaver(allbits, 255, prefix)
    return True


def rnd_multpoint(l):
    ub, p = l
    r = randrange(ub)
    tmp = (r * p).x
    return int(tmp)


def test_curve(c, TESTS):
    if c == "Curve25519":
        TESTS = FixTests(TESTS, 255)
        TestCurve25519(TESTS)
        return True
    else:
        if c == "P192":
            E = curve.P192
        elif c == "P224":
            E = curve.P224
        elif c == "P256":
            E = curve.P256
        elif c == "P384":
            E = curve.P384
        elif c == "P521":
            E = curve.P521
        elif c == "secp192k1":
            E = curve.secp192k1
        elif c == "secp224k1":
            E = curve.secp224k1
        elif c == "secp256k1":
            E = curve.secp256k1
    x, y, p = E.gx, E.gy, E.p
    L = len(bin(p)) - 2
    TESTS = FixTests(TESTS, L)
    P = Point(x, y, E)
    pl = Pool(8)
    lst = [[q, P]] * TESTS
    points = pl.map(rnd_multpoint, lst)
    allbits = bitarray()
    for pnt in points:
        pnt = padnum(pnt, L)
        allbits = allbits + bitarray(pnt)
    filesaver(allbits, L, c)
    return True


def filesaver(barray, L, prefix):
    upperb = bitarray()
    lowerb = bitarray()
    q1 = bitarray()
    q2 = bitarray()
    q3 = bitarray()
    q4 = bitarray()
    with open(prefix + ".raw", "wb") as fout:
        barray.tofile(fout)
    for i in range(len(barray) // L):
        chunk = barray[i * L: (i + 1) * L]
        upperb += chunk[:L // 2]
        lowerb += chunk[L // 2:]
        q1 += chunk[:L // 4]
        q2 += chunk[L // 4:L // 2]
        q3 += chunk[L // 2:(3 * L) // 4]
        q4 += chunk[(3 * L) // 4:]
    # delete intermediate variables to free memory
    with open(prefix + "_u.raw", "wb") as fout:
        upperb.tofile(fout)
    del upperb
    with open(prefix + "_l.raw", "wb") as fout:
        lowerb.tofile(fout)
    del lowerb
    with open(prefix + "_Q1.raw", "wb") as fout:
        q1.tofile(fout)
    del q1
    with open(prefix + "_Q2.raw", "wb") as fout:
        q2.tofile(fout)
    del q2
    with open(prefix + "_Q3.raw", "wb") as fout:
        q3.tofile(fout)
    del q3
    with open(prefix + "_Q4.raw", "wb") as fout:
        q4.tofile(fout)
    del q4
    return True


parser = argparse.ArgumentParser(
    prog='CurveTester', description='Collects statistics by computing random points on elliptic curves Ed25519, P256, P384, and P521. All statistics are saved in raw files, overwriting existing ones. If you ask for for many tests, this would be a slow process, so better grab a coffee.')
parser.add_argument('-t', '--tests', type=int, default=10000,
                    help='Minimum tests to perform, default set to 1000.')

args = parser.parse_args()
for ec in ["Curve25519", "P192", "P224", "P256", "P384", "P521", "secp256k1", "secp192k1", "secp224k1"]:
    print ("Working with curve: %s..." % ec)
    test_curve(ec, args.tests)

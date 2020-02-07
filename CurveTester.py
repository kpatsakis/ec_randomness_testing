#!/usr/bin/env python3
from random import randrange
from fastecdsa import curve
from fastecdsa.curve import P192, P224, P256, P521, P384, secp192k1, secp224k1, secp256k1, brainpoolP160r1, brainpoolP192r1, brainpoolP224r1, brainpoolP256r1, brainpoolP320r1, brainpoolP384r1, brainpoolP512r1
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
    prefix = "Ed25519"
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
    if c == "ed25519":
        TESTS = FixTests(TESTS, 255)
        TestCurve25519(TESTS)
        return True
    else:
        # let's use eval for now
        E = eval("curve." + c)
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


ed = ["ed25519"]
NIST = ["P192", "P224", "P256", "P384", "P521"]
Certicom = ["secp256k1", "secp192k1", "secp224k1"]
BSI = ["brainpoolP160r1", "brainpoolP192r1", "brainpoolP224r1",
       "brainpoolP256r1", "brainpoolP320r1", "brainpoolP384r1", "brainpoolP512r1"]
parser = argparse.ArgumentParser(
    prog='CurveTester', description='Collects statistics by computing random points on elliptic curves. By default no curve is selected, check syntax on how to enable them. All statistics are saved in raw files, overwriting existing ones. If you ask for for many testsW, this would be a slow process, so better grab a coffee.')
parser.add_argument('-t', '--tests', type=int, default=1000,
                    help='Minimum tests to perform, default set to 1000.')
parser.add_argument("--BSI", action='store_true', default=False,
                    dest='use_bsi', help="Use the BSI curves, default is False.")
parser.add_argument("--CRT", action='store_true', default=False,
                    dest='use_cert', help="Use the Certicom curves, default is False.")
parser.add_argument("--ed", action='store_true', default=False,
                    dest='use_ed', help="Use the Ed25519 curve, default is False.")
parser.add_argument("--NIST", action='store_true', default=False,
                    dest='use_nist', help="Use the NIST curves, default is False.")
args = parser.parse_args()
crvs = []
if args.use_bsi:
    crvs += BSI
if args.use_nist:
    crvs += NIST
if args.use_cert:
    crvs += Certicom
if args.use_ed:
    crvs += ed
for ec in crvs:
    print ("Working with curve: %s..." % ec)
    test_curve(ec, args.tests)

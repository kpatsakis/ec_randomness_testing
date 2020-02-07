#!/usr/bin/env python3
from random import randrange
from fastecdsa import curve
from fastecdsa.curve import P256, P521, P384
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
    prefix = "EC25519"
    UB = 2**255 - 19
    p = Pool(8)
    lst = [UB] * TESTS
    points = p.map(rnd_multpoint25519, lst)
    allbits = bitarray()
    for pnt in points:
        allbits += bitarray(padnum(pnt, 255))
    filesaver(allbits, 255, prefix)
    return True


CurveP = {"P256": {"x": 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
                   "y": 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5, "UB": 2**256 - 2**224 + 2**192 + 2**96 - 1}, "P384": {"x": 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7, "UB": 2**384 - 2**128 - 2**96 + 2**32 - 1, "y": 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f}, "P521": {"UB": 2**521 - 1, "x": 0xc6858e06b70404e9cd9e3ecb662395b4429c648139053fb521f828af606b4d3dbaa14b5e77efe75928fe1dc127a2ffa8de3348b3c1856a429bf97e7e31c2e5bd66, "y": 0x11839296a789a3bc0045c8a5fb42c7d1bd998f54449579b446817afbd17273e662c97ee72995ef42640c550b9013fad0761353c7086a272c24088be94769fd16650}}


def rnd_multpoint(l):
    ub, p = l
    r = randrange(ub)
    tmp = (r * p).x
    return int(tmp)


def test_curve(c, TESTS):
    if c == "Curve25519":
        TestCurve25519(TESTS)
        return True
    else:
        if c == "P256":
            E = curve.P256
        elif c == "P384":
            E = curve.P384
        elif c == "P521":
            E = curve.P521
        L = int(c[1:])
        TESTS = FixTests(TESTS, L)
    x, y, UB = E.gx, E.gy, E.p
    P = Point(x, y, E)
    p = Pool(8)
    lst = [[UB, P]] * TESTS
    points = p.map(rnd_multpoint, lst)
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

parser = argparse.ArgumentParser(prog='CurveTester', description='Collects statistics by computing random points on elliptic curves Ed25519, P256, P384, and P521. All statistics are saved in raw files, overwriting existing ones. If you ask for for many tests, this would be a slow process, so better grab a coffee.')
parser.add_argument('-t','--tests', type=int, default=1000,
                   help='Minimum tests to perform, default set to 1000.')

args = parser.parse_args()
for ec in ["Curve25519", "P256", "P384", "P521"]:
    print ("Working with curve: %s..." % ec)
    test_curve(ec, args.tests)

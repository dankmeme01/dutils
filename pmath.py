import math
from fractions import Fraction
from . import pyutils

whole, beautify, overload = pyutils.whole, pyutils.beautify, pyutils.overload

def sin(deg: float): return math.sin(math.radians(deg))
def cos(deg: float): return math.cos(math.radians(deg))
def tan(deg: float): return math.tan(math.radians(deg))
def ctan(deg: float): return 1 / tan(deg)
def asin(deg: float): return math.asin(math.radians(deg))
def acos(deg: float): return math.acos(math.radians(deg))
def atan(deg: float): return math.atan(math.radians(deg))

def frac(num: float, sameiflong: bool = True):
    if len(str(Fraction(num))) > 6 and sameiflong: return beautify(num)
    return str(Fraction(num))

def pyth(h: float, k1: float, k2: float):
    #if any([elem <= 0 for elem in [h, k1, k2]]): raise ValueError("Incorrect value has been passed")
    if h != 0 and (h <= k1 or h <= k2): raise ValueError("First argument should be zero, or more then other arguments")
    if h == 0.0:
        h = math.sqrt(k1**2 + k2**2)
        return h
    elif k1 == 0.0:
        k1 = math.sqrt(h**2 - k2**2)
        return k1
    else:
        k2 = math.sqrt(h**2 - k1**2)
        return k2

def prime(num: int) -> list[bool, int, int]:
    if num > 1:
        for i in range(2,num):
            if (num % i) == 0:
                return [False, i, num//i]
        else: return [True, 1, num]
    else:
        return [False, 1, 1]

def getprimes(fromv: int, to: int) -> list[int]:
    if to <= fromv: raise ValueError("First argument should be less than second")
    primes = []
    for i in range(fromv, to):
        if(prime(i)[0]): primes.append(i)
    return primes

def getfactors(number: int, incl: bool=True) -> list[int]:
    factors = [wh for wh in range(1, number+1) if number % wh == 0]
    if not incl:
        factors.remove(1)
        try: factors.remove(number)
        except ValueError: pass
    return factors

def addfloats(n1: float, n2: float):
    times = 1
    while True:
        if not whole(n1*times) or not whole(n2*times): times *= 10#; print(n1*times, n2*times)
        else: n1 = int(n1*times); n2 = int(n2*times); break
    #print(times)
    return (n1+n2)/times

def fromsqrt(sqrt: int) -> str:
    # √27 -> 3√3
    factors = getfactors(int(sqrt), False)
    for f in factors:
        for i in factors:
            if f*i == sqrt:
                if whole(math.sqrt(f)):
                    return "√" + beautify(f) + "*" + beautify(i) + " | " + beautify(int(math.sqrt(f))) + "√" + beautify(i)
                elif whole(math.sqrt(i)):
                    return "√" + beautify(i) + "*" + beautify(f) + " | " + beautify(int(math.sqrt(i))) + "√" + beautify(f)
                else:
                    continue
            else: continue
    return "Impossible."

def intosqrt(mult: int or float, sqrt: int or float) -> str:
    # √96 | 0.125 -> √0.015625 * 96 -> √1.5
    theanswer = beautify(mult)+"√"+beautify(sqrt)+" | √" + beautify(mult) + "^2 " + "* " + beautify(sqrt) + " | √" + beautify(round(mult**2, 5)) + "*" + beautify(sqrt) + " | √" + beautify(round(sqrt * (mult**2), 5)) + " | " + frac(math.sqrt(sqrt * (mult**2)))
    return theanswer

def solvequad(a: int or float, b: int or float, c: int or float, quiet : bool = False) -> str:
    d = b**2-4*a*c
    if not quiet: print("Discriminant is b²-4ac: " + str(b) + "²-4*" + str(a) + "*" + str(c) + " = " + str(d))
    if not quiet: print("Solution(s) for -b±√D/2a: ", end="")
    below = 2*a
    upper = lambda pos : -b+d**(1/2) if pos else -b-d**(1/2)
    if d < 0: return ("∅")
    elif d == 0: return str(-b/(2*a))
    else: return beautify(upper(True)/below) + " or " + beautify(upper(False)/below)

def quadform(formula: str) -> list[int or float]:
    for i in "a b c d e f g h i j k l m n o p q r s t u v w x y z".split(" "):
        if i in formula:
            formula = formula.replace(i, "x")
    equation = formula.strip()
	# equation must look like ax**2 ± bx ± c
	# first token is all before x, and 1 if nothing is found
	# also we remove = 0 to be clearer
    equation = equation.partition("=")[0].replace("^","**")
    a = equation.partition("x")[0]
    if len(equation.partition("x")) != 3 or equation.partition("x")[0] == "":
    	a = "1"
    	equation = "1"+equation
    if a[0] == "-" and float(a)> 0: a = str(float(-a))
    if a == "0": raise ValueError("Incorrect equation, a cannot be zero")
    # remove parts of a
    equation = equation.replace(a+"x**2", "")
    # finding b and c is less tricky, now equation should be ± bx ± c
    part = equation.partition("x")
    b = eval("0"+part[0]) # 0 ± b
    c = eval("0"+part[2])
    return float(a),b,c

def investmulti(sides: int) -> str:
    diag = (sides*(sides-3))/2
    deg = 180 * (sides-2)
    return str(sides) + "-sided polygon has " + str(diag) + " diagonals and total " + str(deg) + " degrees."

def solvemulti(degs_diags: int):
    if not whole(degs_diags): return TypeError("Degrees/diagonals argument must be whole")
    if degs_diags >= 180:
        #solve for degrees. formula = 180(n-2) = degs_diags
        if not whole(degs_diags/180+2): return "Invalid polygon"
        return str(int(degs_diags/180+2)) + " sides"
    else:
        #solve for diags. formula - d = n(n-3)/2 or (n^2 - 3n)/2
        degs_diags *= 2 # so we can use n^2 - 3n without dividing by 2 and we can use quad formula here now
        return int(solvequad(1, -3, -degs_diags, True).partition("or")[0].strip()) + " sides"

@overload # square
def area_square(side: float):
    return side*side
@overload # square
def area_square(side: int):
    return area_square(float(side))

def area_rectangle(side1: float or int, side2: float or int):
    return side1*side2

@overload
def area_parall(side: float, height: float):
    return side*height
@overload
def area_parall(side1: float, side2: float, angle: int):
    return side1 * side2 * math.sin(math.radians(angle))
@overload
def area_parall(side1: float, side2: float, angle_sin: float):
    return side1 * side2 * angle_sin

@overload
def area_trapez(side1: float, side2: float, height: float):
    return ((side1+side2)/2)*height
@overload
def area_trapez(height: float, middle_line: float):
    return height * middle_line

@overload
def area_rhomb(side: float, height: float):
    return side*height
@overload
def area_rhomb(diag1: float, diag2: float):
    return (diag1*diag2)/2
@overload
def area_rhomb(side: float, angle: int):
    return side**2 * math.sin(math.radians(angle))
@overload
def area_rhomb(side: float, angle_sin: float):
    return side**2 * angle_sin


def resolvemath(mathstring: str) -> None:
    whatdo = None
    if "exec " in mathstring:
        whatdo = [exec, mathstring.replace("exec ", "from math import *; ")]
    elif "sqrt" in mathstring or "√" in mathstring:
        if "(sqrt)" in mathstring:
            mathstring = mathstring.replace("(sqrt)", "√")
        elif "sqrt" in mathstring:
            mathstring = mathstring.replace("sqrt", "√")
        f = mathstring.partition("√")
        listc = list(f)
        if len(f[0]) <= 0: listc.remove(f[0]); f = tuple(listc)
        if f[0] == "√":
            whatdo = [fromsqrt, float(eval(f[1]))]
            print("Matched: fromsqrt")
        else:
            whatdo = [intosqrt, float(eval(f[0])), float(eval(f[2]))]
            print("Matched: intosqrt")
    else:
        try:
            splat = [float(x) for x in mathstring.split(" ")]
        except ValueError:
            pass
        else:
            if len(splat) == 3 and any([num == 0 for num in splat]):
                print("Matched: pyth")
                whatdo = [pyth, float(splat[0]), float(splat[1]), float(splat[2])]
    if whatdo == None:
        #print(mathstring)
        #print(quadform(mathstring))
        try:
            whatdo = [solvequad, *(quadform(mathstring))]
            print("Matched: quadratic equation")
        except Exception as e:
            whatdo = [eval, mathstring]
    #print(whatdo)
    if len(whatdo) == 3:
        return whatdo[0].__call__(whatdo[1], whatdo[2])
    elif len(whatdo) == 2:
        return whatdo[0].__call__(whatdo[1])
    elif len(whatdo) == 1:
        return whatdo[0].__call__()
    elif len(whatdo) == 4:
        return whatdo[0].__call__(whatdo[1], whatdo[2], whatdo[3])

if __name__ == "__main__":
    """
    Cheat sheet:
    Together:
        - whole(int | float): checks if number is a whole: whole(4.0) - return: True, whole(2.01) - return: False
        - beautify(float): Beautifies a number. Returns that float but with less digits.
        - frac(float): Returns a fraction of a number if it is not long enough. Otherwise returns beautify function of that float
        - resolvemath(str): resolve equation - sample usage: resolvemath(sqrt9*3) - resolved: intosqrt(9, 3) - return: 3sqrt3
    Algebra:
        - fromsqrt(int): no desc - sample usage: stealfromsqrt(27) - return: √9*3 | 3√3
        - intosqrt(int, int): reverse of above - sample usage: intosqrt(3, 3) - return: √3**2 * 3 | √9*3 | √27 | 5.196152422706632
        - getfactors(int, bool): get factors from number: - sample usage: getfactors(27, True) - return: 1, 3, 9, 27
        - getprimes(int, int): get prime numbers from int to int - sample usage: getprimes(0, 25) - return: 2, 3, 5, 7, 11, 13, 17, 19, 23
        - prime(int): check if number is a prime - sample usage: prime(17) - return: True
        - solvequad(float, float, float): Solve for x in quadratic formula - sample usage: solvequad(1, 3, 10) - return: 0.5 or -0.2
        - quadform(str): Returns tokens of quadratic equation - sample usage: quadform("x**2 + 3x - 10") - return: (1, 3, 10)
    Geometry:
        - pyth(float, float, float): pythagoreans theorem, for unknown numbers use 0 or get errored - sample usage: pyth(0, 4, 3) - return: 5.0
        - investmulti(int): find how many diagonals and total degree amount in n-sided polygon
        - solvemulti(int): find how many sides polygon has by degrees or diagonals
    """
    while True:
        print(resolvemath(input("Equation: ")))
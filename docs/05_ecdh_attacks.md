# ECDH Attacks
## The Order Of The Generator Is Too Small
Perhaps the wrong use for ECDH that is easiest to attack is choosing a generator with an order `n` that is too small.
As mentioned, it is possible solve the ECDLP problem with a complexity of $O(\sqrt{n})$. When `𝑛` is too small, for example 32 bit, then it becomes feasible to solve this problem. There are several algorithms that solve the problem, including Baby-Step Giant-Step, Pollard's Rho, and Pollard's Lambda. These algorithms can be run as a black box with the help of SageMath, by using the `discrete_log` function:
```python
import random
p = random_prime(2^32)
a = random.randrange(p)
b = random.randrange(p)
E = EllipticCurve(GF(p), [a,b])
G = E.gens()[0]
n = G.order()
private_key = random.randrange(n)
A = private_key * G
found_key = G.discrete_log(A)
assert found_key * G == A
assert private_key == found_key
print("success!")
```

In this code snippet we choose parameters for the curve randomly under the limitation that `𝑝` is 32 bits long. This limitation guarantees us that the number of points on the curve is $O(2^{32})$ and therefore the order of each point in it is at most $O(2^{32})$ as well. After that we create the curve, choose some generator in it, generate a random private key, and calculate the public key. Finally, from the generator and the public key, we calculate the the discrete logarithm to find the private key, and verify that the key found is indeed correct. This code takes just a few seconds at most to find the private key.



## The Order Of The Generator Is A Smooth Number
As mentioned, the order of a generator is defined as the number of points in the "circle" formed when we add the generator point to itself over and over again, and it is denoted by `𝑛`. If `𝑛` is a composite number that can be factored into smaller prime factors, then it is possible to solve ECDLP efficiently. Such a number is called a Smooth Number, and for the purpose of this article, it is a number which can be factored into enough prime factors, each of which is small enough for our attack to work. The formal definition of a Smooth Number is a little different and not relevant for us.

Intuitively, this is done by "attacking" each of the prime factors separately. Given a generator point `𝐺` which forms a very large "circle", and some point `𝑃` in the "circle" such that `𝑃 = 𝑘𝐺`. The large "circle" can be dismantled into several small "circles", each the size of one prime factor of `𝑛`. In each small "circle" we can map `G` and `P` to other corresponding points `G'` and `P'` that are located in the small "circle", and satisfy `𝑃′ = 𝑘′𝐺′`. Because the "circle" is small, it is relatively easy to solve the problem and find `𝑘′`. Finally, we can combine all the small `𝑘′`s we found into the desired `𝑘` in the original "circle".

The algorithm that performs what I described is called Pohlig-Hellman Algorithm. Its runtime complexity is $O(\sqrt{p_{max}})$ where $p_{max}$ is the largest prime factor in the decomposition of `𝑛`. It also makes sense, because the "heaviest" part in the algorithm is solving the ECDLP problem in the largest "circle" among the smaller "circles". For example, `n` might be a 128 bit number, and it decomposes into prime factors such that the largest of which is a 30 bit number. The algorithm reduces the complexity of solving the problem from $2^{64}$ to $2^{15}$, thus turning it form unfeasible to feasible.

Fortunately, SageMath's `discrete_log` function performs this algorithm in its implementation. To run the attack you can simply call the function:


```python
p = 183740305291166889900894879302858411333
a = 13
b = 37
E = EllipticCurve(GF(p), [a,b])
G = E(123764810000715262449972298016641419881,
144640915410606177233842123838934486566)
n = G.order()
print("number of bits in n:", n.nbits())
print("n's factors:", n.factor())
print("number of bits in n's greatest factor:", n.factor()[-1][0].nbits())
import random
private_key = random.randrange(n)
A = private_key * G
print("Calculating discrete_log...")
found_key = G.discrete_log(A)
assert found_key * G == A
assert private_key == found_key
print("success!")
```

In this code snippet we define an elliptic curve and a generator in it, and print the prime factors of its order. The output is:


```
number of bits in n: 128
n's factors: 2 * 3 * 13 * 101 * 211 * 21141581 * 38581057 * 60652309 *
2234328781
number of bits in n's greatest factor: 32
Calculating discrete_log...
success!
```

It can be seen that although the order of the generator is 128 bits long, it breaks down into prime factors such that the largest prime factor is 32 bit.

After that, just like in the previous attack - we choose a random private key, calculate a public key from it, and then given the generator and the public key, calculate the private key and verify that it is correct.


Although we are done, we haven't seen how the "small" circles are defined, how to map the points `𝐺` and `𝑃` to their corresponding points `𝐺′` and `𝑃′`, and how to combine all of the small solutions into a big solution. I will try to explain it intuitively here, because the next attack is based on this part as well.


Suppose we have a "circle" of order `3𝑥5𝑥7 = 105`, and its generator is `𝐺`. We'll define a point `𝐺′ = (5𝑥7)𝐺 = 35𝐺`, and look at the "circle" generated from it. If we proceed from `𝐺′` one "step", i.e. we will add `𝐺′` to itself it will be like advancing 35 steps from the point `35𝐺` in the original "circle", and we will reach point `2𝐺′ = 70𝐺`. If we advance one more "step", we will reach the point `3𝐺′ = 105𝐺 = 𝒪`, and if we advance from it another "step", we will reach the point `4𝐺′ = 35𝐺 = 𝐺′`, i.e. back to the starting point. The "circle" formed by `G′` is of order `3`, and it is no coincidence, because on a "circle" of order `105` it is possible to take exactly `3` "steps" of the size `35`. Similarly, we could create a "circle" of order `5` by defining the point `𝐺′ = (3𝑥7)𝐺 = 21𝐺`, and a circle of order `5` by defining `𝐺′ = (3𝑥5)𝐺 = 15𝐺`.

When we look at it the other way around it gets more interesting. Suppose that in the original "circle" we took `𝑛` steps from the point `G` and we reached the point `𝑛𝐺`. If also in the small "circle" we took `𝑛` steps from the point `𝐺′`, we would reach the point `𝑛′𝐺′` such that `𝑛 ≡ 𝑛′ (𝑚𝑜𝑑 3)`. And why is it interesting? Because the order of `𝐺′` is much smaller than the order of `𝐺` and therefore given `𝐺′` and `𝑛′𝐺′`, we can relatively easily find `𝑛′`. If we do it, and do it also for the two other prime factors of the order of the "circle", which are `5` and `7`, we would have the following values:

𝑛 ≡ $𝑛'_1$ (𝑚𝑜𝑑 3)\
𝑛 ≡ $𝑛'_2$ (𝑚𝑜𝑑 5)\
𝑛 ≡ $𝑛'_3$ (𝑚𝑜𝑑 7)

From these three values, `𝑛` can be easily found by using the Chinese Remainder Theorem, and thus solve the original problem.


## The Order Of The Generator Is Almost A Smooth Number, And The Private Key Is Small
Suppose that, similarly to the previous attack, we would get a curve in which the order of the generator decomposes into prime factors, but this time, the largest prime factor is too large for it to be practical to solve its ECDLP. For example, if the generator order is `256 bit`, but the largest prime factor is `128 bit`.
The Pohlig-Hellman Algorithm will require about $O(2^{64})$ operations in order to find the private key, which is unfeasible.


If we know that the private key used is relatively small, it can still be found efficiently.
Let's assume that the private key is `64 bit` (instead of `256 bit`). When the public key is created, the generator is multiplied by the private key and you get some point in the "circle" that the generator creates. Although the "circle" is the size of about $2^{256}$ points, this point will "fall" somewhere in the "first" $2^{64}$ points. There is no "interaction" between the private key and the points in the "circle" that correspond to larger values.


It is possible to run the Pohlig-Hellman algorithm, but "discard" the too large "circles", provided that the product of the orders of the remaining "circles" will be at least as the length of the private key. If found enough small prime factors, whose product is at least `64 bit`, then the corresponding "circles" will be sufficient enough to perform the same attack we saw earlier.

If earlier we had an easy life in terms of writing code, this time we will have to implement things ourselves, because SageMath's `discrete_log` function doesn't know that we want to "discard" some of the prime factors. The following code snippet does this:


```python
p = 88664572752015126127869404674421545790506871948117527783533589813159111825511
a = 13
b = 37
E = EllipticCurve(GF(p), [a,b])
G = E(19374976316789648652022260955836934561553454311144967863145605756652014623129,
      68630819472054489323664324766002023315775509214344811025345735680440707888471)
n = G.order()

print("Number of bits in n:", n.nbits())
factors = n.factor()
print("n's factors:", factors)

PRIVATE_KEY_BIT_SIZE = 64
import random
private_key = random.randrange(2^PRIVATE_KEY_BIT_SIZE)
P = private_key * G

print("We know that the private key is", PRIVATE_KEY_BIT_SIZE, "bits long")
print("Lets find which of the factors of G's order are relevant for finding the private key")
# find factors needed such that the order is greater than the secret key size
count_factors_needed = 0
new_order = 1
for p, e in factors:
    new_order *= p^e
    count_factors_needed += 1
    if new_order.nbits() >= PRIVATE_KEY_BIT_SIZE:
        print("Found enough factors! The rest are not needed")
        break
factors = factors[:count_factors_needed]
print("Considering these factors:", factors)

print("Calculating discrete log for each quotient group...")
subsolutions = []
subgroup = []
for p, e in factors:
    quotient_n = (n // p ^ e)
    G0 = quotient_n * G # G0's order is p^e
    P0 = quotient_n * P
    k = G0.discrete_log(P0)
    subsolutions.append(k)
    subgroup.append(p ^ e) # k the order of G0

print("Running CRT...")
found_key = crt(subsolutions, subgroup)
assert found_key * G == P
assert private_key == found_key
print("success!")
```

In this code snippet we define an elliptic curve and a generator in it, and print the prime factors of its order. The output is:

```
Number of bits in n: 256
n's factors: 2 * 3 * 29 * 2699 * 28751 * 831913766251 * 92996710252298530263979 *
84878782522781478604307230464271
```

The order of the generator is `256 bit`, and it decomposes into several prime factors, such that the two largest ones  are `77 bit` and `107 bit`. They are large enough so that it would be impractical to solve ECDLP. Then, a private key of `64 bit` is randomly generated, and a public key is calculated. In the next step we "collect" enough prime factors until we get an order with length of at least `64 bit`. The output is:

```
We know that the private key is 64 bits long
Lets find which of the factors of G's order are relevant for finding the private key
Found enough factors! The rest are not needed
Considering these factors: [(2, 1), (3, 1), (29, 1), (2699, 1), (28751, 1), (831913766251, 1)]
```

It can be seen that the two largest factors are redundant, and the largest factor we are left with is `40 bit`. In the next step, for each of the factors we are left with, we calculate points `𝐺′` and `𝑃′` as I explained earlier, and for each one of them we solves ECDLP. The results and the prime factors are kept in the lists `subsolutions` and `subgroups` respectively. Finally, all the results are combined using the Chinese Remainder Theorem into the private key, and we verify it is indeed correct.


## Not verifying That A Point Is On The Curve
Examining the definition of points addition in elliptic curves, we notice an interesting property where in points addition there is no use of the value `𝑏`, but only the values `​𝑎` and `𝑝`.This means adding points that lie on one curve can also be meaningful for another curve, which differs from it only by that value of `𝑏`. This is of course also true for multiplying a point by a number. If the user does not verify that the point they receive from the other party as a public key indeed lies on their curve, then they expose themselves to an Invalid Curve Attack.

Suppose two parties agreed on some elliptic curve $E_1$. An attacker can create a malicious curve $𝐸_2$, which has the same `𝑎` and `𝑝` values ​​as $𝐸_1$ but a different `𝑏` value. In curve $𝐸_2$ the attacker will choose a point `𝑃` whose order is small, for example `3`. Of course, the point `𝑃` ​​will not lie on $𝐸_1$, because it holds an equation with a different `𝑏` value than that of $𝐸_1$. The attacker will send the point `𝑃` ​​as their public key to the user. Let's say the user doesn't bother to verify that the point they receive is indeed on the curve $𝐸_1$ that the parties agreed upon. The user will take the public key they received from the attacker, multiply it with their private key, and reach a point that should be the shared secret point as we saw in the definition of the ECDH protocol. From the user's point of view, they will calculate the multiplication operation on the curve $𝐸_1$. But because the point `𝑃` ​​is not at all on it, but on $𝐸_2$, the user will actually calculate the multiplication operation on the curve $𝐸_2$. Later, the user will use the shared secret point to continue communication with the attacker. Let's assume that the parties use the `𝑥`-coordinate of the point as an AES encryption key. In this case, the user will encrypt some message and send it to the attacker.

Since the order of `𝑃` is `3` there are only `3` possibilities for the shared point for the user to calculate. The attacker will go through the these possible points, and find which of them corresponds to the key that successfully decrypts the encrypted message that the user sent. Given this point and the starting point `𝑃`, the attacker can deduce the remainder of dividing the user's private key by the number `3`. The attacker can send the user additional malicious `𝑃` points, with increasing orders, for example `5`, `7`, and so on. In this way the attacker can collect enough values ​​that represent remainders of divisions of the user's private key by small numbers. Finally the attacker can use the Chinese Remainder Theorem to calculate the user's private key, in the same way as we saw in the previous attack.

Here is a more intuitive explanation: an attacker can provide the user with a point on a very small "circle", for example of length `2`. The user will advance forward in this "circle" any number of steps and reach the destination point. The attacker knows the user's destination point, which can be one of `2` possibilities. Therefore the attacker can tell if the user has taken an even or odd number of steps on the circle. The attacker can provide the user with additional points on "circles" of lengths `3`, `5`, `7`, and so on. Until the attacker has enough such factors, each of which contains little information about the number of steps the user has taken. Finally the attacker can combine all these values ​​into the exact number of steps the user has taken, which is his private key.

The following code demonstrates the attack:

```python
from ecdsa.ecdsa import generator_128r1, curve_128r1
from Crypto.Util.number import long_to_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import random


# Select a curve and generator
curve = curve_128r1
G = generator_128r1
n = G.order()
p = curve.p()
a = curve.a()

# This is the private key of the other side, we don't know it and don't use it!
private_key = random.randrange(n)


# Both sides encrypt and decrypt data the same way
# key is the shared point's x coordinate, IV is point's y coordinate
def encrypt_data(shared_point, message):
    if shared_point.is_zero():
        x, y = 0, 0
    else:
        x, y = shared_point.xy()
    key = long_to_bytes(int(x)).rjust(16, b"\x00")
    iv = long_to_bytes(int(y)).rjust(16, b"\x00")
    cipher = AES.new(key, AES.MODE_CBC, iv)

    message = pad(message.encode(), 16)
    return cipher.encrypt(message)


def decrypt_data(shared_point, enc_message):
    if shared_point.is_zero():
        x, y = 0, 0
    else:
        x, y = shared_point.xy()
    key = long_to_bytes(int(x)).rjust(16, b"\x00")
    iv = long_to_bytes(int(y)).rjust(16, b"\x00")
    cipher = AES.new(key, AES.MODE_CBC, iv)

    decrypted = cipher.decrypt(enc_message)
    return unpad(decrypted, 16)


def ECDH(A):
    # Send our public key to the other side
    # Have them reach the shared point and
    # Send us an encrypted message using the shared point as key

    # This part takes place remotely and is unknown to the attacker
    shared_point = private_key * A
    message = "Inconceivable!"
    return encrypt_data(shared_point, message)


def brute_force_encrypted_message(A, encrypted_message, max_order):
    # Returns n such that n*A matches the key used to encrypt the message
    for i in range(1, max_order):
        shared_point = i * A
        try:
            # If both padding is correct and all characters are ascii
            # Then it is probably the correct encryption key
            decrypted = decrypt_data(shared_point, encrypted_message)
            decrypted = decrypted.decode()
            return i
        except:
            continue
    raise Exception("Did not find a value for one of the encrypted messages")


def find_curves_with_small_subgroup(p, a, max_order):
    # Yield tuples of (order, point) such that the point is
    # on a curve with the same a & p values, but different b
    # and the point's order is <= max_order
    orders_found = set()
    b = 0
    while True:
        b += 1
        if b == p:
            # Ran out of b values
            break
        if (4*a^3 + 27*b^2) % p == 0:
            # Curve is singular
            continue

        E = EllipticCurve(GF(p), [a, b])
        for _ in range(100):
            R = E.random_point()
            n = R.order()
            for f, e in n.factor():
                if f in orders_found:
                    continue
                if f > max_order:
                    break

                # Create a point with order f
                orders_found.add(f)
                P = (n // f) * R
                assert P.order() == f
                yield (f, P)


subsolutions = []
subgroup = []
max_order = 10000
upto = 1
for order, A in find_curves_with_small_subgroup(p, a, max_order):
    upto *= order
    print("Found point with order", order, "so now can find keys of size up to", upto)

    # Send this point as our public key and get an encrypted message from other side
    encrypted_message = ECDH(A)

    # Find the value n such that: private_key = n (mod order)
    key_mod_order = brute_force_encrypted_message(A, encrypted_message, max_order)

    # Save result to be used in CRT later
    subsolutions.append(key_mod_order)
    subgroup.append(order)

    # Found enough values to calculate private key
    if upto >= n:
        break

print("Found enough values! Running CRT...")
found_key = crt(subsolutions, subgroup)
print("Found private key", found_key)
assert private_key == found_key
print("success!")
```

In this code snippet, a curve and a generator are selected, the user randomly generates a private key and uses it for all uses of the ECDH protocol. The function `find_curves_with_small_subgroup` finds pairs of points and orders, such that the order of each point is relatively small, and the point is on some curve that is different from the original curve only by the value of `𝑏`. The code generates such pairs until enough pairs are found. For each pair, the public key is sent to the user and an encrypted message is received from them.

Brute force is performed on the encrypted message in order to find the value of the user's private key, modulo the current order. All of these results are saved, and finally we use the Chinese Remainder Theorem to calculate the user's private key and verify it is correct. In this case the parties agreed that the communication will be done in AES, with the encryption key that is the `x` coordinate of the shared secret point, and IV which is its `𝑦` coordinate.

The complexity of the attack is $𝑂(𝑛_{𝑚𝑎𝑥})$ where $𝑛_{𝑚𝑎𝑥}$ is the largest order among the orders of the malicious points. This is because the "heaviest" part of the attack is the brute force on the largest "circle" among the small "circles", and luckily for the attacker, they can control this value almost completely. Therefore this attack is relatively efficient in terms of complexity. As mentioned, the root of the problem in this case is that the user does not check that the point they received is even on the curve they are working with. In addition, the user uses the same private key in every new use of ECDH, which is not so safe.


## The Curve Is Singular
One of the important properties that an elliptic curve must have to be cryptographically secure is that it is non-singular. A non-singular curve is a curve whose certain value, called the "discriminant" of the curve, is nonzero. It holds when its parameters `𝑎` and `𝑏` satisfy the inequality:

$4a^3 + 27b^2 ≠ 0$

A curve that does not satisfy this inequality has a "problematic" point called a `singular point`. There are two types of such points: node and cusp. A node point exists on a curve that has a kind of loop that intersects itself at the singular point, and two different tangents to the curve can be passed through this point.
A cusp point is a point where the curve is "sharp", as if two lines come out of it, but there is only one tangent to the curve at that point.


<img src="images/singular.png" alt="Singular Elliptic Curves"  width="500">

In a node type point there is a double root, so the curve's equation can be written as:

$y^2 = (x-x_0)^2(x-x_1)\ \ \ \ (mod\ p)$

The curve can be "moved" left by replacing the variable $x$ with the variable $(𝑥 + 𝑥_0)$ and reach the form:

$y^2 = x^2(x+x_0-x_1)\ \ \ \ (mod\ p)$

So now the singular point is at the origin of the axes. The numerical value of $t = (x_0-x_1)$ can be used to create a mapping between points on the curve to integers, such that the addition operation between points on the curve will be equivalent to the operation of multiplication between numbers. For each point `(𝑥, 𝑦)` we will match the number
$\frac{y+\sqrt{t}x}{y-\sqrt{t}x}$. In particular, to a pair of points `𝐺` and `𝑄` such that `𝑄 = 𝑛𝐺` we can map numbers `𝑔` and `𝑞` such that $𝑞 ≡ 𝑔^𝑛\ \ \ \ (mod\ p)$, and this is a "normal" DLP problem. To illustrate this process, I've added a link to an example with small numbers in the references at the end of the article. In the mapping we did, we used the equation of the linear lines $y+\sqrt{t}x$ and $y-\sqrt{t}x$, and those are the lines that correspond to the two tangents that can be drawn at the singular point (after we "moved" the curve), which is basically why this attack can be used.

Such a DLP problem can be solved efficiently with the help of the Pohlig-Hellman algorithm, which we have already seen before, because it can also be used on integers instead of points on the curve. In the context of points, we saw that the algorithm is useful when the order of the generator is a smooth number. Unlike a "circle" of points on a curve, which may have any order, in the field of integers modulo a prime number `𝑝` the order is `𝑝 − 1`. If `𝑝 − 1` is a smooth number, then the algorithm will solve the DLP problem efficiently, thus finding the private key `n`.

The following code snippet does this:

```python
p = 102360775616927576983385464260307534406913988994641083488371841417601237589487
a = -3
b = 2
assert (4*a^3 + 27*b^2) % p == 0

Gx = 1777671135698746847568710125129424132255529153914112337834835240247819869964
Gy = 6786424314307625790108882554225666781375821855884993473586521771737454762217
Qx = 45541468695354471317248123146376609839909398850045396377931300808635064950836
Qy = 42191909885728105279718027025083923092282618497451601162405594991792376530066

x = GF(p)["x"].gen()
f = x^3 + a*x + b
roots = f.roots()

assert len(roots) == 2 # two roots, so one must be double
if roots[0][1] == 2:
    double_root = roots[0][0]
    single_root = roots[1][0]
else:
    double_root = roots[1][0]
    single_root = roots[0][0]

print("double root:", double_root)
print("single root:", single_root)

# map G and Q to the new "shifted" curve
Gx = (Gx - double_root)
Qx = (Qx - double_root)

# Transform G and Q into numbers g and q, such that q=g^n
t = double_root - single_root
t_sqrt = t.square_root()

def transform(x, y, t_sqrt):
    return (y + t_sqrt * x) / (y - t_sqrt * x)

g = transform(Gx, Gy, t_sqrt)
q = transform(Qx, Qy, t_sqrt)
print("g:", g)
print("q:", q)

# Find the private key n
print("Factors of p-1:", factor(p-1))
print("Calculating discrete log for g and q...")
found_key = discrete_log(q, g)
print("Found private key:", found_key)

from Crypto.Util.number import long_to_bytes
print("The secret is:", long_to_bytes(found_key).decode())
```



In this code snippet, we define the parameters of an elliptic curve, and verify it is indeed singular. We find the roots of the polynomial corresponding to the curve, and identify which of them is the double root. We use the double root to "move" the curve, and reach the "moved" points `𝐺` and `𝑄`. Then calculate $\sqrt{t}$ from the roots that we found and use it to map the points `𝐺` and `𝑄` to the numbers `𝑔` and `𝑞`. We print the decomposition of `𝑝 − 1` to its prime factors (to verify that the DLP can indeed be solved efficiently). Finally we calculate the DLP and interpret the result as a string. 

The output is:
 ```
double root: 1
single root:
102360775616927576983385464260307534406913988994641083488371841417601237589485
g: 79308184675041981395063385790064051127319168083579208141274962436724168376607
q: 72551144069373709737718398534799929820619379063890479978458954196900267190559
Factors of p-1: 2 * 41 * 2422091127107 * 3224683479179 * 3224849279789 * 3269304069319
* 3792634171577 * 3997021218613
Calculating discrete log for g and q...
Found private key:
30943506368388267314266516224984737426569114488424608324579076903023329506337
The secret is: Digital Whisper is pretty great!
 ```

This time I hid a message in the private key itself. It should be noted that because it is a singular curve, it is not possible in SageMath to create it in a normal way, define points on it and perform operations with them as we did before. In this code I defined the coordinates of the points as constant variables. To calculate the point `𝑄` I multiplied the private key with generator myself using my own implementation of the Double And Add algorithm.


## The Curve Is Supersingular
Given an elliptic curve modulo `𝑝`, and a generator whose order is `𝑛`, the Embedding Degree of the curve with respect to the generator is defined to be the smallest number `k` that satisfies the equation $p^k ≡ 1\ \ \ \ (mod\ 𝑛)$. With certain transformations, the ECDLP problem can be reduced into a DLP problem in a field of order $𝑝^𝑘$. The value `𝑘` is usually a very large number (about same size as `𝑝` itself), but when it is relatively small (say, smaller than `6`), the curve is called `supersingular` and it becomes feasible to solve this DLP problem efficiently. This attack is called MOV attack, named after its three inventors (Menezes-Okamoto-Vanstone).

The transformations I mentioned are functions that receive two points, and return some number in the complex numbers field. Transformations that can be used are Weil Pairing or Tate Pairing, and we will use them as a black box. Such transformation `𝑇` satisfies the following property for every pair of points `𝑃`, `𝑄`:

$T(mP, nQ)=T(P,Q)^{mn}$


Therefore, given two points `𝐺` and `𝑄 = 𝑚𝐺`, we can randomly select a third point `𝑅` and calculate the two values: \
$g = T(G, R)$ \
$q = T(Q, R)=T(mG,R)=T(G,R)^m=g^m$
From here we can solve the DLP problem for `𝑔` and `𝑞` in a field of order $p^k$, thus finding the private key `𝑚`. I included a link to a more detailed explanation of the math behind this attack, in the references at the end of the article.

The following code snippet performs this attack:

```python
p = 682209701131405092329016993551
a = -35
b = 98
E = EllipticCurve(GF(p), [a, b])
G = E(516365702870683577608927237052, 
      524474557735717484100814381066)

# Find embedding degree k
Gn = G.order()
k = 1
while p^k % Gn != 1:
    k += 1
print("Found k:", k)

# Select private key, and calculate public key Q
private_key = 5072587499125503347
Q = private_key * G

# Define new curve mod p^k and the points on it
Ek = EllipticCurve(GF(p ^ k), [a, b])
Gk = Ek(G)
Qk = Ek(Q)
Rk = Ek.random_point()

# Find a point T with order d such that d divides G's order
m = Rk.order()
d = gcd(m, Gn)
Tk = (m // d) * Rk
assert Tk.order() == d
assert (Gn*Tk).is_zero() # Point INFINITY

# Using T, pair G and Q to integers g and q such that q=g^n (mod p^k)
g = Gk.weil_pairing(Tk, Gn)
q = Qk.weil_pairing(Tk, Gn)
# Alternatively:
#g = Gk.tate_pairing(Tk, Gn, k)
#q = Qk.tate_pairing(Tk, Gn, k)

# Make sure the pairing did not break anything
assert g ^ private_key == q

print("Calculating private key...")
found_key = q.log(g)
assert found_key == private_key
print("success!")

from Crypto.Util.number import long_to_bytes
print("The private key is:", long_to_bytes(found_key).decode())
```

In this code snippet we define a curve and its generator, and calculate its Embedding Degree value, which is `2` in this case, therefore it is practical to perform the attack. We define a curve identical to the original curve, except that the calculations are done modulo $𝑝^𝑘$ instead of modulo $𝑝$. The two points `𝐺` and `𝑄` are also on the new curve. Then we find a third point whose order divides `𝑛`.

Using the third point, we map the points `𝐺` and `𝑄` to the numbers `𝑔` and `𝑞` and calculate the discrete logarithm for them. Finally, we verify  the result obtained is indeed correct.

The output is:
```
Found k: 2
Calculating private key...
success!
The private key is: Festivus
```

From a computational point of view, today there are Index Calculus algorithms that can solve the DLP problem in a relatively efficient way, and they do it with complexity of $e^{O((log\ p^k)^{1/3}(log\ log\ p^k)^{2/3})}$. This expression may seem scary, but compared to ECDLP algorithms whose complexity is $O(\sqrt{p})=e^{O(log\ p)}$, it can be seen that it is easier to solve the DLP problem, assuming that the Embedding Degree (denoted by `𝑘`) is indeed small.



## The Curve Is Anomalous
If a certain curve has the property that the order of the curve (the number of points on it) is exactly equal to the modulus `𝑝`, then it is called an `Anomalous Curve` and is vulnerable to an attack called Smart's Attack. This attack uses `𝑝-adic numbers`. Such a number can be represented as a sum of powers of `p` (positive and negative) with coefficients. Formally, such a number `s` is a series of the form:

$s=\sum_{i = -k}^{\infty} a_{i}p^i = a_{-k}p^{-k} + \cdots + a_0 + a_1p + a_2p^2 + \cdots$

When the coefficients are integers in the range $0 ≤ 𝑎_𝑖 < 𝑝$, and the sum can be infinite in the direction of the positive powers of `𝑝`. In such numbers, we "look at" the digits from right to left instead of from left to right, and therefore such a series can converge to some value. Such numbers belong to a different number system than the one we are familiar with, and behave very differently from the "normal" mathematical rules. An entire separate article can be written only about this topic, and for those who are interested in it, I have included in the references at the end of the article a link to a video that presents it in a relatively clear way.

In any case, in this attack a new curve is created from the given curve, which is defined to be over the p-adic numbers. Given two points `𝐺` and `𝑄 = 𝑚𝐺` on the original curve, we map them to corresponding points on the new curve. From the coordinates of the obtained points it is easy to calculate `𝑚`.

The following code performs the attack:

```python
def lift(P, E, p):
    # lift point P from old curve to a new curve
    Px, Py = map(ZZ, P.xy())
    for point in E.lift_x(Px, all=True):
         # take the matching one of the 2 points corresponding to this x on the p-adic curve
        _, y = map(ZZ, point.xy())
        if y % p == Py:
            return point


p = 82880337306360052550952380657384418102169134986290141696988204552000561657747
a = 26413685284385555604181540288021678971301314378522544469879270355650843743231
b = 10017655579196313780863100027113686719855502076415017585743221280232958057095
E = EllipticCurve(GF(p), [a, b])
G = E(37991937053350834320678619330546903567320901767090609881924528835279022654346,
      28947208718252880061735762506756351277969075978732800286053352115837132331595)
assert E.order() == p

private_key = 28153370716511608040616395150859085058202177279382452583684367923334520519740
P = private_key * G

# Lift the points to some new curve over p-adic numbers
E_adic = EllipticCurve(Qp(p), [a+p*13, b+p*37]) 
G = p * lift(G, E_adic, p)
P = p * lift(P, E_adic, p)

# Calculate discrete log
Gx, Gy = G.xy()
Px, Py = P.xy()
found_key = int(GF(p)((Px / Py) / (Gx / Gy)))
assert found_key == private_key
print("success!")

from Crypto.Util.number import long_to_bytes
print("The private key is:", long_to_bytes(found_key).decode())
```

In this code snippet, a lift function is defined, which receives a point on the original curve, and corresponds to it a point on the new curve. Then a we define an elliptic curve and a generator in it, and verify that the order of the curve is indeed `p`. We choose a private key and calculate the corresponding public key, Then perform the attack. We define a new curve over the 𝑝-adic numbers, and map the original points `𝐺` and `𝑃` to corresponding points in the new curve using the lift function and multiplying them by `𝑝`.

For each new point, we calculate the ratio between its `𝑥` coordinate and its `𝑦` coordinate. The quotient of these two values is the ECDLP solution of the original points.

The output is:
```
success!
The private key is: >>>>> Extraordinarily Nice <<<<<
```

The reason this calculation works is related to the fact that the number of points on the curve is exactly `𝑝`. This property allows us to perform several mappings, the last of which maps between points on a curve over 𝑝-adic numbers, to numbers modulo $p^2$. This mapping has the property that the ratio between the pair of numbers corresponding to the two original points is exactly the result of the logarithm of the two points. We will leave all these mappings as a black box, but at the end of the article I added references to the relevant mathematical explanations.


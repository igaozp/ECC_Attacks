# ECDSA Attacks
## Not Hashing The Message Before Signing It
We saw that in the process of signing a message, first the hash of the message is calculated, and the high bits of the hash are used in the signature calculation. Let's assume that in some implementation of a signature signing and verification, this hashing step is skipped, and instead of taking the high bits of the hash, the bits are taken from the message as it is. In such an implementation, the only part of the message that affects its signature is the beginning of the message. In other words, if we have a message and its signature, we can keep the beginning of the message and change the rest of it, and the signature will remain valid. It's a really simple attack.


Suppose, for example, that you write the following message to your bank and sign it without hashing it:
```
"Please transfer 1,000$ from my account to GitHub so that they can continue hosting awesome repositories"
```
The bank will successfully verify this message, and will perform the action. Some ... attacker ... could create the the following message:
```
"Please transfer 1,000$ from my account to GitHub and 1,000,000$ to Eli Kaski"
```
And use the signature you just created. The signature will also be valid for this message, and the bank will perform the action. Not good (well, depends to who).

The following code demonstrates the attack:

```python
from ecdsa import SigningKey, NIST256p

signing_key = SigningKey.generate(NIST256p)
verifying_key = signing_key.verifying_key

class MyHash:
    def __init__(self, data):
        self.data = data

    def digest(self):
        return self.data

# Sign the message and verify the signature
message = "Please transfer 1,000$ to GitHub"
signature = signing_key.sign(message.encode(), hashfunc=MyHash)
assert verifying_key.verify(signature, message.encode(), hashfunc=MyHash)

# Construct an evil message and verify the original message's signature is valid for it as well
evil_message = "Please transfer 1,000$ to GitHub and 1,000,000$ to Eli Kaski"
assert verifying_key.verify(signature, evil_message.encode(), hashfunc=MyHash)
print("success!")
```

In this code snippet, the library ecdsa is used, along with a known curve. We define a class that should implement a hash function but does not do this, and instead leaves the message as it is. Therefore when signing a message, only the first bits from the original message are used, instead of from its hash. Then the message is signed and verified successfully. A malicious message is then created, and the code verifies that the signature of the original message also matches the malicious message.

In such a scenario we may have not obtained the private key in order to generate our own new signatures, but given one signature, we can sign as many messages as we want, provided they start with the same prefix.


## Reusing The Same Value Of `k` In Different Signatures
As part of the message signing process, the user is required to randomly generate a `𝑘` value and use it to sign the message. It is very important to use different `𝑘` values ​​in different signatures. Otherwise - given two signed messages where the user used the same value `𝑘` instead of re-generating it, an attacker could calculate the user's private key.

As mentioned, during message signing the user publicly sends $r=x_1\ \ \ \ (mod\ p)$ and and $s=k^{-1}(z+rd_A)$. Assuming that the user signed two different messages corresponding to $𝑧_1$ and $𝑧_2$, and publicly sent two pairs of values $𝑟, 𝑠_1$ and $𝑟, 𝑠_2$, i.e. used the same `𝑘` value in these two signatures. We note that:

$s_1-s_2=k^{-1}(z_1+rd_A)-k^{-1}(z_2+rd_A)=k^{-1}(z_1+rd_A-z_2-rd_A)=k^{-1}(z_1-z_2)$

From this, the attacker can find the value of `𝑘` by calculating:

$\displaystyle k=\frac {z_1-z_2}{s_1-s_2}$

After the attacker found `𝑘`, they can calculate the user's private key from one of the signatures. Note that:

$r^{-1}(ks-z)=r^{-1}(kk^{-1}(z+rd_A)-z)=r^{-1}(z+rd_A-z)=r^{-1}rd_A=d_A$

Given the values ​​of `𝑟`, `𝑠` and `𝑧` of a message and its signature, and the value of `𝑘` that the attacker found, the attacker can calculate $d_A=r^{-1}(ks-z)$. From this point, the attacker can sign any message they want, on behalf of the user whose private key they obtained.

The following code snippet performs this attack:

```python
from ecdsa.ecdsa import curve_256, generator_256, Public_key, Private_key
from Crypto.Util.number import bytes_to_long,  long_to_bytes
from hashlib import sha256
import random

# Select a curve and generator
curve = curve_256
generator = generator_256
n = generator.order()

# Create private key and public keys
secret_key = 6743529130774090927928101169617481154782309
public_key = Public_key(generator, generator * secret_key)
private_key = Private_key(public_key, secret_key)

# Sign 2 messages using the same k
k = random.randrange(curve.p())
message1 = "Life is like a box of chocolates."
message2 = "You never know what you're gonna get."
z1 = bytes_to_long(sha256(message1.encode()).digest())
z2 = bytes_to_long(sha256(message2.encode()).digest())

signature1 = private_key.sign(z1, k)
signature2 = private_key.sign(z2, k)

# Given the two messages and their signatures, find k
found_k = (z1 - z2) * inverse_mod(signature1.s - signature2.s, n) % n
assert k == found_k

# Given k and one of the messages, find the private key
found_key = inverse_mod(signature1.r, n) * (found_k * signature1.s - z1) % n
assert found_key == secret_key
print("success!")
print("The secret is:", long_to_bytes(found_key).decode())
```


In this code snippet, the library ecdsa is used, along with a known curve. We define a private key and use it to sign two messages. The value of `𝑘` is randomly generated, but it remains the same for the two signatures. Given the two messages and their signatures, the code performs the calculation we saw to find `𝑘`. Finally, we use the value of `𝑘` we found to calculate the private key as we saw. The output is:

```
Success!
The secret is: Mistakes were made
```

It is interesting to note that this attack was actually used in 2010, when Sony insecurely implemented  their signing mechanism on the PlayStation console software. Sony used a static value of `𝑘` for its signatures, which allowed attackers to obtain Sony's private key using the above calculation. This led to the ability to sign any code, and make PlayStation agree to run it. Later this ability was used to install pirated and unofficial games on the console.


## Generating `k` Values Insecurely
If the user chooses `𝑘` in an insufficiently random way, then the private key can be found. For example, if the attacker knows that `𝑘` is in a very small range of values, or some of the bytes of `𝑘` are known to the attacker, then it is possible by a simple brute force to find the user's private key given a single signed message. The attacker will run the calculation we saw in the previous attack for the different `𝑘` values, until they reach the correct value and obtains the private key from it.

To overcome this problem, sometimes users randomly generate some value, calculate its hash with some hash function, and use the result as `𝑘`. This method might cause problems. Suppose, for example, that the order of generator `𝑛` is `256 bit`, and the selected hash function is SHA-1. The output of this function is a `160 bit` number. In calculations modulo `𝑛`, it is known that the value of `𝑘` contains 96 zeros at the beginning, meaning `𝑘` is a relatively small number. In such a situation, the `𝑘` values ​​are said to be `biased`, and given several messages that are signed with the same private key, the private key can be found.

The attack is based on an algebraic structure called Lattice. Informally, a lattice can be thought of as a set of vectors in an `𝑚`-dimensional space, which can be expressed as a linear combination of "basis" vectors with integer coefficients. Mathematically, if $`\{b_1,\dots,b_d\}`$ are the basis vectors over $ℝ^𝑚$, then the Lattice corresponding to them is $L=$ $`\{\sum_{i=1}^d a_ib_i\mid a_i \in Z\}`$. In this structure there is the known problem: given the basis of a lattice, find the shortest vector that exists in the lattice. In this context, informally, a "short vector" is a vector whose elements are as close to zero as possible. This problem is called the Shortest Vector Problem (SVP), and it is considered NP-hard. There are algorithms that solve a similar but easier problem - finding some short vector, i.e. a vector relatively "close" to the shortest vector in the lattice. This problem is called the Closest Vector Problem (CVP), and one of the algorithms that solves it is called the Lenstra-Lenstra-Lovász (LLL) algorithm. In this attack we will use this algorithm as a black box.


Given `𝑑` signed messages, it is possible to build a lattice that contains the vector $(𝑘_1, \dots , 𝑘_𝑑)$, where each element of the vector is a `𝑘` value that corresponds to one signature. The LLL algorithm will find an approximation to the shortest vector in this lattice. Since the values ​​of `𝑘` are known to be small, there is a high probability that the short vector that the algorithm finds will contain at least one correct `k` element. Once a correct `𝑘` is found, the private key can be calculated as we saw in the previous attack.

To construct this lattice, its basis vectors need to be defined. I have included in the references at the end of the article a link to an article that explains how these basis vectors are defined. Technically, the basis vectors of the lattice can be represented as a matrix, such that each row in it consists of the elements of one basis vector. To improve the accuracy of the LLL algorithm, it is recommended to add to this matrix two columns that contain information about the expected size of the `𝑘` values ​​and the ratio between `𝑘` and `𝑛`. This improvement is also explained in the reference I attached. The following code snippet demonstrates this attack:

```python
from ecdsa.ecdsa import curve_256, generator_256, Public_key, Private_key
from Crypto.Util.number import bytes_to_long, long_to_bytes
from hashlib import sha1
import random


def build_matrix(signatures, bias, q):
    # M matrix should be:
    """
    [
            B 0   m'1 m'2 m'2 ... m'n
            0 B/q r'1 r'2 r'3 ... r'n
            0 0
            0 0        q * I
            0 0
    ]
    where:
        m' = s^-1 * m
        r' = s^-1 * r
    """

    # Construct the first 2 rows of M:
    row1 = [bias, 0]
    row2 = [0, bias / q]
    for m, r, s in signatures:
        row1.append((inverse_mod(s, q) * m) % q)
        row2.append((inverse_mod(s, q) * r) % q)
    top_rows = Matrix(QQ, [row1, row2])

    # Construct the q*I block along with 2 columns of zeros
    zero_cols = zero_matrix(QQ, len(signatures), 2)
    qI = q * identity_matrix(QQ, len(signatures))
    bottom_rows = block_matrix([[zero_cols, qI]])

    # Combine all rows into one matrix
    M = top_rows.stack(bottom_rows)
    return M


def find_private_key(L, signatures, public_key):
    # Check if any valid k was found in L
    generator = public_key.generator
    q = generator.order()
    for row in L.rows():
        for i in range(len(signatures)):
            m,r,s = signatures[i]
            # Skip the first two vector components we used to improve LLL
            possible_k = row[i+2]
            # LLL might have swapped the sign of the found short vectors
            for k in [possible_k, -possible_k]:
                d = inverse_mod(r,q)*(k*s-m) % q
                if d*generator == public_key.point:
                    return d


# Select a curve and generator
curve = curve_256
generator = generator_256
q = int(generator_256.order())

# Create private key and public key
secret_key = 1793056234309773077862125006843383726029262764680727851636
public_key = Public_key(generator, generator * secret_key)
private_key = Private_key(public_key, secret_key)

# Sign some messages
messages_to_sign = [
    "And then I go and spoil it all",
    "By saying somethin' stupid like",
    "I love you"
]

signatures = []
for message in messages_to_sign:
    message_hash = bytes_to_long(sha1(message.encode()).digest())
    k = bytes_to_long(sha1(long_to_bytes(random.randrange(q))).digest())
    signature = private_key.sign(message_hash, k)
    signatures.append((message_hash, signature.r, signature.s))

# Given the messages and their signatures, retrieve the private key

# Build the matrix out of the signatures
# We know that k < 2^160 because it is the result of sha1
bias = 2^160
M = build_matrix(signatures, bias, q)

# Calculate the closest short vector
L = M.LLL()

# Find the private key!
found_key = find_private_key(L, signatures, public_key)
assert found_key == secret_key
print("success!")
print("The secret is:", long_to_bytes(found_key).decode())
```

In this code snippet a standard curve is used, a private key is selected and the corresponding public key is calculated from it. 3 messages are created and are signed with 3 random `k` values that are a result of SHA-1 hash function. Then we create the matrix corresponding to the basis of the lattice as explained in the article, and run the LLL algorithm on it. Afterwards, we go through the rows of the resulting matrix and check if a correct value of any `𝑘` is found in one of them.

The check is performed by calculating the private key from the potential `𝑘`, as we saw in the previous attack, and checking if the received key is indeed correct. Finally, we make sure that the private key found is indeed correct. The output is:

```
success!
The secret is: I am Jack's broken heart
```

The complexity of this attack is as the complexity of the LLL algorithm,which is $O(d^6\ \log^3B)$, where `𝐵` indicates the length of the bias of `𝑘` ($2^{160}$
in our case), and `𝑑` indicates the number of signed messages (3 in our case). The question arises as to what is the minimum number of signed messages that we are required to use in order to be able to run the attack. The answer to this is 
$\displaystyle d=O(\frac {\log n}{\log n-\log B})$ where `𝑛` is the order of the generator and `𝐵` is the bias. An explanation for this appears in the second link in the references I attached to this topic at the end of the article.

In practice, a variation of this attack can also be run in cases where the upper bits of `𝑘` are known, or just any bits of `𝑘`. The attack can be run even if the value of only one bit is known, or even if the value of only one bit is known with a probability greater than 50%! But of course, in these cases, many more signed messages are required in order to perform the attack.

## Not Verifying The Generator Is Valid
We saw that in the process of signature verification, the signing party sends the pair of values `​𝑟` and `𝑠` to the verifying party. In browsers that implement the HTTPS protocol, for example, it is customary to send this pair of values ​​in a certificate, which may also contain data on the curve that the signing party used. The verifying party needs to make sure that the curve data found in the certificate does match the previously agreed upon curve. If they don't, it can be problematic.

Suppose that in a certain curve Alice has a private key $d_A$ and a public key $𝑃_𝐴$ that corresponds to it, which means that $𝑃_𝐴 = 𝑑_𝐴𝐺$ for the generator `𝐺` in this curve. With the private key $𝑑_𝐴$, Alice can sign her messages as we saw in the ECDSA protocol definition. Suppose that the party verifying the signature also receives the generator `𝐺` from the user, and does not verify that the generator received from the user is indeed the agreed upon generator. An attacker can send as a generator the point that is Alice's public key, $𝐺^′ = 𝑃_𝐴$. The attacker will choose as a "fake" private key the value $𝑑_𝐴^′ = 1$, and hence it is clear that $𝑃_𝐴 = 𝑑_𝐴^′𝐺^′$. This means that the attacker can "prove" that they have the private key that matches Alice's public key. Thus an attacker can create any message they want, and calculate for it a pair of values `​𝑟` and `𝑠` in the usual way with $𝑑_𝐴^′$, and the resulting signature will be successfully verified.



Intuitively, in the process of signature verification, the signing party proves that they are indeed the "owner" of the public key, which is actually a "destination" point on the curve. This is because only the signer knows how many steps to take from the starting point to reach the destination point. If the verifying party does not verify that the starting point received from the user is indeed the true starting point, then an attacker can decide that the starting point is the destination point, and that the number of steps to take from it is zero. All other parts of the signature verification remain the same, and the signature will be verified successfully. This attack is called Curveball.

This attack can be generalized with additional values. The attacker will choose some value `𝑥`, and calculate $𝐺^′ = 𝑥𝑃_𝐴$. The fake private key will be $𝑑'_𝐴 = 𝑥^{−1}\ \ \ \ (mod\ n)$. Then clearly it holds that $𝑑'_𝐴𝐺^′ = 𝑥^{−1}𝑥𝑃_𝐴 = 𝑃_𝐴$.

The following code demonstrates the attack:
```python
from ecdsa.ecdsa import generator_256
from Crypto.Util.number import bytes_to_long
from hashlib import sha256
import random


def hash_message(message):
    return bytes_to_long(sha256(message.encode()).digest())

def verify(public_key, G, message, r, s):
        n = G.order()
        if r < 1 or r > n - 1 or s < 1 or s > n-1:
            return False
        hash = hash_message(message)
        u1 = (hash * inverse_mod(s, n)) % n
        u2 = (r * inverse_mod(s, n)) % n
        P = u1 * G + u2 * public_key
        return P.x() % n == r

def sign(private_key, G, message):
    n = G.order()
    k = random.randrange(n)
    hash = hash_message(message)

    r = (k * G).x() % n
    s = inverse_mod(k, n) * (hash + r * private_key) % n
    return r, s


# Create private and public keys
G = generator_256
n = G.order()
private_key = random.randrange(n)
public_key = private_key * G

# Sign a message and verify it
message = "Let me be the one that shines with you"
r, s = sign(private_key, G, message)
assert verify(public_key, G, message, r, s)

# Create a fake private key and generator that match the original public key
x = random.randrange(n)
fake_G = x * public_key
fake_private_key = inverse_mod(x, n)
assert fake_private_key != private_key
assert fake_G != G

# Sign an evil message and verify it using the same public key
evil_message = "Where did I go wrong?"
r, s = sign(fake_private_key, fake_G, evil_message)
assert verify(public_key, fake_G, evil_message, r, s)
```

In this code snippet we choose a known generator, a private key and a public key. We sign a message and make sure it is successfully verified. Then we create a fake private key and a fake generator such that both match the original public key. An evil message is signed with the fake key, and finally the fake signature is successfully verified with the original public key. The problem with this code is that the verification algorithm does not verify that the generator `𝐺` matches the public key. Although in this attack we did not find the user's private key, an attacker can exploit the incorrect implementation for signature verification, and create a signature that is successfully verified. However, the attacker cannot create "real" signatures that will indeed be successfully verified in a correct implementation of signature verification.

It is interesting to note that this is a real vulnerability that existed in the Windows CryptoAPI architecture. In the function responsible to verify the signature of a certificate, there was insufficient verification of the parameters of the curve, in cases where they were included in the certificate itself. In particular, there was no check that the generator is indeed the generator that corresponds to the public key. An attacker could create fake certificates that are considered trusted because they look like they were signed by a trusted Certificate Authority. This was done by adding malicious curve fields to certificate, and choosing the generator in the way I described. The vulnerability was discovered by the NSA organization, fixed in 2020 and received the number CVE-2020-0601.

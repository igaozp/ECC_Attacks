# ECDSA 攻击
## 签名前不对消息进行哈希
我们知道，在签名消息的过程中，首先计算消息的哈希值，然后在签名计算中使用哈希值的高位比特。假设在某个签名和验证的实现中，跳过了这个哈希步骤，而是直接从消息本身提取比特，而不是从哈希值中提取高位比特。在这样的实现中，消息中唯一影响其签名的部分是消息的开头。换句话说，如果我们有一条消息及其签名，我们可以保持消息的开头不变并修改其余部分，签名仍然有效。这是一个非常简单的攻击。


例如，假设您向银行写了以下消息并在没有哈希的情况下签名：
```
"Please transfer 1,000$ from my account to GitHub so that they can continue hosting awesome repositories"
```
银行将成功验证此消息，并执行该操作。某些...攻击者...可以创建以下消息：
```
"Please transfer 1,000$ from my account to GitHub and 1,000,000$ to Eli Kaski"
```
并使用您刚刚创建的签名。该签名对此消息也有效，银行将执行该操作。这不好（嗯，取决于对谁而言）。

以下代码演示了这种攻击：

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

在这个代码片段中，使用了 ecdsa 库以及一条已知曲线。我们定义了一个应该实现哈希函数但实际上没有这样做的类，而是保持消息原样。因此，在签名消息时，只使用原始消息的前几个比特，而不是其哈希值的比特。然后对消息进行签名并成功验证。接下来创建了一条恶意消息，代码验证了原始消息的签名也匹配这条恶意消息。

在这种情况下，我们可能没有获得私钥来生成新的签名，但是给定一个签名，我们可以签署任意多条消息，只要它们以相同的前缀开头。


## 在不同签名中重复使用相同的 `k` 值
作为消息签名过程的一部分，用户需要随机生成一个 `k` 值并使用它来签署消息。在不同的签名中使用不同的 `k` 值非常重要。否则——如果给定两条签名消息，其中用户使用了相同的 `k` 值而不是重新生成它，攻击者就可以计算出用户的私钥。

如前所述，在消息签名期间，用户公开发送 $r=x_1\ \ \ \ (mod\ p)$ 和 $s=k^{-1}(z+rd_A)$。假设用户签署了对应于 $z_1$ 和 $z_2$ 的两条不同消息，并公开发送了两对值 $r, s_1$ 和 $r, s_2$，即在这两个签名中使用了相同的 `k` 值。我们注意到：

$s_1-s_2=k^{-1}(z_1+rd_A)-k^{-1}(z_2+rd_A)=k^{-1}(z_1+rd_A-z_2-rd_A)=k^{-1}(z_1-z_2)$

由此，攻击者可以通过计算以下公式找到 `k` 的值：

$\displaystyle k=\frac {z_1-z_2}{s_1-s_2}$

在攻击者找到 `k` 之后，他们可以从其中一个签名中计算出用户的私钥。注意：

$r^{-1}(ks-z)=r^{-1}(kk^{-1}(z+rd_A)-z)=r^{-1}(z+rd_A-z)=r^{-1}rd_A=d_A$

给定消息及其签名的 `r`、`s` 和 `z` 值，以及攻击者找到的 `k` 值，攻击者可以计算 $d_A=r^{-1}(ks-z)$。从这一点开始，攻击者可以代表私钥被获取的用户签署任何他们想要的消息。

以下代码片段执行此攻击：

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


在这个代码片段中，使用了 ecdsa 库以及一条已知曲线。我们定义了一个私钥并使用它来签署两条消息。`k` 的值是随机生成的，但在两个签名中保持相同。给定两条消息及其签名，代码执行我们看到的计算来找到 `k`。最后，我们使用找到的 `k` 值按照我们看到的方法计算私钥。输出是：

```
Success!
The secret is: Mistakes were made
```

有趣的是，这种攻击实际上在2010年被使用过，当时索尼在 PlayStation 游戏机软件上不安全地实现了他们的签名机制。索尼在其签名中使用了静态的 `k` 值，这使得攻击者能够使用上述计算获得索尼的私钥。这导致了能够签署任意代码，并使 PlayStation 同意运行它。后来，这种能力被用于在游戏机上安装盗版和非官方游戏。


## 不安全地生成 `k` 值
如果用户以不够随机的方式选择 `k`，那么私钥就可以被找到。例如，如果攻击者知道 `k` 在一个非常小的值范围内，或者 `k` 的某些字节对攻击者是已知的，那么通过简单的暴力破解，给定一条签名消息，就可以找到用户的私钥。攻击者将对不同的 `k` 值运行我们在上一个攻击中看到的计算，直到达到正确的值并从中获得私钥。

为了克服这个问题，有时用户会随机生成某个值，用某个哈希函数计算其哈希值，并将结果用作 `k`。这种方法可能会导致问题。例如，假设生成元 `n` 的阶是 `256 位`，而选择的哈希函数是 SHA-1。该函数的输出是一个 `160 位` 数字。在模 `n` 的计算中，已知 `k` 的值在开头包含96个零，这意味着 `k` 是一个相对较小的数字。在这种情况下，`k` 值被称为有 `偏差`，给定几条用相同私钥签署的消息，就可以找到私钥。

该攻击基于一种称为格（Lattice）的代数结构。非正式地说，格可以被认为是 `m` 维空间中的一组向量，这些向量可以表示为具有整数系数的"基"向量的线性组合。数学上，如果 $`\{b_1,\dots,b_d\}`$ 是 $ℝ^m$ 上的基向量，那么与它们对应的格是 $L=$ $`\{\sum_{i=1}^d a_ib_i\mid a_i \in Z\}`$。在这个结构中存在一个已知问题：给定格的基，找到格中存在的最短向量。在这个上下文中，非正式地说，"短向量"是其元素尽可能接近零的向量。这个问题称为最短向量问题（SVP），它被认为是 NP-困难的。有一些算法可以解决类似但更容易的问题——找到某个短向量，即相对"接近"格中最短向量的向量。这个问题称为最近向量问题（CVP），解决它的算法之一称为 Lenstra-Lenstra-Lovász（LLL）算法。在这次攻击中，我们将把这个算法作为黑盒使用。


给定 `d` 条签名消息，可以构建一个包含向量 $(k_1, \dots , k_d)$ 的格，其中向量的每个元素是对应于一个签名的 `k` 值。LLL 算法将找到这个格中最短向量的近似值。由于 `k` 的值已知是较小的，因此算法找到的短向量很有可能包含至少一个正确的 `k` 元素。一旦找到正确的 `k`，就可以像我们在上一个攻击中看到的那样计算私钥。

要构建这个格，需要定义其基向量。我在文章末尾的参考资料中包含了一篇文章的链接，该文章解释了如何定义这些基向量。从技术上讲，格的基向量可以表示为一个矩阵，使得其中的每一行由一个基向量的元素组成。为了提高 LLL 算法的准确性，建议向该矩阵添加两列，其中包含有关 `k` 值的预期大小以及 `k` 和 `n` 之间比率的信息。这个改进也在我附加的参考资料中进行了解释。以下代码片段演示了这种攻击：

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

在这个代码片段中，使用了标准曲线，选择了一个私钥并从中计算出相应的公钥。创建了3条消息，并使用3个随机的 `k` 值进行签名，这些 `k` 值是 SHA-1 哈希函数的结果。然后，我们创建与格的基对应的矩阵（如文章中所解释的），并对其运行 LLL 算法。之后，我们遍历结果矩阵的行，检查是否在其中某一行中找到了任何 `k` 的正确值。

检查是通过从潜在的 `k` 计算私钥（如我们在上一个攻击中看到的）来执行的，并检查接收到的密钥是否确实正确。最后，我们确保找到的私钥确实正确。输出是：

```
success!
The secret is: I am Jack's broken heart
```

这种攻击的复杂度与 LLL 算法的复杂度相同，即 $O(d^6\ \log^3B)$，其中 `B` 表示 `k` 的偏差长度（在我们的例子中为 $2^{160}$），`d` 表示签名消息的数量（在我们的例子中为3）。问题是，为了能够运行攻击，我们需要使用的最少签名消息数量是多少。答案是
$\displaystyle d=O(\frac {\log n}{\log n-\log B})$，其中 `n` 是生成元的阶，`B` 是偏差。对此的解释出现在我在文章末尾附加的关于此主题的参考资料中的第二个链接中。

在实践中，这种攻击的变体也可以在 `k` 的高位比特已知或 `k` 的任何比特已知的情况下运行。即使只知道一个比特的值，甚至只知道一个比特的值有大于50%的概率，攻击也可以运行！但是当然，在这些情况下，需要更多的签名消息才能执行攻击。

## 不验证生成元是否有效
我们看到，在签名验证过程中，签名方向验证方发送一对值 `r` 和 `s`。例如，在实现 HTTPS 协议的浏览器中，通常在证书中发送这对值，证书中还可能包含签名方使用的曲线数据。验证方需要确保证书中的曲线数据确实与先前商定的曲线匹配。如果他们不这样做，可能会有问题。

假设在某条曲线中，Alice 有一个私钥 $d_A$ 和与其对应的公钥 $P_A$，这意味着 $P_A = d_AG$ 对于该曲线中的生成元 `G`。使用私钥 $d_A$，Alice 可以像我们在 ECDSA 协议定义中看到的那样签署她的消息。假设验证签名的一方也从用户那里接收生成元 `G`，但不验证从用户接收的生成元是否确实是商定的生成元。攻击者可以发送 Alice 的公钥作为生成元，$G^′ = P_A$。攻击者将选择值 $d_A^′ = 1$ 作为"伪造"私钥，因此显然 $P_A = d_A^′G^′$。这意味着攻击者可以"证明"他们拥有与 Alice 的公钥匹配的私钥。因此，攻击者可以创建任何他们想要的消息，并用 $d_A^′$ 以通常的方式为其计算一对值 `r` 和 `s`，生成的签名将被成功验证。



直观地说，在签名验证过程中，签名方证明他们确实是公钥的"所有者"，而公钥实际上是曲线上的"目标"点。这是因为只有签名者知道要从起点走多少步才能到达目标点。如果验证方不验证从用户接收的起点是否确实是真正的起点，那么攻击者可以决定起点就是目标点，并且从它出发的步数为零。签名验证的所有其他部分保持不变，签名将被成功验证。这种攻击称为 Curveball。

这种攻击可以用额外的值推广。攻击者将选择某个值 `x`，并计算 $G^′ = xP_A$。伪造的私钥将是 $d'_A = x^{−1}\ \ \ \ (mod\ n)$。那么显然有 $d'_AG^′ = x^{−1}xP_A = P_A$。

以下代码演示了这种攻击：
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

在这个代码片段中，我们选择了一个已知的生成元、一个私钥和一个公钥。我们签署一条消息并确保它被成功验证。然后我们创建一个伪造的私钥和一个伪造的生成元，使得两者都与原始公钥匹配。用伪造的密钥签署一条恶意消息，最后用原始公钥成功验证伪造的签名。这段代码的问题在于验证算法没有验证生成元 `G` 是否与公钥匹配。虽然在这次攻击中我们没有找到用户的私钥，但攻击者可以利用不正确的签名验证实现，并创建一个成功验证的签名。然而，攻击者无法创建"真正的"签名，这些签名将在正确的签名验证实现中被成功验证。

有趣的是，这是 Windows CryptoAPI 架构中存在的真实漏洞。在负责验证证书签名的函数中，对曲线参数的验证不足，特别是在这些参数包含在证书本身的情况下。特别是，没有检查生成元是否确实是与公钥对应的生成元。攻击者可以通过向证书添加恶意曲线字段并以我描述的方式选择生成元来创建被视为可信的伪造证书，因为它们看起来像是由受信任的证书颁发机构签署的。该漏洞由 NSA 组织发现，在2020年被修复，并获得了编号 CVE-2020-0601。

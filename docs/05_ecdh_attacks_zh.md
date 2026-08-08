# ECDH 攻击
## 生成元的阶太小
对于 ECDH 来说，可能最容易攻击的错误使用是选择一个阶 `n` 太小的生成元。
如前所述，可以用 $O(\sqrt{n})$ 的复杂度来解决 ECDLP 问题。当 `n` 太小时，例如 32 位，那么解决这个问题就变得可行了。有几种算法可以解决这个问题，包括 Baby-Step Giant-Step、Pollard's Rho 和 Pollard's Lambda。这些算法可以通过 SageMath 的帮助作为黑盒运行，使用 `discrete_log` 函数：
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

在这段代码中，我们在 `p` 为 32 位长的限制下随机选择曲线参数。这个限制保证了曲线上的点数为 $O(2^{32})$，因此其中每个点的阶最多也是 $O(2^{32})$。之后我们创建曲线，在其中选择某个生成元，生成一个随机私钥，并计算公钥。最后，从生成元和公钥出发，我们计算离散对数以找到私钥，并验证找到的密钥确实是正确的。这段代码最多只需几秒钟就能找到私钥。



## 生成元的阶是光滑数
如前所述，生成元的阶定义为当我们将生成元点一次又一次地与自身相加时形成的"圆圈"中的点数，用 `n` 表示。如果 `n` 是一个可以分解为较小素因子的合数，那么就可以高效地解决 ECDLP。这样的数称为光滑数（Smooth Number），就本文而言，它是一个可以分解为足够多素因子的数，其中每个素因子都足够小以使我们的攻击有效。光滑数的正式定义略有不同，与我们无关。

直观上，这是通过分别"攻击"每个素因子来完成的。给定一个生成元点 `G`，它形成一个非常大的"圆圈"，以及"圆圈"中的某个点 `P`，使得 `P = kG`。大"圆圈"可以分解为几个小"圆圈"，每个小"圆圈"的大小为 `n` 的一个素因子。在每个小"圆圈"中，我们可以将 `G` 和 `P` 映射到位于小"圆圈"中的其他对应点 `G'` 和 `P'`，并满足 `P′ = k′G′`。因为"圆圈"很小，所以相对容易解决问题并找到 `k′`。最后，我们可以将找到的所有小 `k′` 组合成原始"圆圈"中所需的 `k`。

执行我所描述的算法称为 Pohlig-Hellman 算法。它的运行时复杂度是 $O(\sqrt{p_{max}})$，其中 $p_{max}$ 是 `n` 分解中的最大素因子。这也是合理的，因为算法中"最重"的部分是在较小"圆圈"中最大的"圆圈"中解决 ECDLP 问题。例如，`n` 可能是一个 128 位的数，它分解为素因子，其中最大的是一个 30 位的数。该算法将解决问题的复杂度从 $2^{64}$ 降低到 $2^{15}$，从而使其从不可行变为可行。

幸运的是，SageMath 的 `discrete_log` 函数在其实现中执行了这个算法。要运行攻击，你可以简单地调用该函数：


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

在这段代码中，我们定义了一个椭圆曲线和其中的一个生成元，并打印其阶的素因子。输出是：


```
number of bits in n: 128
n's factors: 2 * 3 * 13 * 101 * 211 * 21141581 * 38581057 * 60652309 *
2234328781
number of bits in n's greatest factor: 32
Calculating discrete_log...
success!
```

可以看到，虽然生成元的阶是 128 位长，但它分解为素因子，其中最大的素因子是 32 位。

之后，就像在前一个攻击中一样——我们选择一个随机私钥，从中计算公钥，然后给定生成元和公钥，计算私钥并验证它是正确的。


虽然我们已经完成了，但我们还没有看到如何定义"小"圆圈，如何将点 `G` 和 `P` 映射到它们对应的点 `G′` 和 `P′`，以及如何将所有小解组合成一个大解。我将在这里尝试直观地解释它，因为下一个攻击也是基于这部分的。


假设我们有一个阶为 `3×5×7 = 105` 的"圆圈"，其生成元是 `G`。我们定义一个点 `G′ = (5×7)G = 35G`，并查看从它生成的"圆圈"。如果我们从 `G′` 前进一"步"，即我们将 `G′` 与自身相加，这就像在原始"圆圈"中从点 `35G` 前进 35 步，我们将到达点 `2G′ = 70G`。如果我们再前进一"步"，我们将到达点 `3G′ = 105G = O`，如果我们再从它前进一"步"，我们将到达点 `4G′ = 35G = G′`，即回到起点。由 `G′` 形成的"圆圈"的阶为 `3`，这并非巧合，因为在阶为 `105` 的"圆圈"上，可以恰好采取 `3` 步大小为 `35` 的"步"。同样，我们可以通过定义点 `G′ = (3×7)G = 21G` 来创建阶为 `5` 的"圆圈"，通过定义 `G′ = (3×5)G = 15G` 来创建阶为 `7` 的圆圈。

当我们反过来看它时，它变得更有趣。假设在原始"圆圈"中，我们从点 `G` 走了 `n` 步，我们到达了点 `nG`。如果在小"圆圈"中我们也从点 `G′` 走了 `n` 步，我们将到达点 `n′G′`，使得 `n ≡ n′ (mod 3)`。为什么这很有趣？因为 `G′` 的阶远小于 `G` 的阶，因此给定 `G′` 和 `n′G′`，我们可以相对容易地找到 `n′`。如果我们这样做，并且也对"圆圈"阶的另外两个素因子（即 `5` 和 `7`）这样做，我们将得到以下值：

n ≡ $n'_1$ (mod 3)\
n ≡ $n'_2$ (mod 5)\
n ≡ $n'_3$ (mod 7)

从这三个值，可以使用中国剩余定理轻松找到 `n`，从而解决原始问题。


## 生成元的阶几乎是光滑数，且私钥较小
假设与前一个攻击类似，我们得到一条曲线，其中生成元的阶分解为素因子，但这次最大的素因子太大，以至于解决其 ECDLP 不切实际。例如，如果生成元阶是 `256 位`，但最大的素因子是 `128 位`。
Pohlig-Hellman 算法将需要大约 $O(2^{64})$ 次操作才能找到私钥，这是不可行的。


如果我们知道使用的私钥相对较小，仍然可以高效地找到它。
假设私钥是 `64 位`（而不是 `256 位`）。当创建公钥时，生成元乘以私钥，你会在生成元创建的"圆圈"中得到某个点。虽然"圆圈"的大小约为 $2^{256}$ 个点，但这个点将"落"在"第一个" $2^{64}$ 个点的某处。私钥与"圆圈"中对应于更大值的点之间没有"交互"。


可以运行 Pohlig-Hellman 算法，但"丢弃"太大的"圆圈"，前提是剩余"圆圈"的阶的乘积至少与私钥的长度一样大。如果找到足够多的小素因子，其乘积至少为 `64 位`，那么相应的"圆圈"将足以执行我们之前看到的相同攻击。

如果之前我们在编写代码方面生活很轻松，这次我们将不得不自己实现一些东西，因为 SageMath 的 `discrete_log` 函数不知道我们想要"丢弃"一些素因子。以下代码片段执行此操作：


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

在这段代码中，我们定义了一个椭圆曲线和其中的一个生成元，并打印其阶的素因子。输出是：

```
Number of bits in n: 256
n's factors: 2 * 3 * 29 * 2699 * 28751 * 831913766251 * 92996710252298530263979 *
84878782522781478604307230464271
```

生成元的阶是 `256 位`，它分解为几个素因子，其中最大的两个是 `77 位` 和 `107 位`。它们足够大，以至于解决 ECDLP 是不切实际的。然后，随机生成一个 `64 位` 的私钥，并计算公钥。在下一步中，我们"收集"足够多的素因子，直到我们得到至少 `64 位` 长度的阶。输出是：

```
We know that the private key is 64 bits long
Lets find which of the factors of G's order are relevant for finding the private key
Found enough factors! The rest are not needed
Considering these factors: [(2, 1), (3, 1), (29, 1), (2699, 1), (28751, 1), (831913766251, 1)]
```

可以看到，最大的两个因子是多余的，我们剩下的最大因子是 `40 位`。在下一步中，对于我们剩下的每个因子，我们计算点 `G′` 和 `P′`，如我之前解释的那样，对于每一个我们都解决 ECDLP。结果和素因子分别保存在列表 `subsolutions` 和 `subgroups` 中。最后，使用中国剩余定理将所有结果组合成私钥，我们验证它确实是正确的。


## 未验证点是否在曲线上
检查椭圆曲线中点加法的定义，我们注意到一个有趣的性质，即在点加法中不使用值 `b`，而只使用值 `a` 和 `p`。这意味着位于一条曲线上的点的加法对于另一条曲线也可能有意义，而另一条曲线与它仅在 `b` 值上不同。这对于将点乘以数字当然也是正确的。如果用户不验证他们从另一方收到的作为公钥的点确实位于他们的曲线上，那么他们就会暴露在无效曲线攻击（Invalid Curve Attack）中。

假设双方就某条椭圆曲线 $E_1$ 达成一致。攻击者可以创建一条恶意曲线 $E_2$，它具有与 $E_1$ 相同的 `a` 和 `p` 值，但 `b` 值不同。在曲线 $E_2$ 中，攻击者将选择一个阶很小的点 `P`，例如 `3`。当然，点 `P` 不会位于 $E_1$ 上，因为它满足的方程具有与 $E_1$ 不同的 `b` 值。攻击者将发送点 `P` 作为他们的公钥给用户。假设用户不费心验证他们收到的点确实在双方商定的曲线 $E_1$ 上。用户将接收从攻击者那里收到的公钥，将其与他们的私钥相乘，并到达一个应该是共享秘密点的点，正如我们在 ECDH 协议的定义中看到的那样。从用户的角度来看，他们将在曲线 $E_1$ 上计算乘法操作。但因为点 `P` 根本不在它上面，而是在 $E_2$ 上，用户实际上将在曲线 $E_2$ 上计算乘法操作。之后，用户将使用共享秘密点继续与攻击者通信。假设双方使用点的 `x` 坐标作为 AES 加密密钥。在这种情况下，用户将加密某些消息并将其发送给攻击者。

由于 `P` 的阶是 `3`，用户计算的共享点只有 `3` 种可能性。攻击者将遍历这些可能的点，并找到其中哪一个对应于成功解密用户发送的加密消息的密钥。给定这个点和起始点 `P`，攻击者可以推断出用户私钥除以数字 `3` 的余数。攻击者可以向用户发送额外的恶意 `P` 点，阶递增，例如 `5`、`7` 等。通过这种方式，攻击者可以收集足够多的值，这些值表示用户私钥除以小数字的余数。最后，攻击者可以使用中国剩余定理来计算用户的私钥，就像我们在前一个攻击中看到的那样。

这里有一个更直观的解释：攻击者可以为用户提供一个非常小的"圆圈"上的点，例如长度为 `2`。用户将在这个"圆圈"中向前前进任意数量的步数并到达目标点。攻击者知道用户的目标点，它可能是 `2` 种可能性之一。因此，攻击者可以判断用户在圆圈上走了偶数步还是奇数步。攻击者可以为用户提供长度为 `3`、`5`、`7` 等的"圆圈"上的额外点。直到攻击者有足够多的这样的因子，每个因子都包含关于用户所走步数的少量信息。最后，攻击者可以将所有这些值组合成用户所走的确切步数，这就是他的私钥。

以下代码演示了攻击：

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

在这段代码中，选择了一条曲线和一个生成元，用户随机生成一个私钥并将其用于 ECDH 协议的所有使用。函数 `find_curves_with_small_subgroup` 找到点和阶的配对，使得每个点的阶相对较小，并且该点位于仅在 `b` 值上与原始曲线不同的某条曲线上。代码生成这样的配对，直到找到足够多的配对。对于每个配对，将公钥发送给用户并从他们那里接收加密消息。

对加密消息执行暴力破解，以找到用户私钥对当前阶取模的值。保存所有这些结果，最后我们使用中国剩余定理来计算用户的私钥并验证它是正确的。在这种情况下，双方商定通信将使用 AES 完成，加密密钥是共享秘密点的 `x` 坐标，IV 是其 `y` 坐标。

攻击的复杂度是 $O(n_{max})$，其中 $n_{max}$ 是恶意点的阶中最大的阶。这是因为攻击中"最重"的部分是对小"圆圈"中最大"圆圈"的暴力破解，幸运的是对于攻击者来说，他们几乎可以完全控制这个值。因此，这种攻击在复杂度方面相对有效。如前所述，在这种情况下问题的根源是用户不检查他们收到的点是否甚至在他们正在使用的曲线上。此外，用户在每次新使用 ECDH 时都使用相同的私钥，这不太安全。


## 曲线是奇异的
椭圆曲线必须具有的一个重要属性才能在密码学上安全，就是它是非奇异的。非奇异曲线是指其某个值（称为曲线的"判别式"）非零的曲线。当其参数 `a` 和 `b` 满足不等式时，它成立：

$4a^3 + 27b^2 ≠ 0$

不满足此不等式的曲线有一个"有问题"的点，称为"奇异点"。这样的点有两种类型：结点（node）和尖点（cusp）。结点存在于一条曲线上，该曲线有一种在奇异点自相交的环，并且可以通过该点画出两条不同的切线。
尖点是曲线"尖锐"的点，好像有两条线从它出来，但在该点只有一条切线。


<img src="images/singular.png" alt="Singular Elliptic Curves"  width="500">

在结点类型的点中存在双根，因此曲线的方程可以写为：

$y^2 = (x-x_0)^2(x-x_1)\ \ \ \ (mod\ p)$

可以通过用变量 $(x + x_0)$ 替换变量 $x$ 来将曲线向左"移动"，并达到以下形式：

$y^2 = x^2(x+x_0-x_1)\ \ \ \ (mod\ p)$

所以现在奇异点在坐标轴的原点。数值 $t = (x_0-x_1)$ 可用于在曲线上的点与整数之间创建映射，使得曲线上点之间的加法操作等价于数字之间的乘法操作。对于每个点 `(x, y)`，我们将匹配数字
$\frac{y+\sqrt{t}x}{y-\sqrt{t}x}$。特别是，对于一对点 `G` 和 `Q`，使得 `Q = nG`，我们可以映射数字 `g` 和 `q`，使得 $q ≡ g^n\ \ \ \ (mod\ p)$，这是一个"正常"的 DLP 问题。为了说明这个过程，我在文章末尾的参考文献中添加了一个带有小数字示例的链接。在我们所做的映射中，我们使用了线性线 $y+\sqrt{t}x$ 和 $y-\sqrt{t}x$ 的方程，这些是对应于可以在奇异点（在我们"移动"曲线之后）画出的两条切线的线，这基本上就是为什么可以使用这种攻击。

这样的 DLP 问题可以借助 Pohlig-Hellman 算法高效解决，我们之前已经见过，因为它也可以用于整数而不是曲线上的点。在点的上下文中，我们看到当生成元的阶是光滑数时，该算法是有用的。与曲线上可能具有任何阶的点"圆圈"不同，在模素数 `p` 的整数域中，阶是 `p − 1`。如果 `p − 1` 是光滑数，那么该算法将高效地解决 DLP 问题，从而找到私钥 `n`。

以下代码片段执行此操作：

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



在这段代码中，我们定义了椭圆曲线的参数，并验证它确实是奇异的。我们找到对应于曲线的多项式的根，并识别其中哪个是双根。我们使用双根来"移动"曲线，并到达"移动"的点 `G` 和 `Q`。然后从我们找到的根计算 $\sqrt{t}$，并使用它将点 `G` 和 `Q` 映射到数字 `g` 和 `q`。我们打印 `p − 1` 到其素因子的分解（以验证 DLP 确实可以高效解决）。最后，我们计算 DLP 并将结果解释为字符串。

输出是：
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

这次我在私钥本身中隐藏了一条消息。需要注意的是，因为它是一条奇异曲线，在 SageMath 中无法以正常方式创建它，在其上定义点并像我们之前那样执行操作。在这段代码中，我将点的坐标定义为常量变量。为了计算点 `Q`，我使用我自己实现的 Double And Add 算法将私钥与生成元相乘。


## 曲线是超奇异的
给定一条模 `p` 的椭圆曲线和一个阶为 `n` 的生成元，关于生成元的曲线的嵌入度（Embedding Degree）定义为满足方程 $p^k ≡ 1\ \ \ \ (mod\ n)$ 的最小数 `k`。通过某些变换，ECDLP 问题可以简化为阶为 $p^k$ 的域中的 DLP 问题。值 `k` 通常是一个非常大的数（与 `p` 本身的大小相同），但当它相对较小（比如小于 `6`）时，曲线被称为"超奇异"（supersingular），并且高效解决这个 DLP 问题变得可行。这种攻击被称为 MOV 攻击，以其三位发明者（Menezes-Okamoto-Vanstone）命名。

我提到的变换是接收两个点并在复数域中返回某个数字的函数。可以使用的变换是 Weil 配对或 Tate 配对，我们将把它们用作黑盒。这样的变换 `T` 对于每一对点 `P`、`Q` 满足以下属性：

$T(mP, nQ)=T(P,Q)^{mn}$


因此，给定两个点 `G` 和 `Q = mG`，我们可以随机选择第三个点 `R` 并计算两个值：\
$g = T(G, R)$ \
$q = T(Q, R)=T(mG,R)=T(G,R)^m=g^m$
从这里我们可以在阶为 $p^k$ 的域中解决 `g` 和 `q` 的 DLP 问题，从而找到私钥 `m`。我在文章末尾的参考文献中包含了一个关于这次攻击背后数学的更详细解释的链接。

以下代码片段执行此攻击：

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

在这段代码中，我们定义了一条曲线及其生成元，并计算其嵌入度值，在这种情况下是 `2`，因此执行攻击是切实可行的。我们定义一条与原始曲线相同的曲线，只是计算是模 $p^k$ 而不是模 `p`。两个点 `G` 和 `Q` 也在新曲线上。然后我们找到第三个点，其阶整除 `n`。

使用第三个点，我们将点 `G` 和 `Q` 映射到数字 `g` 和 `q`，并为它们计算离散对数。最后，我们验证获得的结果确实是正确的。

输出是：
```
Found k: 2
Calculating private key...
success!
The private key is: Festivus
```

从计算的角度来看，今天有一些指数演算（Index Calculus）算法可以以相对有效的方式解决 DLP 问题，它们的复杂度为 $e^{O((log\ p^k)^{1/3}(log\ log\ p^k)^{2/3})}$。这个表达式可能看起来很可怕，但与复杂度为 $O(\sqrt{p})=e^{O(log\ p)}$ 的 ECDLP 算法相比，可以看出解决 DLP 问题更容易，假设嵌入度（用 `k` 表示）确实很小。



## 曲线是反常的
如果某条曲线具有这样的性质：曲线的阶（其上的点数）恰好等于模数 `p`，那么它被称为"反常曲线"（Anomalous Curve），并且容易受到称为 Smart 攻击的攻击。这种攻击使用 `p`-进数（p-adic numbers）。这样的数可以表示为 `p` 的幂（正和负）与系数的和。形式上，这样的数 `s` 是以下形式的级数：

$s=\sum_{i = -k}^{\infty} a_{i}p^i = a_{-k}p^{-k} + \cdots + a_0 + a_1p + a_2p^2 + \cdots$

当系数是范围 $0 ≤ a_i < p$ 中的整数时，和在 `p` 的正幂方向上可以是无限的。在这样的数字中，我们从右到左"看"数字，而不是从左到右，因此这样的级数可以收敛到某个值。这样的数字属于与我们熟悉的数字系统不同的数字系统，其行为与"正常"数学规则非常不同。仅关于这个主题就可以写一整篇单独的文章，对于那些对此感兴趣的人，我在文章末尾的参考文献中包含了一个以相对清晰的方式呈现它的视频链接。

在任何情况下，在这次攻击中，从给定曲线创建一条新曲线，该曲线定义在 p 进数上。给定原始曲线上的两个点 `G` 和 `Q = mG`，我们将它们映射到新曲线上的对应点。从获得的点的坐标可以很容易地计算 `m`。

以下代码执行攻击：

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

在这段代码中，定义了一个 lift 函数，它接收原始曲线上的一个点，并为其对应新曲线上的一个点。然后我们定义一个椭圆曲线和其中的一个生成元，并验证曲线的阶确实是 `p`。我们选择一个私钥并计算相应的公钥，然后执行攻击。我们在 p 进数上定义一条新曲线，并使用 lift 函数将原始点 `G` 和 `P` 映射到新曲线中的对应点，并将它们乘以 `p`。

对于每个新点，我们计算其 `x` 坐标与其 `y` 坐标之间的比率。这两个值的商是原始点的 ECDLP 解。

输出是：
```
success!
The private key is: >>>>> Extraordinarily Nice <<<<<
```

这个计算之所以有效，与曲线上的点数恰好是 `p` 这一事实有关。这个性质允许我们执行几个映射，最后一个映射在 p 进数上的曲线上的点与模 $p^2$ 的数字之间进行映射。这个映射具有这样的性质：对应于两个原始点的一对数字之间的比率恰好是两个点的对数的结果。我们将把所有这些映射留作黑盒，但在文章末尾我添加了相关数学解释的参考文献。

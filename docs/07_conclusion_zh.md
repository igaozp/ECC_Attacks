# 结论
## ECDH 攻击概述
| 问题类型  | 问题描述 | 攻击方法 | 攻击原理 | 攻击复杂度 |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| 选择不安全生成元的曲线 | 生成元的阶 `n` 太小 | Baby-Step Giant-Step | 中间相遇攻击 | $𝑂(\sqrt n)$ |
| 选择不安全生成元的曲线 | 生成元的阶 `n` 是光滑数 | Pohlig-Hellman | 将 `𝑛` 分解为质因数，分别攻击每个质因数，然后使用中国剩余定理组合结果 | $O(\sqrt{p_{max}})$，其中 $p_{max}$ 是 `𝑛` 分解中的最大质因数 |
| 选择不安全生成元的曲线 + 选择不安全的私钥 | 生成元的阶 `n` 几乎是光滑数，且私钥很小 | 改进的 Pohlig-Hellman | 将 `𝑛` 分解为质因数，丢弃过大的因数，分别攻击每个质因数，然后使用中国剩余定理组合结果 | $O(\sqrt{p_{max}})$，其中 $p_{max}$ 是 `𝑛` 分解中的最大质因数 |
| ECDH 实现不正确 | 未验证点是否在曲线上 | 无效曲线攻击 | 将恶意曲线上阶数较小的点作为公钥发送，分别攻击每个点，然后使用中国剩余定理组合结果 | $𝑂(𝑛_{𝑚𝑎𝑥})$，其中 $𝑛_{𝑚𝑎𝑥}$ 是恶意点阶数中的最大值 |
| 曲线参数选择不安全 | 曲线是奇异的 | 将 ECDLP 归约到 DLP | 将点映射到数字，使得点加法转换为整数乘法 | $O(\sqrt{p_{max}})$，其中 $p_{max}$ 是 $(p-1)$ 分解中的最大质因数 |
| 曲线参数选择不安全 | 曲线是超奇异的 | 将 ECDLP 归约到 DLP | 将点映射到数字，使得点加法转换为整数乘法 | $e^{O((log\ p^k)^{1/3}(log\ log\ p^k)^{2/3})}$，其中 `k` 是相对于生成元的嵌入度 |
| 曲线参数选择不安全 | 曲线是反常的 | Smart 攻击 | 在曲线上的点与 `p-adic` 数域上的曲线点之间进行一系列映射，最后映射回整数 | $O(1)$ |


## ECDSA 攻击概述
| 问题类型  | 问题描述 | 攻击方法 | 攻击原理 | 攻击复杂度 |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| 签名和验证实现不正确  | 签名前未对消息进行哈希 | 给定已签名的消息，伪造对应相同签名的其他消息 | 保持消息前缀不变，修改其余部分 | $O(1)$ |
| 签名算法使用不正确 | 在不同签名中重复使用相同的 `k` 值 | 找到用户的私钥 | 找到 `k` 的值，并由此计算出用户的私钥 | $O(1)$ |
| 签名算法使用不正确 | `k` 值生成不安全 | 给定多个已签名的消息，找到用户的私钥 | 将问题归约为在格中寻找短向量，找到 `k` 的值，并由此计算出用户的私钥 |  $O(d^6\ \log^3B)$，其中 `B` 是 `k` 的偏差，`d` 是已签名消息的数量 |
| 验证实现不正确 | 未验证生成元是否有效 | 伪造可成功验证的签名（Curveball） | 选择与其他用户公钥对应的伪造生成元和私钥 | $O(1)$ |


## 针对这些攻击的防护措施
需要注意的是，在 ECDH 中，双方必须在协议开始时就曲线达成一致。如果用户与攻击者通信，而攻击者是提供曲线参数的一方，那么攻击者可以提供不安全的参数。结果，攻击者可以获得用户的私钥。如果用户总是使用相同的私钥，那么攻击者可以解密该用户与任何其他用户之间的所有对话。因此，如果不可信任的陌生用户提供曲线参数，非常重要的是不要允许他们这样做。此外，您必须确保从外部用户收到的每个点确实在商定的曲线上。当然，您还应该确保所选曲线本身不易受到我们所见过的已知攻击之一的影响。此外，最好在每次使用 ECDH 协议时使用新的私钥。

同样，在 ECDSA 中，必须小心正确实现签名和验证算法。不要跳过消息的哈希处理、每次使用协议时 `𝑘` 值的随机安全生成，当然在签名验证中，如果生成元是从用户处接收的 - 请确保它确实是之前商定的那个。

## 参考文献
- 本文中使用的图表来自 Christof Paar 的《Understanding Cryptography》一书：\
https://gnanavelrec.wordpress.com/wp-content/uploads/2019/06/2.understanding-cryptography-by-christof-paar-.pdf


- 一个展示密码学椭圆曲线外观的网站：\
https://graui.de/code/elliptic2/

- 椭圆曲线中加法和乘法运算的详细解释：\
https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication

- 椭圆曲线和点加法入门讲座 - 作者 Christof Paar：\
https://www.youtube.com/watch?v=vnpZXJL6QCQ

- 关于生成元、ECDLP、问题难度、ECDH、Double And Add 的讲座 - 作者 Christof Paar：\
https://www.youtube.com/watch?v=zTt4gvuQ6sY

- 不同加密算法的安全级别解释：\
https://en.wikipedia.org/wiki/Security_level

- ECDH 解释：\
https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman

- ECDSA 解释：\
https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm

- ElGamal 签名解释：\
https://en.wikipedia.org/wiki/ElGamal_signature_scheme

- 中国剩余定理解释：\
https://en.wikipedia.org/wiki/Chinese_remainder_theorem

- 奇异曲线的判别式与其具有重根的事实之间关系的解释：\
https://www.quora.com/For-an-elliptic-curve-in-the-form-Y-2-X-3+AX+B-why-is-4A-3+27B-2-neq-0-the-condition-for-non-singularity

- 奇异曲线中点与数字之间映射的小数值示例：\
https://crypto.stackexchange.com/questions/61302/how-to-solve-this-ecdlp/61434#61434

- 𝑝-adic 数的解释：\
https://en.wikipedia.org/wiki/P-adic_number \
https://www.youtube.com/watch?v=3gyHKCDq1YA

- MOV 攻击背后的数学解释：\
https://risencrypto.github.io/WeilMOV/

- Smart 攻击背后的数学解释（相当复杂，请注意）：\
https://wstein.org/edu/2010/414/projects/novotney.pdf \
http://www.monnerat.info/publications/anomalous.pdf

- 基于格的攻击和 LLL 算法的解释：\
https://forum.vac.dev/t/lattice-attacks-on-ecdsa/136 \
\
该攻击基于 Joachim Breitner 和 Nadia Heninger 文章的第 4 部分：\
https://eprint.iacr.org/2019/023.pdf

- CVP 问题的解释：\
https://en.wikipedia.org/wiki/Lattice_problem#Closest_vector_problem_(CVP)

- LLL 算法的解释：\
https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm

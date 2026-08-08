# 椭圆曲线密码学的已知攻击

**语言：** [English](README.md) | 简体中文

- [介绍](#介绍)
- [椭圆曲线介绍](#椭圆曲线简介)
- [密码学背景下的椭圆曲线](#密码学背景下的椭圆曲线)
- [ECC 攻击](#ecc-攻击)

### ECDH 攻击
- [生成元的阶太小](#生成元的阶太小)
- [生成元的阶是光滑数](#生成元的阶是光滑数)
- [生成元的阶几乎是光滑数，且私钥较小](#生成元的阶几乎是光滑数且私钥较小)
- [未验证点是否在曲线上](#未验证点是否在曲线上)
- [曲线是奇异的](#曲线是奇异的)
- [曲线是超奇异的](#曲线是超奇异的)
- [曲线是反常的](#曲线是反常的)

### ECDSA 攻击
- [签名前不对消息进行哈希](#签名前不对消息进行哈希)
- [在不同签名中重复使用相同的 k 值](#在不同签名中重复使用相同的-k-值)
- [不安全地生成 k 值](#不安全地生成-k-值)
- [不验证生成元是否有效](#不验证生成元是否有效)

### 结论
- [ECDH 攻击概述](#ecdh-攻击概述)
- [ECDSA 攻击概述](#ecdsa-攻击概述)
- [针对这些攻击的防护措施](#针对这些攻击的防护措施)
- [参考文献](#参考文献)

# 介绍
近年来，椭圆曲线密码学（Elliptic Curve Cryptography）方法因其高效性和强大的安全性而变得流行。本文的目的是以比当今互联网上存在的更清晰的方式来介绍这个主题。

在本文中，我将介绍什么是椭圆曲线、可以对其执行的基本操作，以及如何在密码学背景下使用它们。本文的大部分内容包括对错误实现或错误使用椭圆曲线的已知攻击示例。在整篇文章中，我尝试将解释分为直观的高层次部分和深入细节的数学部分。读者可以根据自己的兴趣重点关注其中的某些部分，而跳过不太感兴趣的部分。

祝阅读愉快！

# 椭圆曲线简介
### 什么是椭圆曲线
一般来说，椭圆曲线是一种曲线。一个例子是抛物线，其方程形式为 $𝑦 = 𝑎𝑥^2 + 𝑏𝑥 + 𝑐$，它看起来像这样：

![Parabola](images/parabola.png)

在密码学中，通常使用方程如下的椭圆曲线：

$𝑦^2 = 𝑥^3 + 𝑎𝑥 + 𝑏$

例如，对应于方程 $𝑦^2 = 𝑥^3 − 3𝑥 + 3$ 的椭圆曲线看起来像这样：

<img src="images/simple_elliptic_curve.png" alt="Simple elliptic curve" width="287" height="287">

曲线的方程定义了曲线上点的 `𝑥` 坐标与其 `𝑦` 坐标之间的关系。在密码学中，我们限制 `𝑥`、`𝑦`、`𝑎`、`𝑏` 为整数，并限制计算在某个大质数下进行模运算。因此，椭圆曲线的方程是：

$𝑦^2 = 𝑥^3 + 𝑎𝑥 + 𝑏\ \ \ \ (mod\ 𝑝)$.

这意味着曲线上有有限数量的点。用数学语言来说，该曲线定义在阶为 `𝑝` 的有限域上。因此，现在并非每个 `𝑥` 坐标都一定有对应的曲线上的点，因为对应的 `𝑦` 坐标可能不是整数。


### 曲线上的点
曲线上的点集由满足曲线方程的整数对 `(𝑥, 𝑦)` 组成。除了这些点之外，还定义了一个称为"无穷远点"的特殊点，用 `𝒪` 表示。用数学语言来说，这个点是曲线上点集关于加法运算的中性元素，我们将在下一节中定义该运算。曲线上的点数（包括点 `𝒪`）称为"曲线的阶"。

另一个观察是椭圆曲线关于 `X` 轴对称。这意味着如果点 `𝑃 = (𝑥, 𝑦)` 在曲线上，那么点 `−𝑃 = (𝑥, −𝑦)` 也在曲线上。事实上，这些点被认为是彼此的"逆元"（因此第二个点标记为 `−𝑃`），它们之间加法运算的结果被定义为中性元素 `𝒪`。

一个称为哈斯定理（Hasse's Theorem）的定理提供了曲线阶 `#𝐸` 的估计，其数量级为 `Θ(𝑝)`。更准确地说：

$𝑝 + 1 − 2\sqrt𝑝 ≤ 𝐸 ≤ 𝑝 + 1 + 2\sqrt𝑝$

### 点的加法
给定曲线上的两个点，可以定义它们之间的加法运算，结果是曲线上的第三个点。要在几何上找到这个点，我们在两个给定点之间画一条直线，并延续它直到它与曲线相交于第三个点。这个点关于 `𝑋` 轴进行反射，得到的点被定义为加法的结果。

下面是一个示意图，显示了给定点 `𝑃` 和 `𝑄`，如何找到点 `𝑃 + 𝑄`：

<img src="images/points_addition.png" alt="Points addition" width="300" height="300">

从这个描述中可能产生的一个问题是，如果在两点之间画的线不再与曲线相交会发生什么？在这种情况下，该直线被称为与曲线在"无穷远处"相交，加法的结果是点 `𝒪`。注意，当所画的直线是垂直的时，即我们试图将点 `𝑃` 与其逆点 `−𝑃` 相加时，就会出现这种情况：

<img src="images/point_addition_infinity.png" alt="Points addition infinity" width="283" height="283">

从中可以推导出两个基本恒等式。对于每个点 `𝑃`，都有：

`𝑃 + 𝒪 = 𝑃`\
`𝑃 + (−𝑃) = 𝒪`

几何描述中出现的另一个问题是，我们如何将一个点加到它自己？我们看到，为了将两个不同的点 `𝑃` 和 `𝑄` 相加，我们在它们之间画一条直线，并查看其延续与曲线的交点。直观地说，我们将保持 `𝑃` 不变，并观察当我们将 `𝑄`"越来越接近"`𝑃` 时所形成的直线，直到 `𝑄` 与 `𝑃` 重合。我们得到的是在点 `𝑃` 处越来越"切"于曲线的直线，这正是当我们想要将 `𝑃` 加到自己时要查看的直线：

<img src="images/point_multiplication.png" alt="Points multiplication" width="300" height="300">

要将点 `𝑃` 加到自己，我们在点 `𝑃` 处画曲线的切线，并延续它直到它与曲线在第二个点相交。这个点关于 `𝑋` 轴进行反射，得到的点被定义为加法的结果。习惯上将加法的结果标记为 `𝑃 + 𝑃 = 2𝑃`。同样，如果切线不与曲线在第二个点相交，那么它被称为与曲线在"无穷远处"相交，在这种情况下加法的结果是点 `𝒪`。

这些可视化的几何描述很好地说明并帮助我们理解点加法的工作原理。但我们实际上如何计算它呢？当然是数学方程！

给定点 $𝑃 = (𝑥_𝑃, 𝑦_𝑃)$ 和 $𝑄 = (𝑥_𝑄, 𝑦_𝑄)$，它们加法的结果是点 $𝑅 = (𝑥_𝑅, 𝑦_𝑅)$，使得：


$𝑥_𝑅 = 𝜆^2 − 𝑥_𝑃 − 𝑥_𝑄\ \ \ \ \ \ \ \ \ (mod\ 𝑝)$ \
$𝑦_𝑅 = 𝜆(𝑥_𝑃 − 𝑥_𝑅) − 𝑦_𝑃\ \ \ \ (mod\ 𝑝)$

其中 `𝜆` 被定义为连接两点的直线的斜率（如果它们不同），或者曲线在该点处的切线斜率（如果点加到自己）。正式地：

$\displaystyle𝜆 = \frac{𝑦_𝑃 − 𝑦_𝑄}{𝑥_𝑃 − 𝑥_𝑄}\ \ \ \ \ (mod\ 𝑝)\ \ \ ;\ \ \   𝑖𝑓 𝑃 ≠ 𝑄$\
$\displaystyle𝜆 = \frac{3{𝑥_𝑃}^2 + 𝑎}{2𝑦_𝑃}\ \ \ \ (mod\ 𝑝)\ \ \ ;\ \ \   𝑖𝑓 𝑃 = 𝑄$

点加法背后的数学计算对于本文的其余部分并不重要。就此而言，我们可以将点加法看作一个黑盒，它接收曲线上的两个点并返回曲线上的第三个点。

### 椭圆曲线上点的标量乘法
我们看到可以将点 `𝑃` 加到自己，我们将得到的点记为 `2𝑃`。如果我们再次将点 `𝑃` 加到这个结果上，我们将得到一个记为 `3𝑃` 的点，以此类推。通过这种方式，可以通过重复将点加到自己来定义点的"标量乘法"（类似于数字之间的乘法）：

$𝑛𝑃 = 𝑃 + 𝑃 + ⋯ + 𝑃\ \ \ \ \ (n\ times)$

表面上看，要将一个点乘以数字 `𝑛`，我们需要执行 `𝑛` 次点之间的加法运算。这是因为给定一个起点，很难提前知道"最后"的点会落在哪里，而不必"逐步"到达它。这样的计算效率会很低，因为 `𝑛` 可能非常大。

为此，存在`倍加法（Double And Add）`算法，我们从点 `𝑃` 开始，然后对于 `𝑛` 的二进制表示中的每一位，当前点乘以 `2`（即加到自己），如果位值为 `1`，则将其加到结果中。该算法的运行时复杂度为 `𝑂(log 𝑛)`，它允许高效地将点乘以非常大的数字。

我们稍后将使用的点乘法的一个重要性质是，对于每个点 `𝑃` 和数对 `𝑎`、`𝑏`，都有：

$𝑏(𝑎𝑃) = (𝑏𝑎)𝑃 = (𝑎𝑏)𝑃 = 𝑎(𝑏𝑃)$

直观地说，假设我们从点 `𝑃` 开始，从中走 `𝑎` 步，到达点 `𝑎𝑃`。从这个点，我们走"大小"为 `𝑎` 的 `𝑏` 步，到达点 `𝑏(𝑎𝑃)`。或者，在另一种情况下，我们可以从点 `𝑃` 开始，从中走 `𝑏` 步，到达点 `𝑏𝑃`。从这个点走"大小"为 `𝑏` 的 `𝑎` 步，到达点 `𝑎(𝑏𝑃)`。

在两种情况下，我们从点 `𝑃` 总共走了相同数量的 `𝑎𝑏` 步，因此在两种情况下我们到达了相同的最终点。从数学上讲，点的标量乘法是满足结合律的。


### 生成元
如果我们从点 `𝑃` 开始，一次又一次地将它加到自己，在每一步中我们都会到达曲线上的某个新点。因为曲线上有有限数量的点，在某个阶段我们将再次到达之前到达过的点，我们将处于某种循环或"圆圈"中。更准确地说，在某个阶段我们将到达点 `-𝑃`，下一步我们将到达点 `𝒪`，再下一步我们将再次到达我们开始的点 `𝑃`。

创建这样"圆圈"的点称为生成元（Generator），因为整个"圆圈"都可以从它生成，习惯上用字母 `𝐺` 表示它。"圆圈"中点的数量（包括点 `𝒪`）称为"生成元 `𝐺` 的阶"，通常用 `𝑛` 表示。曲线上的每个点都形成某种"圆圈"。从数学上讲，这个"圆圈"上的点集是一个循环群。

由此产生的一个有趣性质是，将点 `𝐺` 乘以其阶 `𝑛` 会给我们无穷远点：\
`𝑛𝐺 = 𝒪`

### 困难问题
"给定点 `𝑃` 和 `𝑄`，使得对于某个 `𝑥` 有 `𝑄 = 𝑥𝑃`，找到 `𝑥` 是困难的。"


用话来说，假设某人从某个起点开始，从中走了一定数量的步数，并到达了一个终点。给定起点和终点，我们如何知道他们走了多少步？

这个问题的答案并不那么直观，因为很难从起点提前预测从中走步将到达哪些点。一个简单的解决方案可能是我们自己从 `𝑃` 开始，一步一步地向前推进并计算我们走的步数，直到我们到达 `𝑄`。该解决方案的复杂度为 `𝑂(𝑥)`，如果已知 `𝑥` 是一个大数字，例如如果 `𝑥` 是 `256 位`，这是不可行的。


这个问题被称为椭圆曲线离散对数问题（ECDLP），它是一个困难问题。但它有多难呢？

在密码学中，习惯上用称为`安全级别`的度量来衡量"问题的难度"或"密码系统的强度"。在这个度量中，如果已知的最佳攻击在 $𝑂(2^𝑛)$ 步内解决问题，则称该问题具有"`𝑛` 位安全性"。

目前，解决 ECDLP 问题的最佳算法以 $𝑂(\sqrt n)$ 的复杂度完成，其中 `𝑛` 是点 `𝑃` 的阶，它使用中间相遇攻击（Meet In The Middle attack）来完成。当选择一个足够大阶的点时，解决它是不可行的，因此问题的强度。

例如，如果我们选择大小为 `256 位`的 `𝑛`，我们得到 ECDLP 问题具有 `128 位`安全性的安全级别。相比之下，要在基于整数分解问题的 RSA 加密中实现相同的 `128 位`安全性安全级别，需要大小为 `3072 位`的公钥。这使得椭圆曲线的使用在计算上相对更高效。

# 密码学背景下的椭圆曲线
在对椭圆曲线世界进行了所有这些介绍之后，我们将继续了解在密码学背景下可以用它们做什么。正如我们所知，密码系统通常基于一个难以解决的"困难问题"。例如，RSA基于我们提到的数字因式分解问题，或者迪菲-赫尔曼协议基于离散对数问题。基于椭圆曲线ECDLP问题的密码系统属于椭圆曲线密码学家族，简称ECC。


### 椭圆曲线的第一个应用 - 协商共享密钥
让我们从一个故事开始。想象你在一个派对上——一个满是人的房间，每个人都可以和每个人交谈，每个人都能听到每个人的声音。在这个房间里还有Alice和Bob，他们以前从未见过面。Alice喜欢Bob，她想约他出去。Alice有点害羞，所以她想在不让所有其他派对客人听到的情况下告诉Bob这个秘密消息。Alice和Bob事先没有协调任何事情，Alice对Bob说的一切都会被房间里所有其他客人听到。Alice如何在不让其他人听到的情况下向Bob传达这个消息？

如果你回答"椭圆曲线"，那么你是对的！

Alice将选择某个椭圆曲线及其中的一个生成元，并告诉Bob。具体来说，Alice将向Bob（以及房间里的其他所有人）传递两个曲线参数`𝑎`、`𝑏`、模数`𝑝`和生成元`𝐺`。此外，Alice将在$1 ≤ 𝑑_𝐴 ≤ 𝑛 − 1$范围内选择某个值$𝑑_𝐴$，其中`𝑛`是`𝐺`的阶。值$𝑑_𝐴$被称为Alice的私钥。Alice将计算点$𝐴 = 𝑑_𝐴𝐺$，这被称为Alice的公钥，并告诉Bob。类似地，Bob将选择一个私钥$𝑑_𝐵$，计算点$𝐵 = 𝑑_𝐵𝐺$，这被称为Bob的公钥，并告诉Alice。

Alice将获取Bob的公钥，用她的私钥乘以该点，并到达第三个点$𝑃_𝐴 = 𝑑_𝐴𝐵$。类似地，Bob将获取Alice的公钥，用他的私钥乘以它，并到达他自己的第三个点$𝑃_𝐵 = 𝑑_𝐵𝐴$。如果我们检查Alice和Bob分别到达的点，我们会发现他们到达了同一个点！这个事实来自我们之前看到的点乘以常数的结合律性质：

$𝑃_𝐴 = 𝑑_𝐴𝐵 = 𝑑_𝐴(𝑑_𝐵𝐺) = 𝑑_𝐵(𝑑_𝐴𝐺) = 𝑑_𝐵𝐴 = 𝑃_𝐵$

在整个过程结束时，Alice和Bob成功地就曲线上的某个点达成了一致，并且在任何阶段都没有任何一方将该点传递给另一方。每个人听到的信息是：`𝑎`、`𝑏`、`𝑝`、`𝐺`、`𝐴`、`𝐵`。房间里正在监听此信息的人无法用它找到Alice和Bob达成一致的点。


这是因为如果房间里的另一个人想要找到那个点，他们需要知道Alice的私钥或Bob的私钥，以便将`𝐵`或`𝐴`与它们相乘。例如，要找到Alice的私钥，他们将查看$𝐴 = 𝑑_𝐴𝐺$，因为这是唯一发送的并且"包含"Alice私钥的信息。给定`𝐺`和$𝑑_𝐴𝐺$，找到$𝑑_𝐴$相当于解决椭圆曲线中的离散对数问题，如前所述，这是一个困难问题。

这个美妙的协议被称为：椭圆曲线迪菲-赫尔曼（ECDH）。

### 使用共享密钥进行进一步通信
我们的故事还没有结束。虽然 Alice 和 Bob 已经就一个共享秘密点达成一致，但 Alice 仍未向 Bob 发出她一直期待的约会邀请。

在双方就共享秘密点达成一致后，他们可以将其用作任何加密方法（例如AES）的加密密钥，并从那时起通过加密安全地进行通信。

通常会取点的`𝑥`或`𝑦`坐标之一并使用它。为了保持安全性，建议对所选值进行哈希处理，并仅使用哈希结果作为加密密钥。实际上，有时该值太大而无法用作加密密钥。例如，如果使用的哈希函数是SHA-1，其输出长度为`160 bit`，而AES加密仅需要`128 bit`。在这种情况下，通常仅使用`160`位中的`128 bits`，并丢弃其余部分。

无论如何，此时Alice和Bob就加密密钥达成一致，而他们是唯一知道它的人。从此刻起，他们通过加密进行通信，房间里的任何监听者都无法理解他们在说什么。

这是协议的示意图：
<img src="images/ECDH.png" alt="ECDH">

使用约定的密钥，Alice加密消息"嘿Bob，你明天晚上想出去喝咖啡吗？"，并将加密的消息传递给Bob。Bob用他也知道的密钥解密消息。Alice希望Bob会说好，但这不是协议的一部分。

### 椭圆曲线迪菲-赫尔曼与迪菲-赫尔曼之间的相似性
在已知的迪菲-赫尔曼（DH）协议中，双方公开传输素数`𝑝`和生成元`𝑔`，该生成元在与值`𝑝`对应的群中。Alice随机生成私钥`𝑎`并公开广播她的公钥$𝐴 = 𝑔^𝑎\ \ \ \ (mod\ 𝑝)$。类似地，Bob随机生成私钥`𝑏`并公开广播他的公钥$𝐵 = 𝑔^𝑏\ \ \ \ (mod\ 𝑝)$。然后Alice获取Bob的公钥并将其提升到她的私钥的幂，从而计算值$𝐾 = 𝐵^𝑎 = (𝑔^𝑏)^𝑎 =𝑔^{𝑎𝑏}\ \ \ \ (mod\ 𝑝)$。以同样的方式，Bob计算值$𝐾 = 𝐴^𝑏 = (𝑔^𝑎)^𝑏 =𝑔^{𝑎𝑏}\ \ \ \ (mod\ 𝑝)$。在整个过程结束时，Alice和Bob能够就相同的共享秘密`𝐾`达成一致，而无需在他们之间传输它。

监听他们的攻击者无法在给定广播值`𝑝`、`𝑔`、`𝐴`、`𝐵`的情况下找到`𝐾`。为了做到这一点，他们必须找到Alice或Bob的私钥。例如，要计算Alice的私钥，他们必须在给定`𝑔`和$𝑔^𝑎\ \ \ \ (mod\ 𝑝)$的情况下找到`𝑎`，这是一个困难问题。这个问题被称为离散对数问题（DLP）。

基于DLP的DH和基于ECDLP的ECDH之间有非常明显的相似性（它们基本上是相同的，只是带有EC前缀）。在这两种协议中，相互交谈的两方可以就某个共享秘密值达成一致，而无需事先协调任何事情。任何监听双方之间消息的人都会接触到他们之间传递的公共信息，但将无法获得他们之间共享的秘密值。


### 椭圆曲线的第二个应用 - 签名消息
继续我们的故事，假设Alice和Bob去了约会并度过了一个愉快的夜晚。第二天，Alice收到一条消息，上面写着"嗨Alice，我是Bob，昨天和你在一起我度过了一段美好的时光，我很想在这个周末再次见到你"。Alice怀疑不是Bob发送了这条消息，因为她知道Bob昨天和她玩得很开心，他不会等到周末才见她，而是想明天就见她！Alice如何验证是Bob写的这条消息？

如果你回答"椭圆曲线"，那么你又对了！

ECDLP问题的难度也可以用于签名消息。在他们的约会期间，Alice和Bob就某个椭圆曲线及其中的生成元`𝐺`达成了一致。Bob生成了某个值$𝑑_𝐵$，称为Bob的私钥，并计算了点$𝑃_𝐵 = 𝑑_𝐵𝐺$，称为Bob的公钥。Bob将他的公钥给了Alice，以便她可以用它来验证她收到的消息是否确实由他签名。

假设Bob想要签署某条消息`𝑚`。他将使用某个安全的哈希函数计算值$z = hash(m)$，并从结果中保留等于`n`的位长度的比特数，`n`是生成元`𝐺`的阶。Bob将在$1 ≤ 𝑘 ≤ 𝑛 − 1$范围内生成某个随机值`𝑘`。然后Bob将计算点$𝑘𝐺 = (𝑥_1, 𝑦_1)$，取其`𝑥`坐标，并计算$𝑟 = 𝑥1\ \ \ \ (mod\ n)$。最后，Bob将计算值$𝑠 = 𝑘^{−1}(𝑧 + 𝑟𝑑_𝐵)$。

消息`𝑚`的签名被定义为计算值`𝑟`和`𝑠`的对。

假设Alice收到了某条消息`𝑚`，其签名由一对值`​𝑟`和`𝑠`组成。Alice想要确保确实是Bob签署了该消息。Alice将以与Bob相同的方式计算值$z = hash(m)$。然后Alice将计算值$𝑢_1 = 𝑧𝑠^{−1}$和$𝑢_2 = 𝑟𝑠^{−1}$。最后，Alice将使用Bob的公钥$𝑃_𝐵$，并计算点$𝑢_1𝐺 + 𝑢_2𝑃_𝐵 = (𝑥_1, 𝑦_1)$。如果满足$𝑟 ≡ 𝑥_1\ \ \ \ (mod\ n)$，则签名将被视为有效。这是正确的，因为它成立：

$𝑢_1𝐺 + 𝑢_2𝑃_𝐵 = 𝑧𝑠^{−1}𝐺 + 𝑟𝑠^{−1}𝑃_𝐵 = 𝑠^{−1}(𝑧𝐺 + 𝑟𝑃_𝐵) = 𝑠^{−1}(𝑧𝐺 + 𝑟𝑑_𝐵𝐺) = 𝑠^{−1}(𝑧 + 𝑟𝑑_𝐵)𝐺 = 𝑘(𝑧 + 𝑟𝑑_𝐵)^{−1}(𝑧 + 𝑟𝑑_𝐵)𝐺 = 𝑘𝐺$

如果签名有效，该点的`𝑥`坐标确实应该是`𝑟`，因为它在消息签名中的定义。应该注意的是，生成元`𝐺`的阶，用字母`𝑛`表示，应该是一个素数，这样才能在签名和验证算法中计算逆数。

可以看出，只有持有私钥$𝑑_𝐵$的人才能为公钥$𝑃_𝐵$创建有效签名。没有值$𝑑_𝐵$的攻击者无法计算签名中与$𝑃_𝐵$对应的值`𝑠`。如果攻击者想要创建与特定消息匹配的签名，他们将不得不解决ECDLP问题，即在给定$𝐺$和$𝑃_𝐵 = 𝑑_𝐵𝐺$的情况下找到私钥$𝑑_𝐵$，这是一个困难问题。

这个签名协议被称为椭圆曲线数字签名算法，简称ECDSA。该协议确保签名的消息没有被篡改或伪造，此外还确保签署消息的人不能否认他们创建了它。

在 ECDH 协议中，双方不必事先协调任何事情；而在 ECDSA 协议中，双方必须事先确认公钥。只有在每一方确定其持有的公钥确实属于预期通信对象之后，才能使用该协议。否则，使用未经确认的公钥验证签名就没有意义。

回到我们的故事。Alice确信她拥有的公钥$𝑃_𝐵$确实属于Bob，因为Bob在他们的约会中明确地给了她。Alice试图用它验证消息并发现不匹配。当然！其他人创建并签署了该消息，正如Alice所怀疑的那样。

这是协议的示意图：
<img src="images/ECDSA.png" alt="ECDSA">


### ECDSA与埃尔加马尔之间的相似性
在用于签名消息的埃尔加马尔协议中，双方就一个大素数`𝑝`和一个生成元`𝑔`达成一致。签名方在$1 ≤ 𝑑 < 𝑝 − 1$范围内生成某个值`𝑑`，称为私钥，计算值$𝑦 = 𝑔^𝑑\ \ \ \ (mod\ p)$，称为公钥，并发布它。

为了签署某条消息，他们计算值$z = hash(m)$并在$1 ≤ 𝑘 < 𝑝 − 1$范围内生成一个与$(p-1)$互质的随机值`𝑘`。他们计算$𝑟 = 𝑔^𝑘\ \ \ \ (mod\ p)$和$𝑠 = 𝑘^{−1}(𝑧 − 𝑑𝑟)\ \ \ \ (mod\ (p-1))$。消息`m`的签名被定义为计算值`​​𝑟`和`𝑠`的对。

接收到某条消息`𝑚`的一方，其签名由一对值​​`𝑟`和`𝑠`组成，使用公钥`𝑦`通过计算值$​𝑢_1 = 𝑟^𝑠𝑦^𝑟$和$𝑢_2 = 𝑔^𝑧$来验证签名。如果$𝑢_1 = 𝑢_2$，则签名将被视为有效。这是因为根据`𝑠`的定义，它表示：\
$𝑠 = 𝑘^{−1}(𝑧 − 𝑑𝑟)$，因此$𝑘𝑠 = 𝑧 − 𝑑𝑟$，因此$𝑧 = 𝑘𝑠 + 𝑑𝑟$。因此：

$𝑢_2 = 𝑔^𝑧 = 𝑔^{𝑘𝑠+𝑑𝑟} = 𝑔^{𝑘𝑠}𝑔^{𝑑𝑟} = (𝑔^𝑘)^𝑠(𝑔^𝑑)^𝑟 = 𝑟^𝑠𝑦^𝑟 = 𝑢_1$

攻击者无法在不知道私钥`𝑑`的情况下为公钥`𝑦`创建有效签名。要在给定公钥的情况下获得私钥，攻击者必须解决DLP问题，这是一个困难问题。

这里也存在基于ECDLP的ECDSA和基于DLP的埃尔加马尔之间的明显相似性。在这两种情况下，双方都必须事先协调公钥，并且每次我们想要签署新消息时都需要生成一个随机的`𝑘`值。此外，在这两种情况下，监听双方之间消息的攻击者都无法推断出可用于伪造签名的有用信息。

# ECC 攻击
我们已经了解了椭圆曲线如何在密码系统中用于协商秘密值和签署消息。与生活中的一切一样，在实际应用时，事情并不总是按计划进行。在本文的其余部分，我将介绍攻击基于ECC的密码系统的不同方法，这些系统可能被用户误用或以不安全的方式实现。

自然地，我将这部分分为针对ECDH的攻击和针对ECDSA的攻击。在这两种情况下，如果我们找到了其中一方的私钥，我们就认为攻击"成功"了，到此为止。对于ECDH，这就足够了，因为从私钥可以得到共享秘密值以及后续用它加密的所有信息。对于ECDSA，这也足够了，因为私钥可以用来随意签署消息。

### SageMath
SageMath是一个免费的开源数学软件。它可以用几乎与Python相同的语法编写，也可以作为Python库使用。这个库实现了与椭圆曲线相关的有用函数，因此对于我们在ECC环境中需要进行的计算非常有用。作为本文的一部分，我提供了用这个库编写的代码片段。我发现在Ubuntu操作系统上安装它最简单，特别是22.04版本。要安装它，只需运行命令：`sudo apt install sagemath`。
要运行包含代码的文件，请将文件保存为.sage扩展名，然后运行命令：`sage file.sage`。

此外，可以使用解释器，类似于Python的解释器，通过运行命令：`sage`。也可以创建导入sage.all库的.py文件，并使用命令`python3 file.py`运行它们。注意，当使用`sage`命令运行文件时，符号`^`被解释为幂运算，而使用`python3`运行时，该符号被解释为异或运算。

在本文中，我主要使用SageMath中的以下函数：
- `E.gens()` - 在曲线`E`中查找生成元
- `G.order()` - 计算生成元`G`的阶
- `n*G` - 将生成元`G`乘以数字`n`
- `n.factor()` - 将数字`n`分解为其因子 - 该函数返回一个由`(𝑝, 𝑒)`对组成的列表，其中`𝑝`是质因子，`𝑒`是它的指数，即`𝑝`在`n`的分解中出现的次数
- `crt` - 求解中国剩余定理的方程组

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

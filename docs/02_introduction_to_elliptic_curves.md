# Introduction To Elliptic Curves
### An Elliptic Curve
In general, an elliptic curve is some kind of curved line. An example of this is the parabola, whose equation is of the form $𝑦 = 𝑎𝑥^2 + 𝑏𝑥 + 𝑐$ and it looks like this:

![Parabola](images/parabola.png)

In the context of cryptography, it is customary to use elliptic curves whose equation is of the form

$𝑦^2 = 𝑥^3 + 𝑎𝑥 + 𝑏$

For example, an elliptic curve corresponding to the equation $𝑦^2 = 𝑥^3 − 3𝑥 + 3$ looks like this:

<img src="images/simple_elliptic_curve.png" alt="Simple elliptic curve" width="287" height="287">

The equation of the curve defines the relation between the `𝑥` coordinate of a point on the curve and its `𝑦` coordinate. In a cryptographic context, we restrict `𝑥`, `𝑦`, `𝑎`, `𝑏` to be integers, and restrict the calculations be modulo some large prime number. So the equation of the elliptic curve is:

$𝑦^2 = 𝑥^3 + 𝑎𝑥 + 𝑏\ \ \ \ (mod\ 𝑝)$.

This means that we have a finite number of points on the curve. In mathematical language, the curve is defined to be over a finite field of order `𝑝`. As a result now not necessarily every `𝑥` coordinate will have a corresponding point on the curve, because it may be that the `𝑦` coordinate corresponding to it is not an integer.


### Points On The Curve
The set of points on the curve consists of pairs of integers `(𝑥, 𝑦)` that satisfy the equation of the curve. In addition to these points, another special point called "Infinity" is defined, and it is denoted by `𝒪`. In mathematical language, this point is the neutral element of the set of points on the curve with respect to the addition operation, which we will define in the next section. The number of points on the curve (including the point `𝒪`) is called the "order of the curve".

Another observation is that elliptic curves are symmetric to the `X` axis. Which means that if the point `𝑃 = (𝑥, 𝑦)` is on the curve, then the point `−𝑃 = (𝑥, −𝑦)` is also on the curve. In fact, these points are considered "inverses" of each other (hence the marking `−𝑃` for the second point), and the result of the addition operation between them is defined to be the neutral element `𝒪`.

A theorem called Hasse's Theorem provides an estimation of `#𝐸`, the order of the curve, and is the order of magnitude of `Θ(𝑝)`. More accurately:

$𝑝 + 1 − 2\sqrt𝑝 ≤ 𝐸 ≤ 𝑝 + 1 + 2\sqrt𝑝$

### Points Addition
Given two points on the curve, it is possible to define an addition operation between them, resulting in a third point that is also on the curve. To find this point geometrically, we draw a line between the two given points, and continue it until it intersects the curve at a third point. This point is reflected in relation to the `𝑋` axis, and the resulting point is defined as the result of the addition.

Here is a diagram that shows how, given the points `𝑃` and `𝑄`, the point `𝑃 ​​+ 𝑄` can be found:

<img src="images/points_addition.png" alt="Points addition" width="300" height="300">

A question that may arise from this description is what happens if the line that is drawn between the two points does not intersect the curve again? In this case the line is said to intersect the curve at "infinity", and the result of the addition is the point `𝒪`. Notice that this case happens if the drawn line is vertical, that is, we are trying to add a point `𝑃` ​​with its inverse point, `−𝑃`:

<img src="images/point_addition_infinity.png" alt="Points addition infinity" width="283" height="283">

Two basic identities are derived from this. For every point `𝑃` it ​​holds that:

`𝑃 + 𝒪 = 𝑃`\
`𝑃 + (−𝑃) = 𝒪`

Another question that arises from the geometric description is how do we add a point to itself? We saw that in order to add two different points `𝑃` and `𝑄`, we draw a line between them and look at the intersection point of its continuation with the curve. Intuitively, we will leave `𝑃` constant, and look at the line that is created as we move `𝑄` "closer and closer" to `𝑃`, until `𝑄` will merge with `𝑃`. What we will get is a line that is more and more "tangent" to the curve at the point `𝑃`, and this is exactly the line we will look at when we want to add `𝑃` to itself:

<img src="images/point_multiplication.png" alt="Points multiplication" width="300" height="300">

To add a point `𝑃` to itself, we draw a tangent to the curve at the point `𝑃`, and continue it until it intersects the curve at a second point. This point is reflected in relation to the `𝑋` axis, and the resulting point is defined as the result of the addition. It is customary to mark the result of the addition as `𝑃 + 𝑃 = 2𝑃`. Again if the tangent does not intersect with the curve at a second point then it is said to intersect the curve at "infinity", and the result of the addition in this case is the point `𝒪`.

These visual geometric descriptions illustrate nicely and help us understand how point addition works. But how do we actually calculate it? Mathematical equations, of course!

Given the points $𝑃 = (𝑥_𝑃, 𝑦_𝑃)$ and $𝑄 = (𝑥_𝑄, 𝑦_𝑄)$, the result of their addition is the point $𝑅 = (𝑥_𝑅, 𝑦_𝑅)$ such that:


$𝑥_𝑅 = 𝜆^2 − 𝑥_𝑃 − 𝑥_𝑄\ \ \ \ \ \ \ \ \ (mod\ 𝑝)$ \
$𝑦_𝑅 = 𝜆(𝑥_𝑃 − 𝑥_𝑅) − 𝑦_𝑃\ \ \ \ (mod\ 𝑝)$

Where `𝜆` is defined to be the slope of the line connecting the points, if they are different, and the slope of the tangent to the curve at the point, if the point is added to itself. Formally:

$\displaystyle𝜆 = \frac{𝑦_𝑃 − 𝑦_𝑄}{𝑥_𝑃 − 𝑥_𝑄}\ \ \ \ \ (mod\ 𝑝)\ \ \ ;\ \ \   𝑖𝑓 𝑃 ≠ 𝑄$\
$\displaystyle𝜆 = \frac{3{𝑥_𝑃}^2 + 𝑎}{2𝑦_𝑃}\ \ \ \ (mod\ 𝑝)\ \ \ ;\ \ \   𝑖𝑓 𝑃 = 𝑄$

The mathematical calculations behind points addition are not critical for the rest of the article. For that matter, we can look at point addition as a black box that receives two points on the curve and returns a third point that is also on the curve.

### Multiplying A Point On The Curve By A Constant
We saw that it is possible to add a point `𝑃` ​​to itself, and we denoted the resulting point by `2𝑃`. If we add the point `𝑃` ​​to this result again, we will reach a point denoted by `3𝑃`, and so on. In this way it is possible to define "multiplication" of a point by a constant, by repeatedly adding the point to itself (similarly to the multiplication between numbers):

$𝑛𝑃 = 𝑃 + 𝑃 + ⋯ + 𝑃\ \ \ \ \ (n\ times)$

Seemingly, to multiply a point by a number `𝑛` we need to perform `𝑛` add operations between points. This is because given a starting point, it is difficult to know in advance where the "last" point will fall, without reaching it "step by step". Such a calculation would be very inefficient, because `𝑛` could be very large.

For this purpose, the `Double And Add` algorithm exists, in which we start from the point `𝑃`, then for each bit in the binary representation of `𝑛`, the current point is multiplied by `2` (that is, it is added to itself), and is added to the result if the bit value is `1`. The runtime complexity of this algorithm is `𝑂(log 𝑛)`, and it allows to efficiently multiply points by very large numbers.

An important property of point multiplication that we will use later is that for every point `𝑃` and pair of numbers `𝑎`, `𝑏` it holds:

$𝑏(𝑎𝑃) = (𝑏𝑎)𝑃 = (𝑎𝑏)𝑃 = 𝑎(𝑏𝑃)$

Intuitively, suppose we start from point `𝑃`, take `𝑎` steps from it, and reach the point `𝑎𝑃`. From this point, we take `𝑏` steps of "size" `𝑎` and reach the point `𝑏(𝑎𝑃)`. Alternatively, in another scenario, we could start from point `𝑃`, take `𝑏` steps with it and reach point `𝑏𝑃`. From this point take `𝑎` steps of "size" `𝑏` and reach the point `𝑎(𝑏𝑃)`.

In both scenarios we took the same amount of `𝑎𝑏` steps from the point `𝑃` in total, so in both scenarios we reached the same final point. Mathematically, multiplying a point by a constant is associative.


### Generator Point
If we start from a point `𝑃` ​​and add it to itself again and again and again, at each such step we will reach some new point on the curve. Because there is a finite number of points on the curve, at some stage we will reach again to points we have reached before, and we will be in some kind of loop, or a "circle". More precisely, at some stage we will reach the point `-𝑃`, in the next step we will reach the point `𝒪`, and in the step after that we will again reach the point `𝑃`, from which we started.

The point that creates such a "circle" is called a Generator, because the entire "circle" can be generated from it, and it is customary to mark it with the letter `𝐺`. The number of points in the "circle" (including the point `𝒪`) is called the "order of the generator `𝐺`", and is usually denoted by `𝑛`. Each point on the curve forms a "circle" of some sort. Mathematically, the set of points on this "circle" is a cyclic group.

An interesting property that results from this is that multiplying a point `𝐺` by its order `𝑛` gives us the point of infinity:\
`𝑛𝐺 = 𝒪`

### The Hard Problem
“Given points `𝑃` and `𝑄` such that `𝑄 = 𝑥𝑃` for some `𝑥`, it is hard to find `𝑥`.”


And in words, suppose someone started from some starting point, took a certain number of steps from it, and reached a final point. Given the starting point and the final point, how do we know how many steps they took?

The answer to this question is not so intuitive, because it is difficult to predict in advance from a starting point which points will be reached by taking steps from it. A naive solution could be to start from `𝑃` ourselves, advance forward from it one step at a time and count the steps we take, until we reach `𝑄`. The complexity of this solution is `𝑂(𝑥)`, and it is unfeasible if it is known that `𝑥` is a large number, for example if `𝑥` is `256 bit`.


This problem is called the Elliptic Curve Discrete Logarithm Problem (ECDLP), and it is a hard problem. But how hard is it?

In a cryptographic context, it is customary to measure "difficulty of problems", or "strength of a cryptographic system", with a metric called `Security Level`. In this metric, a problem is said to have "`𝑛` bits security" if the best known attack solves the problem in $𝑂(2^𝑛)$ steps.

Currently, the best algorithm that solves the ECDLP problem does it with a complexity of $𝑂(\sqrt n)$, where `𝑛` is the order of the point `𝑃`, and it does it using a Meet In The Middle attack. When a point with a big enough order is selected, solving it is unfeasible, hence the strength of the problem.

For example, if we choose `𝑛` of size `256 bit`, we get that the ECDLP problem has a security level of `128 bit` security. For comparison, to achieve the same security level of `128 bit` security in RSA encryption, which is based on the problem of integer factorization, a public key with a size of `3072 bit` is required. This makes the use of elliptic curves relatively more computationally efficient.


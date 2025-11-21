# ECC Attacks
We saw how elliptic curves can be used in cryptographic systems for agreeing on a secret value and for signing messages. As with everything in life, when it comes to putting something into practice, things don't always work as planned. In the rest of the article I will present different ways to attack ECC-based cryptographic systems that have been misused by the user, or implemented in an unsafe manner.

Naturally, I split this part into attacks on ECDH and attacks on ECDSA. In both cases we will say that we "succeeded" in the attack if we find the private key of one of the parties, and we will stop there. In the case of ECDH, it is enough because from the private key it is possible to reach the shared secret value and all the information encrypted with it later. In the case of ECDSA, this is enough because the private key can be used to sign messages as we wish.

### SageMath
SageMath is a free and open-source mathematical software. It can be written in almost the same syntax as Python, and it can also be used as a Python library. This library implements useful functions that are relevant to elliptic curves and is therefore very useful for the calculations we need to do in the context of ECC. As part of this article I provide code snippets written in this library. I found it is easiest to install it on the Ubuntu operating system, specifically version 22.04. To install it, simply run the command: `sudo apt install sagemath`.
To run a file that contains code, save the file with the .sage extension and run the command: `sage file.sage`.

Additionally, an interpreter can be used, similarly to Python's interpreter, by running the command: `sage`. It is also possible to create .py files in which the library sage.all is imported, and run them with the command `python3 file.py`. Note that when running a file with the command `sage`, the notation `^` is interpreted as power, while when running with `python3`, this notation is interpreted as xor.

In this article I mainly use the following functions in SageMath:
- `E.gens()` - finding generators in curve `E`
- `G.order()` - calculating the order of the generator `G`
- `n*G` -multiplication of the generator `G` by the number `n`
- `n.factor()` - factorize the number `n` into its factors - the function returns a list of pairs `(𝑝, 𝑒)` such that `𝑝` is a prime factor, and `𝑒` is its exponent, i.e. the number of times that `𝑝` appears in the decomposition of `n`
- `crt` - solving an equation system of the Chinese remainder theorem



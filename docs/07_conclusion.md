# Conclusion
## ECDH Attacks Overview
| Problem Type  | The Problem | The Attack | How The Attack Works | Attack Complexity |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| Selecting a curve with an unsafe generator | The order of the generator `n` is too small | Baby-Step Giant-Step | Meet In The Middle | $𝑂(\sqrt n)$ |
| Selecting a curve with an unsafe generator | The order of the generator `n` is a smooth number | Pohlig-Hellman | Decomposing `𝑛` to prime factors, attacking each of them separately, and combining the results using the Chinese Remainder Theorem | $O(\sqrt{p_{max}})$ where $p_{max}$ is the largest prime factor in the decomposition of `𝑛` |
| Selecting a curve with an unsafe generator + selecting an insecure private key | The order of the generator `n` is almost a smooth number, and the private key is small | Improved Pohlig-Hellman | Decomposing `𝑛` to prime factors, discarding factors that are too big, attacking each of them separately, and combining the results using the Chinese Remainder Theorem | $O(\sqrt{p_{max}})$ where $p_{max}$ is the largest prime factor in the decomposition of `𝑛` |
| Incorrect implementation of ECDH | Not verifying that a point is on the curve | Invalid Curve Attack | Sending points with small orders on malicious curves as a public key, attacking each of them separately, and combining the results using the Chinese Remainder Theorem | $𝑂(𝑛_{𝑚𝑎𝑥})$ where $𝑛_{𝑚𝑎𝑥}$ is the largest order among the orders of the malicious points |
| Selecting curve parameters insecurely | The curve is singular | Reducing ECDLP to DLP | Mapping points to numbers in a way that converts points addition to integers multiplication | $O(\sqrt{p_{max}})$ where $p_{max}$ is the largest prime factor in the decomposition of $(p-1)$ |
| Selecting curve parameters insecurely | The curve is supersingular | Reducing ECDLP to DLP | Mapping points to numbers in a way that converts points addition to integers multiplication | $e^{O((log\ p^k)^{1/3}(log\ log\ p^k)^{2/3})}$ where `k` is the embedding degree with respect to the generator |
| Selecting curve parameters insecurely | The curve is anomalous | Smart's Attack | A series of mappings between points on a curve to points on a curve over `p-adic` numbers, and back to integers | $O(1)$ |


## ECDSA Attacks Overview
| Problem Type  | The Problem | The Attack | How The Attack Works | Attack Complexity |
| ------------- | ------------- | ------------- | ------------- | ------------- |
| Incorrect implementation of signature and verification  | Not hashing the message before signing it | Given a signed message, forging additional messages that correspond to the same signature | Keeping the message prefix as-is and modifying the rest of it | $O(1)$ |
| Incorrect usage of the signature algorithm | Reusing the same value of `k` in different signatures | Finding the private key of the user | Finding the value of `k`, and calculating the private key of the user from it | $O(1)$ |
| Incorrect usage of the signature algorithm | Generating `k` values insecurely | Given several signed messages, find the private key of the user | Reducing the problem to finding short vector in a lattice, Finding the value of `k`, and calculating the private key of the user from it |  $O(d^6\ \log^3B)$ where `B` is the bias of `k`, and `d`d is the number of signed messages |
| Incorrect implementation of verification | Not verifying the generator is valid | Forging signatures that are successfully verified (Curveball) | Selecting fake generator and private key that correspond to the public key of another user | $O(1)$ |


## Protection Against These Attacks
It should be noted that in ECDH, both parties have to agree on the curve at the beginning of the protocol. If a user is communicating with an attacker, and the attacker is the one providing the curve parameters, then the attacker can provide unsafe parameters. As a result the attacker can obtain the user's private key. If the user always uses the same private key, then the attacker can decrypt all conversations between that user and any other user. That is why it is very important not to allow unfamiliar users to provide the curve parameters if they cannot be trusted. In addition, you have to make sure that every point received from a foreign user is actually on the agreed upon curve. And of course, you should make sure that the selected curve itself is not vulnerable to one of the known attacks that we have seen. Also, it is better to use a new private key every time you use the ECDH protocol.

Similarly, in ECDSA, care must be taken to properly implement the signature and verification algorithms. Do not skip the hash of the message, the random and safe generation of the `𝑘` value in every time the protocol is used, and of course in the signature verification, if the generator is received from the user - make sure it is indeed the one that was agreed upon earlier.

## References
- In this article I used graph charts from the book Understanding Cryptography by Christof
paar:\
https://gnanavelrec.wordpress.com/wp-content/uploads/2019/06/2.understanding-cryptography-by-christof-paar-.pdf


- A site that illustrates what cryptographic elliptic curves look like:\
https://graui.de/code/elliptic2/

- Detailed explanation of the addition and multiplication operations in elliptic curves:\
https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication

- Lecture on introduction to elliptic curves and points addition - by Christof Paar:\
https://www.youtube.com/watch?v=vnpZXJL6QCQ

- Lecture on generators, ECDLP, difficulty of problems, ECDH, Double And Add - by Christof Paar:\
https://www.youtube.com/watch?v=zTt4gvuQ6sY

- Explanation of the Security Level of different encryption algorithms:\
https://en.wikipedia.org/wiki/Security_level

- Explanation of ECDH:\
https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman

- Explanation of ECDSA:\
https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm

- Explanation of signatures with ElGamal:\
https://en.wikipedia.org/wiki/ElGamal_signature_scheme

- Explanation of the Chinese remainder theorem:\
https://en.wikipedia.org/wiki/Chinese_remainder_theorem

- Explanation of the relationship between the discriminant of a singular curve and the fact that it has a double root:\
https://www.quora.com/For-an-elliptic-curve-in-the-form-Y-2-X-3+AX+B-why-is-4A-3+27B-2-neq-0-the-condition-for-non-singularity

- An example in small numbers of the mapping between points and numbers in singular curves:\
https://crypto.stackexchange.com/questions/61302/how-to-solve-this-ecdlp/61434#61434

- Explanations of 𝑝-adic numbers:\
https://en.wikipedia.org/wiki/P-adic_number \
https://www.youtube.com/watch?v=3gyHKCDq1YA

- Explanation of the mathematics behind the MOV attack:\
https://risencrypto.github.io/WeilMOV/

- Explanations of the mathematics behind the Smart's Attack (it is quite complicated, you've been warned):\
https://wstein.org/edu/2010/414/projects/novotney.pdf \
http://www.monnerat.info/publications/anomalous.pdf

- Explanation of the lattice-based attack and the LLL algorithm:\
https://forum.vac.dev/t/lattice-attacks-on-ecdsa/136 \
\
The attack is based on part 4 in an article by Joachim Breitner and Nadia Heninger:\
https://eprint.iacr.org/2019/023.pdf

- Explanation of the CVP problem:\
https://en.wikipedia.org/wiki/Lattice_problem#Closest_vector_problem_(CVP)

- Explanation of the LLL algorithm:\
https://en.wikipedia.org/wiki/Lenstra%E2%80%93Lenstra%E2%80%93Lov%C3%A1sz_lattice_basis_reduction_algorithm

# Elliptic Curves In The Context Of Cryptography
After all this introduction to the world of elliptic curves, we will move on to see what can be done with them in a cryptographic context. As we know, cryptographic systems are usually based on a "hard problem" that is difficult to solve. For example RSA with the problem of factoring a number that we mentioned, or the Diffie-Hellman protocol with the discrete logarithm problem. A cryptographic system that is based on the ECDLP problem in an elliptic curve belongs to the Elliptic Curve Cryptography family, or for short ECC.


### First Use Of Elliptic Curves - Agreement On A Shared Secret
Let's start with a story. Imagine you are at a party - a room full of people, where everyone can talk to everyone and everyone hears everyone. In this room there are also Alice and Bob, who have never met before. Alice likes Bob, and she wants to ask him out. Alice is a little shy, so she wants to tell Bob this secret message without all the other party guests hearing her. Alice and Bob have not coordinated anything in advance, and everything Alice says to Bob will be heard by all the other guests at the party. How can Alice tell the message to Bob without anyone else hearing it?

If you answered "elliptic curves", then you are right!

Alice will select some elliptic curve and a generator in it, and tell them to Bob. Specifically, Alice will pass to Bob (and everyone else in the room) the two curve parameters `𝑎`, `𝑏`, the modulus `𝑝`, and the generator `𝐺`. In addition, Alice will select some value $𝑑_𝐴$ in the range $1 ≤ 𝑑_𝐴 ≤ 𝑛 − 1$ where `𝑛` is the order of `𝐺`. The value $𝑑_𝐴$ is called Alice's private key. Alice will calculate the point $𝐴 = 𝑑_𝐴𝐺$, which is called Alice's public key, and tell it to Bob. Similarly, Bob will select a private key $𝑑_𝐵$, calculate the point $𝐵 = 𝑑_𝐵𝐺$, which is called Bob's public key, and tell it to Alice.

Alice will take Bob's public key, multiply that point by her private key, and reach a third point $𝑃_𝐴 = 𝑑_𝐴𝐵$. Similarly, Bob will take Alice's public key, multiply it by his private key, and reach a third point of his own $𝑃_𝐵 = 𝑑_𝐵𝐴$. If we examine the points that Alice and Bob reached separately, we find that they reached the same point! This fact comes from the associativity property of multiplying a point by a constant we saw before:

$𝑃_𝐴 = 𝑑_𝐴𝐵 = 𝑑_𝐴(𝑑_𝐵𝐺) = 𝑑_𝐵(𝑑_𝐴𝐺) = 𝑑_𝐵𝐴 = 𝑃_𝐵$

At the end of the whole process, Alice and Bob managed to reach an agreement on some point on the curve, and at no stage did either of them pass that point to the other person. The information everyone has heard is: `𝑎`, `𝑏`, `𝑝`, `𝐺`, `𝐴`, `𝐵`. A person who is in the room listening to this information cannot find the point that Alice and Bob agreed on with it.


This is because if another person in the room wanted to find that point, they would need to know either Alice's private key or Bob's private key in order to multiply `𝐵` or `𝐴` by them. To find Alice's private key for example, they will look at $𝐴 = 𝑑_𝐴𝐺$, because this is the only information that was sent and "contains" Alice's private key. Given `𝐺` and $𝑑_𝐴𝐺$, to find $𝑑_𝐴$ is equivalent to solving the discrete logarithm problem in elliptic curves, which is, as mentioned, a hard problem.

This beautiful protocol is called: Elliptic Curve Diffie-Hellman (ECDH).

### Using The Shared Secret For Further Communication
We haven't finished our story. Although Alice and Bob agreed on a shared secret point, Alice still did not ask Bob on the date she so badly wanted.

After the parties have agreed on a shared secret point, they can use it as the encryption key of any encryption method, for example AES, and from that point communicate securely through encryption.

It is common to take one of the `𝑥` or `𝑦` coordinates ​​of the point, and use it. To maintain safety, it is recommended to hash the selected value and use only the hash result as an encryption key. In practice, sometimes the value is too big to be used an an encryption key. For example, if the hash function used is SHA-1, its output length is `160 bit`, while AES encryption requires only `128 bit`. In such a case, it is customary to use only `128 bits` out of the `160`, and discard the rest.

Anyway, at this point Alice and Bob agree on an encryption key, and they are the only ones who know it. From this point on they communicate through encryption, and anyone listening in the room cannot understand what they are saying.

Here is a diagram of the protocol:
<img src="images/ECDH.png" alt="ECDH">

Using the agreed upon key, Alice encrypts the message "Hey Bob, would you like to go out for coffee tomorrow evening?", and passes the encrypted message to Bob. Bob decrypts the message with the key he also knows. Alice hopes that Bob will say yes, but that is not a part of the protocol.

### The Similarities Between Elliptic Curve Diffie-Hellman And Diffie-Hellman
In the known Diffie-Hellman (DH) protocol, the parties openly transmit a prime number `𝑝` and a generator `𝑔` that is in the group corresponding to the value `𝑝`. Alice randomly generates a private key `𝑎` and openly broadcasts her public key $𝐴 = 𝑔^𝑎\ \ \ \ (mod\ 𝑝)$. Similarly Bob randomly generates a private key `𝑏` and openly broadcasts his public key $𝐵 = 𝑔^𝑏\ \ \ \ (mod\ 𝑝)$. Alice then takes Bob's public key and raises it to the power of her private key, thus calculates the value $𝐾 = 𝐵^𝑎 = (𝑔^𝑏)^𝑎 =𝑔^{𝑎𝑏}\ \ \ \ (mod\ 𝑝)$. In the same way Bob calculates the value $𝐾 = 𝐴^𝑏 = (𝑔^𝑎)^𝑏 =𝑔^{𝑎𝑏}\ \ \ \ (mod\ 𝑝)$. At the end of the process, Alice and Bob were able to agree on a common `𝐾` value, without transmitting it between them.

An attacker listening to them cannot find `𝐾` given the broadcasted values `𝑝`, `𝑔`, `𝐴`, `𝐵`. In order to do this, they will have to find either Alice's or Bob's private keys. To calculate Alice's private key for example, they would have to find `𝑎` given `𝑔` and $𝑔^𝑎\ \ \ \ (mod\ 𝑝)$, which is a hard problem. This problem is called the Discrete Logarithm Problem (DLP).

There is a very clear similarity between DH, which is based on DLP, and ECDH, which is based on ECDLP (they are basically the same, only with an EC prefix). In both protocols, two parties talking to each other can agree on some shared secret value , without them coordinating anything in advance. Anyone who listens to the messages between the parties will be exposed to the public information they pass between them, but will not be able to reach the secret value shared between them.


### Second Use Of Elliptic Curves - Signing A Message
Continuing our story, let's say that Alice and Bob went on their date and spent a nice evening together. The next day Alice receives a message saying "Hi Alice, this is Bob, I had a great time with you yesterday and I would love to meet you again this weekend". Alice suspects that it is not Bob who sent the message, because she knows that Bob had so much fun with her yesterday, that he will not wait until the weekend to meet her, but will want to meet her tomorrow! How can Alice verify that it is Bob who wrote the message?

If you answered "elliptic curves", then you are right again!

The difficulty of the ECDLP problem can also be used to sign messages. During their date, Alice and Bob agreed on some elliptic curve and a generator `𝐺` in it. Bob generated some value $𝑑_𝐵$, called Bob's private key, and calculated the point $𝑃_𝐵 = 𝑑_𝐵𝐺$, called Bob's public key. Bob gave Alice his public key so that she could use it to later verify if a message she receives was indeed signed by him.

Let's say Bob wants to sign a certain message `𝑚`. He will calculate the value $z = hash(m)$ using some secure hash function, and keep an amount of bits from the result equal to the bit length of `n`, the order of the generator `𝐺`. Bob will generate some random value `𝑘` in the range $1 ≤ 𝑘 ≤ 𝑛 − 1$. Bob will then calculate the point $𝑘𝐺 = (𝑥_1, 𝑦_1)$, take its `𝑥`-coordinate, and calculate $𝑟 = 𝑥1\ \ \ \ (mod\ n)$. Finally, Bob will calculate the value $𝑠 = 𝑘^{−1}(𝑧 + 𝑟𝑑_𝐵)$.

The signature of the message `𝑚` is defined to be the pair of calculated values ​​`𝑟` and `𝑠`.

Suppose that Alice received a certain message `𝑚`, and its signature consists of a pair of values `​𝑟` and `𝑠`. Alice wants to make sure that it is indeed Bob who signed the message. Alice will calculate the value $z = hash(m)$ in the same way as Bob. Alice will then calculate the values $𝑢_1 = 𝑧𝑠^{−1}$ and $𝑢_2 = 𝑟𝑠^{−1}$. Finally Alice will use Bob's public key $𝑃_𝐵$, and calculate the point $𝑢_1𝐺 + 𝑢_2𝑃_𝐵 = (𝑥_1, 𝑦_1)$. The signature will be considered valid if it holds that $𝑟 ≡ 𝑥_1\ \ \ \ (mod\ n)$. The reason this is correct is that it holds:

$𝑢_1𝐺 + 𝑢_2𝑃_𝐵 = 𝑧𝑠^{−1}𝐺 + 𝑟𝑠^{−1}𝑃_𝐵 = 𝑠^{−1}(𝑧𝐺 + 𝑟𝑃_𝐵) = 𝑠^{−1}(𝑧𝐺 + 𝑟𝑑_𝐵𝐺) = 𝑠^{−1}(𝑧 + 𝑟𝑑_𝐵)𝐺 = 𝑘(𝑧 + 𝑟𝑑_𝐵)^{−1}(𝑧 + 𝑟𝑑_𝐵)𝐺 = 𝑘𝐺$

If the signature is valid, the `𝑥` coordinate of this point should indeed be `𝑟` as it is defined in the message signature. It should be noted that the order of the generator `𝐺`, which is denoted by the letter `𝑛`, should be a prime number, and this is so that it will indeed be possible to calculate the inverse numbers in the signature and verification algorithms.

It can be seen that only the person who holds the private key $𝑑_𝐵$ can create a valid signature for the public key $𝑃_𝐵$. An attacker who does not have the value $𝑑_𝐵$, cannot calculate the value `𝑠` corresponding to $𝑃_𝐵$ in the signature. If the attacker wants to create a signature that matches a certain message, they will have to solve the ECDLP problem, that is, find the private key $𝑑_𝐵$ given $𝐺$ and $𝑃_𝐵 = 𝑑_𝐵𝐺$, which is a hard problem.

This signature protocol is called Elliptic Curve Digital Signature Algorithm, or ECDSA for short. The protocol ensures that the signed messages have not been altered or forged, and in addition ensures that the person who signed the message cannot deny that they created it.

Unlike the ECDH protocol, where the parties did not have to coordinate anything in advance, in the ECDSA protocol the parties must agree in advance on a public key. Only after each party knows for sure that the public key they hold indeed belongs to the person they want to communicate with, the protocol can be used. Otherwise, there is no meaning in verifying the signature with the public key that each party possesses.

Back to our story. Alice knows for sure that the public key $𝑃_𝐵$ in her possession does belong to Bob, because Bob explicitly gave it to her on their date. Alice tries to verify the message with it and discovers that there is no match. of course! Someone else created the message and signed it, just as Alice suspected.

Here is a diagram of the protocol:
<img src="images/ECDSA.png" alt="ECDSA">


### The Similarities Between ECDSA And ElGamal
In the ElGamal protocol for signing messages, the parties agree on a large prime number `𝑝` and a generator number `𝑔`. The signing party generates some value `𝑑` in range $1 ≤ 𝑑 < 𝑝 − 1$, called the private key, calculates the value $𝑦 = 𝑔^𝑑\ \ \ \ (mod\ p)$, called the public key, and publishes it.

In order to sign a certain message, they calculate the value $z = hash(m)$ and generate a random value `𝑘` in the range $1 ≤ 𝑘 < 𝑝 − 1$ that is co-prime to $(p-1)$. They calculate $𝑟 = 𝑔^𝑘\ \ \ \ (mod\ p)$ and $𝑠 = 𝑘^{−1}(𝑧 − 𝑑𝑟)\ \ \ \ (mod\ (p-1))$. The signature of the message `m` is defined to be the pair of calculated values `​​𝑟` and `𝑠`.

The party that has received a certain message `𝑚`, and its signature consists of a pair of values ​​`𝑟` and `𝑠`, uses the public key `𝑦` to verify the signature by calculating the values $​𝑢_1 = 𝑟^𝑠𝑦^𝑟$ and $𝑢_2 = 𝑔^𝑧$. The signature will be considered valid if $𝑢_1 = 𝑢_2$. This is because according to the definition of `𝑠` it denotes:\
$𝑠 = 𝑘^{−1}(𝑧 − 𝑑𝑟)$, therefore $𝑘𝑠 = 𝑧 − 𝑑𝑟$, hence $𝑧 = 𝑘𝑠 + 𝑑𝑟$. Therefore:

$𝑢_2 = 𝑔^𝑧 = 𝑔^{𝑘𝑠+𝑑𝑟} = 𝑔^{𝑘𝑠}𝑔^{𝑑𝑟} = (𝑔^𝑘)^𝑠(𝑔^𝑑)^𝑟 = 𝑟^𝑠𝑦^𝑟 = 𝑢_1$

An attacker cannot create a valid signature for the public key `𝑦` without knowing the private key `𝑑`. To obtain the private key given the public key, the attacker would have to solve the DLP problem, which is a difficult problem.

Here too there is a clear similarity between ECDSA, which is based on ECDLP, and ElGamal, which is based on DLP. In both cases, the parties have to coordinate a public key in advance, and it is required to generate a random `𝑘` value every time we want to sign a new message. Also, in both cases an attacker listening to the messages between the parties cannot deduce useful information that would allow them to forge signatures.


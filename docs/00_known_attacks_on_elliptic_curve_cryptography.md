# Known Attacks On Elliptic Curve Cryptography
- [Introduction](#Introduction)
- [Introduction To Elliptic Curves](#Introduction-To-Elliptic-Curves)
- [Elliptic Curves In The Context Of Cryptography](#Elliptic-curves-in-the-context-of-cryptography)
- [ECC Attacks](#ECC-Attacks)

### ECDH Attacks
- [The Order Of The Generator Is Too Small](#The-order-of-the-generator-is-too-small)
- [The Order Of The Generator Is A Smooth Number](#The-order-of-the-generator-is-a-smooth-number)
- [The Order Of The Generator Is Almost A Smooth Number, And The Private Key Is Small](#The-order-of-the-generator-is-almost-a-smooth-number-and-the-private-key-is-small)
- [Not Verifying That A Point Is On The Curve](#Not-verifying-that-a-point-is-on-the-curve)
- [The Curve Is Singular](#The-curve-is-singular)
- [The Curve Is Supersingular](#The-curve-is-supersingular)
- [The Curve Is Anomalous](#The-curve-is-anomalous)

### ECDSA Attacks
- [Not Hashing The Message Before Signing It](#Not-hashing-the-message-before-signing-it)
- [Reusing The Same Value Of k In Different Signatures](#Reusing-the-same-value-of-k-in-different-signatures)
- [Generating k Values Insecurely](#Generating-k-values-insecurely)
- [Not Verifying The Generator Is Valid](#Not-verifying-the-generator-is-valid)

### Conclusion
- [ECDH Attacks Overview](#ECDH-attacks-overview)
- [ECDSA Attacks Overview](#ECDSA-attacks-overview)
- [Protection Against These Attacks](#Protection-against-these-attacks)
- [References](#References)

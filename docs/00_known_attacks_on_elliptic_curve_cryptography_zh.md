# 椭圆曲线密码学的已知攻击
- [介绍](#Introduction)
- [椭圆曲线介绍](#Introduction-To-Elliptic-Curves)
- [密码学背景下的椭圆曲线](#Elliptic-curves-in-the-context-of-cryptography)
- [ECC 攻击](#ECC-Attacks)

### ECDH 攻击
- [生成元的阶太小](#The-order-of-the-generator-is-too-small)
- [生成元的阶是一个光滑数](#The-order-of-the-generator-is-a-smooth-number)
- [生成元的阶几乎是光滑数，且私钥很小](#The-order-of-the-generator-is-almost-a-smooth-number-and-the-private-key-is-small)
- [不验证点是否在曲线上](#Not-verifying-that-a-point-is-on-the-curve)
- [曲线是奇异的](#The-curve-is-singular)
- [曲线是超奇异的](#The-curve-is-supersingular)
- [曲线是反常的](#The-curve-is-anomalous)

### ECDSA 攻击
- [签名前不对消息进行哈希](#Not-hashing-the-message-before-signing-it)
- [在不同签名中重复使用相同的 k 值](#Reusing-the-same-value-of-k-in-different-signatures)
- [不安全地生成 k 值](#Generating-k-values-insecurely)
- [不验证生成元是否有效](#Not-verifying-the-generator-is-valid)

### 结论
- [ECDH 攻击概述](#ECDH-attacks-overview)
- [ECDSA 攻击概述](#ECDSA-attacks-overview)
- [防御这些攻击](#Protection-against-these-attacks)
- [参考文献](#References)

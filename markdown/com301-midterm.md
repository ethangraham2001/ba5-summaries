---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: COM301 Summary for Midterm
author: Ethan Graham
date: \today
---

# Week 01: Basics and Definitions

## Basic Properties
Generally when we design software, we seek the following properties:

1. **Correctness:** For a given input, we should provide an expected output
2. **Safety:** Well-formed programs cannot have bad (or even dangerous) outputs
3. **Robustness:** Cope with errors (both input and execution)

*Properties of a computer system must hold in the presence of a ressourced strategic adversary*

## Security Policy
A high-level description of the security properties that must hold in the 
system in relation to assets and principals.

## Thread Model 
Describes the resources available to the adversary and the adversary's
capabilities *(observe, influence, corrupt...)*

The adversary is a malicious entity aiming at breaching the security policy.
The adversary is strategic, and will choose the ***optimal*** way to use their
resources to mount an attack that violates the security properties.


## All together
If the properties hold within the thread model, it means there are no vulnerabilities
that can be exploited to materialize threats, and no harm happens.

## Security Mechanism
Technical mechanism used to ensure that the security policy is not violated
by an adversary **within the thread model**

Showing insecurity is as easy as finding a single exploitable vulnerability. 
Proving security is much more difficult as it requires proving that there are
zero exploitable vulnerabilities. We call this a **security argument**, and it
must be rigourous (either mathimatically or verbally).

We musn't ask *"is this system secure"*, we must ask
*"is this system secure under this specified threat model"*

# Week 02: Principles

## 1. Economy of Mechanism
Keep implementation/mechanisms as simple and as small as possible.

We do this because we want it to be easy to reason about our mechanisms to more
easily audit and verify them. Operational testing is bullshit and you shouldn't
do it.

**KISS:** Keep it simple, stupid.

A *(preferably small)* security mechanism on which the system relies is called
**TCB** for trusted computing base. We trust it to operate correctly. Something
going wrong in the TCB violates the security policy. By definition, if something
if something fucks up outside of the TCB, the security policy hasn't failed.

## 2. Fail-Safe Defaults
Base decisions on permissions instead of exclusion. Put otherwise, whitelist,
do not blacklist.

We do this because lack of permission is easy to detect and solve. 

If something fails, it should be as secure as if it had not failed at all. To
illustrate this, think of the automatic door example *(if it breaks, then it should stay closed)*.
If something fucks up, we should go to a known safe-state. Don't try to fix anything.

## 3. Complete Mediation
Every access to every object must be checked for authority. Put otherwise,
actions should be checked before we allow something to happen.

In reality, this principle is very difficult to implement. Picture checking
every single memory access on a computer. Or in a distributed system, where
do even place the checks? It becomes very complex very quickly, and hard to check
for correctness.

## 4. Open Design
The design should not be secret. We should design a system under the assumption
that the adversary will immediately gain full familiarity with it - it shouldn't
require secrecy.

**Linus' Law:** Given enough eyes, all bugs are shallow.

## 5. Separation of Privilege
No single accident, deception, or breach of trust is sufficient to compromise
the protected information.

Having one entity (user, process, etc...) be solely responsible for a security
critical task is no good.

This introduces some complexity. Picture two-factor authentication for a bank
account, which is a pain in the ass. How do we access an account if we don't
have a phone with us??

Having to meet more than one condition increases complexity, which is in direct
violation of the *economy of mechanism principle*

## 6. Least Privilege
Every program and every user should operate with the least amount of privilege
required to complete the job - right as needed, discarded after use.

The idea is to minimize high-privilege actions/interactions as much as possible.
As an example, we can think of guest accounts on a platform, or the
data minimization principle.

## 7. Least Common Mechanism
Minimize the number of mechanisms common to more than user, and depended on by
all users.

Having common mechanisms makes the system more complex.

## 8. Psychologial Acceptability
We should hide the complexity introduced by security mechanisms, otherwise
users may not routinely and automatically apply them correctly.

## 9. Work Factor (Extra Principle)
Compare the cost of circumventing the mechanism with the resources of a potential
attacker. This is difficult to transpose to computer security since shit is free

## 10. Compromise Recording (Extra Principle)
Reliably record that a compromise of information has occurred. I.e. keep
tamper evidence logs - they may enable recovery.

## Summary
Principles are important as they allow us to recognize unsafe patterns, but they
shouldn't be used a blind checklist.

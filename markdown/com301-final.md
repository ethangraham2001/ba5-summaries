---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS323 Notes/Summary for Final 
author: Ethan Graham
date: \today
---

# Week 01 - Basics

We can define computer security as:

Properties of a computer system must hold in the presence of a resourced
strategic adversary.

## Properties

- Confidentialiy: prevent unauthorized disclosure of information
- Integrity: prevent unauthorized modification of information
- Availability: prevent unauthorized denial of service
- Authenticity
- Anonymity
- Non-repudiation

## Security Policy *(Properties that must hold)*

High level description of the security properties that must hold in the system
in relation to assets and principals.

## Threat Model *(Description of the resourced strategic advsersary)*

Describes the resources available to the adversary and the adversary's
capabilities *(observe, influence, corrupt)*.

## Security Mechanism

Technical mechanism to ensure that the security policy is not violated by an
adversary ***within the threat model***.

Note that human's are also part of the system, and they could be the reason that
it fails.

## Security Argument

Rigorous argument that the security mechanisms in place are indeed effective in
maintaining the security policy *(verbal or mathematical)*. This is subject
to the assumptions of the threat model.

# Week 02 - Principles of CompSec

We use basic principles to build security mechanisms - they help *guide*
design and contribute to an implementation without security flaws. We should
always try to follow them - although there are tradeoffs. If a rule isn't
followed, it should be with good reason, and the risk should be understood.

## 1. Economy of Mechanism

***KISS:*** Keep it simple, stupid.

A simple security mechanism is easy to reason about, and check for correctness.
Operational testing, wherein we test the functionality of the system, isn't 
really valid in this context - an adversary will be trying to breach security
with non-trivial program inputs.

### TCB

The *(preferably small)* security mechanism on which the entire system relies to
maintain the security policy is called the ***Trusted Computing Base***, or TCB.

Every component of the security policy will place their trust in the TCB, so it
had better not fail - this would meen a compromised security policy.
By definition, if something goes wrong outside of the TCB,
the security police is not affected - if the TCB is working, the security policy
cannot be violated. 

## 2. Fail-Safe Defaults

If something fails, it should be as secure as if it hadn't. Think of the
automatic door example - on failure it should be closed instead of open. We err
on the side of the security policy.

As an example of this phenomenon, we should always prioritize whitelisting 
over blacklisting - we can never blacklist the infinite set of non-permissions, 
but we can easily whitelist the finite set of permission holders.

## 3. Complete Mediation

The idea here is that all actions should be checked before they are allowed to
happen.

### Reference Monitor

This is the component that mediates actions for compliance with the security
policy. Implementing the ideal reference monitor is exceptionally difficult -
think how slow it gets when every single access it manually checked. What if
the time to check is greater than the time to use - introduces huge overhead.

Distributed systems have resources that are divided across machines and even
different networks - subjects / objects aren't even on the same machine anymore,
so where should the reference monitor even be? 

## 4. Open Design

*"Given enough eyeballs, all bugs are shallow."*

No security mechanism should require keeping its design secret in order to 
operate correctly. Open designs can be revised by experts who find 
vulnerabilities and suggest ways to fix them. You should always assume that the
adversary knows the ins and outs of your security mechanism - the best way to 
enforce this type of thinking is to just keep it open.

## 5. Separation of Privilege

*"No single accident, deception, or breach of trust is sufficnet to compromise
the protected information".*

The idea here is to separate privilege, making it so that no single entity
*(be it user, process, etc...)* is responsible for a critical security task -
this is undesirable. While this helps with security, it does have downsides -
namely increased complexity in implementation of security mechanism and use of
services, and dillution of responsibility which can even **lower** security.

## 6. Least Privilege

*"Every program and every user of the system should operate using the least
set of privileges necessary to complete the job."*

This one relates to damage control in the event of a security breach - we 
minimize high privilege actions and interactions as they can cause the most
potential damage. This principle is very related to the *fail safe defaults*
principle in that it aims to minimize damage in the event of a compromise. The
compromised principle cannot execute unauthorized actions, helping stay in a
safe state.

## 7. Least Common Mechanism

*"Minimize the amount of mechanisms common to more than one user and depended 
on by all users.*"

Remember the *economy of mechanism* principle - it is hard to reason about a
complex security mechanism. This is somewhat related - having loads of 
mechanisms that are common load more than one user creates more potential points
of failure.

## 8. Psychological Acceptability

*"It is essential that the human interface be designed for ease of use, so that
users routinely and automatically apply the protection mechanisms correctly"*

We aim to hide the complexity introduced by security mechanisms, or else human
users won't use them as intended - this can introduce security flaws.

## 9. Work Factor (Bonus)

Compare the cost of circumvention with the resources of an attacker.
This doesn't really apply to computer security since everything is basically
free *(although you could make the argument for somehting like public key
encryption)*.

## 10. Compromise Recording (Bonus)

Reliably record that a compromise has occured. Could keep logs, but they aren't
magic - for example, how do we keep integrity of logs? Moreover, a log doesn't
mean that we can reliably recover from an attack. Logs may contain sensitive
information themselves.

# Discretionary Access Control *(DAC)*

This is act of verifying that every action respects the security policy under
the presumption that is every action respects it, then the system is secure.


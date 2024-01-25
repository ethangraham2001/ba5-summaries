---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS301 Notes/Summary for Final 
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

# Week 03 - Discretionary Access Control *(DAC)*

This is act of verifying that every action respects the security policy under
the presumption that if every action respects it, then the system is secure
within the threat model.

Given a tuple `(principal, object, action)`, an access control mechanism returns
either `authorized` or `unauthorized`.

Both authentication *(seen later on in the course)* and access control are key
mechanisms - thus they must be placed inside the TCB.

## Implementation

Don't do check soup

```C
if ( action == read && (userID == "Alice" || userID == "Bob") )
{
    // do thing...
}
// ...
```

This is prone to errors, is difficult to debug, and is hard to modify down the
line.

What should be done is systematic calls to a reference monitor - all programs
should check this when requiring access control. This violates the least common
mechanism principle, but fulfils the economy of mechanism principle as well
as complete mediation.

## DAC vs. MAC

In DAC, the object permissions are decided by the owner of the object - this
works well since users generally own objects. As object-count grows, so does
complexity. To address this, we usually let users pick between a set of options.

In MAC, the decision is made by a central authority, and is generally a
system-wide policy. Used by organizations mainly. Depending on needs, the focus
can be placed on, for example, confidentiality or integrity.

## Implementing DAC

### Access Control Matrix

Abstract representation of all permitted triplets 
`(subject, object, access right)` in a system. Subject doesn't necessarily have
to be a user - it could also be a process or a service. Objects don't
necessarily have to be a file or folder - could also be a printer, a database
row, system's memory. Access right could be read, write, append, execute.

This gets complex to reason about as the number of principals and objects grows,
hence the introduction of the access control matrix. However, as convenient as
it sounds, it isn't directly implementable - it is usually very sparse, which
makes filling it error prone.

### Access Control List

Instead of storing a global access control matrix, we can store access control
lists alongside the objects. They are difficult to check and modify at runtime,
which make them error prone.

### Role Based Access Control

The insight here is that subjects are similar to each other, thus we can assign
the same rights to them. It is hierarchical.

- Assign permissions to roles
- Assign roles to subjects
- Subjects select an active role - they have the permissions of the active role,
depending on what action they are trying to do *(e.g. the nurse that has both
doctor and nurse roles so that she can see all patient data)*

There are a few problems with RBAC. The ones introduced in class are

1. Role Explosion as we are tempted to create fine-grained roles which ends up
reversing any benefits of RBAC
2. Simple, limited expressiveness. Can be difficult to satisfy the least 
privilege principle
3. Difficult to implement separation of privilege - if we need two doctors to
authorize a producedure, how do we know that they are both distinct?

### Group Based Access Control

Insight here is that some permissions are always needed together.

- Assign permissions to access objects to groups
- Assign subjects to groups
- Subjects have the permissions of ***all*** of their groups

If a user in some group **shouldn't*** have access to some object, a
group they're associated does have access to this object, then we can assign
them a ***negative permission***. This negative permission is always checked
first during access control

## Capabilities

We described before that with an access control list, we can store the 
permissions directly with the object. However, a second option is to store 
permissions with the subject - we call this the subjects capabilities. If a 
subject doesn't have any assigned permissions for a specific file, then they
will store no information about it. This is nice because we can save storage.

The idea is that the subject shows their credentials to any system or subsystem.
This is especially handy for distributed systems as it is difficult to keep
track of permissions across all files.

Moreover, delegating permissions is simpler - we just have to transfer 
permission from one subject to another *(credentials)*. These capabilities do
also have problems though, notably in revoking permissions as revoking a single
permission is $O(num_{users})$. Moreover, given how simple delegation is, how
do we verify the legitimacy of these delegations.

## Ambient Authority

Recurrent problem in access contorl. Refers to the situations in which when
performing an action in a system, we don't specify the subject but only the
action and the object on which it is performed. If the subject is implicit, then
it can lead to a *confused deputy problem*. 

### Example 1 - Ambient Authority

```C
file = open("ur_mums_creditcard.txt", "r");
send_to(malicious_user, file);
```

If the above program `download_ram.exe` is run by a user, it will be run with
their set of permissions.

### Example 2 - Confused Deputy Problem

Consider a pay-per-use compiler, which takes two files as arguments:
`input` and `output`. It compiles the file `input`, writes any errors to 
`output`, and writes a record of the compile process to `bill` for billing
purposes.

Let's assume now that Alice wants to compile without paying. She doesn't have
access rights to `bill`, so she can't do anything about it herself. What she can
do however, is pass `bill` as `output` argument - all compilation errors will
be written to `bill` by **by the compiler** which has write access, corrupting 
it and making it impossible for her to be billed.

### Avoiding Confused Deputies

To address the second example, we could for instance make it so that Alice must
provide access to the `output` file. Alice isn't able to give any capabilities
for `bill` as she does not own the file.

$\rightarrow$ capabilities has no ambient authority.

## Linux / UNIX Acces Control

- Uses User-IDs *(UID)* and Group-IDs *(GID)*
- Each user has their own directory `/home/username/`, and user accounts are
stored in `/etc/passwd`
- Users belong to one or more groups.

each line in `/etc/group/` contains a group with its GID, as well as a list of
all users belonging to the group.

In UNIX, everything is a file, and each user "owns" a set of files. All 
processes run by a user will run with their privileges *(ambient authority)*.

The special `root` user has UID 0. This root is in the TCB.

- `sudo` executes a single action as super user
- `su <UID>` changes active user. If no `UID` is specified, then it switches to
super user. Doing this is dangerous.

### Directories

Directories are marked with the `d` bit at the beginning of `ls -l` output on
UNIX/Linux systems. Read privilege `r` means that we can only list the contents
of the file - for example with `ls` command. `x` privilege means that we can
perform operations on that directory, such as changing into it with `cd`.

### Special Rights

There are `suid` and `sgid` bits that serve to indicate that a file is not run
with the privileges of the launcher, but the privileges of the owner user or
group. This is specifically useful for running programs that require root,
respecting the least privilege principle.

# Week 04 - Mandatory Access Control

In MAC the policy is given - object owners cannot set their own permissions -
only assign the rights dictated by the policy.

## Security Models

A design pattern for a specific security property or set of properties. When
faced with a standard security problem, it's better to use a tried and tested
solution.

The security model isn't all-encompassing however. Many aspects aren't covered
such as who the subject are, what the objects are, and what the implementation
mechanism will be.

### Bell-La Padula Model *(BLP)*

this model assums that the system has subjects $S$ and objects $O$. Access is
described by four attributes

1. **Execute:** cannot observe or modify, but can run it
2. **Read:** can only observe the object
3. **Append** cannot read the object, but can add content to the end of it
4. **Write** can see and object and can modify it - delete, change, add, etc...

### Level Function for Objects *Security Level*

We define a level function to be able to associate objects to a security level.
***Classification*** is a total ordering of labels *(unclassified, classified,
secret, top secret)* whereas ***Categories*** are compartments of objects with
a common topic *(Nuclear, NATO, ...)*

A tuple $( Classification \lbrace Categories \rbrace )$ is called a security
level.

For this security level function, we define a **dominance relationship**.

`(l1, c1)` dominates `(l2, c2)` $\Leftrightarrow$ `l1>=c1` `c2` $\subset$ `c1`.

We can go further by defining the ***dominance lattice***, which represents
as a graph the dominance relationships between security levels on both
aspects: labels and categories.

We note that dominance is a transitive relation.

### Level Function for Subjects *Clearance Level*

BLP sometimes calls this classification.

**Clearance** is defined as the maximum security level that has been assigned
to a subject - how secret are the objects that they can access. 
***Current Security Level:*** besides their overall clearance, subjects can
also act at a lower level.

### BLP System: SS Property

This is called the simple security policy. We can formulate it as: *if 
`(subject, object, r)` is a current access, then `level(subject)` dominates
`level(object)`*

What it is saying fundamentally is that a subject can only access objects whose
classification is dominated by the subject's clearance. This implies that a
subject cannot read anything above their clearance.


### BLP System: *-Property

This "star" property says not to write down. A subject cannot write in clearance
levels lower than their own. Prevents leakages.

The previous property wasn't enough - a malicious high-clearance user could
copy sensitive information to lower levels of clearance, thus exposing it to
anyone with lower clearance that shouldn't be able to access said sensitive
information.

### BLP System: DS Property

This stands for *discretionary property*. Regardless of the subjects clearance
levels, information should only be provided on a need to know basis *(by the
least privilege principle)*. I.e. An Access control matrix is still required.

## BLP: Basic Security Theorem

This basically says that if all state transitions are secure and the initial
state is secure, then all subsequent state will be secure regardless of inputs.
*(kind of like a proof by induction type of thing)*. This allows us to reason
about a security system relatively easily.

In the BLP model, all aforementioned properties should hold. 

### Problem with BLP

Even if the rules are respected, there can still be information leakage from
higher levels to lower levels.

### Covert Channels

A covert channel is any channel that allows information to contrary to the 
security policy.

To mitigate these, we can isolate *(communication with low-level rendered 
impossible)* or add noise to communication.

### Declassification

Common place *(think of military example)*. To enable communication with lower
layers given a no-write-down policy, we can clean an object from a higher level
of sensitive information before passing it down.

In practice, this is pretty difficult.

### Limitations of BLP

BLP is very much confidentiality-oriented, and doesn't really consider integrity
or availabity. Moreover, the three properties still do not guarantee that
confidentiality is achieved.

## Protecting Integrity

This is key for security in general. Remember that a security policy places all
of its trust into the TCB, thus it must remain integral.

## BIBA Model for Integrity

Here we only consider two operations - read and write. There are also two key
properties

1. High-level subjects should never see lower-level information so as to not
corrupt their vision
2. Lower-level subjects should never write to high-levels so that high-integrity
information cannot be polluted

#### Example

The bank director can establish a rule and all employees will read it. However
employees cannot rewrite the rules.

In a computer, a web application open in the browser should not be able to write
to the filesystem.

### BIBA Variant 1: Low Water-Mark for Subjects

Subjects start processes at their highest integrity level.
If we need to access a lower-level object, just downgrade our integrity level.
This is similar to *sandboxing* - executing a process with potentially dirty
information in a safe environment. If we lower integrity level, then we can 
no longer write up and compromise higher-level information until we upgrade
integrity again - hence the comparison with sandboxing.

Problem with this is that you could have a label creep problem wherein all
subjects end up in a lower level and no-one is able to write at a higher level
anymore.

### BIBA Variant 2: Low Water-Mark for Objects

Once an object has been written to by a subject, it assumes the lowest level
of the subject or object. If a subject pollutes an object with information by
writing to it, the object is automatically downgraded to the level of the 
subject to avoid problems.

This policy only allows for integrity violation detection - the file cannot
harm a higher-level, but tampering may have happened. A solution to prevent
tampering is to replicate objects - after the operation has happened we can
sanitize or upgrade the replica

### Biba Axioms And Integrity Hierarchy

We define a hierarchy of integrity levels

- High Integrity: critical and sensitive information
- Medium Integrity: Less sensitive, but still important for proper functioning
of the system
- Low Integrity: Least trusted level. Contains information that is considered
public

There are two main axioms that are followed.

***Simple Integrity Axiom:*** A subject with a given integrity level should not
write to any object at a lower level than its own.

***Star Integrity Axiom:*** A subject with a given integrity level should not 
write to data at a higher level than its own.

## Sanitization

The process of taking moving a low integrity object to high integrity.

This is the cause of many real-world security vulnerabilities. Think SQL 
injection / XSS.

The fundamental principle of sanitization is the *fail-safe default* principle.
We check that all desired properties hold, instead of blacklisting 
undesired properties. If not all of the properties hold, we don't accept the
input.

## Principles to Support Integrity

- Separation of Duties: require multiple principals to perform an operation
- Rotation of Duties: Allow a principlal only a limited time on any particular
role and limit other actions while within this role
- Secure Logging: taper evident log to recover from integrity failures. Should
be consistent across multiple entities.

## Chinese Wall Model

1. All objects associated with a label denoting their origin
2. The originators define "conflict sets" of labels
3. Subjects are associated with a history of their access to objects, and in
particular, their labels.

The idea is to avoid subjects from transfering data from multiple objects in a
conflict set $\rightarrow$ conflict of interest.

This is part of the BIBA model.

# Week 05 - Cryptography I

When data has to be transfered between two systems that don't share a CPU,
there is no TCB to enforce access control. Cryptography can be used to ensure
the confidentiality and integrity of data in transit. It can also be used to
build authentication methods, protect from denial of service, or support 
anonymous communications.

## Cryptographic Primitives

This means the *"minimal algorithm"*, i.e. cannot be reduced further without
functioning/being able to build a security argument, that implements some 
cryptographic function. It is a building block for building more complex
cryptographic functions.

## Cryptographic Algorithms for Confidentiality from a High Level

The idea is to generate some key `k`, making sure that the receiver has it. We
then encrypt the plaintext, sending them `enc(k, m)`. They can then descrypt
using `dec(k, m)`.

Old school algorithms had a problem - frequency analysis. If we use a simple
Caeser cipher or just permute the alphabet, an adversary can just analyse the
frequencies and reconstruct the message effortlessly. 

The ideal encryption method is the
***one-time-pad***, which provides perfect secrecy *(provided the key is
distributed randomly and itself isn't subject to frequency analysis)*. Downside
is that the receiver needs to know the key before-hand, and the key needs to be
as long as the message. Moreover, the key is never to be reused. Moreover, this
method ***only ensured confidentiality - it doesn't ensure integrity***.

## Modern Cryptography Methods

### Stream Ciphers

A stream cipher received two inputs: 

1. A small key `k` s.t. $|key| << |message|$
2. An initialization vector `IV` *(doesn't need to be secret)*.

The keystream generator outputs a stream of bits that is pseudorandom, denote
this `stream(k, IV)`. This stream seems entirely random for an adversary that
doesn't have the key.

`IV` is a fixed-size input for cryptographic primitives, and shouldn't be used
more than once for the same `k`. The idea is to make message encrypted with the
same key look completely different. Although `IV` doesn't need to be secret,
it should be unpredictable when used in some block ciphers.

To implement this

```python
# Alice...
def send_encoded(m: str):
    enc = stream(k, IV) xor m
    send(IV, enc)

# Bob...
def decode(m: str):
    dec = stream(k, IV) xor m
    return dec
```

Note that given `k` and `IV` both are able to construct an identical stream. The
issue with this method is that `k` must be known to both parties in advance.
Furthermore, since the encryption is done bit-by-bit, it's difficult to detect
tampering, thus this method is susceptible to bit-flipping attacks *(doesn't
protect message integrity very well)*.

As with everything, don't try and design an implementation of this from scratch,
use some tried and tested implementation instead.

### Block Ciphers

A block cipher operates on small blocks, taking a key `k` and message `m` and
outputting a block that is the same size as the input. The algorithm is such 
that the output block looks entirely random - input is independent of output.

The decryption algorithm is *(in general)* not the same as the encryption
algorithm.

The algorithm always works on blocks that are the same size as `k`, so typically
128 or 256 bytes. However, messages are longer than keys in general, therefore
we define ***chaining*** which is called a mode of operation.

#### Mode of Operation 1: Electronic Code Book

This mode is straightforward to implement, but a terrible idea. We partition
`m` into `m_1`, ..., `m_n`, and then encrypt them separately with the same key
`k`. If two blocks appear the same, however, this implies that they have the
same plaintext content. This shouldn't be used.

#### Mode of Operation 2: Cipher Block Chaining

In this mode, every block depends on previous blocks to be decrypted. We have
a recurrence relation for encoding

- $C_0 = IV$
- $C_i = ENC(k; m_i \oplus C_{i-1})$

Since `IV`/`m` change every time, the text will always appear random. Decryption
involves doing the inverse operation.

- $C_0 = IV$
- $m_i = DEC(k; C_i) \oplus C_{i-1}$

However, we notice right away that if `IV` is incorrect, than nothing can be
recovered. This is very susceptible to tampering.

Moreover, if we don't change `IV` between successive messages, then the first
block will $C_0$ will be the same in those blocks. Thus if encrypting the same
message twice will have the same output *(remember, `k` is fixed!)*. This is a
common vulnerability.

#### Mode of Operation 3: Counter Mode

The insight is to use an increasing nonce to add randomness without introducing
dependencies between blocks like in CBC mode.

We use a unique number composed by a **nonce** and a **counter** so that the 
encryption receives a new number every time. When encrypted, this number becomes 
a random one-time-pad that we XOR with the plaintext to obtain the cipher text.

$$
C_i = Enc(k; Nonce+i) \oplus m_i \text{, where i is the counter }
$$

The counter is increasing, changing the nonce every iteration - thus the output
of will be different for every block. A nonce should only be used once, 
otherwise we are feeding the encryption with the same number and we obtain the
same random pad at the output - effectively like reusing a one time pad.

To decrypt, we need the same random sequence of bits *(as it operates like a 
one-time-pad)*, so we just use the same algorithm as encryption.

Note *(from live exercises)* we can actually reuse the same nonce under 
different keys, as it will produce a different OTP. However, important to never
use the same nonce for the same key.

#### Summary on Block Ciphers

**Strengths:**

- Great diffusion: every bit of input affects several blocks of output
- Chaining helps detect insertion of modification as modifications propagate,
and receiped ciphertext won't make sense upon decryption.

**Weaknesses:** 

- Block ciphers are slow compared to stream ciphers because they
need to wait for a full block before encryption/decryption.
- Error propagation

## Integrity from Symmetric Encryption: Message Authentication Codes *(MAC)*

A message authentication code received two inputs

1. A small key `k` that is kept secret
2. A message `m` whose integrity needs to be kept

The MAC algorithm outputs a short string that helps the intended receiver to
verify integrity of the received message - this works because it is 
exceptionally difficult to produce a pair `(message, MAC(k, message))` without
knowing `k`.

When Alice sends a message to Bob, and Bob verifies the message using the MAC
algorithm, he knows that the message has not been tampered with as `k` is needed
to generate the message authentication code.

### Example: CBC-MAC

A block cipher in CBC mode can be turned into a MAC.

- $C_0 = 0$ *(or any fixed IV)*
- $C_i = ENC(k; m_i \oplus C_{i-1})$
- $MAC(k; m_1 \dots m_x) = C_n$

This is deterministic.

## Confidentiality and Integrity

- **Encrypt and append MAC:** MAC is deterministic and computed on the 
plaintext,  may reveal information about the message. Moreover, we don't have 
any mechanism for verifying the integrity of cipher-text before deciphering 
message.

- **MAC then Encrypt:** Still no integrity check on the ciphertext unforunately.
No information is revealed about the MAC since the adversary doesn't see it.

- **Encrypt then MAC:** Ensures integrity of ciphertext and plaintext. No
information is revealed about plaintext since the MAC is also encrypted.

# Week 06: Cryptography II

We talk about asymmetric cryptography in this lecture. Already covered RSA to 
death in other lectures so I'll keep it brief and will ommit some definitions.

## Hash Function Properties

1. **Pre-image resistence:** Given $H(m)$, difficult to find $m$. 
Non-invertible
2. **Second pre-image resistence:** Given $m$ and $H(m)$ it is hard to find 
another $m'$ such that $H(m) = H(m')$.
3. **Collision resistance:** It is hard to find two messages $m$, $m'$
such that $m \neq m'$ with the same hash $H(m) = H(m')$.

It is very difficult to design a hash function that fulfils these properties -
as well as being efficient to compute.

## Asymmetric Key Encryption

### Confidentiality

Message can only be decrypted with secret key.

### Integrity

Sign messages so that they can be verified by the receiver. We can sign a 
message by sending, alongside the message, the message encrypted using ones
own secret key. When the receiver gets the message, they decrypt the message
using sender's public key. This proves integrity of the message, as well as
being able to know where the message came from.

#### Example From Live Exercises

One could think that a solid way to prove integrity if to add a hash of the 
message, and then encrypt this along with the message. But this doesn't prove
provenance of the message *(an adversary could pose as Alice and send something
to Bob)*. 

However, signing the message with Alice's secret key, and having Bob decrypt
the signature using Alice's public key can prove this, as Alice's secret key is 
known only to Alice, and Bob has access to Alice's public key through the 
public key infrastructure. This proves integrity of the message, as no one
else could have produced the signature.

### Digital Signatures

We want to ensure **integrity** of message, **authenticity** of sender, and 
**non-repudiation** - since no party other than the sender can create a valid
signature for a message, if a message hasa valid signature, the sender cannot
claim they did not sign it *(no-one else can produce such a signature)*.

Digital signatures are used in the internet public key infrastructure to sign
certificates which authenticate web servers / domain names.

#### Public Key Infrastructure: Certifiates

1. Authority signs a mapping between names, or names and encryption public keys.
2. Authority signs a mapping between names and verification keys.

## Limitations of Asymmetric Cryptography

Asymmetric cryptography is computationally pretty costly, much more so than
symmetric counterparts of equivalent security. There aren't any good cipher
modes for ecrypting large messages - we can only do one block.

To overcome these shortcomings, we use hybrid encryption.

## Digital Signatures on Hash Functions

The insight is that if we sign long messages, both signing and verifying will
take a long time and won't be practical. We choose to sign using the hash

```python
# Alice; m is the cipher text
def send_message(m: str):
    h = hash_func(m)
    signature = sign(secret_key, h)
    send(m, signature)

# Bob, upon receiving message.
def verify_message(m: str, signature: str):
    h = hash_func(m)

    if lines_up(public_key_sender, h, signature):
        return True
    else 
        return False
```

For this process, we need second pre-image resistance and collision resistance.
We don't need pre-image resistance as the message m is already sent in public.

## Hybrid Encryption

Use asymmetric key encryption to send a symmetric key. We then use this
symmetric key for the rest of communication. Every time Alice wants to 
communicate with Bob, she creates a new key. However the problem here is that
if an adversary gets hold of Bob's key, then the secrecy of all past sessions
is compromised as well. This brings us to a new desired property: **foward
secrecy** - the secrecy of a session is maintained even if long term keys are
compromised. A compromise at time $t$ should not compromise and communication
at $t', \, t' < t$. RSA basically makes it impossible to compute secrete keys
given the complexity of prime factorisation for large primes.

# Week 07 - Authentication

This is the process that entities use to verify the identity of other entities
that they are interacting with. This happens before access control - to be able 
to grant access privileges to an entity we need to first know who they are.

## Passwords

There are things to be considered when using passwords

1. We require secure transfer between client and host
2. When trying an erroneous password, no information should be given about the
real password
3. Storage should be secret
4. Secrecy depends on how easy it is to predict.

### Secure Transfer

Use some form of encryption as seen in previous lectures. This guarantees that 
it cannot be eavesdropped by third parties. This doesn't entirely solve the 
issue because of potential replay attacks.

Example: a malicious third part saves the ***encrypted message*** containing 
login information, and then reuses the encrypted message at a later point to
login into the account.

#### Challenge Response Protocols

1. Client that wants to authenticate sends their intention to login.
2. Host sends a challenge, which is a random number from a large space to avoid
easy prediction.
3. Princpal encrypts the password together with the challenge. Ensures that the
password is correct and that the password is never encrypted to the same value.

The host then deletes the challenge so that the message cannot be replied.

### Secure Storage

This is to protect against password breaches if security is compromised.

#### Password Hashing

This is great, but there are some caviats

- Anyone can compute a hash relatively inexpensively
- Passwords are never truly random - they only fill up a fraction of the total
sample space.

#### Password Hashing with Salts

We store passwords as a hash plus a salt. We add the salt to the end of the 
password, and then hash it - storing the salt with it so that we can compare
password attempts with the correct salt during authentication. 

This prevents people from using precomputed rainbow tables since different salts
are added to passwords. Insight: a password will hash differently with different
salts added.

However this doesn't mean that a dictionary attack is impossible *(dictionary
attack refers to using a list of possible hashed passwords and using them on
an exposed database)*. Breaking a single password is still possible - it's just
excessively hard to get all passwords from a database. Requiring specific 
elements in passwords, thus increasing entropy, is still required. And, of 
course, access control to the database is key.

### Secure Checking

Checking letter by letter, for example, reveals information on the password.
If password is instantly rejected, then the first letter is probably wrong. If 
it only rejects after a while, then the chances are we have the first few 
password symbols correct. In general, this is called a ***timing attack***, 
where an attacker exploits how long the system takes to perform a certain 
action.

We should always check everything, and take the same time regardless on whether 
or not it fails. There are many libraries that handle all of this stuff.

### Difficule to Predict

Long and hard to remember passwords are often recycled - this isn't great.

## Ways to Prove Who You Are

There are both traditional and non-traditional ways to prove one's identity.

## Biometrics *(What you are)*

There are problems with biometrics. Firstly, they are hard to keep secret - 
e.g. a signature on a card or a fingerprint left on a door handle. It is 
difficult, even impossible maybe, to revoque biometrics - you can't create a new
fingerprint for yourself. They are also identifiable and unique, and thus linked
across systems.

## Tokens *(What You Have)*

We can authenticate by proving ownership of a token.

- Token-based authentication uses symmetric-key cryptography. No public keys
are used. They share a secret key, which is required to be able to compute
the same value.
- The token requires a shared secret that is input to a keyed cryptographic
function. Hashes don't work - otherwise anyone could compute new token values
- Tokens aren't deleted after use, otherwise no futher verification values can
be computed.

### Implementation

- Synchronize time between client and server
- Share a seed between client and server
- Compute a token by performing some cryptographic function $n$ times on the
shared seed, where $n$ is the number of time intervals since synchronization.
$v = f^n(seed; k)$.
- The server compares the value sent by the client with the value that it
computed.

Since the $f$ function is keyed with some shared secret $k$, it is impossible
for an adversary to predict past, current, or future values. This wouldn't be
the case if we'd used some hash function, as anyone can compute a hash.

## 2FA *(What You Have, What You Know, What You Are)*

Combines multiple elements. We cannot keep, for example, secret keys on 
smartphones as they aren't secure enough - this is why SMS codes and QR codes
are used during 2FA.

## Authenticating Machines

This is done using public key cryptography to produce **digital signatures.**
This is used in internet protocols such as `https` and `tls`. This is very
difficult to implement in practice.

# Week 08 - Adversarial Thinking I

Having a good understanding of attackers helps make us a better defender. For
example, pentesting is a pretty major industry. However, we must keep in mind
that the lack of found attacks doesn't guaranetee security. This relates to
the failsafe principle.

## The Security Engineering Process

Attacks are typically developed systematically - it enables adversaries to
explore many angles where a potential vulnerability could lie.

We can define a process for securiyt engineering

1. Define a security policy and a thread model $\rightarrow$ **What to protect
from**
2. Define security mechanisms that support the policy given the thread model
$\rightarrow$ **How to protect it**
3. Build an implementation that supports/embodies the mechanism $\rightarrow$
implement the protection

Many things can go wrong here

- Forgetting the principal, assets of properties
- Underestimation of the advsersary
- etc...

## The Attack Engineering Process

The goal here is to exploit weaknesses introduced during the security
engineering process. 

## Exploiting Security Policy Flaws

### Exploiting Misidentified Assets in the Security Policy

We illustrate this with an example. An HSM is a CPU that is secured physically.
That is, it can hold cryptographic keys that cannot be extracted by observing
the device, or measuring the device characteristics *(be it power consumption,
computation timing, etc...)*. Their security partly comes from them having a
strict API for interaction with them - following economy of mechanism, HSMs
can only be accessed with very few commands. One function is
`extract_from_key` which on `offset` and `key_length` generates a key using
the secret key kept internally.

Since the key to this `extract_from_key` operation only has $2^8 = 256$ bits,
it can be searched exhaustively to extract the key.

### Expoiting Unforeseen Access Capabilities

We could, for instance, consider during design that physical access will be
required to exploit vulnerabilities. However, in upgrading the aforementioned
design, we may add network capabilities without thinking to revise the security
policy. How the device is vulnerable to network attacks.

IoT devices are weakly protected, and can easily be manipulated.

### Exploiting Unforeseen Capabilities

Take as example the GSM network. When it was created, it was assumed that it
wouldn't be feasible to create an antenna in terms of cost and know-how. Thus,
when running the protocol to connect phones to the network, antennae don't 
authenticate.

However, these days, iwe have software defined radio boards that can be easily
programmed to impersonate an antenna - tricking other devices into thinking that
it is the base station and connecting to it.

### Exploiting Unforeseen Computational Capabilities

One of the examples is brute forcing RSA long keys. One reason why the internet
is changing to longer RSA keys.

## Exploiting Mechanism Design Weaknesses

Security by obscurity is generally a bad idea. We can cite examples such as 
Tesla key fobbing algorithms as well as weak cryptography schemes. It may be
easier than you think to reverse engineer secret algorithms. $\rightarrow$ open
design principal.

## Exploiting Bad Implementation

An example that we can list is the implementation WEP using RC4, which is a 
stream cipher using a small IV. The fact that the IV is small means that when
there is enough traffic, the IV gets repeated - if we repeat the IV with a
given key, a stream cipher will produce the same pseudorandom string multiple
times, which then is intended to serve as a one-time-pad. Given the stream
reuse, an adversary can recover information about the message and because of the
internals of RC4 even recover the symmetric key and decrypt all communication.

Besides bad parametrization of algorithms, programming mistakes can also be the
cause of security vulnerabilities.

- Forgetting checks
- Checking the wrong things
- Poor sanitization
- Confusion


## Threat Modelling Methodologies

This helps a security engineer reason about threats to a system through a 
*"what could go wrong?"* approach. We prioritize problems during implementation
of security mechanisms through systematic analysis

- What are the most relevant threats?
- What kind of problems can threats result in?
- Where should I put my effort?

There are a few structures that help with this

### Attack Trees

The attack goal is the root, and the ways to achieve this goal are represented
by branches. The leaves represent the weak resources

### STRIDE

This was introduced by microsoft. We model the target system with entities,
assets, and flows. This allows us to reason about

- **Spoofing** which threatens authenticity.
- **Tampering** which threatens integrity
- **Repudiation** which threatens non-repudiability. Repudiation is to falsely 
deny having done something in the system
- **Information disclosure** which threatens confidentiality
- **Denial of service** which threatens availability
- **Elevation of privilege** which threatens authorization. This is when an
adversary obtains more permissions than what should be allowed.

This helps us consider different dangers and harms in a systematic way.

# Week 09 - Advsersarial Thinking II 

## Common Weaknesses Enumeration *(CWE)*

The idea is to have a database of software errors that lead to vulnerabilities
to help security engineers avoid common pitfalls. The idea is to not repeat
known errors.

### CWE I Secure Interaction Between Components

This is when a programmer doesn't check the information that is sent between
different components in a system - this is unsanitized information and it can
result in unintended behaviors, allowing the adversary to break security.

An example of this is OS command injection. Similarly, we can think of **XSS**, 
wherein a user inputs javascript code which will be run.

All of this can be avoided with proper input sanitization. Remember BIBA - 
never bring low-integrity *(unknown)* information to high-integrity territory 
*(OS)*. Proper input sanitization is very difficult.

We can also list the example of **CSRF** which is short for cross-site request
forgery, where an attacker performs actions while impersonating someone else.
E.g. we make a fake website that sends forged requests to the real website using
the victim's credentials. This is an example of the confused deputy problem, and
taking advantage of ambient authority - when the victim is logged in, the web
client acts with there privileges.

#### Same Origin Policy **SOP**

This is a web-browser security mechanism. Restricts scripts of one origin from
accessing data from another origin.

Assume an origin `https://example.com/a`
- **Yes, origin match:** `https://example.com/b`
- **No, protocol mismatch:** `http:/example.com`
- **No, host mismatch:** `https://www.example.com/a`
- **No, port mismatch:** `https://www.example.com:5000/a`

#### Cookies

This is a small piece of data stored by a browser on a user's device which 
serves many purposes from storing stateful information to tracking users. 
Cookies don't follow the SOP *(it is a different security model)*.

A new `HTTP` request to `bank.com` will include all cookies for `bank.com`, 
even if the request originated from another domain.

What this implies for CSRF is that when a victim visits a malicious site, all
cookies for the legit site will be included. This means that the attacker can
reuse these credentials *(such as session cookie)* to send forged traffic to the
legit site. 

To mitigate CSRF, we generally employ the SOP - don't accept a 
cookie that doesn't come from where it is supposed to. A second mitigation is
avoiding requests that change server state *(e.g. requests can't change 
database values)*. To avoid replay attacks, we can include challenges when 
serving requests so that adversaries cannot replay cookies. A definitive 
solution would be to eliminate cookies and ask users to authenticate for every 
action, but this introduces usability problems.

Because HTTP is stateless, developpers need to create their own sessions for
everything - there is no standard for establishing/structuring sessions; errors
are common.

## CWE II Risky Resource Management

This is when programmers don't check the resources they create and manage. This
is again related to unsanitized information used by the program, which results 
in unintended behaviors, allowing attackers to break security.

There are a whole family of buffer overflow bugs, insufficient sanitization bugs
and *"TCB under the control of advserary"* bugs.

In particular, executing full pieces of code without checks *(for example in
updates)* can make it so that tampered software is included into critical
parts of the system.

## CWE III Porous Defenses

This is when complete mediation principle isn't respected by programmers - for
example when security functionalities are only partialy covered.

Common errors include poor implementation of security mechanisms, or errors in
authentication procedures *(e.g. badly assigned permissions, improper use of
encryption, etc...)*.

# Week 10 - Software Security

## Memory Corruption Through Buffer Overflow

If input sanitized *(in particular, checked for length)*, then overflows can
occur, overwriting other locations in memory.

```C
void
vulnerable(int user_1, int value, int *array)
{
    // no bound check is done. This could overwrite another location in the
    // program!
    array[user_1] = value;
}
```

## Memory Safety: Temporal Error

Temporal safety means that when we acccess the object that is pointed to, it
should 

1. Point to a valid object
2. Point to the same object as when the pointer was created

```C
void
vulnerable(char *buf)
{
    free(buf);
    printf("%c", buf[12]); // memory is no longer associated to buf!!
}
```

## Memory Safety: Spatial Error

Spatial safety is a property that ensures that all memory accesses in a program
are within memory bounds. 

```C
void
vulnerable()
{
    char buf[12];
    char *ptr = buf[11];
    char *ptr++ = 10; // dereferences and then adds 1 -> ptr = buf[12]
    *ptr = 42;        // we aren't allowed to make this access. Out of bounds
}
```

In many cases, memory safety errors cause seg-faults which halts program.

This can be exploited, for example, in the following.

```C
void
vulnerable()
{
    int authenticated = 0;
    char buf[80];

    gets(buf); // overflows if input is larger than 80 bytes.
    // ...
}
```

## Uncontrolled Format String

Imagine we have the following

```C
#include <stdio.h>

int
main(int argc, char **argv)
{
    char buf[100];
    strncpy(buf, argv[1]);
    printf(buffer);
    return 0;
}
```

What happens here if `argv[1] = "You scored %d\n"`? Well basically it will go
and look for 4 bytes from the stack *(integer)*. If input was `4%$p` we could
be able to read the fourth parameter from the stack.

The programmer should decide to format the string instead of leaving it up
to the runtime. The programmer should define parameters, and not let the user
input them.

## Attack: Code Injection

The goal is to execute code *(e.g access a file)* in a running process, or
modify contorl flow to execute unexpected instructions.

Control flow attacks are most common on current systems. In these attacks, 
the adversary can use memory corruption to modify a code pointer and prepare
data to be processed by system functions.

### Code Injection Attack

Consider 

```C
void 
vulnerable(char *u1)
{
    char tmp[MAX];
    strcpy(tmp, u1);
    // ...
}

// somewhere else in program
vulerable(&exploit);
```

When a function is called, program prepares the stack - reserving a new stack
frame where the data of the function will be stored. Firstly, the function 
argumnet `exploit` will be pushed to stack, followed by the return address for
the program. Before starting the function, we also reserve space in the stack
for local variables - in this case `MAX` bytes for `tmp[MAX]`. There is also 
saved space for the base pointer *(4 bytes or 8 bytes depending on OS)*.

During runtime, the call to `strcpy` will started copying the content of `u1`
into `tmp` - let's assume that its some *(malicious)* executable code. ***We
never check the size of `u1`***. This means that it can overflow out of the
`tmp` buffer, and into the other stack memory. At this point, this is a memory
safety violation *(a spatial one)*. 

- We could write into the stack base pointer
- We could write into the return address

At this point, if we wrote some shellcode into `tmp[]`, and we got the return
address to point to `&tmp`, then when the function returns it will execute the
malicious code that we have injected. We have violated the integrity of the
return pointer.

### Security Measure: Data Execution Prevention *(DEP)*

This is enforced at the hardware level, more specifically at page granularity,
by setting an write/executable bit to say if the page is writeable or 
executable - we also refer to this method as `W^X`, write xor execute, for this
reason.

This the prevents self-modifying code. This does, however, also
impede on many functionalities in applications offered as a service where the 
user executes server-provided code *(for example javascript being executed
on browser)*.

### Attack Scenario: Code Reuse - Control Flow Highjack

This is a way of circumventing DEP. The idea is instead of injecting code, we 
find code that is already present in memory *(and therefore executable)* and 
rediract the program control flow to those pieces. These pieces of code are 
typically known as gadgets. 

```C
void 
vulnerable(char *u1)
{
    char tmp[MAX];
    strcpy(tmp, u1);
    // ...
}

vulnerable(&exploit);
```
Again, the stack will fill up as described before, with `tmp[]` sitting on top.

Instead of now filling up `tmp[]` with exploitable code, we can just overflow
and get the return address to point to some function `&system()`. For this to
actually cause harm, though, the adversary overflows out of `tmp[]` even 
further, preparing the stack to be in the state that is expected by `system()`,
i.e. providing a base pointer, a return address for after the call, and function
arguments for the call to `system()`.

When `vulnerable` returns/exits, control flow will have been redirected to
`system()`. We can chain these together to execute arbitrary chains of 
instructions.

### Security Measure: Address Space Layout Randomization

The goal is to prevent an attack from reaching a certain target address - which
stems from adversaries knowing where system functions lie in memory. A defense
against these types of attacks is randomizing memory layout so that the attacker
can't know where to redirect the function.

This defense does have its own set of issues however

- The adversary can still redirect the program; not necessarily guaranteeing
success of the attack, but something bad could still happen for example 
triggering other unintended functionality and reading from memory.
- In runtime, the OS needs to undo the randomization of the program, thus
slowing down execution.
- Not all regions can be randomized due to the way in which CPU and memory are
constructed *(some regions are always the same, and ASLR cannot defend them)*.

### Security Measure: Stack Canaries

This is named after coal mine canaries. When they died, it would indicate that
the air was unsafe to breathe.

The idea is to protect the return instruction pointer on the stack by inserting
a random value between the writable area in the stack and the return address.
Since it is randomly generated, it is highly unlikely that the attacker has any
chance of predicting it and writing the same value and then return address.

So this indeed protects against writes from an attacker, but this does not 
protect against reads *(such as ones leveraging string formatting as discussed
previously in this chapter)*.

## Security Testing

Testing for security is difficult. We can never ensure that we have found all
bugs that matter.

***"Testing can only show the presence of bugs, never their absence."***

Ideally we would like to test all possible control paths through the program,
as well as all data flows. This is impossible - in fact the halting problem
is literally undecidable.

```C
void
program()
{
    int a = read();
    int x[100] = read();

    if (a >= 0 && a <= 100) {
        x[a] = 42;
    }
    // ...
}
```

Here, all control-flows are explored since they are discretized completely.
However, not all data-flows are considered since we don't know what `read()`
will return - not all possible variable values are explored.

### How to Test Security Properties

#### Manual Testing

- Exhaustive: Cover all inputs *(not feasible)*
- Functional: Cover all requirements *(depends on specification)*
- Random: automate test generation
- Structural: Cover all code *(works for small code bases, e.g. unit testing)*

#### Automated Testing

- **Static Analysis:** Analyze program without executing. Imprecise, however, 
due to lack of runtime information. Only finds basic errors, and can't catch 
race conditions that happen when address is pointed to by more than one variable.
- **Symbolic Analysis:** Execute the program symbolically and keep track of 
branch conditions. This is very formulaic, and super effective as it considers 
all possible paths. Doesn't scale well at all because it requires a huge amount 
of state.
- **Dynamic Analysis:** Execute the code with diverse inputs. The main challenge
is covering all paths *(control and data flows)*.

### Coverage

Measure how complete a set of tests if by quantifying how many statements of the
program are executed by the tests. We talk about **statement coverage** *(how 
many statements e.g. assignment, comparison, etc...)* have been executed and
**branch coverage** *(how many branches among all possible paths have been 
executed)*.

Neither of these two types of coverages are complete, unfortunately. We may
have tested all branches without testing all values within those branches and
vice-versa.

### Fuzzing

A random testing technique that mutates input to improve test coverage.

1. **Dumb Fuzzing:** unaware of input structure, randomly mutates input
2. **Generation-based Fuzzing:** has a model which described input; input
generation produces new input seeds at each round
3. **Mutation-based Fuzzing:** leverages a set of valid seed inputs; input
generation modified inputs based on feedback from previous rounds.

We can either choose to give the fuzzer no knowledge of the code, partial 
knowledge of the code, or full knowledge. We refer to these as black box, grey
box, and white box.

## Sanitization

We can use sanitization to detect bugs earlier, and increase bug
detection chances. A famous example is **AddressSanitizer** which detects
memory errors, marking red-zones i.e. zones that the program should not catch.
Doubles execution time.

- out of bounds accesses to heap
- use-after-free
- use-after-return
- use-after-scope
- double-free
- memory leaks

Another famous example is **UndefinedBehaviorSanitizer** which detects various
forms of undefined behavior. It instruments code to trap undefined behavior in
C/C++ programs.

- unsigned / misaligned pointers
- signed integer overflow
- illegal use of `NULL` pointers
- illegal pointer arithmetic

# Week 11 - Network Security I

Up until now we have covered attacks on the host, but we haven't covered attacks
on the network yet. Networks are non-linear and complex infrastructures - 
communication can pass through a number of different devices between Alice and
Bob. Including LAN and WAN.

## Desired Network Properties

1. **Naming Security:** Association between lower level names *(e.g. network
addresses)* and higher level names *(human readable)* mustn't be influencable
by adversaries. $\rightarrow$ Integrity, Authentication, Availability of naming
service
2. **Routing Security:** The route over the networks and the eventual delivery
of messages must not be influenced by the adversary $\rightarrow$ Integrity,
Authentication, Availability, Authorization
3. **Session Security:** Messages within the same session cannot be modified
*(ordering is maintained, and no messages are added/removed)*. $\rightarrow$
Integrity, Authentication
4. **Content Security:** The content of the messages must not be readable or
influenced by adversaries. $\rightarrow$ Confidentiality, Integrity

## Where Are the Problems?

Computers communicate at different layers, which are typically modeled by the
OSI *(Open System Interconnection)* model which covers from as low as the 
physical layer all the way up to the application layer.

## IP Routing and ARP

When Alice sends a message to Bob who resides on a different IP subnet, she 
doesn't in general know his MAC *(medium access code)* address. This is where
**ARP** *(address resolution protocol)* comes in - it enables machines to find
mappings between IPs and MACs. Each host maintains a `(IP, MAC)` mapping that
they cache - when they can't find a mapping, they broadcast an ARP request to
query for the target IP, which is replied by the host corresponding to that IP.

ARP doens't provide naming security - ARP responses don't include signatures
or authentication codes. This means that the receiver can't check for integrity
of the packet or authenticity of the sender - we can't confirm that there is
no adversary impersonating the sender.

### ARP Spoofing

This involves impersonating another machine. Several attacks can be achieved
through this

- Man in the middle attacks
- Abuse of resource allocation
- Denial of service *(deny packets arriving to intended host)*

The same attacks can happen in DNS, IP, Ethernet, etc... Since network protocols
weren't initially designed with security in mind. This is a very naïve threat
model which supposes that outsiders are bad and that insiders are always
trustworthy.

#### Defenses

The problem with defending against ARP spoofing is rooted in the fact that there
is no authentication of who is providing the `(IP, MAC)` mapping. We can 
address this in a couple of ways. One way is to use static and read-only
entries for critical services in the ARP cache of a host. The other is to use
some form of ARP spoofing detection/prevention software. These programs can 
work in several ways

- Check if one IP has more than one MAC or one MAC reported by multiple IPs
- Certify requests by cross-checking
- Send out an email if an IP-MAC association changes

The two latter methods effectively implement the separation of privilege
principle by requiring that adversary compromise more than one entity for a
security breach.

## DNS *(Domain Name System)*

This allows a user to resolve a domain name with a corresponding IP address.

### DNS Spoofing

There are a couple of ways to go about doing this in practice. One is **cache
poisoning** which involves polluting the resolver's cache with fake 
`(IP, Domain)`, expoiting the fasct that resolver's don't authenticate the
origin of a request before including an association and allowing fake 
associations to be introduced in the goal of misdirecting victims.

Another method is **DNS Hijacking** which exploits the fact that traffic from
DNS resolvers don't have any authenticity or integrity protections. We can play
man in the middle and impersonate the DNS server and misdirect victims, deny
service to them, or monitor them.

#### Defenses

We have a few solutions in place to address these security vulnerabilities.

- Domain Name System Security Extensions *(DNSSEC)* which extend DNS by 
providing origin authentication *(through digital signatures on DNS responses
sent by authroritative name server, prevents poisoning)*. THis doesn't provide
confidentiality however as the traffic isn't encrypted.
- DNS-over-HTTPS *(DOH)* which has been use since 2019 and provides integrity
and confidentiality by encrypting DNS traffic.
- Others, including DNS-over-TLS, DNSCrypt, DNSCurve

## BGP *(Border Gateway Protocol)*

This protocol constructs routing tables between autonomous systems.

- Routers maintain tables of `(IP subnet -> router IP, cost)` tables.
- Routes change, therefore BGP updates constantly.
- Cost is crucial: BGP chooses the routes with the lowest cost.

There is a so called *weak authentication* mechanism between routers which is
aimed at preventing denial of service. It is built with a short and shared
secret key *(about 80 bytes)* and ad-hoc message authentication codes based on
MD5 which is a weak algorithm.

This does not guarantee integrity of the advertised routes - **BGP Hijacking**,
where an adversary controls or compromises a router somewhere on the internet,
allows them to inject low-cost routes to redirect portions of traffic to 
themselves and which eventually propagates to routing tables. Note that this
attack doesn't itself enable the adversary to redict traffic to themselves - 
they modify the route not the destination. However, this does open the 
possibility of performing on-path attacks and modifying packets.

#### Defenses

A possible defense would be to, just like in ARP, try to identify incosistencies
in routes. For example, a packet travelling from Switzerland to Italy probably
has no business passing through the USA, although is by no means a technical
definition as routes also depend on economical factors.

There is a standard BGPSec which works similarly to DNSSec and aims at 
mitigating hijacking by ensuring that routes are signed by authoritative
autonomous systems, i.e. those hosting the IPs.

## Lesson to be Learned From Spoofing

1. The network is hostile, and we should assume that insiders aren't trustworthy
2. The solution is tied to cryptography as there is no centralized authority
in place to act as a policy originator or to provide a TCB
3. Asking who has authority

## IP Security

IP *(internet protocol)* enables addressing and routing of packets between hosts
in a network. IP packets do not include any protection to preserve the integrity
of the source and destination address - all they have is a non-cryptographic
checksum. Adversaries can tamper with the IPs *(IP spoofing)* and learn the
destination of packets *(privacy invasion)*.

### IP Spoofing

Being able to spoof IPs opens up the possibility for the following attack types

- Impersonation
- Man in the middle, which can involve changing packets or denying service
*(to do this we may also need to hijack TCP connection)*
- Denial of Service: we can trigger a server to send packets to a victim's
computer by impersonating the victim's IP

IPSec, which is cryptographic security properties that hold at the IP level,
can help mititage these security flaws. It works using

- Key exchange based on public key cryptography or shared symmetric keys
- **Authentication header** which provides authentication and integrity using 
HMAC, and protects against replay attacks by including a sequence number
- **Encapsulating Security Payload** which provides confidentiality, 
authentication, and replay protection by using the same algorithms as the
authentication header but on the IP datagram portion of the IP packets.

#### IPSec: Transport Mode

In this moade, IPSec protects the packet paylod *(either with authentication,
confidentiality, or both depending on the choice)*. The original IP header is
left intact - the original information is still available and observable 
including source and destination.

#### IPSec: Tunnel Mode

This creates a new header - the full packet is encrypted and authenticated. 
The original source and destination of the packet are protected from any 
potential observers.

Using IPSec in tunnel mode is one of the means used to create a VPN. Inside the
VPN, packets are fully protected by IPSec. VPNs don't protect against denial
of service, and doesn't solve the authentication problem as it only 
authenticates at the network level - applications and programs aren't 
authenticated.


## VPN vs. Proxy

Where a proxy separates two networks, a VPN acts as one network. They both
have different threat models. Since a proxy sits on the boundary between two
networks, they can see what happens on both sides and in that way that act as a
man in the middle. A VPN creates a single network wherein all traffic is 
end-to-end encrypted, thus no man-in-the-middle can see what happens.

## TCP Security

IP has limitations given that it
is only designed to facilitate routing.

- **No reliability:** messages can get dropped, and there is no mechanism to 
ensure arrival of message
- **No congestion/flow control**  on host or client side
- **No sessions:** no way of associating messages together in either direction.
- **No multiplexing:** no way to associate messages to a network address or
to specific applications/users on host

TCP *(transmission control protocol)* addresses these limitations by helping
hosts establish and maintain a connection to exchange a stream of messages.
It determines how the data set by the application is divided into packets that
can be routed through the network. It manages flow, retransmission, and order.
It is built up of 

- Ports used to multiplex applications over a connection
- Sequence, window, and ack numbers used to manage the flow number and 
guarantee error-free transmission
- Flags including `ACK` *(acknowledgement)*, `RST` *(terminates a connection)*,
`SYN` *(acknowledge the beginning of a session)*, `FIN` *(another way of 
terminating a connection)*.

### Three-Way Handshake

TCP uses a three-way handshake to initialize connection.

1. `SYN`: this is sent by the client as a means to establish desire to connect
with the server.
2. `SYN` + `ACK`: the server responds with both flags set, and using the
received sequence number incremented by 1.
3. `ACK`: this is sent by the client to acknowlegde the response of the server
and establishing reliable connection - they can now start the actual data
transfer.

Like the previous protocols, TCP doesn't include and integrity or authentication
mechanisms. The sequence numbers act as a vey weak secret that is used as
authentication - clients and server accept packets as long as the sequence
number matches what they're expecting to receive. This means that if an 
adversary can predict the sequence of numbers, then the connection can be
hijacked, be mitm'd, or can have packets modified.

If the advserary is on-path, then they can directly observe the sequence 
numbers. In some cases, hosts use a weak random number generator *(e.g. based on
current time)* that allows adversaries to make guesses with a high chance of 
collision.


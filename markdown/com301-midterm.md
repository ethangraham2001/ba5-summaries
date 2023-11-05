---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: COM301 Summary for Midterm
author: Ethan Graham
date: \today
---

***
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

***
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

***
# Week 03: Discretionary Access Control *(DAC)*
## Access Control Definition
IRL as well as in the software world, we have resources that shouldn't be
accessed by everyone.

Formally, access control is a security mechanism that ensures that all accesses
and actions on objects are within the security policy.

- Can I read this file?
- Can I open a TCP socket to ...?
- Can I write to row 15 of `GRADES` table?

Access control is the foundation of security mechanisms, and it is super
important to get it right.

## Who Does Access Control? 
Access control is about deciding whether a principal is ***authorized***. This
is different to ***authenticated*** which comes later in the course. Access
control is ***done by the TCB***

## Implementing Access Control
Shouldn't be a bunch of checks. This is too prone to errors. We should have
***one place where everything is checked***, by making calls to a reference monitor.

This reference monitor does indeed violate the *least common mechanism principle* - 
if it fails or is compromised, the security policy can be breached. On the other
hand, it fulfils both *economy of mechanism* and *complete mediation* principles.

In this example, we see that not all security policies can be satisfied at once.
We choose to make this tradeoff, as it is more secure.

## DAC vs. MAC
Pretty simple:

- **DAC:** Object owners assign permissions $\rightarrow$ fine-grain
- **MAC:** Central security policy assigns permissions $\rightarrow$ system-wide 

## Access Control Matrix
Used for DAC, it is an abstract representation of all `(subject, object, access right)`
triplets within a system. We generally classify access rights as 

- read
- write
- append
- execute

This isn't directly implementable realistically. If we have loads of files, 
then we are going to have shite time complexity

$$
O(f \cdot u)
$$

Where $f$ is the number of files, and $u$ the number of users. Filling up such
a large matrix is also error prone.

## Access Control Lists
Store a list of permissions for each object.

Here's an example: 
`file1: {(Alice, write), (Bob, read/write)}`

What's great about ACL is that it can be stored with the object. It is however
tricky to remove permissions from an object, and is error-prone during auditing
(check confused deputy analogy)

## Role-based Access Control Lists
Since systems have too many subjects that come and go, fuck it just assign them
a role. We assign permissions based on roles instead of individual users.

### Drawbacks

- temptation to create fine-grain roles and remove all drawbacks of this mechanism
- limited expressiveness since everything is grouped based on pre-defined roles
- difficult to implement separation of duty

## Group-based Access Control
Group permissions into groups. We assign these permissions to groups, and then
assign users to *(one or several)* groups. Users have the rights of all the
groups that they are in.

If we want to add finer grain policies, we can add negative permissions to 
individual users. These negative permissions should be tested first, before
testing group permissions.

Example, `Group_0` has `read/write` permissions for `text.txt`, and Alice is in 
`Group_0`. However, Alice should only have `read` permission on `text.txt`. We
give Alice a negative permission on this file, and test it before checking the 
`Group_0` privileges.

## Capability-Based Access Control
In this model, we associate the permissions to the subjects. Think *tokens*.
We call these capabilities.

This is advantageous because we can store the access rights with the subject, 
making them portable $\rightarrow$ subject flashes their token to any subsystem
or node to prove authority, and it is easy to see all associated permissions.

The drawbacks of this model are:

- revoking permissions is hard
- searching for permission is linear in the number of users (a bit shit)
- transferability is too easy (Alice can give token to Bob) and if Bob shouldn't
be able to access that file according to the aforementioned access control matrix,
then this action has violated the security policy.
- how do we check authenticity of permissions when they reside with the subject?

## Ambient Authority
$\rightarrow$ a process or user is granted excessive privileges due to the 
environment in which it operates. Violates least-privilege mechanism, as a 
process/user should only be given the least amount of privilege necessary to
get the job done.

**Example:** `program.exe` modifies `file.csv`. When being executed, `program.exe`
is granted the privileges of the user running the program. This is an example
of ambient privilege.

Ambient authority simplifies system design a whole lot, but the drawback is that
it is difficult to enforce least privilege when authority isn't clear.

### Confused Deputy Problem
A privileged program/user can be tricked to misuse its privilege.

## Access Control In Linux
Operating Systems, in this case Linux, rely on discretionary access control.

- Everything is a file
- Every user "owns" a set of files
- Each file has a simple ACL
- All user processes run by a user are run with that user's privileges
$\rightarrow$ ambient authority!!!

Every file is associated an owner **UID and GID**. Every file has 9 permission
bits `read`, `write`, `execute`, and three subjects `owner`, `group`, `other`.
Additionally, there are 3 attributes `suid`, `sgid` and `sticky`.

- `ls` is a read operation
- `mv` is a write operation (or renaming a file, etc...)
- `cd` is an execute operation (move into directory...)

In practice, in Unix systems, one cannot read and write the files on directory 
unless the execution bit `x` is also active.

### ACL Example
`-rwxrwx-w- 1 username groupname 4096000 Nov 5 17:36 bbc_fun.mov`

From the left:

- `bit 0`: `-` if file, `d` if directory
- `bits 1-3`: owner permissions. Here owner can read, write, and execute
- `bits 4-6`: group permissions. Here the group can read, write, and execute,
- `bits 6-8`: other permissions. Here the other entities can only write
- `4096`: the size of the file in bytes
- `Nov 5 17:36`: when the file was last modified
- `bbc_fun.mov`: the filename

The **owner** of the file can change permissions using the `chmod` command.

### In Practice
UNIX compares the `UID` or `GID` of the process trying to execute the command
with.

- If our `UID` is that of the owner, execute with owner privileges
- If not, we check our `GID` bits to see if we are in the owning group. If those
match, we execute with group privileges
- If both of those checks fail, execute with other privileges.

If the `UID` is that of the root user, we are always granted permission.
`root` is in the TCB!!

- `sudo` executes **one** action as super user
- `su` changes the current user to super user. This is dangerous as any actions
afterwards will not undergo any security checks

### `sid` and `sgid` bits
Set to tell the file that it isn't to be run with the privileges of the launcher,
but with the privileges of the owning user/group respectively.

## Special Rights: Nobody
This is `uid=2`. Owns no files and belongs to no user. It's safer to execute 
unknown code using these access rights. Limits damage if the code misbehaves

***
# Week 04: Mandatory Access Control *(MAC)*
## No Ownership
Even if a given user produces a file, they are not the ones setting the access
rights on it. That is determined by the security policy.

Remember that a security model is **not** a policy or mechanism - it is simply
a design pattern and a way of reasoning about security properties. They
provide no details about the policy - that is still to be designed by the 
security engineer, and carefully following the model doesn't guarantee security.

## Bell-La Padula Model *(BLP)*
We associate subjects and objects to a level of confidentiality: i.e. protect
objects against being accessed from non-authorized subjects.

### Recall: Access Rights

- Execute
- Read
- Append
- Write

## Level Function for Objects
We associate each object to a ***security level*** based on a ***label*** and 
one or more ***categories***
```
security_level = (classification, {set of categories})
```

- **Classification** is a total ordering of labels
- **Categories** are compartments of objects with a common topic

### Dominance Relationship
A security level `(l_0, c_0)` *dominates* `(l_1, c_1)` iff. `l_0 >= l_1` 
*(in the defined total ordering)* and $c_1 \subset c_0$

### Dominance Lattice
There are three key properties to keep in mind

1. "Dominates" is transitive
2. There are top and bottom elements
3. "Dominates" only has a partial order (not all elements can be compared as they 
have no relationship)

#### Clearance Level
This is defined as the maximum security level that a subject has been assigned.
We define this as $level(S_i)$

#### Current Security Level
Subjects can operate at lower security levels than this
We define this as $current-level(S_i)$

***The clearance level dominates the current security level.***

## 1. Simple Security *(SS)* Property in BLP System
The subject can only access objects that are in its current security level, 
which by definition is dominated by their clearance level. We also call this
property **no-read-up**

The problem with forbidding people to read up is that if a malicious user
and higher clearance modifies code giving classified information to lower-clearance 
users, thus violating the SS property.

## 2. Star Property or *-Property in a BLP System
Formally, if a subject has simulataneous *observe* `(r, w)` access to $O_1$, 
and *alter* `(a, w)` access to $O_2$, then $level(O_2)$ dominates $level(O_1)$

What this means is that subjects can't write in clearance levels lower than
theirs, therefore they can't leak information to lower levels.

## 3. Discretionary Property or DS-Property in a BLP System

If an access `(subject, object, action)` takes place, then it must be in the 
access control matrix. 

This is saying that we need DAC as well basically. Regardless on privilege,
accesses should be done on a need-to-know basis. Always.

## BLP Basic Security Theorem
If all state transistions are secure, and the initial state is secure, then 
every subsequent state change is also secure regardless of the inputs.

If all three aforementioned properties hold for any individual access, then 
sequential composition security holds. This implies that a system can be analyzed
in terms of single step transitions of states.

## Covert Channels
Any channel in which information flows contrary to the security. The more
resources are shared, the harder it is to prevent them.

### Mitigating Them
The best we can do is add noise to data, or try isolte high-level information
(prevent it from flowing down). This doesn't eliminate anything, just limits.

## Big Problem with BLP
BLP says nothing about level-changes. This can be problematic, and lead to the
flow of classified higher-clearance information.

*How does the general communciate with soldiers after reading classified information
if there is a no-write-down policy?*

To communicate with lower levels, it is common to include a declassification process.
$\rightarrow$ clean a higher-level process of information so that it can be
shared with lower-levels. It is very difficult to rule out information leakage
however.

### Limitations

- Only cares about confidentiality (doesn't consider integrity or availability)
- State-based + sinle-transition model isn't expressive enough
- The three properties aren't enough to ensure confidentiality

We will not talk about ensuring integrity as well...

## BIBA Model for Integrity
BIBA implements the following

- **No read-down:** protects higher-level integrity principals being corrupted
by lower-integrity data
- **No write-up:** prevents lower integrity principals from corrupting high
integrity data

Here we only consider operations `read` and `write` (so two instead of four).

### Example 1:
In a bank, a director can establish a rule and every employee can read it.
Employees cannot rewrite any rules.

### Example 2:
On a computer, a web application open in the browser shouldn't write to the 
filesystem (at most `/tmp`).

## BIBA Variant 1: Low-water-mark for Subjects
Subjects start processes at their highest integrity level. When accessing a
an object, the process's current level is lowered to `min(curren_level(s), level(o))`.

$\rightarrow$ We temporarily downgrade for the session to be able to leave low
integrity data.

## BIBA Variant 2: Low-water-mark for Objects


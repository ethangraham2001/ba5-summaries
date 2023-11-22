---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: COM301 Summary Weeks 7 to 14
author: Ethan Graham
date: \today
---

# Week 07 Authentication
**Authentication** is the act of verifying a claimed identity. This happens
before access control - we must know that the person is who they claim to be
before checking for access privileges. 

## Passwords
We consider 4 problems that need to be solved related to passwords

1. Secure Transfer
2. Secure Check
3. Secure Storage
4. Secure Passwords

# Week 08 Adversarial Thinking I

# Week 09 Adversarial Thinking II

## CWE *(Common Weaknesses Enumeration)*
The idea is to make a "database" of software errors leading to vulnerabilities
to help security engineers avoid common pitfalls.

### XSS *(Cross-Site Scripting)*
This common weakness stems from improper neutralization of input during web-page
generation.

#### Example
I visit a webpage that takes some input, and that this input will be displayed
to other users afterwards. Instead of the requested fields, I input some
malicious JS code. Let's assume that the input isn't sanitized.

What happens is that my input will be displayed on the website, and run
on other users browers since it is JS code. Hence I have just executed malicious
code on another users system.

## CSRF *(Cross-Site Request Forgery)*
The idea is to make a bait website `B` and lure a user into using it. When this
happens, site `B` highjacks the users active session for site `A`, and forwards
requests through to it on their behalf - which is no good.

It's basically an instance of the confused deputy problem. This happens with
cookie-based authentication, which is an ambient authority.
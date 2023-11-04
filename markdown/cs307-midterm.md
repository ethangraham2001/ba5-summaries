---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS307 Summary for Midterm
author: Ethan Graham
date: \today
---

# Week 01: Introduction

## Moore's Law, and The Age of the Uniprocessor
Moore's law states that every 2 years, the number of transistors in a processor
double. This held true for decades, and saw an exponential increase in
the performance of single-core processors all the way up until around 2005.

This era also saw the innnovation of uniprocessor architecture, with such
innovations as out-of-order execution.

## End of the Uniprocessor - Beginning of the Multiprocessor
Since voltage levels hit a floor, we weren't able to increase transistor count
anymore without it causing a serious thermal problem - we can only dissipate
so much heat.

Since we couldn't feasibly make single-core processors much faster, we started
making multi-core processors: several slower cores working together perform
better than a single faster core.

## Models of Parallelism
There are a few common types of parallelism

### Instruction-Level Parallelism
A single processor executes multiple instructions concurrently. Limited by
data-dependencies in the program

### Task-Level Parallelism
Multiple threads of the same program execute concurrently (either on the same,
or on different CPUs). This is limited by the algorithm used and by sychronization
overheads.

### Data-Level Parallelism
One instruction executes concurrently on multiple data (**SIMD**)

## Multiprocessor Caches
In a multiprocessor, memory accesses (`ld`, `st`) are not commonly executed
in program order or atomically. We will learn to deal with this throughout the
course.



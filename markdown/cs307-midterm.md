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

---
# Week 02: Parallelism

## Recall: Unicore Parallelism
On the big fancy unicore processors that used to be used commonly, most of the
parallelism-related work being done was just book-keeping

- What branches are there?
- Which instructions are dependent on eachother? Which ones aren't?

Caches were getting bigger, cores were getting bigger, we were running more
out-of-order instructions. Doing this required dividing up transistors
appropriately.


## Expressing Parallelism in Practice
The two common ways to express parallelism as

- Language-level constructs
- Compiler Directives

OMP is a compiler directive, whereas languages like Java and Scala have
language-level constructs for writing parallel code.

## SIMD on Modern CPUs
Nowadays, this is normally handled by the compiler *(or assembly programmer)*.
This is different to parallelism, which is requested explicitly by the 
programmer using the aforementioned ways to express parallelism.

## Principle of Parallelism

- Finding enough parallelism
- Granularity (division of work)
- Scaling 
- Communication and Synchronization

## Amdahl's Law
$$
Speedup = \frac
{
    1
}
{
    \frac{Fraction_{enhanced}}{{Speedup_{enhanced}}} + (1 - Fraction_{enhanced})
}
$$

When parallelising a program, we want to be able to reduce overhead as much
as possible - everything that isn't execution of a task is overhead.

## Three Models of Communication Abstractions

1. Shared Address Space
2. Message Passing
3. Data Parallel

### Shared Address Space
Threads communicate by reading and writing to shared variables. This is done
implicitly *($thread_0$ writes to shared variable, $thread_1$ reads from it)*

We can implement this naturally in two ways

- Threads share an address space.
- Threads have their own address space. Shared variable address maps to the same
physical memory location.

### Data Parallel
This is what we are doing when we all `#pragma omp parallel for`.

## NUMA
The problem with uniform access is that although costs are uniform, memory is
also uniformly far away.

Non-uniform access allows for high-bandwidth and low-latency access to local
memory. Bandwidth scales with number of nodes since most accesses are local.

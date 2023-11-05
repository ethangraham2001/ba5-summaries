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

***
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

***
# Week 03: Coherence

## Temporal and Spacial Locality

- **Temporal:** Whatever I use, I am likely to use again
- **Spacial:** If I use a piece of data, I am likely to use neighboring data


## Shared Memory Expectation
Any core $P$ reading from address $X$ should get the last value written to $X$.

### SWMR Invariant: Single Writer, Multiple Reader
Either the last reader, or any writer, has a valid copy

## Valid/Invalid Protocol
We use a shared bus *(connected to all processors)* to announce all reads and
all writes

- When I read, I put `Rd(X)` on the bus and get it from memory
- When I write, I put `Wr(X)` on the bus. All other processors with this data
must invalidate, and I write through to memory.

Since the shared bus is serialized by design, this protocol serializes memory
accesses and modifications $\rightarrow$ only one processor can get to the bus
at any given time, and only one can go first.

The problem with this is that the bus gets way too much traffic using this
protocol. The amount of traffic increases exponentially with the number of cores.

Furthermore, in this model, memory always has the authoritative copy of the 
data.

## MSI Protocol
Writeback caches have three states

1. Valid
2. Invalid
3. Dirty

Valid and invalid are the same as before. Dirty indicated that the
**main memory** contains dirty data. Thus, upon eviction of a dirty cache line,
the result in main memory must be updated. We thus *write back* to memory.

The ***MSI*** protocol has three states

1. **Modified (dirty):** This cache contains the authoritative copy. Memory is 
stale and needs to be updated upon eviction of this cache line.
2. **Shared (valid):** One or more caches hold the value, and thus we have read
permissions only.
3. Invalid

In this protocol, we distinguish between a read and a read with intent to modify.
If we write to a block in **S** state, we must invalidate this data in other
caches *(we send an invalidate message)*

When a block in the modified state snoops a `rd` for that block on the bus, 
it writes back, and puts the block into the shared state.

### Example
Assume the following program

```C
int a;

// cache 0 runs this
for (int i = 0; i < 100; i++)
    a++; // read a, write a

// cache 1 runs this afterwards
for (int i = 0; i < 100; i++)
    a--; // read a, write a
```
Assume that a block size if 128 bytes, that `a` begins in the shared state
for both caches, that a `BusInv` is 4 bytes, that a single word write is 8 bytes,
and that `BusRd` is free.

Compute the bus traffic

#### Write-Through Cache (Valid/Invalid Protocol)
**Cache 0:**

The first read is a free, and is a hit. However, every write is written-through
to main memory, which costs 8 bytes per write $\rightarrow 8 \cdot 100 = 800$
bytes

**Cache 1:**

The first read is a miss, so the cache block is retrieved from memory. This costs
$128$ bytes. The rest is the same as cache 0, with $8 \cdot 100 = 800$ bytes
of bus traffic due to the writes.


In total, we get $1728$ bytes of traffic.

#### Write-Back Cache (MSI Protocol)
**Cache 0:**

The first read hits which costs nothing. The first write hits, and a 4-byte `BusInv` is
sent so that cache 1 invalidates its cache block. Every subsequent write is a hit.

**Cache 1:**
The cache block is retrieved from main memory following the first read miss, which
costs 128 bytes. The first write requires a 4-byte `BusInv`, and every subsequent
write is a hit.

In total we get $136$ bytes of traffic on the bus.

## MESI protocol
This is similar to MESI, but with an exclusive state (hence the **E**)

The key insight is that we can avoid sending a `BusInv` when writing 
if we know that we are the only cache that holds a specific block

## Point-to-Point Network, and Directory Based Cache Protocol
Shared buses aren't really used in practice anymore. Instead, point-to-point
networks are used. The Insight is that it's really fast to communicate with a
neighboring cache in a ring.

To maintain cache coherence, we use a **coherence directory**.

### Directory-Based MSI Protocol
The class slides have a good example. It essentially works as before, just
communication passes through the directory. If we write to an ***S*** cache line,
we must wait for an ACK from all other caches holding this line before proceeding
to the modified state.

### Anatomy of a Coherence-Based Directory Entry
Each entry stored, in a bit-vector

- The MSI/MESI state
- The tag
- The core ID

Each directory entry corresponse to a cache-line on each processor.

Assume that cache line $L_i$ contains four tags. Assuming that we have four
processors, each with a line $L_i$, this means that we have to keep state of
sixteen cache tags per directory entry. Performing lookups on 16-cache tags per
directory is expensive.

What we choose to do is steal an extra bit from the cache tag to index more
directory sets. This allows for a narrower *(less associative)* cache directory.
We make a really tall directory, instead of a really wide one.

## Notes on Sparse Directories
***TODO***

---
# Week 04: Optimization
What we want to do, knowing memory hierarchy, is maximize the number of L1
hits, given that lower-level memory accesses are the biggest cause of bottlenecks.

## Four C's
We define four different types of cache misses

- **Compulsory:** Data is accessed for the first time
- **Capacity:** Cache isn't big enough *(try and access an array bigger than cache)*
- **Conflict:** Two addresses map to the same address and way
- **Coherence:** Block is removed due to coherence messages from other cores

## True Sharing vs. False Sharing

- **True Sharing:** Producer/Consumer communication. One processor writes while
the other reads the same value
- **False Sharing:** Two processors update different data that happens to be 
placed in the same cache block.

### Data Padding
This is a technique used to avoid false sharing. If data is padded enough, then
we avoid two data elements stored in two different caches being stored in the 
same cache blocks. This behavior depends on underlying hardware, and this should
be a deciding factor in choosing how much to pad a piece of data.

#### The Problem with Padding
In caches with large block sizes, we naturally have to pad more. This means
that more data is needed for every individual element, and we end up having more
capacity misses due to each element requiring more space in cache.


## Optimization Examples
### Optimization Example: Tiling
This is a true sharing optimization that involves optimizing cache-locality. 
Every threads loads data in such a way that it loads data that will be needed
soon after.

### Optimization Example: Avoid Excessive Fork-Joins
Instead of
```C
#pragma omp parallel for
for(...)

#pragma omp parallel for
for(...)

#pragma omp parallel for
for(...)

#pragma omp parallel for
for(...)
```

Go for something like
```C
#pragma omp parallel
{
    #pragma omp for
    for(...)

    #pragma omp for
    for(...)

    #pragma omp for
    for(...)

    #pragma omp for
    for(...)
}
```
### Optimization Example: Loop Unrolling
Instead of 
```C
#pragma omp parallel for
for (int i = 0; i < n; i++)
    a[i]++;

```

Go for
```C
#pragma omp parallel for
for (int i = 0; i < n; i+=4)
{
    a[i]++;
    a[i+1]++;
    a[i+2]++;
    a[i+3]++;
}
```

## Division of Work and Load Balancing
There are three different types of load balancing, each accompanies by their
own clauses in OMP.

**Static**

- Low overhead
- May exhibit high workload imbalance

**Dynamic (Task Queue)**

- High overhead
- Can reduce workload imbalance

**Guided**

- Less overhead than dynamic
- Comparable to dynamic in reducing workload imbalance

***
# Week 05: Memory Consistency I

## Coherence vs. Consistency
Coherence solves the problem of two caches transparently sharing a single
memory location $X$. Coherence gives the programmer the illusion of uniform
memory across all CPUs.

Consistency defines the behavior of read and write operations across different
addresses

## Memory Access Overlaps
It is possible for modern CPUs to re-order memory accesses. This is illustrated
with the following....

Assume that $P_0$ runs
```python
# A = r_0 = 0

A = 1
r_0 = B
print(r_0)
```
and assume that processor $P_1$ runs this concurrently
```python
# B = r_1 = 0

B = 1
r_1 = A
print(r_1)
```

It is possible, in this example, that the lines $r_0 = B$ and $r_1 = A$ are
executed ***before*** the lines $A = 1$ and $B = 1$. This means that `0, 0` is a 
valid output. How is this possible? Memory access overlapping.


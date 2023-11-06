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

It goes as follows: 

0. Both A and B start in the shared state of both processors' caches.
1. Both $P_0$ and $P_1$ issue their writes into the point-to-point network 
simultaneously
2. Both CPUs issue their reads. Since their caches are non-blocking, they hit
before the the writes have finished.

Thus they both return `A = B = 0`.

## Sequential Consistency
*"Multiprocessors should behave like multitasked uniprocessors*". More formally,
the result of any execution is the same as if all operations of all processors
were executed in some sequential order, and the operations of each individual 
processor appear in this sequence in the order specified by its program.

In **SC**, memory appears like it has a "switch" in front of it, executing
each program's memory accesses atomically and in program order.

In the example above, the observed result is such that $A = 1$ always happens
before $r_0 = B$, and $B = 1$ always happens before $r_0 = B$. SC doesn't say
anything else about the interleaving of the two processes, however.

### Implementing SC
We require the following:

1. Memory accesses happen in program order
2. Memory operations appear atomic

## Reminder: Out-of-order Pipeline
The idea is that we fetch instructions in order, execute them out of order
(including memory accesses) and retire them in order again. Retiring in order
is necessary if we want to be able to keep track of exceptions, and where they
happened.

## Register Dependencies, and Memory Dependencies
Register names are encoded in the instruction, and all register dependencies
are established at the decode stage, thus in program order.

This is non-trivial with memory ops. Consider the following example
```asm
st $r2, 4($r1)
ld $r3, 8($r5)
```
If `4($r1)` and `8($r5)` are the same, then `$r3` needs to get the value from
`$r2`. If not, then they could have been re-ordered safely.

We need to do the following:

- Track the FIFO program order of loads and stores
- Resolve addresses when they are ready
- On a load, check for the **youngest** store to this address

We do this with a ***load-store queue*** (LSQ) which

1. Resolves which load/store addresses overlap
2. Holds all store operations until they retire

An LSQ cannot write speculative values to caches. Speculative values are those
that ran out of order, so the LSQ waits until all prior accesses are complete
before writing them, otherwise it could corrupt the system's state.

Load-store queues get super hot, because they do so much work.

### Address Resolution in LSQ
The idea is to use a $N \times N$ half-matrix of comparators that cross-checks
every entry against all **older** entries.

### Blocking Speculative Stores
The LSQ and ROB work hand-in-hand. The idea is that we only remove an LSQ entry
when a store exits the ROB.

Once a store is in the retired state, we can't revert it back anymore. We have
to be sure before retiring.

## Store Buffer
The store buffer sits between the core and the L1 cache, and holds all committed
stores. When a store leaves the core, it goes into the store buffer. Allows us
to avoid using L1 bandwidth when we are loading recently stored values. We now
check both the SB and the L1 when we load.

The store buffer is considered to be a part of L1. We just use it temporarily
hold recently committed stores.

## Using Stalled Operations in LSQ
Assume that some load/store operation is stalled waiting for operations ahead of it
in the queue to commit. In traditional SC, I can't do anything with it... When this instruction
gets to the head of the queue, and it misses in L1 cache, I spend 100 cycles
waiting for that block to be retrieved from lower-level cache.

**Key insight:** I can fetch cache blocks corresponding to any stalled load/store
operations before they are needed, and put them in L1 in anticipation for their
arrival at the head of the queue.

This does not impact order or atomicity, and we can save loads of cycles by
overlapping this fetch with the current fetch that is happening at the front of 
the queue.

Note, **I do not put this fetched value in the core**, I just put it in L1. When
the instruction finally arrived at the head of the LSQ, it will hit. We have
effectively overlapped two instructions without violating program order or atomicity.

This is called **L1 peeking**, and it helps overlap all long-latency operations.
We do this for all waiting ops in an attempt overlap latency.

## Relaxed Consistency Models
We can only go so far with SC and peeking. If the ROB is full, then even if we
have peeked and are loading in more cache blocks to overlap latency, we can't
fetch anymore new instructions while waiting.

**Idea:** relax write-to-read dependencies *(that is, writes block younger reads)*.

## Processor Consistency *(a.k.a Per-Processor Consistency)*
Formally, we define with the following specification

- Before a load is performed with respect to other processors, all preceeding
loads must be performed
- Before a store is performed with respect to other processors, all preceeding
operations (loads and stored) must be performed

Since this description is very unclear, a better way to put it is:

"Each processor observes operations in an order that is consistent with its own
program, but the global order of memory operations may differ between processors,
providing more flexibility for optimization and better performance."

This consistency model is widely employed, since it is fast while remaining
relatively easy to reason about. Most ISAs provide instructions that enfoce
atomicity, *e.g.* `xchg` on x86 architecture.

## Weak Consistency Intro
Memory ops are classified either as data or synchronization. Only synchronization
ops have any notion of ordering, whereas data ops have no enfored order among
themselves. Synchronization ops are called `Fences`. This consistency model is
used on ARM architectures.

***
# Week 06: Memory Consistency II

## Some Consistency Models
### Recall: Sequential Consistency 
Sequential consistency is the strongest model.

- Ensuring program order requires resolving addresses between ops *(using LSQ)*
and managing speculation, only writing authoritative values *(combine ROB and SB)*
- Ensuring atomocity requires explicit communication between all processors after
every write operation.

### Recall: Processor Consistency
The simple idea is that we let indepent loads bypass the stores. The address
resolution is taken care by the LSQ.

### Arm Memory Model
"ARM implements a weakly consistent memory model for normal
memory. Loosely, this means that the order of memory accesses
observed by other observers may not be the order that appears in
the program, for either loads or stores."

In plain english, be careful because you could see any order.

## Language Level Consistency
At the ISA level, loads and stores can have different purposes
*(storing data that doesn't fit in registers, communication between cores, etc...)*.
As a programmer, however, we don't want to have to think about ISA too much, if
at all. Statements in a higher-level programming language don't always translate
exactly into the ISA.

### Problem: Register Allocation

Consider the following example, which is how some programmers try to manage
concurrency.

Thread 0:
```C
// val = done = 0
val = expensive_func();
done = 1;
```

Thread 1:
```C
// done = 0

while (!done)
{
    ... = val
}
```

The compiler *(and many do this)* may detect `done` as loop-invariant and 
compile it out of the loop like this: 

Thread 0:
```C
// val = done = 0
val = expensive_func();
done = 1;
```

Thread 1:
```C
// done = 0

tmp = done;
if (!tmp) {
    while (1)
    {
        ... = val
    }
}

```

To prevent register allocation, we can use the `volatile` keyword in C. This
indicates that the value can change at any time, and that the compiler should
disable register allocation and other optimizations.

However, the processor still allows reordering here - what if we want to NOT
reorder the lines :
```C
val = expensive_func();
done = 1;
```

## Disallowing Re-ordering
This previous problem is non-deterministic and completely compiler/architecture
dependent. We can kill it with fences, but this kills cross-ISA portability
which is no fun.

Moreover, inserting ASM into C code defeats the whole point in having different
levels of abstraction between the two. Example, using 
```C
asm volatile("mfence":::"memory");
```

We want to provide an end-to-end guarantee of program correctness. Challenge
is to agree upon what a *correct* program is.

## What Should We Guarantee?
Sequential consistency is still the most intuitive model. However, what we choose
to do is use sequential consistency only the places where the threads will 
communicate. If we do this, we have to make sure that all parallelism is guarded
using for example `#pragma omp critical` and similar. 
$\rightarrow$ I only worry when I know someone else is going to use my data.

## Selectively Enforce SC
We add `fence`s, and prevent re-ordering across them. It ensures write visibility
before the next operation. Basically says *"get your shit together"*.

Programmers should write correctly synchronized code with no data races. Then,
language, virtual machine and hardware, will **guarantee SC**.

We call this ***data race free = SC***

### Data Race
Two conflicting memory operations from different threads occur simultaneously
$\rightarrow$ have back-to-back accesses in any sequentially consistent interleaving.

## Solving Data Races
We used to add fences like this:

```C
int a = 1;
_sync_synchronize();
r_1 = b;
print(r_1);
```

But now we use compiler directives like:

```c++
atomic int a = 0;
```

Which ensures atomicity and program order for you.

### Before
Needed to adjust programs based on ISA and consistency model of target architecture

### Now
As long as we follow the rules, $DRF \Rightarrow SC$ holds!

## Java Memory Model: JMM
Memory order in JMM is defined by *happens-before* relationships denoted by
$\rightarrow$. This ensures that certain operations in a thread are visible to 
other threads in a predictable way. For example, the `synchronized` notation
from ParaConc.

Imagine we have the following Java code

```Java
class SharedResource {
    private int value = 0;

    public synchronized void increment() {
        value++;
    }

    public synchronized int getValue() {
        return value;
    }
}
```
When $T_0$ calls `increment()`, it enters the `synchronized` block and increments
`value` then exits. The *happens-before* relationship ensures that any modifications
made by $T_0$ in the `synchronized` block are visible to other threads.

Here are some salient "$\rightarrow$" relationships

- Actions in the same thread $\rightarrow$ each other in program order
- Unlocking a monitor $\rightarrow$ all locking operations 
- Writing to `volatile` $\rightarrow$ all reads of that field
- All actions in a thread $\rightarrow$ a `join()` on that thread
- if `A_x` $\rightarrow$ `A_y` and `A_y` $\rightarrow$ `A_z`, then `A_x` $\rightarrow$ `A_z`

If we can find two actions `A_x` and `A_y` such that

- `A_x` does not $\rightarrow$ `A_y`
- `A_y` does not $\rightarrow$ `A_x`

then we have found a data race.

In the Java memory model, any action sees **all** actions that $\rightarrow$ it.
For example:

- `rel(m)` $\rightarrow$ `acq(m)`
- `acq(m)` $\rightarrow$ `rd(t)`
- `rel(m)` $\rightarrow$ `wr(t)`

In the slide 53 example. Where `acq(m)`/`rel(m)` are acquiring/releasing lock `m`
respectively.
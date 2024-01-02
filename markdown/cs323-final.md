---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS323 Summary for Final (Weeks 7 to 14)
author: Ethan Graham
date: \today
---

# Week 07: Paging

Focus of the lecture: Memory virtualization using paging

## The Idea Behind Paging

We split the address space *(code, stack, heap)* into fixed-size chunks called
**pages**. We assign memory based on page-granularity.

The page is the minimal unit of an address space. In a process context, which
is a virtual address space, we call this a **virtual page**. Physical memory
is divided into an array of fixed-size slots called **page frames** or physical
page. Each page frame can contain a single virtual-memory page, and page
size should be designed in such a way to minimize internal fragmentation. A
common size if 4KiB.

We note that the allocated physical memory can be non-contiguous on a page-basis
while virtual address space always appear contiguous.

## Address Translation

Thet translation from virtual to physical address is done with the MMU.

- High order bits designate **page number**: different to physical page frame
- Low order bits designate **page offset**: same as corresponding physical 
address.

## Page Table

A page table stores the virtual-to-physical address translations - it basically
stores address trnalsations for each of the virtual pages in the address space,
and allows the MMU to know where in physical memory each of the virtual pages
resides.

Every process has one page table which resides in memory, and is managed by 
the OS. A pointer to this page table is stored in a register i.e.
*page-table base register* `PBTR` on some Intel chips.
The value of `PBTR`is saved and restored in the PCB on context switch.

The table contains **page table entries** that store the page frame number,
as well as some book-keeping.

- Present bit: is the address translation valid?
- Protection bits: A page can have read/write/execute permission. For example,
code blocks are marked with execute.
- Dirty bit: Whether a page has been modified since the first write.
- Access/Reference bit: Helps track page popularity.

There are ways to clear the dirty/access bits.

## Page Table Structures

### Linear Page Table

This is the easiest way to implement a page table. Every virtual page maps to
a physical page - this means that we need a physical page for every virtual
page which leads to large amounts of memory being dedicated to the page table.

We can compute the page table size in the following way:

$$
2^{
    log(\text{virtual address space}) - 
    log(\text{page size})
}
$$

### Linear Page Table: Bigger Pages

Given the computation from the last section, we see that if we increase page
size, we will decrease the total amount of memory associated to the page
table. This does, however, result in large internal fragmentation, which is
wasted space - wasted memory.

### Multi-Level Page Tables

***Insight:*** Most processes only need a fraction of the address space. One
or more levels of indirection allows for space-efficient encoding. Each
level adds one more memory lookup during address translation.

This creates a tree-like structure, that can be more allocated dynamically.

#### Two-Level Example

Consider a virtual address on a 32-bit machine with 4 KiB pages. This is thus
divided into 

- 12-bit page offset
- 20-bit page number

Since the page table is paged, the 20-bit page number is further divided into

- A 10-bit page number
- A 10-bit page offset

#### Example with 64-bit Addresses

Suppose that we have a 4 KiB page

- We have space for 4 KiB / 64-bits = 512 entries *(9 bits required to index
page tables)*
- 12 bits required for page-offset $\rightarrow$ 64 - 12 = 52 bits $\rightarrow$
we need 6 levels of page tables.

We can further shrink the address space if we want to require less levels of
indirection.

## Paging in Practice

- CPU requests code or data at virtual address
- MMU translates virtual address to the physical address
    1. Access Memory to read page table entry
    2. Translate virtual to physical address
    3. Access memory to fetch the desired code/data


## Pros and Cons of Paging

### Pros

- No external fragmentation, since pages don't need to be contiguous.
- Allocation is fast since we don't have to search for free space.
- Freeing is fast since we don't need to worry about coalescing.

### Cons

- Internal fragmentation. If page size is 512 bytes and we need 513 bytes, then
we need to allocate two pages with the latter being nearly empty
- Page table is stored in memory which eats up some of our available memory
- Additional memory references/transactions to the page table

## Translation Lookaside Buffer *(TLB)*

Evidently given the section ***Paging in Practice*** we see that there is a
fair bit of overhead related to page memory accesses. We address this by caching
translations in the TLB. It works the same as a normal cache does, but stores
only virtual to physical address mappings.

### Paging with TLB

Pseudo-code from the MMU's perspective.

```python

def get_addr_MMU(virtual_addr):
    ret_value, physical_addr = get_physical_addr_from_TLB(virtual_addr)

    if (ret_value == TLB_HIT):
        # address can be used directly
        return physical_addr

    else if (ret_value == TLB_MISS):
        # address not in TLB, we have to perform additional memory actions
        physical_addr = walk_page_table_in_memory(virtual_addr);
        return physical_addr
```

If we have a 4-level page table, a TLB miss costs us one memory access for
every uncached memory address we access as we walk the page table. 
If we get a TLB Hit, then we don't even need to access memory.

## Brief Introduction on Swap Memory

When main memory isn't enough, we can use swap memory stored on-disk. In
particular, the idea is to store unused pages on-disk. This allows the OS
to overprovision memory. When needed, the OS finds and pushes unused pages to
disk.

### Page Faults

Every page table entry at each level has a present bit that indicates if the
reference is valid. This is checked by the MMU during translation, and triggers
a page fault exception when detected *(page not present)*. The OS enforces its
policy handle these page faults.

#### Page Fault Handler

The handler checks

- Which process caused the exception *(locate data structure)*
- What address caused the exception

If the page is on-disk, the OS issues a request to load the faulted page and
tells the scheduler to switch to another process.

If the page is not swapped out, the OS creates the mapping and updates data
structures.

The OS can then resume the faulting process by re-executing faulting 
instruction(s).

# Week 08: Concurrency

## Concurrency vs. Parallelism

Concurrency focuses on maintaining multiple tasks by allowing a ***single
processing unit*** to work on them in such a way that appear to executing
simultaneously. Parallelism focuses on performing multiple tassks or several
parts of a single task in parallel by using ***multiple processing units.***

## OS Concurrency

The OS manages multiple resources to execute multiple tasks.

- Efficiently manage processes
- Efficiently manage hardware devices

Operating Systems were the first concurrent programs. Only much later did user
space applications start using multi-threading.

## Issues with Threads

Scheduling of threads produces non-deterministic output if we don't synchronize
them correctly. This can cause

- Race Condition: timing of order of events afffects the correctness of the
program
- Data Race: One thread accessing a mutable variable while another thread
is writing to it without any synchronization.

This illustrates pretty clearly why we want operations to be atomic.

## Locks

Basic idea is to use lock variables to protect critical sections.

```C
lock_t mutex;
// ...
lock(&mutex);
counter = counter + 1;
unlock(&mutex);
```

We can implement these locks in various ways

### Interruptible Lock

Turns off interrupts when executing a critical section. Nor hardware nor
timer can interrupt execution which prevents the scheduler from switching to
another thread. Code between interrupts thus executes atomically

```C
void
lock(lock_t* l)
{
    disable_interrupts();
}

void 
unlock(lock_t *l)
{
    enable_interrupts();
}
```

This is mostly proposed for single-processor systems. It is super simple to
implement, and it generally works pretty well for low-complexity code.

However, it comes with downsides. Disabling/enabling interrupts is a privileged
operation, and thus requires an OS context switch. Furthermore there is no 
support for multiple locks, and it only works on single-core systems. It
introduces unfairness, since a greedy program can monopolize the lock by holding
it for an arbitrary length, starving other programs. Also, hardware interrupts
can get lost since we are disabling them temporarily with no way to retrieve
them.

### Faulty Spinlock

This is a faulty implementation that sets up why we need hardware support for
mutual exclusion.

```C
bool lock1 = false;

void
lock(bool *l)
{
    while(*l); // spin while waiting for lock
    *l = true; // set lock to `true`
}
```

The idea here is that we use a shared variable to synchronize access to the 
critical section. We just use simple `ld` and `st` operations to acquire the
lock by updating it.

What can happen here is that the OS can deschedule a process `thread_1` right
after it has finished spinning and before it has set the lock. Another thread
can then enter the `lock()` function at this point, and go right through the
spinning process as the lock is free. Both threads then are able to acquire the
lock by calling `*l = true` - this breaks mutual exclusion.

### Test-and-Set

The hardware implements the following code in the form of a single instruction

```C
int
tas(int *ptr, int val)
{
    int old = *ptr;
    *ptr = val;
    return old;
}
```

It allows us to test the old value while simultaneously setting the memory 
location. We can now implement a valid *spinlock* using test-and-set

```C
bool lock1 = false;

void
lock(bool *l)
{
    while (tas(l, true) == true);
}

void
unlock(bool *l)
{
    *l = false;
}
```

Test-and-set spin lock only allows one thread to enter the critical section, 
which satisfies the mutual exclusion property. It is, however, unfair. If
multiple threads are present, a thread spinning may spin forever under the
contention - this leads to starvation.

### Compare-and-Swap

This is a hardware instruction that implements the following code.

```C
int
cas(int *ptr, int expected, int new_val)
{
    int actual = *ptr;
    if (actual == expected)
        *ptr = new_val;
    return actual; // always returns the old actual value at *ptr
}
```

Where test-and-swap always updates the old actual value at `*ptr`,
compare-and-set only does this if the value corresponds to an expected old
value.

Here is a way that we could implement the spin lock using compare-and-swap

```C
bool lock1 = false;

void
lock(bool *l)
{
    while (cas(l, false, true) == true); // spin and wait
}

void
unlock(bool *l)
{
    *l = false;
}
```

This, like the test-and-set implementation, doesn't break mutual exclusion.

## Problem with Spin Locks

Currently, lock waiters keep spinning until they acquire the lock. This is
also known as **busy-waiting** and wastes a bunch of CPU cycles which could be
better utilized by other threads or processes in the system.

Other implementations, such as sleepable locks, allow waiters to give up the
CPU by yielding - waiting until the CPU schedules them again some time later
when the lock is free. We can make it so that waiters are woken up at the
time that the lock is released. We can do this in a couple of ways

- Wake up all threads at the time of lock release and have them all race for
the lock.
- Selectively wake up one threads from the queue, ensuring fairness.




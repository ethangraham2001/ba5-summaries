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

Where test-and-set always updates the old actual value at `*ptr`,
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

# Week 10: Deadlocks and Semaphores

## Condition Variable

The condition variable allows for threads to wait for a certain condition before
they proceed. They are often used with a lock to safely check and wait for
certain conditions.

### Example: Signaling to the parent process that a child process has exited

The simple approach would be for the parent to spin on a shared variable while
waiting for the child to terminate *(setting the shared variable)*.

What we can do here is implement that mechanism with a conditional variable.

- Threads put themselves in a waiting queue when a condition isn't met, and
then wait for the condition to be satisfied.
- Threads leave the queue when the conditions are met.

## Conditional Variable API

We define a `condition_type c` which represents a condition on which threads
wait and signal.

The API itself is structured as follows

- `wait(c)`: Wait until a condition is satisfied
- `signal(c)`: Wake up one waiting thread
- `broadcast(c)`: Wakes up all waiting threads

These correspond to the following POSIX-specific definitions

- `pthread_cond_t c` $\equiv$ `condition_type c`
- `pthread_cond_wait(pthread_cond_t *c, pthread_mutex_t *m)` $\equiv$
`wait(c)`
- `pthread_cond_signal(pthread_cond_t *c)` $\equiv$ `signal(c)`

### Revisiting Example

This relates to the previous example related to a child process signaling to 
the parent process that it has exited. We can implement this in the following
way:

```C
// initialize mutex and CV
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;
Pthread_cond_t c  = PTHREAD_COND_INITIALIZER;
// ...
void*
child(void *arg)
{
    pthread_mutex_lock(&m);     // acquire mutex for `done`
    done = 1;                   // write to shared variable atomically
    pthread_cond_signal(&c);    // signal waiting threads that it is over
    pthread_mutex_unlock(&m);   // release mutex for `done`
    return NULL;
}

int
main(int argc, char *argv[])
{
    // ...
    pthread_mutex_lock(&m);     // acquire mutex for `done`

    // go to sleep and wait if other thread hasn't finished with `done`
    while (done == 0)               
        pthread_cond_wait(&c, &m);

    pthread_mutex_unlock(&m);   // release mutex for `done`

}
```

Note that the `pthread_cond_wait(&c, &m)` which takes as parameter both the
CV as well as the mutex ***releases the lock and puts the calling thread to
sleep atomically***.

### Question: Do we need a state variable `done`?

Suppose that the child *(from before)* runs immediately. It acquires the lock,
and issues a signal. However, in this situation, no thread is asleep on the
condition to receive the signal. When the main thread executes, it will call
`pthread_cond_wait()` and be stuck on it forever as there is no thread to
wake it up! 

### Question: Do we need a lock? 

Suppose the main thread checks for `done`. Right before `pthread_cond_wait()`,
main thread is switched out for the child thread. The child thread sets
`done = 1`, and then calls `pthread_cond_signal()`. After this, we switch 
back to the main thread, which waits forever on `pthread_cond_wait()` as there
is no thread to wake it up *(child thread has already signaled and exited)*.

### Question: Can we replace `while (done == 0)` with `if (done != 0)`?

If there are only two threads present, this isn't an issue. It will, however,
be an issue if there are more than two threads present.

### Guidelines for CV

- Always use `wait` and `signal` while holding the lock on a condition
- Whenever a thread wakes up, recheck the state to avoid race conditions

## Semaphore

A semaphore is very similar to a condition variable, except that it is an object
with an integer value as internal state. This means that a semaphore with binary
values `0` and `1` acts the same as a simple spinlock.

Three routines initialize and modify the semaphore object 

- `sem_init(s, v)`: define the capacity *(number of slots)* of the resource.
- `sem_wait(s)`: waits until the semaphore has at least one slot and decreases
the slot count by 1 when slots are available. This means that execution of the
caller is suspended in the case that the slot count is negative.
- `sem_post(s)`: increments the slot count by 1, and wakes up suspended threads.

We note that the slot count is not visible to callers.

### Semaphore Example

```C
sem_t sem;
sem_init(&sem, 0, X);   // initialize sem to X. In binary example, should be 0

sem_wait(&sem);
// Critical Section
sem_post(&sem);
```

## Bugs in Concurrent Programs

### Atomicity Violation Bugs

This happens when a sequence of operations that are intended to be executed
atomically are interrupted - allowing other operations to interleave and
leading to inconsistent of unexpected states in a progra.

```C
// THREAD 1
if (thd->proc_info != NULL)
{
    // ...
    fputs(thd->proc_info, ...);
    // ...
}

// THREAD 2
thd->proc_info = NULL;
```

`thread_1` can execute the `NULL` check, and then `thread_2` can set the value
to `NULL` before `thread_1` has executed `fputs()`.

***Solution:*** Use a common lock between threads when accessing a shared
resource.

### Order Violation Bugs

This occurs when the expected sequence of operations is not followed due to
incorrect program execution order, leading to incorrect program behavior.

```C
// THREAD 1
void
init() 
{
    mThread = PR_CreateThread(mMain, ...);
    mThread->State = ...;
}

// THREAD 2
void 
mMain()
{
    mstate = mThread->State;
}
```

Here, `thread_2` assumes that `mState` is already initialized and not `NULL`.
If `thread_2` runs before `thread_1`, the program will crash due to the
dereferencing of the `NULL` pointer.

***Solution:*** Use a condition variable to signal that `mState` has been
initialized.

### Deadlock

This happens when two or more processes are unable to proceed with their
execution because each one is waiting for the other to release a resource
they need.

```C
// THREAD 1
pthread_mutex_lock(&l1);
pthread_mutex_lock(&l2);

// THREAD 2
pthread_mutex_lock(&l2);
pthread_mutex_lock(&l1);
```

Several conditions can cause this behavior...

1. Mutual Exclusion: Threads claim exclusive control of resources that they
require
2. Hold and wait: A thread must be holding at least one resource and waiting
to acquire additional resources that are currently being held by other threads
3. No preemption: Resources cannot be preempted; that is, resources cannot be
taken away from a thread unless the thread voluntarily releases them
4. Circular wait: There must be a circular chain of two or more threads, each
of which is waiting for a resource held by the next member in the chain.

***Solution:*** Impose total ordering + obtain all resources or nothing at once
+ release held resources if not all available at the same time

Note that imposing total ordering isn't easy; we generally settle with imposing
partial ordering.

# Week 11: IO

There are a few common services that are in the form of IO *(Input/Output)*.
Some of these are

- Load programs and data from storage
- Write data to a terminal or the screen
- Read / Write packets from a network
- Read data from input devices

Different IO devices have different timescales. In general, IO interaction is
orders of magnitude slower than something like an L1 cache reference.

## Simplified Illustration of Hardware Interaction - Storage Devices

The IO controller support IO devices and is responsible for handling their 
requests. The OS handles device management and exposes a uniform interface to
applications. The OS process all accesses to these devices by reading/writing
to IO registers in hardware - this ranges from commands and arguments to reading
status and results.

$\rightarrow$ OS provides transparency to these hardware interactions.

## Buses

Buses are a common set of wires for communication among hardware devices, 
plus protocols for carrying out data transfer transactions.

In modern IO systems, interaction often happens over the PCI*(-e)* bus. The PCI
packets sent over a PCI bus have header information.

- PCI1: 4 GB/s bandwidth for 16 lanes
- PCI5: 64 GB/s bandwidth for 16 lanes

## High-level Description of a Canonical Device

The CPU will interact with something called the **device controller** by writing
to **device registers**. Device internals are completely hidden to users behind 
abstraction. The device controller signals to the CPU either through
**memory pollling** or with **interrupts**.

### Protocol

The following is some C-like pseudocode that illustrates device protocol at a 
high level.

```C
// 1. spin while waiting for the device to be ready
while (STATUS == BUSY);

// 2. write data to DTA register
*dtaRegister = DATA;

// 3. Write command to CMD register
*cmdRegister = COMMAND;

// 4. spin while waiting for the command to execute
while (STATUS == BUSY);
```

Note that we should set up the data ***before*** setting up the command
register. To link with *EE310*, we should set up the interrupt service handler
before enabling interrupts for that device in particular.

### Interaction with CPU

There are two main ways that the CPU can choose to interact with IO

1. **Port-mapped IO:** CPU uses designated IO ports. Each device has one port
assigned to it. x86, for example, has designated `in`/`out` instructions for
device communication
2. **Memory-mapped IO:** Hardware maps control registers into the physical 
address space *(think NDS hardware for EE310)* and IO is accomplished via 
`ld`/`st` instructions.

Both of these are used in practice and are supported by various architectures.
Memory-mapped IO is predominantly used in high-performance environments.

### Problem with Synchronous IO

In the high-level protocol illustrated above, we see clearly that precious
CPU cycles are wasted while spinning on `while (STATUS == BUSY)`. An elegant
solution to this is asynchronous interrupts. 

- Inform the device of a request
- Wait for a signal *(interrupt)* of completion

Thus the OS waits for an interrupt instead of spinning. These interrupts are
handled through a dispatcher - on interrupt arrival, wakeup a corresponding
kernel thread that was waiting on it.

## Polling vs. Interrupts

Interrupts tends to handle unpredictable events well, but it comes with a 
relatively high overhead associated to it. Polling, however, has low overhead
but this comes at the cost of wasting CPU cycles in the case of infrequent 
or unpredictable IO events.

Real systems use a mix of polling and interrupts.

- Interrupts allow overlap between computation and IO, and is mostly used for
slow devices
- Polling is used for short bursts or small quantities of data or for
high-performance scenarios.

### Livelock

Similar to a deadlock - it is when a process starves and makes no progress yet
the state is changing - we are stuck in a loop yet we never make any meaningful
progress. 

This is a problem in particular for interrupt-handled IO.
As an example, think of a flood of network packets arriving. The system cannot
react as the cost of handling every interrupt through context switches is too
high. Network packets simply queue up or start getting lost.

### Coalescing

This is a possible optimization that involves batching responses *(waiting for
additional requests to complete if necessary)* and sending them all at once.


## DMA

Disk transfers are slow and tedious. **Idea:** have a separate processing unit
that deals only with these slow transfers. The CPU can tell it which data is
needed, and then it handles all of the necessary bus transactions related to it.

A DMA is a form of ***PIO*** which stands for programmed IO.

### Interaction with DMA Controller

1. Device triver is told to transfer disk data to buffer at address `X`
2. Device driver tells disk controller to transfer `C` bytes from disk to
buffer at `X`
3. Disk controller initiates the DMA transfer
4. Disk controller sends each byte to DMA controller
5. DMA controller transfers bytes to buffer `X`, increasing memory address and
decreasing `C` until `C`$= 0$
6. When `C`$=0$, DMA interrupts CPU to signal that the transfer has completed.

## Dealing with a Large Number of Devices

The challenge here is that different devices have different protocols. In
general, device drivers are divided into two pieces

1. **Top Half:** Accessed in call paths from system calls, e.g. `open`/`close`/
`read`/`write`
2. **Bottom Half:** Communicates with the device; runs as interrupt routine.

Device drivers are an example of encapsulation. Different device drivers adhere
to a standardized API - OS only implements and supports APIs based on device
class.

We would like to have a well-designed API that accounts for the tradeoff between
versatility and over-specialization.

## Persistence

### Storage Devices

The commonly used storage devices come in two forms

1. Magnetic disks which have a high capacity and low cost. They have block-level
random access, but are slow for this. Streaming access performance relatively
well.
2. Flash Memory which has an intermediate cost, yet lower capacity than 
magnetic disks. They perform reasonably well for block-level random access.

#### Magnetic Disk Storage

Disk is organized into regions of tracks with the same number of sectors/tracks.
The disk has sector-addressable addresses, with each sector being 512 or
4096 bytes.

We can characterize disk latency as

$$
latency = \text{seek time} + \text{rotation time} + \text{transfer time}
$$

With the following approximate latencies

- Seek: around 5 to 15 ms
- Rotation: around 4 to 8 ms
- transfer: around 25-50 microseconds

```
// TODO: Get back to this section before exam
```

## RAID

Stands for Redundant Array of Inexpensive Disks. The idea is to build a logical
system from many disks.

### RAID 0

The idea here is to *stripe* files across multiple disks. For example, even
stripes go to disk 0 and odd stripes go to disk 1.

- No redundancy of data *(no fault tolerance because no mirroring)*
- Provides great performance *(cumulative bandwidth utilization)*
- Total storage capacity is the sum of capacities of all disks
- No data security

This is mainly used for gaming and video editing *(HPC scenarios)*.

### RAID 1

Where RAID 0 fails to address data security, RAID 1 aims to address only data
security.

- Duplicate file blocks accross storage devices. Thus it deals great with disk
loss, but doesn't actually handle corruption
- Total storage capacity is only that of one disk
- Performance: Only reads can be parallelized since a write requires data to 
be written to all disks.
- Very expensive

This is primarly used in critical infrastructure involving sensitive
information.

### RAID 5

We store different parity *(a mechanism for fault tolerance)* in different
drives, allowing us to reconstruct data from a failed disk by XOR-ing all 
remaining drives. ***(check slides page 54 for illustration)***.

- Reliable: Still works even if we lose a disk
- Affordable
- Used in datacenter environments

### RAID 01

This is a combination of two stripes (RAID 0) that are mirrored (RAID 1)

```
        R1
    ____|____
    R0      R0
   / | \  / | \
 D0 D1 D2 D3 D4 D5
```

During rebuild *(which happens if a disk has failed)*, no other drive from the 
alternate group can fail. In this example, if D0 fails, D3, D4, D5 failing
causes the whole system to halt. If D0 fails and D3 fails, the system is dead.


### RAID 10

Stripe (RAID 0) of a set of mirrored drives (RAID 1).

```
            R0
    ________|________
    R1      R1      R1
  / | \   / | \   / | \
D0 D1 D2 D3 D4 D5 D6 D7 D8
```

Of each mirror, at least one disk must remain healthy.

If D0 fails and D1 fails, the system is dead. If D0 fails, then any other disk
with the exception of D1/D2 can fail without impact.

## Summary of All This

Try and hide low-level implementation with high-level abstraction - as the OS
tries to do in general.


# Week 12: File Systems

## File System Abstraction

Addresses in a file system are needed for long-term information storage (lots
of it) in a way that outlives the program and can support concurrent accesses
from multiple processes. It presents itself to applications with **persistent
and named** data. The two main components are ***files*** and ***directories***.

## File Abstraction

A file is a **named** collection of related *(stored as binary)* information
that is recorded in secondary storage, or simple a linear persistent array of
bytes. It has two components

- **Data:** What the user or application stored in it
- **Metadata:** information added and managed by the OS such as size, security
information, modification time, etc...

There are three different perspectives that we can have of a file

1. Inode and device number *(persistent ID)*
2. File name *(human readable)*
3. File descriptor *(process view)*

Modern file systems mostly use untyped files - just a sequence of bytes. They
done understand or care about the file contents.

### Inode

This is a low-level UID assigned to the file by the file system. Inodes are 
unique in a given file system, but not generally unique globally. Each file has
exactly one associated inode, and it contains associated metadata. They are
recycled after deletion. Inode number is required to access file content.

Multiple files can map to the same inode *(such as shortcuts in Windows)* - 
we call this hard linking. 

#### Inode Table

Storage space is divided into inode table and data storage, with the inode table
sitting at the beginning of the storage media *(mostly the initial block)*.

### File Name

Each file has a human readable format which we call file name. A directory
stores the `filepath` $\rightarrow$ `inode` mappings.

### File Descriptor

The combination of file name and inode/device IDs are sufficient to implement
persistent storage. The drawback is that constant lookups in the directory is
costly.

***Idea:*** Perform the expensive tree traversal once, and store the inode
and device ID in a **per-process table**. This table also keeps additional
information such as file offset.

File descriptors are *linear integer values* that can be reused when freed.


File descriptors 0, 1 and 2 are mapped to `STDIN`, `STDOUT` and `STDERR`
respectively.

## Directory Abstraction

A directory is a special file that stored the mapping between human-friendly
names of files and their inode numbers. A directory can contain subdirectories,
thus a directory can itself be a list of files and other directories. The path
`/` indicates the root of the file system *(in UNIX anyways)*. Everything is
built like a tree that stems from `/`. The root directory has inode number 2.

### Links

Links are file pointers - they do not contain any data themselves but reference
another file.

### Hardlinks

Maps a file's path to a file's inode number. Basically mirror copy of the
original file. Same inode number as the original file.

Hard links are generally used when we want multiple files in different
directories to all point to the same physical file on disk. Changes on the
original file are reflected on all hard links.

### Soft Links / Symbolic Links

Logically maps a file's path to a different file path. Actual link to the
original file - a new inode number is allocated when we use a soft link.

Symbolic links are generally used as shortcuts to simplify filepaths. They can
be hotswapped, allowing for configuration changes by just changing where the 
symbolic link points to.

### Permission Bits

We can set `rwx` bits for owner, group, and everyone.

## File System API

File operations are generally performed, in C, using `<unistd.h>` which provides
an API for doing so, including `open()`, `close()`, `read()` and `write()`.

### C Example

```C
int fd;
// Open file in write only, create file if it doesn't exist
fd = open("example.txt", O_WRONLY | O_CREAT, 0664);

if (fs < 0)
{
    perror("Error opening the file...\n");
    return 1;

    // write data
    const char *text = "Hello, file\n";
    write(fd, text, strlen(text));

    // free file descriptor
    close(fd);
}
```

We also get further APIs such as

```C
// sets offset within file. Initially set to 0 and updated on read/write
off_t lseek(int fd, off_t offset, int whence);

// unlinks / deletes a file
// removes a file from directory when reference count is 0
int unlink(const char *pathname);

// Synchronous write. Flushes all dirty data to file
int fsync(int fd);

// get file metadata
int fstat(int fd, struct stat *statbuf);

```

## Multiple File Systems

In Windows *(cringe)* different file systems are assigned a different 
A - Z letter value.

In Linux/UNIX, file systems are all mapped in a single tree. For example,
`/home` can be a separate filesystem from `/bin`. **Mounting** allows for
multiple volumes to form a single logical hierarchy. Very nice.

## File System Implementation

We've talked about the abstraction, now let's talk about the actual 
implementation.

The file system manages data for users. It is given a large set of $N$ blocks,
and it needs to create data structures that can encode the file hierarchy
and per file metadata. The memory overhead *(metadata vs. file data)* should be
low, the internal fragmentation should be low, and the accesses of file content
should be efficient. All this while implementing the standard file system APIs.

### Layout

The file system is stored on disk, which is partitioned. Sector 0 of the disk
is reserved for the ***Master Boot Record (MBR)*** containing

- Bootstrap code *(loaded and executed by firmware)*
- Partition Table *(addresses where partitions starts and end)*

The first block of each partition is called the ***boot block*** which is loaded
by executing MBR code.

As mentioned, persistent storage is modeled as a sequence of $N$ blocks with
some fixed size of 4KB for example. They are generally assigned in the 
following sort of way

- 2 metadata blocks `0-1` for boot block and super block.
- 2 metadata blocks `2-3` for inode and data bitmap *(tells us which blocks 
are free. Free lists)*
- 5 metadata blocks `4-8` for inode array *(256 bytes, 16 per block. 
In this example, we can have a total of 80 files)*
- 55 data blocks `9-63` can store the data

### FS Superblock

There is one logical superblock per file system which stored all metadata
associated to the filesystem.

- Number of inodes
- Number of data blocks
- Where the inode table begins
- May also contain information related to managing free inodes and data blocks

This is the first thing that is read when mounting a file system.

### File Allocation

There are various way to allocate data to files.

- Contiguous allocation: all bytes together in order
- Linked structure: block ends with a `next` pointer
- File Allocation Table *(FAT)*: a table that contains block references. 
This was used in Lab 4.
- Multi-level indexing: tree of pointers

Different approaches have different tradeoffs. It all depends on fragmentation,
sequential access vs. random access, metadata overhead, tailoring to large or
small files, and the ability to adjust file size.

#### Contiguous Allocation

All data blocks of a file are allocated contiguously. Very simple to implement
since only required metadata for reading is start block and file size. Very
efficient as one seek allows for us to read the whole file. However, it can
lead to serious external fragmentation and even more inconvenient, we need to
know file size at the time of creation.

This is great for read-only file systems like CD/DVD/BluRay.

#### Linked blocks

This is great because there is no external fragmentation, and simple to
implement as we only need to find the first block of the file and the rest
will follow. Random access here is slow because there is a high seek cost on
disk *(remember the latency related to rotating to seek new blocks on magnetic
disks)* since data isn't stored contiguously. In terms of implementation, we
need each block to contain both data and metadata - this also introduces
storage overhead as a `next` pointer is required for each block.

#### FAT

The insight here is to decouple data and metadata - we keep the linked list in
a single table *(Lab 4 woohoo)*. This was proposed by Microsoft in the late
70s.

We get great space utilization here *(no external fragmentation)* and decoupling
of data and metadata. Simple implementation once again as we only need to find
the first block of the file for the rest to follow. Performance-wise, we get
pretty bad random access *(as for linked structure, non-contiguous blocks can
introduce latency for storage media)*. 

We also limit outselves in terms of 
metadata - we get many file seeks unless the whole FAT is stored in memory. 
Imagine as an example that we have 1TB $= 2^{40}$ bytes on disk and 4KB block
size. This means that the FAT must have 256 million entries $\rightarrow$
at 4B per entry in FAT32, we get 1GB of required memory for FS. Not practical.

#### Multi-level Indexing

Idea here is to have a mix of direct, indirect, double indirect, and triple
indirect pointers for data.

Each file is a fixed, asymmetric tree with fixed-size data blocks e.g 4KB as
its leaves. The root of the tree is the file's inode which contains metadata
and a set of 15 pointers

- first 12 pointers point to data blocks
- last three point to intermediate blocks, themselves containing pointers
    1. number 13 points to a block containg pointers to data blocks
    2. number 14 double indirect pointer
    3. number 15 triple indirect pointer

The tree-like structure makes it efficient for finding blocks. It is efficient
for sequential reads as once an indirect block is read, it can read 100s of
data blocks. The fixed structure makes it simple to implement and its 
asymmetric structure allows for the support of large files and small files
don't have to pay a large overhead.

We get a reasonable read cost and low seek cost, but the small amount of
metadata requires extra reads for indirect/double indirect access.

***Example:***

Suppose we have a 4KB file size.

If we access through direct pointers, maximum file size allocation is 4KB.

If we access through 3-level indexing, we need end up with 4KB.

- A triple indirect pointer
- A double indirect pointer
- An indirect block
- the 4KB data block.

Reading data requires 5 blocks to traverse the tree.

# Week 13: Journaling

We start by recalling file systems, and introducing some implementation.

## File Operation: Reading from a File

Firstly, we know that the inode of `/` *(root)* is 2. When we call
`open("/cs323/w13/", O_RDONLY)`, what we do is traverse the directory tree
until we get to the inode "w13. We then read the inode, perform a permission
check, and return a file descriptor. Then for each subsequent `read()`,

- read inode
- read appropriate data block *(depends on offset)*
- Update lass access time in inode metadata
- Update file offset in in-memory open file table for the file descriptor.

## File Operation: Writing to a File

Again, we must open the file before we can perform any actions. In this case,
we call `open("/cs323/w13", O_WRONLY)`. When we write, we may need to allocate
new blocks! This means that each write can generate up to five I/O operations:

1. Reading the free data block bitmap
2. Writing the free data block bitmap
3. Reading the file's inode
4. Writing the file's inode to include a pointer to the new block
5. Writing the new data block

If the directory is full, we must allocate new blocks.

## Performance

### Characterizing Performance

We can define performance based on some of the following metrics

- Number of I/O operations
- Speed of individual I/O operation
- Impact on one program
- Impact on all programs

The key metrics are:

- Latency
- Throughput
- I/O operations per second ***(IOPS)***

### Improving Performance

- **Caching:** Avoid unnecessary operations
- **Batching:** Group operations to increase throughput *(could increase
latency)* and delay idempotent operations *(doesn't change after the first 
application)*
- **Add a level of indirection:** Maintain some nice abstraction, enables
performance optimization.

#### Block Cache

When an OS reads the associated block of an inode many times, it may be 
cached in the ***file system buffer cache***. This is a map 
`{ (inode, block_offset): page_frame }`. The `read()` can return without
performing disk I/O.

This cache sits in memory wherever there is free space. This can utilize all
unused memory in newer systems.

This being said, caching blocks does affect data persistence 
*(we can lose data)*. Caching works
great for `read()`s, but it gets tricky for `write()`s. We can write
synchronously, but as we discuss in a paragraph lower down, this isn't good
for performance. *(ideally we want to delay writes and perform them 
asynchronously )*. We come back to this in crach consistency.

#### Batching Operations

I/O is high latency with limited concurrency. Idea is to batch operations
together, allowing for fewer memory operations but that each have large sizes.
This is possible when consecutive blocks on disk belong to the same inode.

We introduce the notion of disk fragmentation, which is a metric that describes
the fraction of inode content on non-consecutive disk locations.

#### Delaying Operations

A process needs to block on a `read()` as it must wait for the data to be
available to it. We don't need to do this for writes. The idea is to delay all
write operations, performing them asynchronously and reorder them to maximize
throughput. The tradeoff is that content will be lost if the OS crashes -
this is because memory operations aren't immediately commited to main memory.

## Crash Consistency

We start by illustrating with an example why consistency in the event of a crash
is important.

### Example: Updating a Block in a File System

Suppose we append a new data block to a file.

- We add this block `D2`
- We then update the associated `inode`
- We then update the data bitmap

Note that these are all individual writes to the file system. If a crash happens
between any of these operations, the file system will be corrupted. This could
mean any of the following, bearing in mind that the writes could be executed
out of order.

- Inconsistent data/metadata structures *(we write data, but we've given the
file system no way to access it by updating metadata)*
- Inconsistent bitmap state *(marks block as free when it isn't)*
- Inconsistent Data *(if the inode and bitmap updates succeed but the data isn't
written to disk)*

Our goal, ultimately, is to ***atomically*** move file system from one
consistent state to anoher consistent state.

### Possible Consistency Solution: File System Checker

After a certain number of mount operations, or after a crash, check the
consistency of the file system. This can perform hundreds of consistency checks
across different fields, including but not limited to

- Do superblocks match?
- Is the filesystem size "reasonable"
- Are link count equal to the number of directories?

The program `fsck()` has been around since the old UNIX days, and is an example
of a file system checker. Severity of file system corruption led to the phrase
"fsck'ed".

To summarize: Given a file system in consistent state A and a set of writes,
check the resulting state B for correctness.

### Possible Consistency Solution: Journaling

The goal here is to limit the amount of work required after a crash, and to
get correct state instead of just consistent state.

The approach that we take is to turn muliple disk updates into a single write.
To implement this, we *write ahead* a short note to a *log* specifying any
changes that will be made to the file system's data structures. If a crash
occurs while updating these aforementioned data structures, we can consult the
log to determine what fscked up, and what to do. This prevents us from having
to rescan the while disk.

We keep a logbook to maintain significant events, decisions or changes in
course. This basically keeps an archive of the state of the file system at 
different points in time. We can reference this when something goes wrong.

This journal is stored in a special area on disk that stores data in a 
write-ahead fashion. We call it write-ahead logging.

Journaling uses the transactions' atomicity to provide crash consistency
*(recall cs307)*.

## Principles of Transactions

We spoke about the three rules of atomicity at the cache-level in cs307 that
were *borrowed* from databases and file systems. There is an additional rule
that is applied to file systems.

1. Atomic: all or nothing
2. Consistent: Brings the system from one correct state to another
3. Isolated: Actions, from their point of view, appear to be the only
entity accessing the resources; they never interfere with each other.
4. Durable: Once completed, effects are persistent.

We call these **ACID** principles sometimes because catchy. 

## Modern File Systems

Multi-level indexing was introduced back in early UNIX days. The early 1990s
saw the introduction of log-structures file systems. The insight was that
because of caching and increased memory sizes, most I/O is mainly writes - not
reads.

Today, modern file systems leverage ideas from log-structures file systems
for metadata operations. An example is ext4 on linux.

### Log Structured File System - Philosophy

Instead of adding a log to the existing disk, use an entire disk as a log.
In here, we buffer all updated *(including metadata)* into an in-memory
segment. When a segment is full, write the disk in a long sequential transfer
to unusued parts of the disk. We never overwrite existing data - only write a 
set of data blocks or segmets to a free location. This improves disk throughput.


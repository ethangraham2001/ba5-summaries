---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS323 Summary for Midterm
author: Ethan Graham
date: \today
---

***
# Week 01: Introduction
## Hardware and OS
Hardware does influenc OS design choices - hardware designers choose what
abstractions to expose to the OS, and OS programmer uses what's available.

The OS's job is to run programs using the provided hardware abstractions.

## Virtualization
First we discuss virtualization...

The operating system uses virtualization to mask the underlying hardware
restrictions giving the illusion of:

- **Dedicated Hardware:** program has exclusive use of resources
- **Infinite Resources**
- **Higher level objects** like files, users, messages, etc...

More concretely, the operating system provides each program with its own
process consisting of

- Threads
- Address space
- Files
- Sockets

## Protection
The operating system isolates threads from each other, and isolates itself from
other programs. This provides

- **Fault isolation**
- **Resource Sharing:** choose which programs execute, and splitting physical
resources between them
- **Communication:** Provides primitives that allows for communication between
processes

Think of segfaults - this only exists in presence of an operating system
keep memory usage in check.

## Abstraction
The operating system provides us with primitives that can be used for 
platform agnostic programming on the assumption that different operating
systems provide these same basic primitives.

We would like to maximize reuse, and decouple hardware and application
development.

# Week 02: Processes
## What is a Process?
A process is an instance of a program in execution. Consists of the following

- **A UID:** called a process id or `pid`
- **A Memory Image:** Code and data *(static)*, stack and heap *(dynamic)*
- **CPU context registers:** Program counter, current operands, stack pointer
- **File descriptors:** pointers to open files and descriptors *(pointer to an open file)*

## Process Memory Layout and Creating a Process

- Stack that grows downwards *(temporary data such as function parameters, local vars, 
return addresses)*
- Heap that grows upwards *(used for dynamic memory allocation during runtime)*
- Data segment *(static, known at compile time. Allocates global vars and data structures)*
- Read-only text segment *(contains code and constants. Program executable
machine instructions)* 

When the OS creates a process, allocates the required memory regions, initializes
IO (`stdin`, `stdout`, `stderr`), transfers CPU control to the program's entry
point such as the `main()` function.

## Program vs. Process vs. Thread

- A **program** is an executable file on disk.
- A **process** is a running instance of a program.
- A process can consist of multiple **threads** in the same address space working
on the same address space

## Sharing is Caring

- **Time Sharing:** running one task at a time and quickly switching among
other tasks 
- **Space Sharing:** each task gets a portion of the available space

## Process State Transition
A process can be in one of three states during its life cycle

- **Running:** currently executing instructions
- **Ready:** ready to run, but waiting for green light from OS
- **Blocked:** currently not available until some kind of operation allows it

## Process API
The operating system provides a set of interfaces *(syscalls)* to create and
manage processes.

- `fork()`: executes a child process, which is a copy of the parent process
- `exec()`: executes a new program
- `exit()`: terminates the current process
- `wait()`: blocks the current process until the child terminates

This is but a subset of complex process APIs

### `fork()`
Parent process calls `fork()` to create a copy of itself called the child, 
which will have a different PID. It returns an integer value `pid`

```C
int pid = fork();
if (pid == -1) {
    // an error has occured. We Are in parent process and child is not created
} else if (pid > 0) {
    // we are still in parent process, but child was created. pid == child_pid
} else if (pid == 0) {
    // child created successfully and we are in child process
}

```

The operating system allocates all data structures required for child process,
copies all of the caller's memory *(address space)*. Copies everything else
such as file descriptors etc...

At the end of a successful call, the child process is in `READY` state. Both
parent and child **execute in their own copy of the address space**. `fork()` is
implemented by the operating system.

### `exec()`
After `fork()`, both parent and child execute the same program. If we want to
execute a different program, we call `exec()`.

It replaces the old program image with a new program image. *Note: only the
child process's image is replace - the parent process is untouched by this call*

### `wait()`
A parent process uses `wait()` to suspend its execution until one of its children
terminates. The parent process then gets the exit status of the terminated child.

```C
pid_t wait(int *wstatus);
```

If no child is running, then the `wait()` call has no effect. Otherwise it will
suspend the caller process until the termination of one of the children. This
function returns the pid of the terminated child process.

### `exit()`
When a process terminates, it calls this function. *(either directly or via library call)*

```C
void exit(int status);
```

Calling this function resumes execution of a waiting process.

## Waiting for Children to Die uWu
There are two scenarios in which a process is terminated 

- By suiciding itself with `exit()`
- Operating system terminates a misbehaving one

A terminated process exists as a zombie. When a parent process calls `wait()`,
the ***zombie child is cleaned up or "reaped"***

If a parent terminates before a child, the child becomes an ***orphan***. In
this case, the `init` process with `pid=1` adopts the ophans and reaps them. This
`init` process has no parent process.

## Notes on the `init` Process
In a basic process, it is created after hardware initialization. The init process
then spawns a **shell** like bash, zsh, etc...

The shell reads user commands, forks a child *(wtf Sanidyha)*, execs the command
executable, waits for it to finish, and reads the next command.

The shell can do arbitrarily complex things, like redirect output to a `.txt` file.

```console
$ ls > foo.txt
```
Here, `ls` is the program.

# Week 03: Protection
When multiple processes want to access shared and limited resources on a 
system, the OS is the last line of defense - ensuring security, privacy, and the
hardware against unfavorable resource utilization.

## Recall: Sharing is Caring
We introduced the notions of time sharing and space sharing. Given that processes
want to each run with the illusion that they have exclusive CPU and memory access,
but that in reality they are both running on the same resources, there has to be some
sharing. We defined

- Time Sharing
- Space Sharing

In reality, 

- **CPU is time shared** alternating between tasks
- **Memory is space shared**
- **Disk is space shared**

## Circle of Trust
The OS trusts no process for resource management. So how does it execute an
untrusted process *(which is every other process other than itself)*?

The OS should compartmentalize processes properly, so that they can be run
with restricted rights *(such as not being able to modify unallocated resources,
changin behavior of the OS/other processes, obtain sensitive information)*

## Technique 1: Limited Direct Execution
This technique allows the process to execute as fast as possible with some 
restrictions. The OS simply sets up state, allows the process to execute
(for example `main()` entrypoint) and then cleans up associated resources
after the execution is finished.

The problems with this are:

- How do I stop the process from running privileged code?
- How do I get control back, which is required for virtualization?

To remedy these problems, we use provided hardware protection.

## User Mode and Kernel Mode
Hardware uses rings to execute processes with various modes of execution. Most
notably

- **Kernel mode (ring 0):** the CPU executes instructions without any checks.
Everything goes.
- **User mode (ring 3):** each instruction is checked before execution. Only a
limited number of instructions are allowed. 

A user-mode process can request access to resources with a syscall. This syscall
gives execution back to the operating system temporarily

To execute a syscall, the OS executes a special **trap instruction** that makes
the CPU jump into **kernel mode** allowing operations to be performed. When
finished, the OS calles a **return-from-trap instruction** moving back to user
mode. Privileged operations can no longer be performed.

## Syscalls (But with More Detail)
A syscall is just a trap instruction btw

- OS saves registers to **per-process stack**
- changes from ring 3 to ring 0
- Executes juicy privileged instructions
- changes back from ring 0 to ring 3
- Restores the process state by popping from the per-process stack

Traps are also refered to as ***exceptions*** and are synchronous (i.e. invoked
only after the CPU has terminated the invokation of a previous instruction)

## Trap Entries on the Trap Table
During boot, the OS configures the **trap table** with **trap entries** that
tell the hardware what to do in the case of exceptional events. The hardware
will then know what to do in the case that these events occur.

Each syscall has a specified number. The process places this number (related
to the syscall) in a special register that will be checked by the OS for validity
before executing the corresponding syscall code.

$$
trap \equiv exception
$$

## Interrupts for Regaining Control
We know what interrupts are for this point. Since we don't know that a process
is necessarily going to try some illegal action or make a syscall, we can't
guarantee that the OS will regain control over execution.

What we do is that we set a timer within the CPU that sends out an interrupt,
switching it from user mode to kernel mode. ***This is called context switching***.
In the Linux kernel, the CPU takes back control every 10ms.

Note that interrupts are disabled during the execution of an interrupt handler.

# Week 04: Scheduling
An **OS scheduler** is the mechanism used for stopping one process and starting
another. We define two distinct types:

- **Non-preemptive:** Polite ones that switch only when a process is blocked
- **Preemptive:** Can switch even if the process is ready to continue execution.
This ensures that the OS has control

## Context-Switching
Recall that **context-switching** is the term that we use to refer to changing
from one process to the next *(stopping one, starting another)*.

This involves storing the state of the current process state and switching to 
another previously stored context. The process state is represented in the 
***process control block (PCB)*** *(this includes hardware registers that are
stored)*

### Context-Switch Procedure

1. **Save** the process execution state in the PCB
2. **Select** the next thread
3. **Restore** the execution state of the next process 
4. **Passes** control using *return from trap*

The PCB is just a data structure associated with each process.

## Scheduler Implementations
We note in passing that most kernels have a low priority process called the
idle process that is scheduled when there are no other processes to schedule.

Two terms to define before listing off specific scheduler implementations

- **Utilization:** What fraction of time is CPU executing a job. We want to
maximize CPU usage for best efficiency.
- **Turnover Time:** Total time from job arrival to job completion. We want to
minimize turnover time.
- **Response Time:** How long until a job that arrives is scheduled

### FIFO Scheduler *(first in, first out), non-preemptive*
This works reasonably well if we assume that all jobs arrive at the same time
*(an unrealistic assumption)*. However, if a long-latency job arrives first, 
then all jobs arriving at the FIFO afterwards end up waiting for this job to finish.
The avg. turnover time suffers as a result, with the first job dominating
execution time.

### SJF Scheduler *(Shortest Job First), non-preemptive*
If we know the execution times of the jobs that are going to be scheduled, 
then we can schedule the shortest ones first to minimize the avg. turnover time.
Again, this is unrealistic since irl we don't execution time before executing a job.
However, long-executing jobs can't be interrupted and therefore if they arrive
first, this is just as bad as FIFO since the short-execution jobs will have to
wait for them to finish.

Putting the unrealism aside, this scheduler implementation performs better than
FIFO in terms of avg. turnover time.

### STCF Scheulder *(Shortest time to completion), preemptive*
This simply extends SJF by adding preemption. Every time a new job enters the 
system

1. Determine which of the remaining jobs, including new one, has the least time
left.
2. Schedule the shortest job first.

This addresses the issue that is caused when a long job arrives to the queue
first and blocks the short ones. This improves the average turnover time of
SJF.

Until now we only optimized for turnover time, which STCF does well. However,
STCF is shit at response time which has become more important *(for example for
video games, etc...)*

### RR Scheulder *(Round Robin), preemptive*
Instead of running jobs to completion, run them for a fixed time interval, and
then switch to the next `READY` job in the queue.

In a lot of cases RR has better response time than STCF, but worse turnover time.
RR is a fair policy since it evenly divides CPU time among `READY` processes. 

If we now also consider **IO** as something that schedulers need to handle, then
RR works well as it can overlap IO and CPU, leading to better CPU utilization

### MLFQ *(multi-level feedback queue), preemptive*
The goal is to support general purpose scheduling, supporting both long running
background *(batch processing)* and low latency foreground tasks *(interactive
processing)*. The response time isn't important for the first, but is for the 
second.

MLFQ first optimizes turnaround time *(important for batch processes)*, then
optimizes response time *(important for interactive processes)*. We have a 
set of rules that adjusts priorities dynamically.

1. `if priority(A) > priority(B)`, then run `A`
2. `if priority(A) == priority(B)`, then run `A`, `B` in RR
3. Processes start at the top priority
4. If process `A` uses up its total time slice, the scheduler lowers its priority.
5. Periodically move all processes to the topmost priority *(priority boosting)*.
This avoids starvation. We do this after every *boosting window* which can be,
for example, 50ms

# Week 05 Memory Virtualization
We already went over the structure of a process's memory

- Call stack for temporary data
- Heap for dynamic allocation
- Data segment known at compile time
- Read-only text segment

We will go more in depth now

## Stack
FILO data structure with `push` and `pop` operations. When a function is called,
an ***invocation frame*** is allocated that stored all local variables and the
necessary context to run the function that has been called *(callee)*

### Example 1
```C
void func()
{
    int x; 
}
```
All the work here is done statically by the compiler, which is local to the
function run by a process. It allocates and deallocates space in the stack
segment. In this example, we need to store `x` in the invocation frame of
`func`.

### Example 2
```C
int called(int a, int b)
{
    int tmp = a * b;
    return tmp / 42;
}

void main(int argc, char *argv[])
{
    int tmp = called(argc, argv);
}
```
What is stored in the invocation frame? Here we have

- slot for `tmp`
- slot for parameters `a`, `b`
- slot for the return code pointer `RIP`

The order of the stack is thus `b`, `a`, `RIP`, `tmp` (because FILO).

## Heap
We want to be able to allocate memory at runtime, and then indicate when it is
no longer being used. For this we use `alloc` and `free`

We implement it by abstracting the heap into objects called free blocks. To
allocate, we find a fitting object

- **First fit:** Find the first object that fits and split it
- **Best fit:** Find that object that is closest in size
- **Worst fit:** Find the largest object and split it

To free, we merge adjacent blocks.

The heap is managed by a user-space library like `glibc`

### Interaction with OS
The operating system gives the process a large memory region to store heap
objects (`sbrk()`, `mmap()` syscalls to allocate memory).

## Example Putting it all Together

```C
int g;
int main(int argc, char* argv[])
{
    int foo;
    char *c = (char*)malloc(argc*sizeof(int));
    free(c);
}
```

- **stack:** `foo`, `c`
- **heap:** `*c`
- **data:** `g` *(global variable)*
- **text:** `main()` *(since it is code)*

## Virtual Memory
We give every process virtual memory. Addressing starts at `0x0`. Every virual
address maps to a physical address, and the process resides somewhere else in
physical memory.

### Basic System Design Concepts

- **Indirection:** use an intermediate layer to access/manipulate data/resources
without directly interacting with them
- **Batching:** Group operations together to amortize cost
- **Caching:** Store data locally for faster access

## Memory Management Unit
Only the operating system is allowed to configure the MMU. We don't allow any
processes to modify it, and we prevent this by allowing MMU to be managed only
by processes running in ring 0.

Exceptions in user space *(for example illegal memory accesses)* result in a 
trap, switching to kernel mode, and being handled by the OS.

### Simple MMU: Base Register
Idea: translate every virtual address to physical address by adding an offset.
We store this offset in a special register *(controlled by the OS, used by MMU)*.
Each process has a different offset in their base register

In this model, a process can still access memory associated to other processes.

### Simple MMU *(but better)*: Base and Bounds
Like in the previous example we add a base, but this time we also add bounds to
prevent accessing illegal memory addresses. Pseudo code to illustrate:

```c++
if (addr < bounds)
    return *(base + addr)
else
    throw new SegFaultException();
```

The pros of this method is that it is cheap *(performance)* and isolates processes
*(security)*

However, it completely rules out memory sharing, and wastes physical memory since
it must all be allocated statically. It results in **memory fragmentation**,
which is inefficient. 

We define both internal and external fragmentation.

- **Internal:** The allocated memory is slightly larger than the required memory,
and some memory goes unused.
- **External:** We have enough available memory in total, but it isn't contiguous
and therefore we can't allocate it as desired *(good example on slide 61)*

### MMU: Segmentation
One base and bound register per memory area. This allows processes to have
several regions of continous memory mapped from virtual address space to 
physical address space. The OS can place segments independently anywhere in
physical memory *(unlike for base and bound where memory must be contiguous)*

As a result, we minimize memory waste.

To share segments, we mark it using protection bits *(read, write, execute)*
to let other processes know that it is shared.

We define different segment types with different usages:

- Code Segment $\rightarrow$ `CS` register
- Data Segment $\rightarrow$ `DS` register
- Stack Segment $\rightarrow$ `SS` register
- User-defined extra segents $\rightarrow$ `ES`/`FS`/`GS` registers

#### Issues
Each segment must be backed by physical memory. Although fragmentation is 
decreased, it still occurs since hardware needs to allocate enough physical memory 
for every segment *(e.g. stack and heap still need to be large enough)*

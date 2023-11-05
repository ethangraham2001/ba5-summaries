---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS323 Summary for Midterm
author: Ethan Graham
date: \today
---

***
# Week 01: Introduction
*(With Indian Accent)*

OS's are cool and are used everywhere and all. Motherchod

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

It replaces the old program image with a new program image.

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
then spawns a shell like bash, zsh, etc...

The shell reads user commands, forks a child *(wtf Sanidyha)*, execs the command
executable, waits for it to finish, and reads the next command.

The shell can do arbitrarily complex things, like redirect output to a `.txt` file.

```console
$ ls > foo.txt
```
Here, `ls` is the program.

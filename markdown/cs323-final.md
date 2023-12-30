---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: CS323 Summary for Final (Weeks 7 to 14)
author: Ethan Graham
date: \today
---

# Week 07 Paging

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




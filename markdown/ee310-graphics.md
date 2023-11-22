---
title: EE-310 Graphics Notes
author: Ethan Graham
date: \today
---

# Overview
There are two graphics modes on the NDS: ***MAIN*** and ***SUB***. There are
also 9 VRAM banks from A to I with different sizes. We choose to assign
different banks to different modes.

## `REG_POWERCNT - 0x4000304`
Configured with default settings at system boot-up. Activating LCD engines can
be done with

```C
// activating the graphics subsystem
REG_POWERCNT = POWER_LCD | POWER_2D_A;

// deactivating
REG_POWERCNT &= ~(POWER_LCD) & ~(POWER_2D_A);
```

## `VRAM_X_CR`
This register is for controlling individual VRAM banks.

Bits $[0 \dots 2]$ are for setting the graphics mode, 
and bit $7$ is for enabling the VRAM bank. We don't want to be using too many,
so we should disable any banks not being used.

Example of enabling and setting up vram bank:

```C
// enable vram bank A and maps it to LCD
VRAM_A_CR = VRAM_ENABLE | VRAM_A_LCD;
```

## `REG_DISPCNT`
Used to control mode and active backgrounds. For example:

```C
/* 
    activate mode 0 2D (background 0 will be tiled, not 3d)
    activate backgrounds 1 and 3
*/
REG_DISPCNT = MODE_0_2D | DISPLAY_BG1_ACTIVE | DISPLAY_BG3_ACTIVE;
```

## Framebuffer Mode
This is a special mode where we basically make VRAM a bitmap of whatever we want
and display it on the screen. Note that it is only available on the top display.

This mode requires loads of VRAM, and thus are mapped to the 128KiB VRAM branks
`VRAM_A`, ..., `VRAM_D`. Here's an example of activating `VRAM_A` for use with
framebuffer mode 0.

```C

REG_DISPCNT = MODE_FB0;
VRAM_A_CR = VRAM_ENABLE | VRAM_A_LCD;
```

## Rotoscale Mode
We configure this mode with several different registers

- `REG_POWERCNT`: like before we need to make sure the displays are turned on.
- `VRAM_X_CR`: We need to configure VRAM.
- `REG_DISPCNT`: Configure graphics engines
- `BGGTRL[n]`: Set bitmap base address, background size, pixel *configuration
(8 or 16 bits color mode)*
- `BG_PALETTE[0...255]`: initialize palettes when using 8-bit mode.

## Palettes
We can create a palette of 16-bit colours, and then the display references
these colours. What this means is that the display only has to store, for each
pixel, a reference to the palette colour. If we have 256 16-bit colours in the
palette, we have to store $log_2(256) = 8$ bits in each pixel, which is half
as much. 

Palettes are stored in a special palette ram that has a size of 
2KB.

```C
// palette initialization example
for (int i = 0; i < 32; i++)
    myPalette[i] = ARGB16(1, 0, 0, i);
```



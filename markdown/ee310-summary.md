---
geometry: left=2cm, right=2cm, top=2cm, bottom=2cm
title: EE310 Brief Summary of NDS Programming
author: Ethan Graham
date: \today
---

# Week 01
Introduction on embedded systems. Nothing technical in particular.

## Course Evaluation
The LibNDS library used for development in this course is subject to questions
in the midterm and in the final oral exam. Essential that its usage is
understood.

The course has one midterm exam that counts for **35%** and one final exam
that counts for **65%**.

# Week 02

## NDS Architecture

- **2 CPUs:** One ARM9 and one ARM7
- **4MB main memory**
- **656KB VRAM**
- Seventeen 16-bit and eight 32-bit buses

We have to be conservative when programming or the NDS due to the hardwre
constraints.

## Compiling C code with LibNDS

- The compilation from `.c` to `.o` is handled by `arm-eabi-gcc`
- Linking is done from `.o` to `.elf` is handled by `eam-eabi-ld` and
`arm-eabi-objcopy`. This creates one arm9 executable, and one arm7 executable.
- Building to a `.nds` file is done by `ndstool`.

Some libraries are implemented for the target platform. For example, the NDS
has its own implementation of the `printf()` function. This makes it so that
*Hello, world!* will be displayed on the screen.

```C
int main(void)
{
	consoleDemoinit();
	printf("Hello, world!");	// displayed on the sub screen
}
```

# Week 03 - ARM
ARM stands for "Advanced RISC Machine". Not super important to know how to
write ARM assembly for this course. Perhaps for the final project it will
be useful.

# Week 04 - IO

## Interrupts
We configure an ***exception vectors table*** in hardware so that when an 
interrupt is triggered, the hardware knows what instructions to execute. There
is a priority decoder in hardware that decides how to rank the priority of
different interrupts so that it knows which order to execute the handlers in.
This priority decoder is also configurable by the programmer.

## Handling Interrupts in NDS

### Potential Sources of Interrupts
There are 25 sources in total.

- 2 Graphics-related
- 4 Timers
- 4 DMAs
- Keypad
- GBA Flashcard
- FIFO
- DS Card
- GFX FIFO
- Power Management
- SPI
- WIFI

And some more. Here are what they are called in the `libnds` library, which
can all be located at `/opt/devkitPro/libnds/include/nds/interrupts.h`

- `IRQ_VBLANK`: Vertical Blank
- `IRQ_TIMERi`: Timer $i$, $i = 0, 1, 2, 3$
- `IRQ_KEYS`: Keypad
- `IRQ_WIFI`: WiFi
- `IRQ_DMA0`: DMA 0

### Actually Handling Interrupts
First, we initialize the interrupts subsystem *(initialize peripherals*).
```C
void irqInit();
``` 

Then we need to specify which handler will be used for the given interrupt.

```C
void irqSet(IRQ_MASK irq, VoidFunctionPointer handler); // set handler
void irqClear(IRQ_MASK irq); 				// clear handler
```

After we've set the handler for that `IRQ_MASK` we can enable it. Note,
we should always do this afterwards or else we will experience undefined
behavior.

```C
void irqEnable(uint32 irq);  // enable irq
void irqDisable(uint32 irq); // enable irq
```

### Example Program
```C
void keys_ISR()
{
	printf("a key was pressed!\n");
}

int main(void)
{
	irqInit();						// initialize irq subsystem
	irqSet(IRQ_KEYS, &keys_ISR);	// set handler for keypad
	irqEnable(IRQ_KEYS);			// must be after irqSet!!!

	// ... some other stuff

	irqDisable(IRQ_KEYS);			// disable irq (before clear!)
	irqClear(IRQ_KEYS);				// remove the handler
}
```

## Timers
As mentioned previously, there are four timers available in the NDS. Here
are some macros provided by `libnds` that help us deal witih them.

- `TIMER_CR(n)`: Returns a de-referenced pointer to the timer control register n
- `TIMER_DATA(n)`: Returns a de-referenced pointer to the timer data register n
- `TIMER_ENABLE`: Enable the timer
- `TIMER_DIV_VALUE`: Timer will count at $\frac{33.514}{VALUE}$ MHz. Here, value
can take on the values $1, \; 64, \; 256, \; 1024$.
- `TIMER_FREQ_VALUE(freq)`: Set up the register value to start and overflow each
$\frac{1}{freq}$ seconds. Here, `value` can be $64, \; 256\; 1024$.
- `TIMER_IRQ_REQ`: Timer will request an interrupt on overflow.

### Example
```C
// set up control register for timer 0
TIMER_CR(0) = 	TIMER_ENABLE | 		// enable this timer 
				TIMER_DIV_64 | 		// timer counts at 33.514/64 MHz
				TIMER_IRQ_REQ; 		// this timer will get triggered on overflow

// set up data register for timer 0
TIMER_DATA(0) = TIMER_FREQ_64(125); 	// set up starting point
```

Note here that the data register with a starting point that will trigger an
overflow every $\frac 1 125 = 0.008$ seconds. We have to specify the correct
frequency value or else the starting point won't be configured correctly.

### Tradeoff
The higher the frequency, the higher the accuracy. But this also means that
we can't count for as long. We should always opt to choose the highest 
frequency that counts for as long as we need.

# Week 05 - Framebuffer Mode

## Brief Introduction on the Graphics Subsystem

### VRAM Banks
In the DS, there are a total of 9 VRAM banks of different sizes; ranging from
128KB down to 16KB.

### Graphics Control Registers Used in Framebuffer Mode
- `REG_POWERCNT`: Initialized with default settings on system boot
- `REG_DISPCNT`: Configure graphics mode
- `VRAM_x_CR`: Activate VRAM banks, and configure them



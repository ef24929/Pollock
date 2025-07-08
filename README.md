# Pollock

A Python assembler that converts stack-based assembly code into visual representations stored as PNG images. Pollock encodes assembly instructions as RGB pixel values, creating a unique visual programming format.

## Overview

Pollock transforms assembly-like source code into PNG images where each pixel represents program instructions. The RGB values of pixels encode different operations, creating a visual representation of executable code.

## Features

- **Stack-based assembly language** with 27 different operations
- **Visual code representation** as PNG images
- **Label support** for jumps and references (up to 7 characters)
- **Configurable cell size** for output images
- **Multiple output formats** (PNG image or text bytearray)
- **Comprehensive error handling** with optional silent mode

## Installation

Requires Python 3.x with the PIL (Pillow) library:

```bash
pip install Pillow
```

## Usage

```bash
python pollock.py <filename> [options]
```

### Command Line Options

- `-d, --dryrun`: No output generated (validation only)
- `-b, --bytearray`: Output text bytearray instead of PNG
- `-s, --silent`: Silent run with no warnings or errors
- `-c, --cellsize <size>`: Set pixel cell size (2-50, default: 10)
- `-o, --output <name>`: Specify output filename (default: source filename)

### Examples

```bash
# Basic compilation
python pollock.py program.pol

# Compile with larger cells
python pollock.py program.pol -c 20

# Dry run for validation
python pollock.py program.pol -d

# Output as text array
python pollock.py program.pol -b
```

## Assembly Language

### Supported Operations

#### Stack Operations
- `push<value>` - Push value onto stack (0-127 or label reference)
- `pop` - Remove top stack element
- `swap` - Swap top two stack elements
- `dup` - Duplicate top stack element
- `rot` - Rotate top three stack elements

#### Arithmetic Operations
- `add` - Add top two stack elements
- `sub` - Subtract top two stack elements
- `mul` - Multiply top two stack elements
- `div` - Divide top two stack elements
- `rem` - Remainder of division
- `neg` - Negate top stack element

#### Logical Operations
- `not` - Logical NOT
- `or` - Logical OR
- `and` - Logical AND
- `gt` - Greater than comparison
- `eq` - Equal comparison
- `lt` - Less than comparison

#### Bitwise Operations
- `shl` - Shift left
- `shr` - Shift right

#### Control Flow
- `jmpz` - Jump if zero
- `jmpnz` - Jump if not zero
- `halt` - Stop execution

#### I/O Operations
- `outc` - Output character
- `outi` - Output integer
- `inc` - Input character
- `ini` - Input integer

#### Special Operations
- `nop` - No operation
- `pusha` - Push stack top to Alpha channel
- `waita` - Wait for Alpha channel

### Labels and References

Labels can be up to 7 characters long (capital letters and digits):
```assembly
START:  push10; push20; add
        jmpz END
        push42; outc
END:    halt
```

Label slicing is supported for accessing different parts of label addresses:
- `push<LABEL>_1` - Bits 0-6
- `push<LABEL>_2` - Bits 7-13  
- `push<LABEL>_3` - Bits 14-20
- `push<LABEL>_4` - Bits 21-27

### Syntax Rules

- Each line can contain multiple operations separated by semicolons
- Comments start with `#` and extend to end of line
- Empty lines are ignored
- Labels end with `:` and must be on the same line as operations
- Operations are case-sensitive

### Example Program

A simple three channel program.
```assembly
# Simple calculator program
push 0; push 0; push 0
push 1; waita;  waita
pusha;  push 1; push 1
halt;   shl;    shl
nop;    pusha;  outi
nop;    halt;   halt;
```

## Image Format

The generated PNG encodes program metadata and instructions:

### Header Format
- **First pixel**: `[major_version, minor_version, cellsize]`
- **Second pixel**: `[tnol_high, tnol_mid, tnol_low]` where tnol = total number of lines - 2

### Instruction Encoding
Each subsequent pixel represents one line of assembly code with RGB values encoding up to 3 operations per line.

## File Structure

The program creates a square or rectangular grid of colored cells where:
- Each cell represents one line of assembly code
- Cell size is configurable (2-50 pixels)
- Default background color is RGB(188, 188, 188)
- Grid dimensions are calculated to accommodate all instructions

## Error Handling

Pollock provides comprehensive error checking:
- Invalid operations are converted to `nop`
- Out-of-range push values default to 0
- Undefined labels cause compilation errors
- File length limits prevent overflow (2^24 - 2 lines max)

## Version

Current version: 1.0

## License

GPL-3.0 license

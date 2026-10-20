"""Build the CWCheat file for Persona (PSP, ULUS10432) native turbo.

Holding the PSP Note button (map any key or pad button to it in PPSSPP) runs several game
frames per displayed frame. Game logic steps once per frame, so gameplay speeds up while the
music, streamed on its own thread, keeps normal speed and pitch. On a skipped frame the buffer
swap is skipped too and the pad read reuses the last sample instead of blocking for the next
vblank. Frame start chooses the draw buffer from the frame counter's parity, which skipped
frames would break, so it draws into whichever buffer is not on display instead.

Requires: Python 3 and keystone-engine (pip install keystone-engine).
usage: build_cheat.py [OUT.ini]
"""
import struct, sys
import keystone

STATE = 0x08800000      # +0 speed in tenths (<=10 normal), +4 accumulator, +8 frame skipped,
                        # +0x10 last pad sample, +0x20 saved ra, +0x24 saved a0
TURBO = 25              # default speed in tenths
SPEEDS = (15, 20, 25, 30, 35, 40, 45, 50)
NOTE = 0x00800000

WAIT_CAVE = 0x08800100
WAIT_SITE = 0x08805854  # jal sceDisplayWaitVblankCB in the frame flip routine
WAIT = 0x08981194
SWAP_CAVE = 0x08800180
SWAP_SITE = 0x0880585C  # jal sceGuSwapBuffers right after the wait
SWAP = 0x089752DC
CTRL_CAVE = 0x088001C0
CTRL_SITE = 0x088051E4  # jal sceCtrlReadBufferPositive in the input poll
CTRL = 0x08981164
# Frame start picks the draw buffer (0 or 0x88000) from the frame counter's parity, which skipped
# frames break; draw into whichever buffer is not on display instead.
PARITY = 0x088055B4     # lw a0,0x5804(v0) .. ori s1,v0,0x8000
GU_DISP = 0x08B9ED80    # GU context +0x30: display buffer offset
OTHER_BUFFER = 0x88000
GUARD = (0x088051E8, 0x57F8)  # low half of the store in CTRL_SITE's delay slot

# Wait for vblank only when the accumulator says a displayed frame is due.
WAIT_SRC = f"""
    .set noreorder
    lui   $t0, 0x0880
    lw    $t1, 0($t0)
    slti  $t2, $t1, 11
    bnez  $t2, wait
    lw    $t3, 4($t0)
    addiu $t3, $t3, 10
    slt   $t2, $t3, $t1
    beqz  $t2, dowait
    li    $t2, 1
    sw    $t3, 4($t0)
    sw    $t2, 8($t0)
    jr    $ra
    move  $v0, $zero
dowait:
    subu  $t3, $t3, $t1
    sw    $t3, 4($t0)
wait:
    j     {WAIT:#x}
    sw    $zero, 8($t0)
"""

SWAP_SRC = f"""
    .set noreorder
    lui   $t0, 0x0880
    lw    $t1, 8($t0)
    bnez  $t1, skip
    nop
    j     {SWAP:#x}
    nop
skip:
    jr    $ra
    nop
"""

# Real read after a vblank: take Note out of the buttons, set the speed from it, cache the sample.
# After a skipped vblank: return the cached sample instead of blocking.
CTRL_SRC = f"""
    .set noreorder
    lui   $t0, 0x0880
    lw    $t1, 8($t0)
    bnez  $t1, cached
    sw    $ra, 0x20($t0)
    jal   {CTRL:#x}
    sw    $a0, 0x24($t0)
    lui   $t0, 0x0880
    lw    $a0, 0x24($t0)
    lw    $ra, 0x20($t0)
    lw    $t1, 4($a0)
    lui   $t2, {NOTE >> 16:#x}
    and   $t3, $t1, $t2
    xor   $t1, $t1, $t3
    sw    $t1, 4($a0)
    li    $t2, 10
    li    $t4, SPEED
    movn  $t2, $t4, $t3
    sw    $t2, 0($t0)
    lw    $t1, 0($a0)
    sw    $t1, 0x10($t0)
    lw    $t1, 4($a0)
    sw    $t1, 0x14($t0)
    lw    $t1, 8($a0)
    sw    $t1, 0x18($t0)
    lw    $t1, 12($a0)
    jr    $ra
    sw    $t1, 0x1C($t0)
cached:
    lw    $t1, 0x10($t0)
    sw    $t1, 0($a0)
    lw    $t1, 0x14($t0)
    sw    $t1, 4($a0)
    lw    $t1, 0x18($t0)
    sw    $t1, 8($a0)
    lw    $t1, 0x1C($t0)
    sw    $t1, 12($a0)
    jr    $ra
    li    $v0, 1
"""


def jal(target):
    return 0x0C000000 | ((target >> 2) & 0x03FFFFFF)


def patches(speed=TURBO):
    """(address, word) pairs: caves first, then the calls into them."""
    ks = keystone.Ks(keystone.KS_ARCH_MIPS, keystone.KS_MODE_MIPS32 | keystone.KS_MODE_LITTLE_ENDIAN)
    out = []
    caves = [(WAIT_CAVE, WAIT_SRC, SWAP_CAVE), (SWAP_CAVE, SWAP_SRC, CTRL_CAVE), (CTRL_CAVE, CTRL_SRC.replace('SPEED', str(speed)), 0x08800300)]
    for addr, src, limit in caves:
        code = bytes(ks.asm(src, addr)[0])
        assert addr + len(code) <= limit, hex(addr)
        out += [(addr + i, w) for i, (w,) in zip(range(0, len(code), 4), struct.iter_unpack('<I', code))]
    parity = bytes(ks.asm(f"""
        .set noreorder
        lui   $a0, {(GU_DISP + 0x8000) >> 16:#x}
        lw    $a1, 0x5824($v1)
        li    $v0, 1
        lw    $s1, {(GU_DISP & 0xFFFF) - ((GU_DISP & 0x8000) << 1)}($a0)
        lui   $a0, {OTHER_BUFFER >> 16:#x}
        ori   $a0, $a0, {OTHER_BUFFER & 0xFFFF:#x}
        movn  $s0, $v0, $a1
        xor   $s1, $s1, $a0
        nop
    """, PARITY)[0])
    out += [(PARITY + i, w) for i, (w,) in zip(range(0, len(parity), 4), struct.iter_unpack('<I', parity))]
    out += [(WAIT_SITE, jal(WAIT_CAVE)), (SWAP_SITE, jal(SWAP_CAVE)), (CTRL_SITE, jal(CTRL_CAVE))]
    return out


def cheat_lines(speed):
    lines = patches(speed)
    assert len(lines) <= 0xFF
    body = [f'_L 0xE0{len(lines):02X}{GUARD[1]:04X} 0x0{GUARD[0] - 0x08800000:07X}']
    return body + [f'_L 0x2{a - 0x08800000:07X} 0x{w:08X}' for a, w in lines]


def cheat(path, speeds=SPEEDS, enabled=TURBO):
    """One cheat per speed; only the default is switched on."""
    with open(path, 'w', newline='\n') as f:
        f.write('_S ULUS-10432\n_G Shin Megami Tensei: Persona\n')
        for sp in speeds:
            f.write(f'_C{int(sp == enabled)} Turbo {sp / 10:g}x (hold Note) - enable only one\n')
            f.write('\n'.join(cheat_lines(sp)) + '\n')


def main():
    cheat(sys.argv[1] if len(sys.argv) > 1 else 'ULUS10432.ini')


if __name__ == '__main__':
    main()

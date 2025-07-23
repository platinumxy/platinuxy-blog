+++
title = "ToasterBirb's Crackmes"
date = '2025-07-23T22:50:35+00:00'
tags = ['Crackme', 'Rev']
topics = ['General']
series = ['Reverse Engineering']
featured = true
weight = 2
+++

One day upon opening [crackmes.one](https://crackmes.one) I spotted a [user](https://crackmes.one/user/toasterbirb) who appeared to have uploaded their back catalogue of crackmes onto the site. Upon inspecting a few I realised that, although not difficult, they all were quite well made and taken as a whole they could be used as a good introduction to some of the many things you need to look out for as well as being a nice introduction to the different ways you can go about reverse engineering challenges.

The suggested way to approach these if you're using them to learn is to have a go at them yourself until you get stuck, read a little bit until you can keep going rinse and repeat until you've solved it!

**Many thanks to [ToasterBirb](https://github.com/toasterbirb) for making the challenges!**

|Name                                        | Difficulty |
|--------------------------------------------|------------|
|[No-standards](#no-standards)               | Easy       |
|[Seer](#seer)                               | Easy       |
|[Jump](#jump)                               | Easy       |
|[Flags](#flags)                             | Easy       |
|[Interrupted](#interrupted)                 | Medium     |
|[Box](#box)                                 | Medium     |


---

## No-standards

```text
Url https://crackmes.one/crackme/6736b3a09b533b4c22bd2b9f
Description

The programming standards have been entirely thrown out this time around. Literally.
Ignore all of the distractions and figure out the correct password. Patching is fine if it helps with the password recovery process. Good luck!
```

After a quick read of the disassembly we can see a function call to `ptrace` Clearly being used to prevent debugging (because the call fails if a debugger is already attached to the running process), patching it to always return `0` lets us connect our debugger.


![image showing the ptrace call](/posts/toasterbirb/no-standards/anti_dbg.png)


Looking through the strings we see our win destination is reached when `res` is `0`.

![Image containing target function](/posts/toasterbirb/no-standards/target.png)

And after ignoring the bogus conditions that are unable to be called we find the two functions responsible for setting `res`.

![Image containing Important calls](/posts/toasterbirb/no-standards/import_funcs.png)

Now we can have a debugger we can set a breakpoint after the first function to find the "magical keycombination" and it seems to be good old `:wq\n`

![Image containing wq](/posts/toasterbirb/no-standards/wq.png)

Sure enough 

![Image containing win state](/posts/toasterbirb/no-standards/win.png)

---

## Seer

```text
Url https://crackmes.one/crackme/68691771aadb6eeafb398fb9
Description
Take your time or skip to the future. Your task is to figure out the magical passphrase. Patching is allowed (and encouraged (and required)).
```
Unsurprisingly this challenge requires patching and, given that it's un-stripped, we can easily see the problem likely lies in the sleeps between `slow_print` 

![slow_print block in the main function](/posts/toasterbirb/seer/slow_print_block.png)

Going to the sleep definition within the `.plt.sec` and patching it to return instead of calling libc implementation we can cause the binary to run without stopping!

![The strings not decrypting properly](/posts/toasterbirb/seer/not_that_easy.png)

Although, upon closer inspection it appears the time difference is used to decrypt the strings.

![time(nullptr) being used in the decryption](/posts/toasterbirb/seer/slow_print.png)

At this point we can do a couple things, the first and probably most sensible thing we could do is work out how `slow_print` works and create a binary ninja plugin that decrypts the strings using the time called to sleep. However, I'm lazy and I realised the xor key is only a byte long and there's only 9 encrypted strings so we can just brute-force them all.

| # | Key | Decrypted String |
|---|---|---|
| 1 | 27 | I can see into the future, but its really far away... |
| 2 | 10 | You could probably help me by speeding up the time a bit |
| 3 | 13 | I don't want things to go too fast though. It might scare the neighbors away. |
| 4 | 52 | Just imagine the things you could achieve if I told you the next correct lottery number... |
| 5 | e1 | Maybe you could buy me binoculars or something. You can see further away with those, right? |
| 6 |    | *There's a couple options for valid decodes, due to its length* |
| 7 | 93 | We could just cheat the system and teleport straight to the end somehow |
| 8 | f4 | Anyhow, I have one question for you. |
| 9 | 9f | And the correct answer to that question will be: `I_HOPE_YOU_DID_NOT_JUST_WAIT_IT_OUT` |

Well, there's the password: `I_HOPE_YOU_DID_NOT_JUST_WAIT_IT_OUT`. Sure enough, plugging that into the program, we find we've solved the challenge.

![Solved challenge](/posts/toasterbirb/seer/solved.png)

*Quick aside, I originally solved the challenge just using the brute force and not patching because I didn't have a new enough glibcxx on hand to run it. So the authors description might need an update :)*

---

## Jump

```text
Url https://crackmes.one/crackme/6869287daadb6eeafb398fec
Description: 
That illegal instruction minefield looks a bit sketch. Can you jump into the middle of it without having anything blow up?
```
Upon opening the binary, I found it to be a hand crafted non-PIE binary with all its logic stored in `_start` followed by a block of `0x0f0b` aka [`ud2` instructions](https://www.felixcloutier.com/x86/ud) broken up by two `0x90` aka `NOP` instructions and some other asm which appears to be the win function 

![Section of hex in the ud2 block](/posts/toasterbirb/jump/nop_instr.png)

Sure enough converting it into a function yields the final target, now we just need to find a way to jump to it.

![Win function](/posts/toasterbirb/jump/win_func.png)

However, turning back to `_start`, the binary appears to do nothing of note and never appears to make any jump we can control. This is why we need to read the ASM. I spotted that the `rsp` register was sneakily being modified to be `0x00401365` meaning that, when the program returned at the end of `_start`, it wouldn't exit, instead it would unwind using the new stackpointer

![ASM of the _start function](/posts/toasterbirb/jump/_start_asm.png)

Having a look at the new stack we see a few functions which each consist of a single instruction followed by a `ret`

![The new stack](/posts/toasterbirb/jump/new_stack_ptr.png)

We can use these to determine the win function's address is encoded with `(win_address - 0x0040114c) << 0x18`. Putting it together we get a final payload of:
```python
from pwn import *
p = process("./jump")
p.recvuntil(b":")
p.send(p32((0x004011be - 0x0040114c) << 0x18))
p.interactive()
```

---

## Flags
```text
Url https://crackmes.one/crackme/686918c6aadb6eeafb398fbd
Description
I like flags. Some very specific types of flags. I also like keygens. I'd like to have a keygen
```

Given that this specifically asks for a keygen I thought it fitting to use it as an excuse to introduce the basics of `angr` (*in addition to the fact that the binary messes up Binary Ninja's auto analysis*). After looking at the strings I found what appears to be the target `Thanks, that's perfect!\n` so I created an `angr` script to find a path to it.
```python
import angr 

proj = angr.Project("./flags", auto_load_libs=False)
state = proj.factory.entry_state()
simgr = proj.factory.simgr(state)

simgr.explore(find=lambda s: b"Thanks, that's perfect!\n" in s.posix.dumps(1))
if simgr.found:
    print(f"Found a solution:  0x{simgr.found[0].posix.dumps(0).hex()}")
else:
    print("No solution found.")
```

---

## Interrupted
```text
Url https://crackmes.one/crackme/686927e0aadb6eeafb398fe7
Description:
How does one interrupt themselves? Figure out a working password!
```
A quick inspection of the main function shows us it maps a `handler` to all possible [signal interrupts](https://en.wikipedia.org/wiki/Interrupt) and then invokes `kill` (*using pid `0` on kill causes it to invoke the provided interupt against all the process in its group*) using each char in the users input as the signal to send.

![Main function](/posts/toasterbirb/interrupted/main.png)

Looking at the signal handler we see it just indexes into the final password using the `signal % 8`, and then sets the aforementioned index to the signals position in the lowercase alphabet. It should be noted though, that it has a well hidden (possibly intended) bug being that `signal` cannot catch `SIGKILL` and `SIGSTOP` meaning any solver needs to avoid inputs that generate them.

![Signal handler](/posts/toasterbirb/interrupted/signal_handler.png)

Checking how the password is validated we see it just requires that the processed password doesnt include any `a`'s (the default state of the processed password) and that each char isnt followed by a char numericly one less than it

![Validate password function](/posts/toasterbirb/interrupted/validate_password.png)

Given its a 7 char password it seems trivial to use `angr` to find a solution. However, the binary has broken sections preventing `angr` from being able to run it. Although It'd be possible to faff around with the binary to fix it, I decided against it for fear of `angr` not playing nice with the signal interrupts.

Instead I opted to translate the logic into the `z3` SAT solver. I broke the programs conditions into into three main blocks (*for notation I used shadow to mean the password that is modified and validated, and password to mean the original user input*):

1. **Indexing**: Every position in the shadow should be updated to something other than `a` by a char in the original password
2. **Valid inputs**:
    - For simplicity I restricted the password to only alphabetic chars
    - An inputed char shouldn't generate a `SIGKILL` or `SIGSTOP`
    - No `a`'s should be put into the shadow by the password
3. **Ordering of the Shadow**: Each position in the shadow should'nt be followed by a char that is one less than it

The first two were fairly trivial to implement

```python
def valid_chars(password:List[BitVecRef]) -> BoolRef:
    modify = lambda x: ((x & 0b11111) % 0x1a) + 0x61
    is_alpha = lambda x: Or(And(x >= 0x61, x <= 0x7a), And(x >= 0x41, x <= 0x5a))
    is_catchable = lambda x: And((x & 0b1_1111) != 9, (x & 0b1_1111) != 19)
    
    constraints = [modify(password[i]) != 0 for i in range(LENGTH)]
    for i in range(LENGTH):
        constraints.append(is_alpha(password[i]))
        constraints.append(is_catchable(password[i]))
    return And(constraints)

def all_indexes_filled(password: List[BitVecRef]) -> BoolRef:
    cons = [Or([(password[j] & 0xF) == i for j in range(LENGTH)]) for i in range(LENGTH)]
    return And(cons)  
```

However the ordering of the shadow was more complex given it at first glance requires sorting the password values using `& 0b1_1111`. However instead you can use implications, so by finding the possible indexes of each password in the shadow we can brute force the ordering

```python
def valid_order(password: List[BitVecRef]) -> BoolRef:
    modify = lambda x: ((x & 0b11111) % 0x1a) + 0x61
    indices = [password[i] & 0b111 for i in range(LENGTH)]
    constraints = [
        Implies(
            And(indices[i] == idx, indices[j] == idx + 1),
            modify(password[i]) != (modify(password[j]) - 1)
        )
        for idx in range(LENGTH - 1)
        for i in range(LENGTH)
        for j in range(LENGTH)
    ]
    return And(constraints)
```

putting it all to gether we get the following code ([see the full code](/posts/toasterbirb/interrupted/solve.py))

*note that we use length to be 8 to prevent the solver breaking when tying to deal with characters in the password that would overwrite an already modified char in the shadow*

```python
LENGTH = 0x8
answer = [BitVec(f'c{i}', 8) for i in range(LENGTH)]
s = Solver()

s.add(all_indexes_filled(answer))
s.add(valid_chars(answer))
s.add(valid_order(answer))

if s.check() == sat:
    m = s.model()
    result = [m[answer[i]].as_long() for i in range(LENGTH)] 
    print("".join([chr(x) for x in result]))
```

to give us a finished solve script

```bash
$ ./interrupted $(python solve.py)
the password was correct!
```

---

## Box
```text
Url https://crackmes.one/crackme/686919d4aadb6eeafb398fc1
Description:
What does the box do and why doesn't it like my keys? Which key do I need to give to it to make it happy?
```

Starting by running the binary we see the following prompt
```text
$ ./box
     +----█
     |
     v
```
Putting pretty much anything in as our input, we get the following:
```
$ ./box
     +---- aaaaa
     |
\/\/\/\/\/\
     |
     +---> The box deems your key either too short or too long
```
Deciding its time to open the binary, and naming some obvious functions, we see the following loop and check suggeting a required key length of `0x40`

![length check](/posts/toasterbirb/box/lengthcheck.png)

Plugging in a key of length `0x40`, we see the following

![Transforms](/posts/toasterbirb/box/transforms.png)

Clearly, the programs deividing the key into a grid, and applying two transforms finally looking for a key of `algakrwumvauugrvppkcppwaqkpatwifqkknaemavqpnuvakptapcgnwgfgadfcc`

The last transform is easy to guess, as it's just an adding two to each char, so reversing that we get `_je_ipuskt_sseptnniannu_oin_rugdoiil_ck_tonlst_inr_naeluede_bdaa` as our new target key

### A side tangent

When reversing originally I nievely assumed the first transform was independent of the inputed key and so i attempted to skip doing any more reverse engineering and instead created a mapping function. I correctly spotted that each pair of two rows was independent of one another and so I sent `0-f` through the program and took the tranformed data and decoded it's mappings
```python
mappings = {"b23dafce89014567".find(c): i for i, c in enumerate("0123456789abcdef")}

answer = [0x00 for _ in range(0x40)]

for i, c in enumerate(map(lambda x: x - 2, map(ord, "algakrwumvauugrvppkcppwaqkpatwifqkknaemavqpnuvakptapcgnwgfgadfcc"))):
    answer[((i // 16) * 16 )+ mappings[i % 16]] = c
print("".join(map(chr, answer)))
```

Sadly however it wasn't that easy with the "solve" giving a garbage output of `_sjeseptkti_u_spn_nirugdoinnua_nnliist_ito_okl_ce_r_bdaaedanlnue` Which, although wrong, does show us that some of the transformation is dependent on the input data, *and we shouldn't always try take the easy way out before more testing*

### Back on track

After stepping through the code dynamiclly I found the function responsible for the first transform shown to the user; It appears to have 5 differnt transforms it uses, and a few checks dependent on the eveness of parts of the data, along with specific functions for indexing into the grid

![transform function with bare bones annotaition](/posts/toasterbirb/box/tranform_bare.png)

Looking at the index functions we can assume (because the grid is 8x8) and the left shift by 4 `ind_2` is indexing by row and `inx_3` is indexing within a row

![index function](/posts/toasterbirb/box/index_funcs.png)

Using this we can simplfy the even and oddness checks to be equivalent of
```python
if grid[0][1] % 2 != 0 or grid[0][7] % 2 != 0:
    transform_4(grid)

if grid[1][0] % 2 == 0 or grid[1][7] % 2 == 0:
    transform_5(grid)
```

Meaning all we have to do is work out what the rest of the functions do. Now only using static analysis would take far more time than I'd like so instead I opted to use `time travel debugging` to visually see the transformation in memory while stepping backwards and forwards through the binary (*This time I carefully watched for any hidden conditionals*)

Starting with the initial state in memory

![init state](/posts/toasterbirb/box/init_state.png)

We then run `transform_1` revealing that it swaps every second row with the one below itself

![transform one](/posts/toasterbirb/box/transform_one.png)

Next `transform_2` swaps each pair of bytes around

![transform two](/posts/toasterbirb/box/transform_two.png)

Then `transform_3` swaps every second byte in every second row with the one down and to its right 

![transform three](/posts/toasterbirb/box/transform_three.png)

Next we get to the first call to `transform_(4|5)` both of which's behaviour is dependent on if something is even or odd respectively. All it is doing is summing the value of an item in the matrix and the one to its right and if its even/odd then swapping the variables

![transform four](/posts/toasterbirb/box/transform_four.png)

and with that we are now able to implement the mixing algorithm in python to check if our understanding and dynamic analysis was correct [click here to see the code](/posts/toasterbirb/box/solve.py).
Sure enough our python implementation manages to create the same outputs as the binary, so all we have to do now is write the inverse and tada we've got the key

```
$ python solve.py
a l g a k r w u
m v a u u g r v
p p k c p p w a
q k p a t w i f
q k k n a e m a
v q p n u v a k
p t a p c g n w
g f g a d f c c

i t _ j u s t _
k e e p s _ s p
i n n i n g _ a
r o u n d _ u n
t i l _ i t _ l
o o k s _ n i c
e _ a n d _ u n
r e a d a b l e

it_just_keeps_spinning_around_until_it_looks_nice_and_unreadable
```
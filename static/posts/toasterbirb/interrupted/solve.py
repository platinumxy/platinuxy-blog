from typing import List
from z3 import *

def valid_chars(password:List[BitVecRef]) -> BoolRef:
    modify = lambda x: ((x & 0b11111) % 0x1a) + 0x61
    is_alpha = lambda x: Or(And(x >= 0x61, x <= 0x7a), And(x >= 0x41, x <= 0x5a))
    is_catchable = lambda x: And((x & 0b1_1111) != 9, (x & 0b1_1111) != 19)
    
    constraints = [modify(password[i]) != 0 for i in range(LENGTH)]
    for i in range(LENGTH):
        constraints.append(is_alpha(password[i]))
        constraints.append(is_catchable(password[i]))
    return And(constraints) # type: ignore

def all_indexes_filled(password: List[BitVecRef]) -> BoolRef:
    cons = [Or([(password[j] & 0xF) == i for j in range(LENGTH)]) for i in range(LENGTH)]
    return And(cons)  # type: ignore

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
    return And(constraints)  # type: ignore

LENGTH = 0x8
answer = [BitVec(f'c{i}', 8) for i in range(LENGTH)]
s = Solver()

s.add(all_indexes_filled(answer))
s.add(valid_chars(answer))
s.add(valid_order(answer))

if s.check() == sat:
    m = s.model()
    result = [m[answer[i]].as_long() for i in range(LENGTH)] # type: ignore
    print("".join([chr(x) for x in result]))
    exit(0)
    
    # Debugging to show the "shadow" copy of the password the program builds to check
    shadow = []
    for i in range(LENGTH):
        idx = (result[i] & 0b111)
        val = ((result[i] & 0b11111) % 0x1a) + 0x61
        shadow.append((idx, val, result[i]))
    shadow.sort(key=lambda x: x[0])
    print("shadow order:", [result.index(x[2]) for x in shadow])
    print("shadow " + "".join([chr(x[1]) for x in shadow]))
else:
    print("No solution found")
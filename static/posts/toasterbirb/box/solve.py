#!/usr/bin/env python3

def swap(g, a, b):
    g[a], g[b] = g[b], g[a]

def mix_row_swap(grid:list[list[int]]):
    for i in range(0, 8, 2): swap(grid, i, i + 1)

def mix_byte_swap(grid:list[list[int]]):
    for row in grid: 
        for i in range(0, 8, 2): swap(row, i, i + 1)

def mix_cross(grid:list[list[int]]):
    for i in range(0, 6, 2):
        for j in range(0, 8, 2):
            grid[i][j], grid[i + 1][j + 1] = grid[i + 1][j + 1], grid[i][j]

def mix_evenness(grid:list[list[int]]):
    for row in grid:
        for i in range(0, 7):
            if (row[i] + row[i + 1]) % 2 == 0: swap(row, i, i + 1)

def mix_oddness(grid:list[list[int]]):
    for row in grid:
        for i in range(0, 7):
            if (row[i] + row[i + 1]) % 2 != 0: swap(row, i, i + 1)

def add_to_grid(grid:list[list[int]], value:int):
    for row in grid:
        for i in range(8):
            row[i] += value
            if row[i] > 255: row[i] -= 256

def mix_grid(grid:list[list[int]]):
    mix_row_swap(grid)
    mix_byte_swap(grid)
    mix_cross(grid)
    mix_evenness(grid)
    mix_cross(grid)
    
    if grid[1][0] % 2 == 0 or grid[1][7] % 2 == 0:
        mix_evenness(grid)
    
    if grid[0][1] % 2 != 0 or grid[0][7] % 2 != 0:
        mix_oddness(grid)
    add_to_grid(grid, 2)
    return grid


def reverse_evenness(grid:list[list[int]]):
    for row in grid:
        for i in range(7, 0, -1):
            if (row[i] + row[i - 1]) % 2 == 0:
                row[i], row[i - 1] = row[i - 1], row[i]
                
def reverse_oddness(grid:list[list[int]]):
    for row in grid:
        for i in range(7, 0, -1):
            if (row[i] + row[i - 1]) % 2 != 0:
                row[i], row[i - 1] = row[i - 1], row[i]
                
def reverse_cross(grid:list[list[int]]):
    for i in range(6, -1, -2):
        for j in range(6, -1, -2):
            grid[i][j], grid[i + 1][j + 1] = grid[i + 1][j + 1], grid[i][j]
                
def reverse_grid(grid:list[list[int]]):
    from copy import deepcopy
    add_to_grid(grid, -2)
    test_grid = deepcopy(grid)
    reverse_oddness(test_grid)
    if test_grid[0][1] % 2 != 0 or test_grid[0][7] % 2 != 0:
        reverse_oddness(grid)
    
    test_grid = deepcopy(grid)
    reverse_evenness(test_grid)
    if test_grid[1][0] % 2 == 0 or test_grid[1][7] % 2 == 0:
        reverse_evenness(grid)
        
        
    reverse_cross(grid)
    reverse_evenness(grid)
    reverse_cross(grid)
    mix_byte_swap(grid)
    mix_row_swap(grid)


def parse_grid(input_str:str):
    lines = list(map(ord, input_str.strip()))
    grid = []
    for i in range(0, len(lines), 8):
        row = lines[i:i + 8]
        grid.append(row)
    return grid

def grid_to_string(grid:list[list[int]]) -> str:
    return '\n'.join(' '.join(chr(num) for num in row) for row in grid)

def show_key(grid:list[list[int]]):
    return "".join(''.join(chr(num) for num in row) for row in grid)

#grid = parse_grid("0123456789abcdef" * 4)
#print(grid_to_string(grid), end= "\n\n")
#mix_grid(grid)
grid = parse_grid("algakrwumvauugrvppkcppwaqkpatwifqkknaemavqpnuvakptapcgnwgfgadfcc")
print(grid_to_string(grid), end= "\n\n")
reverse_grid(grid)
print(grid_to_string(grid), end= "\n\n")
print(show_key(grid))
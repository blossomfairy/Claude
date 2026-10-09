/* ================= CODE SHORTS ================= */
EPISODES.push({
  id: 'b01', act: 6, label: 'Short 1', title: 'Hello, Lovelace', topic: 'Running Python, print, operators', unit: 'Python boot camp', video: DRIVE('1DazYhedUdH3uuL39-czU2mTP_JGuabv2'),
  steps: [
    { t: 'idea', h: 'Your first program', p: 'Save this as `hello.py`. Run it from the command prompt with **python hello.py**.', w: { type: 'code', text: '# a comment starts with #\nprint("Hello, Lovelace")' }, hook: 'In Python, # starts a comment.' },
    { t: 'idea', h: 'The math operators', p: 'Tap each to see what it does.', w: { type: 'flip', items: [
      ['+  -  *', 'Add, subtract, multiply. `3 * 4` → 12'],
      ['/', 'Division, **always a float**. `4 / 2` → **2.0**'],
      ['//', 'Floor division (drops the remainder). `7 // 2` → 3'],
      ['%', 'Remainder. `7 % 3` → 1'],
      ['**', 'Power. `2 ** 4` → 16'],
    ] }, hook: 'One slash = decimal answer. Two slashes = whole-number answer.' },
    { t: 'check', q: 'What does Python print?', code: 'print(4 / 2)', o: ['2', '2.0', '"2"', 'error'], a: 1, why: '`/` always returns a float in Python 3.' },
    { t: 'check', q: 'What does Python print?', code: 'print(7 % 3)', o: ['2', '1', '2.33', '0'], a: 1, why: '7 = 3 × 2 + **1**. % gives the remainder.' },
    { t: 'recap', items: ['Run a file: **python hello.py**. Comments start with **#**.', '`/` → float (4/2 = 2.0) · `//` → floor (7//2 = 3) · `%` → remainder · `**` → power.'] },
  ],
  quiz: [
    ['`7 % 3` → ?', ['2', '1', '2.33', '0'], 1],
    ['`4 / 2` → ?', ['2', '2.0', '"2"', 'error'], 1, '`/` always returns a float in Python 3.'],
    ['`7 // 2` → ?', ['3.5', '3', '4', '1'], 1],
    ['`2 ** 4` → ?', ['8', '6', '16', '24'], 2],
    ['In Python, a comment starts with:', ['//', '#', '--', '/*'], 1],
    ['To run hello.py from the command prompt you type:', ['run hello', 'python hello.py', 'hello.exe', 'start python'], 1],
  ],
  notes: ['**Try it:** predict, then check `10 % 4` (2), `10 // 4` (2), `10 / 4` (2.5), `3 ** 3` (27).', 'Write your own **prog1 for A3** with its required header and output format.'],
});

EPISODES.push({
  id: 'b02', act: 6, label: 'Short 2', title: 'Ask Me Anything', topic: 'input(), int(), types', unit: 'Python boot camp', video: DRIVE('1Sr6uiqcnfQ2ZXbKaSZ_5jXxD3ctMJnA6'),
  steps: [
    { t: 'idea', h: 'input() always gives you text', p: 'Even if the user types a number, **input() returns a str**. Convert it with **int()** or **float()**.', w: { type: 'code', text: 'year = input("Year Ada wrote her program? ")   # "1815" is TEXT\nyear = int(year)                              # now 1815 is a NUMBER\nprint(year + 1)' }, hook: 'input() hands you a string. Always.' },
    { t: 'idea', h: 'Types change what + and * do', p: '', w: { type: 'flip', items: [
      ['"1815" + 1', '**TypeError**: can’t add text and a number.'],
      ['int("1815") + 1', '**1816**'],
      ['"ha" * 3', '**"hahaha"**: * repeats a string.'],
      ['int("twenty")', '**ValueError**: that text isn’t a number.'],
      ['type(3.5)', '**float**'],
    ] } },
    { t: 'check', q: 'What happens?', code: 'print("1815" + 1)', o: ['1816', '"18151"', 'TypeError', '1815'], a: 2 },
    { t: 'recap', items: ['**input()** returns a **str**. Wrap it: `int(input(...))` or `float(input(...))`.', 'str + int → **TypeError**. `int("twenty")` → **ValueError**.', 'String * number repeats it.'] },
  ],
  quiz: [
    ['`input()` always returns a:', ['int', 'float', 'str', 'list'], 2],
    ['`"1815" + 1` gives:', ['1816', '"18151"', 'TypeError', '1815'], 2],
    ['`int("1815") + 1` gives:', ['1816', '"18151"', 'error', '1815.0'], 0],
    ['`"ha" * 3` gives:', ['error', '"hahaha"', '9', '"ha3"'], 1],
    ['`int("twenty")` gives:', ['20', 'TypeError', 'ValueError', '0'], 2],
    ['The type of `3.5` is:', ['int', 'str', 'float', 'bool'], 2],
  ],
  notes: ['**Try it:** ask for a Celsius temperature with `float(input(...))` and print Fahrenheit. 100 should give 212.0.'],
});

EPISODES.push({
  id: 'b03', act: 6, label: 'Short 3', title: 'Loop Until', topic: 'while loops, if / elif / else', unit: 'Python boot camp', video: DRIVE('1fnoLROfRBY8hgmA9CibAeedflndXIeRV'),
  steps: [
    { t: 'idea', h: 'Plain English first', p: 'Write the algorithm in words before the code. Then the code is just translation.', w: { type: 'compare', cols: [
      { h: 'Plain English', lines: ['Start the total at 0.', 'Ask for a number.', 'While the number isn’t 0: add it, ask again.', 'Print the total.'] },
      { h: 'Python', code: 'total = 0\nn = int(input("Number: "))\nwhile n != 0:\n    total = total + n\n    n = int(input("Number: "))\nprint(total)' },
    ] }, hook: 'Indentation marks what’s inside the loop.' },
    { t: 'idea', h: 'Branches pick ONE path', p: '`if / elif / else` runs **only the first true branch**.', w: { type: 'code', text: 'def letter(score):\n    if score >= 90:\n        return "A"\n    elif score >= 80:\n        return "B"     # letter(83) stops here\n    elif score >= 70:\n        return "C"\n    else:\n        return "F"' } },
    { t: 'check', q: 'With the `letter()` function above, `letter(83)` returns:', o: ['A', 'B', 'C', 'F'], a: 1 },
    { t: 'idea', h: '= vs ==', p: '**=** assigns a value. **==** compares two values.', w: { type: 'code', text: 'x = 5        # store 5 in x\nx == 5       # ask: is x equal to 5?  → True' }, hook: 'One = puts it in. Two == asks a question.' },
    { t: 'recap', items: ['**while** repeats as long as its condition is true.', '**if / elif / else** runs only the **first** true branch.', '**=** assigns, **==** compares.', 'Python uses **indentation** to mark a block.'] },
  ],
  quiz: [
    ['A `while` loop runs:', ['Exactly once', 'While its condition is true', 'Forever', 'A fixed 10 times'], 1],
    ['`if / elif / else` runs:', ['Every true branch', 'Only the first true branch', 'Only else', 'All branches'], 1],
    ['`==` vs `=`:', ['Both assign', '`==` compares, `=` assigns', 'Both compare', '`=` compares'], 1],
    ['With the episode’s `letter()` function, `letter(83)` returns:', ['A', 'B', 'C', 'F'], 1],
    ['What marks the body of a loop or branch in Python?', ['Braces {}', 'Indentation', 'Semicolons', 'END'], 1],
  ],
  notes: ['**Try it:** write an algorithm in plain English, then the code, for a loop that asks for numbers until the user enters 0 and then prints the total.', 'Your **prog3 for A3** (password loop) is yours to write.'],
});

EPISODES.push({
  id: 'b04', act: 6, label: 'Short 4', title: 'Functions & Classes', topic: 'def, return, recursion, inheritance', unit: 'Python boot camp', video: DRIVE('14SSDSOQCNYOc9JOrYCGac-pNdPYobauf'),
  steps: [
    { t: 'idea', h: 'Functions return values', p: '**return** sends a value back to whoever called the function and **ends** the function.', w: { type: 'code', text: 'def km_to_miles(km):\n    return km * 0.621371\n\nprint(round(km_to_miles(10), 2))   # 6.21' } },
    { t: 'idea', h: 'Recursion in Python', p: 'Same idea as Ep 3: base case + smaller call.', w: { type: 'steps', frames: [
      { html: '<pre class="code">def sum_list(xs):\n    if xs == []:          # base case: empty list\n        return 0\n    return xs[0] + sum_list(xs[1:])</pre>', cap: 'The base case is the **empty list**, which returns 0.' },
      { html: '<pre class="code">sum_list([4, 8, 15])\n= 4 + sum_list([8, 15])\n= 4 + 8 + sum_list([15])\n= 4 + 8 + 15 + sum_list([])</pre>', cap: 'Each call uses a **shorter** list.' },
      { html: '<pre class="code">= 4 + 8 + 15 + <span class="hl">0</span>\n= <span class="hl">27</span></pre>', cap: 'Base case reached. Add back up: **27**.' },
    ] } },
    { t: 'idea', h: 'Classes and inheritance', p: '`class Heir(Founder):` means **Heir is a subclass that inherits from Founder**. `super().greet()` calls the **parent’s** version.', w: { type: 'code', text: 'class Founder:\n    def greet(self):\n        return "Welcome to Lovelace Labs"\n\nclass Heir(Founder):\n    def greet(self):\n        return super().greet() + ", from Nadia"' } },
    { t: 'check', q: '`sum_list([4, 8, 15])` returns:', o: ['15', '27', '4', 'error'], a: 1 },
    { t: 'recap', items: ['**return** sends a value back and ends the function.', 'Recursive sum_list: base case = **empty list → 0**.', '`class Heir(Founder)` = Heir inherits from Founder. **super()** reaches the parent.'] },
  ],
  quiz: [
    ['`return` in a function:', ['Prints a value', 'Sends a value back to the caller and ends the function', 'Restarts it', 'Defines it'], 1],
    ['`round(km_to_miles(10), 2)` with the factor 0.621371 →', ['6.21', '16.09', '10', '0.62'], 0],
    ['`sum_list([4, 8, 15])` →', ['15', '27', '4', 'error'], 1],
    ['The base case of `sum_list` is:', ['A list with one item', 'The empty list, which returns 0', 'The first item', 'There is none'], 1],
    ['`class Heir(Founder):` means:', ['Founder inherits from Heir', 'Heir is a subclass that inherits from Founder', 'They’re unrelated', 'Heir deletes Founder'], 1],
    ['`super().greet()` calls:', ['The subclass’s own greet', 'The superclass’s version of greet', 'Nothing', 'A global function'], 1],
  ],
  notes: ['**Try it:** write a recursive `count_down(n)` that prints n, n−1, …, 1. Identify its base case.', 'A3’s prog4 and A4’s programs are yours to design.'],
});

/* Finale quiz: a fresh random 25 from every episode */
(() => {
  const pool = [];
  EPISODES.forEach(e => { if (e.act <= 4) e.quiz.forEach(q => pool.push([q[0] + `  _(${e.label})_`, q[1], q[2], q[3]])); });
  byIdFinale = EPISODES.find(e => e.id === 'ep19');
  byIdFinale.quiz = shuffle(pool).slice(0, 25);
})();
var byIdFinale;

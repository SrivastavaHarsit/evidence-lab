# Watch one real negotiation in VS Code

The line references below predate the function-comment cleanup. Find the quoted
statements in current files when setting breakpoints; executable behavior is unchanged.

Use this to revisit the original one-record checker. For the complete audit,
follow [the milestone-1 guide](MILESTONE_1.md). Here you will put
red dots in the source, start **Run and Debug**, and inspect the paused program
in **Variables**, by hovering, and optionally in **Watch**.

The project already has a ready-to-use configuration in `.vscode/launch.json`
named **Trace first CaSiNo deal**. It selects the existing `.venv` Python,
starts `scripts/check_one.py`, supplies `data/raw/casino.json`, and puts printed
output in **Debug Console**. This session uses VS Code's graphical controls.

Read one stop at a time. Predict a value, inspect it, and explain what changed.
Allow about 60–90 minutes; you can split the session. Line numbers below match
this version of the code. If you edit the source later, find the quoted
statement and use its current line number.

## 1. Open the project folder in VS Code

1. Open VS Code.
2. Choose **File → Open Folder…**.
3. Select `/home/mastii/Desktop/hustle/evidence-lab` and click **Open**.
4. Confirm the Explorer shows **EVIDENCE-LAB** as the project folder, containing
   `scripts`, `src`, `data`, and `.vscode`.
5. Open `docs/DEBUGGER_FIRST_SESSION.md`. For a readable preview, press
   **Ctrl+Shift+V**. Keep the guide beside the source if that helps.

Opening this folder makes `${workspaceFolder}` in the project's launch
configuration refer to `evidence-lab`. You do not need to create a launch
configuration yourself.

If your current VS Code window has `/home/mastii/Desktop/hustle` open, you can
keep that window: it now also has a `.vscode/launch.json` with the same
**Trace first CaSiNo deal** configuration. That version includes `evidence-lab`
in the script, Python, and working-directory paths. File paths in the table
below are relative to `evidence-lab`; in the `hustle` Explorer, expand that
folder first.

I checked that Microsoft's **Python** and **Python Debugger** extensions are
installed on this machine. If you need to check them in your VS Code window,
press **Ctrl+Shift+X** and search `@installed python`. Both should be enabled.

## 2. Learn what the red dot and highlighted line mean

A **breakpoint** is an instruction to pause when the running program reaches
that source location. You set it by clicking the narrow margin immediately
**to the left of the line number**. A red dot appears. Click it again to remove
it. You can also put the cursor on the line and press **F9**.

When execution pauses, VS Code highlights the current execution line and
shows an arrow in the margin. That code is about to execute. If the highlighted
line says `reconstructed = score(...)`, the new `reconstructed` value is not
available until the call and assignment finish. In a loop, an existing value
can still belong to the previous iteration.

For a multiline expression, some inner operations may already have run before
a stop on another part of the expression. The locations below are chosen to
make each particular value available when you inspect it.

Put dots on the executable statements listed below. Blank lines, comments,
and closing brackets are not useful places to stop.

## 3. Place these 13 red dots before starting

Open each file with **Ctrl+P**, type its relative path, and press Enter. To reach
a line, press **Ctrl+G**, type its number, and press Enter. Then click the margin
to the left of that line number.

For example: **Ctrl+P → `scripts/check_one.py` → Enter → Ctrl+G → `21` → Enter →
click the margin**. Repeat for the other locations.

The table is in execution order. A few locations will be visited more than once.

| Stop | File | Line | Statement to put the red dot on | What will be ready to inspect |
| --- | --- | ---: | --- | --- |
| A | `scripts/check_one.py` | 21 | `deal = load_first_accepted(args.path)` | Input path, before loading |
| B | `src/evidence_lab/negotiation/casino.py` | 235 | `if not isinstance(records, list):` | Loaded list of raw records |
| C | `src/evidence_lab/negotiation/casino.py` | 244 | `if terminal == "Accept-Deal":` | Current record and its final event |
| D | `src/evidence_lab/negotiation/casino.py` | 157 | `if proposal["text"] != "Submit-Deal":` | Final submission and acceptance pair |
| E | `src/evidence_lab/negotiation/casino.py` | 184 | `proposer_id: _allocation(...)` | Roles and raw quantities, before the first allocation conversion |
| F | `src/evidence_lab/negotiation/casino.py` | 191 | `for resource in ("food", "water", "firewood"):` | Both converted allocations; this loop header is revisited |
| G | `src/evidence_lab/negotiation/casino.py` | 193 | `if total != UNITS_PER_RESOURCE:` | One resource total; stops three times |
| H | `src/evidence_lab/negotiation/casino.py` | 121 | `outcomes = _mapping(...)` | Raw preferences and converted numeric values; stops for both participants |
| I | `src/evidence_lab/negotiation/casino.py` | 218 | `verify_scores(deal)` | Complete deal, before score verification |
| J | `src/evidence_lab/negotiation/schema.py` | 78 | `reconstructed = score(...)` | Participant's allocation and values, before calculation; stops twice |
| K | `src/evidence_lab/negotiation/schema.py` | 82 | `if reconstructed != participant.recorded_score:` | Calculated and recorded scores; stops twice |
| L | `src/evidence_lab/negotiation/schema.py` | 95 | `return computed[0], computed[1]` | Both checked scores |
| M | `scripts/check_one.py` | 22 | `print(f"Dialogue ...")` | Checked deal returned to the starting script |

Press **Ctrl+Shift+D** to open **Run and Debug**. Expand **BREAKPOINTS** near
the bottom of the sidebar. Check that these locations are listed and checked.
If you have other ordinary breakpoints from earlier work, uncheck those for
this session so the order matches the guide.

You can also add the next dot while paused and then continue. Setting all 13
first makes your first run easier to follow.

## 4. Start the saved configuration

1. In **Run and Debug** (**Ctrl+Shift+D**), find the configuration dropdown at
   the top.
2. Select **Trace first CaSiNo deal**.
3. Click the green **Start Debugging** triangle next to it, or press **F5**.
4. Wait for the program to pause at **A: `check_one.py`, line 21**.

This saved configuration always starts the checker, even if you are viewing
`casino.py` or this guide. Use this configuration's start button for the session.

If execution pauses at line 16 with **SystemExit: 2** and the output says
`the following arguments are required: path`, the checker was launched without
its dataset argument. It stopped before assigning `args`, so that variable
cannot appear yet. Click **Stop** (**Shift+F5**), choose **Trace first CaSiNo
deal** in the Run and Debug dropdown, and start it with the adjacent green
triangle. The saved configuration supplies the missing path. If the dropdown
has not refreshed after the configuration was added, use **Ctrl+Shift+P →
Developer: Reload Window**, then select the configuration again.

The controls in the debug toolbar are:

| Control | Shortcut on Linux | What it does |
| --- | --- | --- |
| Continue | **F5** | Run until the next breakpoint or completion |
| Step Over | **F10** | Advance in the current function, running called functions without walking through their bodies |
| Step Into | **F11** | Enter a function called by the current code |
| Step Out | **Shift+F11** | Finish the current function and pause back in its caller |
| Restart | **Ctrl+Shift+F5** | Start the same session again |
| Stop | **Shift+F5** | End this debug session |

Breakpoints can interrupt stepping, including Step Over and Step Out. A
multiline statement may take several steps. If your laptop uses function keys
for brightness or media controls, use the toolbar buttons or the **Fn** key.

For your first pass, **Continue** is the main control. We will practice
**Step Into** at the score calculation.

## 5. Know where to look while paused

- **VARIABLES → Locals:** names available in the currently selected function
  call. Click the small triangle beside a list, dictionary, or object to expand
  it. Expand nested fields the same way.
- **Hover:** rest your mouse over a variable in the source to see its value.
- **WATCH:** click its **+**, enter a Python expression, and press Enter. For
  example, at stop B, `len(records)` shows the number of loaded records.
- **CALL STACK:** the chain of active function calls. Selecting an older call
  lets you inspect its locals; it does not run or rewind the program. Select
  the most recent paused application frame again to follow the walkthrough.
- **DEBUG CONSOLE:** printed output appears here. Open it with **View → Debug
  Console** or **Ctrl+Shift+Y**. You may also enter an expression such as
  `messages[-2:]` while paused. This evaluates in the selected function call.

Variables and Hover are enough for most of the session. Watch and Debug
Console help with counts and selecting just the final two messages. In those
boxes, enter the expression itself; do not add a `p` prefix.

A name from another function can be unavailable. For example, `records` belongs
to the loader, while `reconstructed` belongs to `verify_scores()`. A Watch
expression can show an unavailable-name error after you leave its function.
Remove it with its context menu, or inspect the relevant call in Call Stack.
That expression error does not mean the program failed.

## 6. Follow the data, one stop at a time

### A — Input location: `check_one.py`, line 21

Expand **Locals → args → path**, or hover over `args.path`.

Expected: `PosixPath('data/raw/casino.json')`.

A `Path` is a location on disk, not the file's contents. The `deal` assignment
has not run yet. If you enter `args.path.exists()` in Watch or Debug Console,
the result should be `True`.

Press **F5** to continue to B.

### B — Loaded data: `casino.py`, line 235

Expand **Locals → records**, then its entry **0**. Look for `dialogue_id` and
`chat_logs` inside that first dictionary. Large lists may be grouped into
ranges in Variables; expand the range containing index 0.

Expected:

- `records` is a list; `len(records)` is **1,030**.
- `records[0]` is a dictionary.
- `records[0]["dialogue_id"]` is **0**.

The preceding line read the file as text and converted JSON into Python
containers. The program does not keep the intermediate text in a separate
variable. It has loaded all entries; it has not checked all their deals.

Press **F5**.

### C — Record selection: `casino.py`, line 244

Inspect **index**, **terminal**, and **raw** in Locals. Expand
**raw → chat_logs**.

Expected: `index = 0`, `raw["dialogue_id"] = 0`, `terminal = "Accept-Deal"`, and
13 chat events.

`index` is the record's position in the list; `dialogue_id` is its source
identity. They happen to match here. The final event says the offer was
accepted, so the loader is about to call `parse_accepted(raw)`.

This loader returns after the first accepted deal. Consequently, this run
will not process the remaining 1,029 records.

Press **F5**.

### D — Final message pair: `casino.py`, line 157

Expand **proposal** and **acceptance** in Locals. Expand
**proposal → task_data**. You can also inspect `messages[-2:]` in Watch or
Debug Console; `[-2:]` selects the last two entries.

Expected:

| Field | Value |
| --- | --- |
| `proposal["text"]` | `"Submit-Deal"` |
| `proposal["id"]` | `"mturk_agent_2"` |
| `acceptance["text"]` | `"Accept-Deal"` |
| `acceptance["id"]` | `"mturk_agent_1"` |
| `proposal["task_data"]["issue2youget"]` | Food `"2"`, Water `"3"`, Firewood `"0"` |
| `proposal["task_data"]["issue2theyget"]` | Food `"1"`, Water `"0"`, Firewood `"3"` |

The raw quantities are strings. `"2"` is text; `2` is an integer.

Predict who owns the quantities under `issue2youget`. Then press **F5**.

### E — Resolve "you" and "they": `casino.py`, line 184

Inspect **proposer_id**, **acceptor_id**, and **task**.

Expected: proposer `mturk_agent_2`, acceptor `mturk_agent_1`, and the same raw
quantity dictionaries you saw in D.

**"You get" belongs to the proposer.** In this record, participant 2 receives
food 2, water 3, firewood 0. Participant 1 receives food 1, water 0, firewood 3.
The meaning depends on who proposed; it is not a fixed participant number.

The upcoming `_allocation()` calls convert and check the quantities. Each
resource quantity must be an integer from 0 to 3 after permitted string
conversion. To observe one conversion inside the helper, use the optional
section below before continuing from this stop.

For the main walkthrough, press **F5**.

### F — Converted allocations: `casino.py`, line 191

Expand **allocations**, then both participant IDs, then their resource fields.

Expected:

```text
mturk_agent_1 → Resources(food=1, water=0, firewood=3)
mturk_agent_2 → Resources(food=2, water=3, firewood=0)
```

Each allocation is now a `Resources` object with named integer fields. The
raw string `"2"` has become the integer `2`. To confirm the type, inspect
`type(allocations["mturk_agent_2"].food)` in Watch or Debug Console: it is `int`.

Participant IDs explicitly identify ownership. Display order in the dictionary
does not determine ownership.

Press **F5** to reach the first G. This dot is on a loop header, so you will
return to F between the resource checks and once more as the loop ends. The
allocations stay the same on those return visits; press **F5** again each time.

### G — Resource totals: `casino.py`, line 193, three visits

Inspect **resource**, **total**, and **UNITS_PER_RESOURCE**. The constant may
appear under Globals; hovering over it also works.

| Visit | resource | total | Available units |
| --- | --- | ---: | ---: |
| First | `"food"` | 3 | 3 |
| Second | `"water"` | 3 | 3 |
| Third | `"firewood"` | 3 | 3 |

Both the loop header F and comparison G have dots, so the actual order is:

```text
F → G (food) → F → G (water) → F → G (firewood) → F → H
```

After each G, press **F5** to return to F, then **F5** again to continue.
The first two pairs of presses reach G for the next resource. After the
firewood check, the pair of presses reaches H. This shows a loop advancing
through its items and finally checking that no items remain.

The sums are `1 + 2`, `0 + 3`, and `3 + 0`. Individual quantity bounds and
combined resource totals are separate checks. Two individually permitted
quantities could still have an impossible combined total.

### H — Preferences become points: `casino.py`, line 121, two visits

Inspect **participant_id**, **allocation**, **preferences**, and **values**.
The preference conversion on the preceding statement has finished; outcomes
and the local `recorded_score` have not yet been extracted for this call.

First visit, participant 1:

```text
participant_id: mturk_agent_1
allocation:    Resources(food=1, water=0, firewood=3)
preferences:   High → Firewood; Medium → Food; Low → Water
values:        Firewood → 5; Food → 4; Water → 3
```

Press **F5**. The same helper runs for participant 2:

```text
participant_id: mturk_agent_2
allocation:    Resources(food=2, water=3, firewood=0)
preferences:   High → Firewood; Medium → Water; Low → Food
values:        Firewood → 5; Food → 3; Water → 4
```

High, Medium, and Low mean 5, 4, and 3 points per unit. `allocation` says how
many items were received; `values` says how many points each item earns.
The parser constructs participant 1 first even though participant 2 proposed.

Here `info` is one participant's information. A different function can use
its own local name `info` for a different container.

Press **F5** to reach I.

### I — Complete deal: `casino.py`, line 218

Expand **deal**, then **participant_1** and **participant_2**, and their
**allocation**, **values**, and **recorded_score** fields.

Expected:

| Participant | Allocation: food, water, firewood | Points per unit in that order | Recorded score |
| --- | --- | --- | ---: |
| mturk_agent_1 | 1, 0, 3 | 4, 3, 5 | 19 |
| mturk_agent_2 | 2, 3, 0 | 3, 4, 5 | 18 |

The deal's `dialogue_id` is 0 and `proposer_id` is `mturk_agent_2`.

This is a structured `AcceptedDeal`, assembled from the raw dictionaries.
Both recorded scores came from the source. Their independent verification
is about to happen; constructing the dataclasses did not itself check scores.

Expand **CALL STACK**. You should see `parse_accepted()` called by
`load_first_accepted()`, called by `check_one.py`. The callers are waiting for
the result. Keep `parse_accepted()` selected, then press **F5**.

### J — Before arithmetic: `schema.py`, line 78

Expand **participant → allocation** and **participant → values**.

First visit: participant 1, allocation `(1, 0, 3)`, values `(4, 3, 5)`.
Predict `1 × 4 + 0 × 3 + 3 × 5 = 19`.

To practice **Step Into**, press **F11** now. VS Code enters `score()` and
highlights its arithmetic near lines 59–61. Inspect **allocation** and
**values** in this function's Locals, or hover over them. These are the inputs
to the calculation; their names differ from the caller's `participant`.

Press **F5** to let the function calculate and return. The next breakpoint
is K. You can also use **F5** directly from J if you prefer to inspect only the
inputs and result.

Later, J will run for participant 2. Its allocation is `(2, 3, 0)` and values
are `(3, 4, 5)`. Predict `2 × 3 + 3 × 4 + 0 × 5 = 18`, then press **F5**.

### K — Compare calculated and recorded scores: line 82, two visits

Inspect **participant.participant_id**, **reconstructed**,
**participant.recorded_score**, and **computed**.

| Visit | Participant | reconstructed | recorded_score | computed so far |
| --- | --- | ---: | ---: | --- |
| First | mturk_agent_1 | 19 | 19 | `[]` |
| Second | mturk_agent_2 | 18 | 18 | `[19]` |

The new calculation is available because the preceding assignment finished.
The list does not yet contain the current participant's score; its append
happens after the disagreement check passes.

At the first K, press **F5** to reach J for participant 2. After that J, press
**F5** to reach the second K. After inspecting the second K, press **F5** to L.

### L — Both checks passed: `schema.py`, line 95

Expand **computed**. Expected: `[19, 18]`.

Both comparisons have now passed. `verify_scores()` will return `(19, 18)`.
The parser uses this function to enforce verification and then returns the
`deal`; it does not store this score tuple.

Press **F5**.

### M — Return to the script: `check_one.py`, line 22

Expand **deal** in Locals. It is the checked result returned to the original
script: dialogue 0, proposer participant 2, recorded scores 19 and 18.

This is where `deal = load_first_accepted(args.path)` has finally completed.
The parser and loader have returned.

Press **F5** once more. The program prints its result in **Debug Console**,
ending with:

```text
PASS: both reconstructed scores match the source.
```

The session ends normally. Red dots remain for your next run. To repeat, select
**Trace first CaSiNo deal** and press **F5** again. To stop a running or paused
session yourself, click the toolbar's square Stop button or press **Shift+F5**.

## 7. Optional: see one string become an integer

Use this after you are comfortable with the main stops. Start another run,
reach E at `casino.py` line 184, and keep the program paused there.

1. Add a red dot on **line 40** in `_integer()`, at
   `if isinstance(value, str) and ...`.
2. Right-click that dot and choose **Edit Breakpoint…**. Choose an expression
   condition if the menu asks, then enter:

   ```python
   field == "issue2youget.Food"
   ```

3. Add another red dot on **line 46**, at
   `if type(value) is not int or not 0 <= value <= maximum:`.
4. Give it the **same condition** using Edit Breakpoint.
5. Press **F5** from E. At line 40, inspect `field`, `value`, and `maximum`.
   Expected: `"issue2youget.Food"`, string `"2"`, and maximum 3.
6. Press **F5**. At line 46, `value` is integer `2` and `maximum` is still 3.
   The conversion has executed, and the type/bounds check is next.
7. Press **F5** to reach F and resume the main guide.

The condition limits these helper stops to this one field. Without it, the
helper also runs for other resources and recorded scores. Remove the two
optional dots when you finish if you want the original 13-dot session again.

## 8. When something looks wrong

| What you see | What to do in VS Code |
| --- | --- |
| The configuration name is missing | Both the `hustle` folder and its `evidence-lab` folder now have a matching launch file. Stop the session, use Ctrl+Shift+P → Developer: Reload Window, and check Run and Debug again. |
| The debugger runs straight to PASS | Check that your dots are set, their boxes are checked in BREAKPOINTS, and breakpoints are active. Hover over the BREAKPOINTS toolbar icons to find Activate Breakpoints if they were deactivated. |
| A dot stays hollow or gray during the session | Hover over it to read the debugger's message; verify the executable statement, file, and enabled Python Debugger extension. |
| An unfamiliar extra stop appears | Look at the highlighted file/function and BREAKPOINTS list. Uncheck unrelated breakpoints. A loop or a helper called twice can legitimately stop at the same line again. |
| A variable or Watch expression is unavailable | Check the selected Call Stack frame and whether its assignment has executed. Return to the current paused application frame; remove Watch expressions that belong to another function. |
| VS Code offers to select a debugger instead of launching | Confirm Python Debugger is enabled, and select the saved Trace first CaSiNo deal configuration in Run and Debug. |
| `the following arguments are required: path` | Start the saved configuration, whose `args` already supplies the dataset path. |
| The Python executable or dataset cannot be found | The checked setup currently has both. Inspect `.vscode/launch.json` and the exact folder you opened; if either file was later removed, share the error so that setup can be repaired. |

If you get lost, click **Stop**, check the dots, and start the same configuration
again. This observation session does not require editing the application code.

## 9. Your readiness check

Explain these points in your own words while looking at the source:

1. A path becomes a list of dictionaries; one dictionary becomes a structured deal.
2. "You get" belongs to the proposer, who can be either participant.
3. Raw quantity strings become checked integers; totals are checked separately.
4. Quantities and points per unit have different meanings.
5. Calculated scores are produced independently and compared with source scores.
6. This loader returns after one accepted record, despite reading 1,030 entries.

You can use the code and notes. Memorizing every line or shortcut is not a
prerequisite for the batch-audit milestone.

The launch options and UI controls follow the official
[VS Code Python debugging guide](https://code.visualstudio.com/docs/python/debugging)
and [general debugging guide](https://code.visualstudio.com/docs/debugtest/debugging).

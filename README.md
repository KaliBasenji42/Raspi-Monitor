# Basics

This is python script that reads `/sys` and `/proc` (or similar). It takes the values and graphs them overtime. There are different graph and system variables that can be edited, it is explained when ran. These variables are stored in the `values` dictionary for easy access.

# Method

`values['method']` and `values['methodInfo']` tells the script how to read files. `values['method']` is a float passed into a function, changed to an interger, and then compared with many elif's. This causies different behaviors. `values['methodInfo']` is a list of strings that stores data needed for handling each method.

## Each Method:

| Method | Description | Equation | methodInfo | For |
| ------ | ----------- | -------- | ---------- | --- |
| 0 | Raw: Reads one line, converts string to float | N/A | [line] | Thermal, Memory |
| 1 | Reads a single line of a cumlated value, and finds rate of change | out = (new - old) / `values['spf']` | [line, old] | Network |
| 2 | Reads a line and breaks it into a list, sums the list for total and takes a position for another value | total = ((newTotal - oldTotal) / `values['spf']`), val = ((newVal - oldVal) / `values['spf']`), out = (total - val) / total | [line, valPos, oldTotal, oldVal] | CPU Load |
| 3 | Similar to method 2 in structure, although only outputs a single value similar to method 1 | out = (new - old) / `values['spf']` | [line, valPos, oldVal] | Disk

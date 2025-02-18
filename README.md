# Basics

This is python script that reads `/sys` and `/proc` (or similar). It takes the values and graphs them overtime. There are different graph and system variables that can be edited, it is explained when ran. These variables are stored in the `values` dictionary for easy access.

[Somewhat usefull Documentation](https://www.kernel.org/doc/Documentation/ABI/testing/)

# Input (Printed on Startup)

`
Inputs:  
  Case does not matter  
  Numbers are validated before use  
    (if logLen is set to -5.2 it will be treated as 1)  
  If there is a error with getCont(), 0 is returned  
  
  "quit": Quits  
  "run": Run graph loop (must kill program to stop)  
  "spf": Seconds per frame for graph, Default: 1  
  "logLen": How many lines are recorded, Default: 20  
  "numLen": Length of ending number, Default: 6  
  "import": Import graph settings from settings.txt  
  "?": Reprint this  
  
  "path": File path for data file, Defualt: (for thermal)  
  "scale": Scale of return value, Default: 1000  
  "method": Method for gathering info, Default: 0  
  "methodInfo": Other info needed for gathering data, Default: ["0"]  
  "type": Looks up paths saved in list for data file  
  "type?": Print types in array noted above  
  
  "barMin": Default: 20  
  "barMax": Default: 100  
  "barLen": number of chars in bar, Default: 50  
  "barMed": Medium Threshold (0 to 1), Default: 0.7  
  "barHi": High Threshold (0 to 1), Default: 0.85  
  "barChr": Character used in bar, Default: "="  
  "barLoC": Low color, Default: 32 (green)  
  "barMedC": Medium color, Default: 33 (yellow)  
  "barHiC": High color, Default: 31 (red)  
  "c?": Print color key  
`

# Method

`values['method']` and `values['methodInfo']` tells the script how to read files. `values['method']` is a float passed into a function, changed to an interger, and then compared with many elif's. This causes different behaviors. `values['methodInfo']` is a list of strings that stores data needed for handling each method.

## Each Method:

| Method | Description | Equation | methodInfo | For |
| ------ | ----------- | -------- | ---------- | --- |
| 0 | Raw: Reads one line, converts string to float | N/A | [line] | Thermal, Memory |
| 1 | Reads a single line of a cumlated value, and finds rate of change | out = (new - old) / `values['spf']` | [line, old] | Network |
| 2 | Reads a line and breaks it into a list, sums the list for total and takes a position for another value | total = ((newTotal - oldTotal) / `values['spf']`), val = ((newVal - oldVal) / `values['spf']`), out = (total - val) / total | [line, valPos, oldTotal, oldVal] | CPU Load |
| 3 | Similar to method 2 in structure, although only outputs a single value similar to method 1 | out = (new - old) / `values['spf']` | [line, valPos, oldVal] | Disk

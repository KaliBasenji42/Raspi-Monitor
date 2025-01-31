import time

# Variables

run = True

cont = 0

# Defaults

values = {

  'path': '/sys/class/thermal/thermal_zone0/temp',

  'spf': 1,
  'contLogLen': 20,

  'barMin': 20,
  'barMax': 100,
  'barLen': 50,
  'barMed': .7,
  'barHi': .85,
  'barChr': '=',
  'barLoC': 32,
  'barMedC': 33,
  'barHiC': 31
  
}

# Keys

types = {
  'thermal': '/sys/class/thermal/thermal_zone0/temp'
}

colorKey = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan']

# Function

def strToFloat(string):
  
  numStr = ''
  
  for i in range(len(string)):
    
    if string[i].isnumeric(): numStr = numStr + string[i]
    if string[i] == '.': numStr = numStr + string[i]
    
  
  if len(numStr) == 0: return 0
  
  if string[0] == '-': return -1 * float(numStr)
  else: return float(numStr)
  

def lenNum(string, length): # Adds 0's to string until at length
  
  add = length - len(string)
  
  out = string
  
  for i in range(add): out = out + '0'
  
  return out
  

def bar(val, minimum, maximum, length, medium, high, char, loColor, medColor, hiColor):
  
  # Validating
  
  val = max(min(val, maximum), minimum)
  
  length = int(max(length, 0))
  
  loColor = int(max(min(loColor, 36), 31))
  medColor = int(max(min(medColor, 36), 31))
  hiColor = int(max(min(hiColor, 36), 31))
  
  # Variables
  
  val = val - minimum
  
  span = maximum - minimum
  
  barLen = round((val / span) * length)
  
  # Output
  
  out = str(minimum) +  '[\033[' + str(loColor) + 'm'
  
  for i in range(barLen):
    
    if i / length >= high: out = out + '[\033[' + str(hiColor) + 'm'
    elif i / length >= medium: out = out + '[\033[' + str(medColor) + 'm'
    
    out = out + char
    
  
  for i in range(length - barLen): out = out + ' '
  
  out = out + '\033[0m]' + str(maximum)
  
  return out
  

def printLog(log, new):
  
  # Roll
  
  log.pop(0)
  
  log.append(new)
  
  # Print
  
  for entry in log: print('\033[F', end = '')
  
  for entry in log: print('\r' + entry, end = '\n')
  
  return log
  

# Try File

try:
  with open(values['path'], 'r') as file: pass
except:
  print('Unable to Open :/\n')
  run = False

# Instructions

print('Inputs:')
print('  Case does not matter')
print('  Numbers are validated before use (if logLen is set to -1.4 it will be treated as -1)')
print()
print('  "quit": Quits')
print('  "run": run graph loop (must kill program to stop)')
print('  "spf": seconds per frame for graph, Default: 1')
print('  "logLen": How many lines are recorded, Default: 20')
print()
print('  "path": File path for data file, Defualt: (for thermal)')
print('  "type": Looks up paths saved in list for data file')
print('  "type?": Print types in array noted above')
print()
print('  "barMin": Default: 20')
print('  "barMax": Default: 100')
print('  "barLen": number of chars in bar, Default: 50')
print('  "barMed": Medium Threshold (0 to 1), Default: 0.7')
print('  "barHi": High Threshold (0 to 1), Default: 0.85')
print('  "barChr": Character used in bar, Default: "="')
print('  "barLoC": Low color, Default: 32 (green)')
print('  "barMedC": Medium color, Default: 33 (yellow)')
print('  "barHiC": High color, Default: 31 (red)')
print('  "c?": Print color key')

# Input Loop

while True:
  
  print()
  inp = input('Input: ')
  print()
  
  inp = inp.lower()
  
  # Quit and Run
  
  if inp == 'quit':
    run = False
    break
  
  elif inp == 'run':
    
    if run: break
    
    print('Error')
    
  
  # Info
  
  elif inp == 'type?':
    for key in types: print(key + ': ' + types[key])
  
  elif inp == 'c?':
    for i in range(len(colorKey)): print(colorKey[i] + ': ' + str(i))
  
  # String Input
  
  elif inp == 'path':
    
    valInp = input('path: ')
    print()
    
    try:
      with open(inp, 'r') as file: pass
    except:
      print('Unable to Open :/')
      run = False
    else:
      values['path'] = pathInp
      print('"path" set to "' + values['path'] + '"')
    
  
  elif inp == 'barChr':
    
    valInp = input('Character: ')
    print()
    
    values['barChr'] = (valInp + ' ')[0]
    
    print('"barChr" set to "' + values['barChr'] + '"')
    
  
  # All Other
  
  else:
    
    for key in values:
      
      if inp == key:
        
        valInp = input('"' + key + '": ')
        print()
        
        values[key] = strToFloat(valInp)
        
        print('"' + key +'" set to "' + values[key] + '"')
        
    
  

# Preloop

contLog = [''] * int(max(values['contLogLen'], 0))

print('Press [CTRL] + [C] to stop')

for entry in contLog: print('')

# Graph Loop

while run:
  
  # Read
  
  with open(values['path'], 'r') as file: cont = strToFloat(file.read())
  
  # Print
  
  newLog = bar(cont/1000, barMin, barMax, barLen, barMed, barHi)
  
  newLog = newLog + ' | ' + lenNum(str(cont / 1000), 5 ) + '  '
  
  contLog = printLog(contLog, newLog)
  
  # Time
  
  time.sleep(spf)
  

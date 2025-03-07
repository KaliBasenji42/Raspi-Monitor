import time
import sys
import select

# Variables

run = True

cont = 0

runGraph = True
graphing = False

settingsFile = 'settings.txt'

debug = ''

# Defaults

values = {

  'path': '/sys/class/thermal/thermal_zone0/temp',
  'scale': 1000,
  'method': 0,
  'methodInfo': ['0'],

  'spf': 1.0,
  'logLen': 20.0,
  'numLen': 6.0,

  'barMin': 20.0,
  'barMax': 100.0,
  'barLen': 50.0,
  'barMed': .7,
  'barHi': .85,
  'barChr': '=',
  'barLoC': 32.0,
  'barMedC': 33.0,
  'barHiC': 31.0
  
}

# Keys

types = {
  'thermal': ['/sys/class/thermal/thermal_zone0/temp',
              1000,
              0,
              ['0'],
              'Core temp in Celcius'],
  'memfr': ['/proc/meminfo',
              1024,
              0,
              ['1'],
              'Free memory in MB'],
  'netrx': ['/sys/class/net/eth0/statistics/rx_bytes',
             1,
             1,
             ['0', ''],
             'Bytes received. "eth0" can be interchanged for different network device'],
  'nettx': ['/sys/class/net/eth0/statistics/tx_bytes',
             1,
             1,
             ['0', ''],
             'Bytes transmitted. "eth0" can be interchanged for different network device'],
  'cpuload': ['/proc/stat',
             0.01,
             2,
             ['1', '4', '', ''],
             'Total CPU load as %, methodInfo[0] can be changed to change core'],
  'diskr': ['/proc/diskstats',
             2,
             3,
             ['24', '5', ''],
             'KB read on disk (sectors (512 Bytes) * 2 )'],
  'diskw': ['/proc/diskstats',
             2,
             3,
             ['24', '9', ''],
             'KB written on disk (sectors (512 Bytes) * 2 )']
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
  

def lenNum(string, length): # Makes number string length
  
  if strToFloat(string) >= 10 ** length:
    
    num = strToFloat(string)
    pwr = 0
    
    while num >= 10:
      pwr += 1
      num = num / 10
    
    return str(num)[:3] + 'e' + str(pwr)
    
  
  string = string[:length]
  
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
    
    if i / length >= high: out = out + '\033[' + str(hiColor) + 'm'
    elif i / length >= medium: out = out + '\033[' + str(medColor) + 'm'
    
    out = out + char
    
  
  for i in range(length - barLen): out = out + ' '
  
  out = out + '\033[0m]' + str(maximum)
  
  return out
  

def printLog(log, new):
  
  # Roll
  
  log.pop(0)
  
  log.append(new)

  global debug
  if debug != '': log[0] = debug
  
  # Print
  
  for entry in log: print('\033[F', end = '')
  
  for entry in log: print('\r' + entry, end = '\n')
  
  return log
  

def getCont(path, method):
  
  out = 0
  
  if int(method) == 0:
    
    with open(path, 'r') as file: cont = file.readlines()
    
    out = strToFloat(cont[int(values['methodInfo'][0])])
    
  
  elif int(method) == 1:
    
    with open(path, 'r') as file: cont = file.readlines()
    
    new = strToFloat(cont[int(values['methodInfo'][0])])
    
    out = new - strToFloat(values['methodInfo'][1])
    out = out / values['spf']
    
    values['methodInfo'][1] = str(new)
    
  
  elif int(method) == 2:
    
    with open(path, 'r') as file: cont = file.readlines()
    
    line = cont[int(values['methodInfo'][0])][:-1].split()
    
    newTotal = sum(float(num) for num in line[1:])
    
    newVal = int(line[int(values['methodInfo'][1])])
    
    oldTotal = strToFloat(values['methodInfo'][2])
    oldVal = strToFloat(values['methodInfo'][3])
    
    total = (newTotal - oldTotal) / values['spf']
    val = (newVal - oldVal) / values['spf']
    
    out = (total - val) / total
    
    values['methodInfo'][2] = str(newTotal)
    values['methodInfo'][3] = str(newVal)
    
  
  elif int(method) == 3:
    
    with open(path, 'r') as file: cont = file.readlines()
    
    line = cont[int(values['methodInfo'][0])][:-1].split()
    
    newVal = int(line[int(values['methodInfo'][1])])
    oldVal = strToFloat(values['methodInfo'][2])
    
    val = (newVal - oldVal) / values['spf']
    
    out = val
    
    values['methodInfo'][2] = str(newVal)
    
  
  return out / values['scale']
  
def detectKey():
  
  if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
    key = sys.stdin.read(1)
    return key
  
  return None
  

# Instructions

instructions = [
  'Inputs:',
  '  Case does not matter',
  '  Numbers are validated before use',
  '    (if logLen is set to -5.2 it will be treated as 1)',
  '  If there is a error with getCont(), 0 is returned',
  '',
  '  "quit": Quits',
  '  "run": Run graph loop (must kill program to stop)',
  '  "spf": Seconds per frame for graph, Default: 1',
  '  "logLen": How many lines are recorded, Default: 20',
  '  "numLen": Length of ending number, Default: 6',
  '  "import": Import graph settings from settings.txt',
  '  "?": Reprint this',
  '',
  '  "path": File path for data file, Defualt: (for thermal)',
  '  "scale": Scale of return value, Default: 1000',
  '  "method": Method for gathering info, Default: 0',
  '  "methodInfo": Other info needed for gathering data, Default: ["0"]',
  '  "type": Looks up paths saved in list for data file',
  '  "type?": Print types in array noted above',
  '',
  '  "barMin": Default: 20',
  '  "barMax": Default: 100',
  '  "barLen": number of chars in bar, Default: 50',
  '  "barMed": Medium Threshold (0 to 1), Default: 0.7',
  '  "barHi": High Threshold (0 to 1), Default: 0.85',
  '  "barChr": Character used in bar, Default: "="',
  '  "barLoC": Low color, Default: 32 (green)',
  '  "barMedC": Medium color, Default: 33 (yellow)',
  '  "barHiC": High color, Default: 31 (red)',
  '  "c?": Print color key'
]

for entry in instructions: print(entry)

# Try File

try:
  with open(values['path'], 'r') as file: pass
except:
  print('\nUnable to Open file :/')
  runGraph = False

# Main Loop

while run:
  
  graphing = False
  
  # Inupt Loop
  
  while True:
    
    print()
    inp = input('Input: ')
    print()
    
    inp = inp.lower()
    
    # Quit and Run
    
    if inp == 'quit':
      run = False
      runGraph = False
      break
    
    elif inp == 'run':
      
      if runGraph: break
      
      print('Error')
      
    
    # import
    
    elif inp == 'import':
      
      try:
        with open(settingsFile, 'r') as file: pass
      except:
        print('\nUnable to Open file :/')
      
      else:
        
        print('WIP')
        
      
    
    # Info
    
    elif inp == '?':
      for entry in instructions: print(entry)
    
    elif inp == 'type?':
      for key in types: print(key + ': ' + types[key][0] +
                              ', scale: ' + str(types[key][1]) +
                              ', method: ' + str(types[key][2]) +
                              ', methodInfo: ' + str(types[key][3]) +
                              '\n  ' + types[key][4])
    
    elif inp == 'c?':
      for i in range(len(colorKey)): print(colorKey[i] + ': ' + str(i+31))
    
    # Type
    
    elif inp == 'type':
      
      valInp = input('"type": ')
      print()
      
      for key in types:
        
        if valInp == key:
          
          try:
            with open(types[key][0], 'r') as file: pass
          except:
            print('Unable to Open :/')
            runGraph = False
          else:
            values['path'] = types[key][0]
            print('"path" set to "' + values['path'] + '"')
            
            values['scale'] = types[key][1]
            print('"scale" set to "' + str(values['scale']) + '"')
            
            values['method'] = types[key][2]
            print('"method" set to "' + str(values['method']) + '"')
            
            values['methodInfo'] = types[key][3]
            print('"methodInfo" set to "' + str(values['methodInfo']) + '"')
            
            runGraph = True
            
          
        
      
    
    # String Input
    
    elif inp == 'path':
      
      valInp = input('"path": ')
      print()
      
      try:
        with open(valInp, 'r') as file: pass
      except:
        print('Unable to Open :/')
        runGraph = False
      else:
        values['path'] = valInp
        print('"path" set to "' + values['path'] + '"')
        runGraph = True
      
    
    elif inp == 'barchr':
      
      valInp = input('"barChr": ')
      print()
      
      values['barChr'] = (valInp + ' ')[0]
      print('"barChr" set to "' + values['barChr'] + '"')
      
    
    # Method Info / Array Input
    
    elif inp == "methodinfo":
      
      valInp = input('"methodInfo": ')
      print()
      
      values['methodInfo'] = valInp.split()
      print('"methodInfo" set to "' + str(values['methodInfo']) + '"')
      
    
    # All Other
    
    else:
      
      for key in values:
        
        if inp == key.lower():
          
          valInp = input('"' + key + '": ')
          print()
          
          values[key] = strToFloat(valInp)
          
          print('"' + key +'" set to "' + str(values[key]) + '"')
          
        
      
    
  
  # Pre-Graph
  
  contLog = [''] * int(max(values['logLen'], 1))
  
  print('Enter "q" to return to Input (wait until loop has ended)')
  
  for entry in contLog: print('')
  
  graphing = True
  
  # Graph Loop
  
  while runGraph:
    
    # Key
    
    if detectKey() == 'q':
      break
    
    # Read
    
    try:
      cont = getCont(values['path'], values['method'])
    except Exception as e:
      cont = 0
      debug = str(e)
    
    # Print
    
    newLog = bar(cont, 
                 values['barMin'],
                 values['barMax'],
                 values['barLen'],
                 values['barMed'],
                 values['barHi'],
                 values['barChr'],
                 values['barLoC'],
                 values['barMedC'],
                 values['barHiC'])
    
    newLog = (newLog + ' | ' +
              lenNum(str(cont), int(max(values['numLen'], 0))) +
              '  ')
    
    contLog = printLog(contLog, newLog)
    
    # Time
    
    time.sleep(max(values['spf'], 0))
    
  

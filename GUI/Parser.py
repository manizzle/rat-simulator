import re
import os, shutil
from Simulator.Sim import sim
from Simulator.Memory.mem_controller import mem_controller
from Simulator.Commands.Subcommand import *
from subprocess import PIPE, Popen, STDOUT

class parser(object):
  def parse (self, asm_name, active, activeCallback):
    if len(asm_name) < 2: return "ERROR: no code generated"
    
    rat_name = '/cygdrive/'+asm_name[0]+asm_name.replace('\\','/')[2:]
    
    process = Popen(['RATASM/ratasm.exe', rat_name], stdout=PIPE, shell=False, stderr=STDOUT, universal_newlines=True, cwd=os.getcwd())
    process.communicate()
    
    errFile = asm_name[:asm_name.rfind('.')]+'.err'
    if not os.path.exists(errFile):
      return "ERROR: no error file generated"
    
    with open(errFile) as f:
      s = f.read()
      if s != "":
        return s
        
    dbgFile = asm_name[:asm_name.rfind('.')]+'.dbg'
    if not os.path.exists(dbgFile):
      return "ERROR: no debug file generated"
    
    with open(dbgFile) as f:
      return self.build_commands(f.readlines(), active, activeCallback, asm_name)
    

  def build_commands(self, dbgIn, active, activeCallback, asm_name):
    #str = stdOut[stdOut.find('List FileKey'):stdOut.find('Symbol Table Key')]
    cmd_hash = {}
    startCode = True
    splitSpaces = re.compile(r'\s*')
    for line in dbgIn:
      #change read mode when a blank newline is detected
      if line == "\n": 
        startCode = False
        continue
      commandList = splitSpaces.split(line)
      
      if startCode: 
        instruction_name = commandList[1].title() 
        memory_add = commandList[2]
        instruction_hex = commandList[3]
        line_number = '-1'
        
      else: 
        instruction_name = commandList[1].title() 
        line_number = commandList[2]
        memory_add = commandList[3]
        instruction_hex = commandList[4]
      
      try:
        cmd_hash[int(memory_add,0)] = eval(instruction_name+"("+line_number+","+instruction_hex+","+memory_add+")")
      except NameError:
        return "ERROR: simulator does not support "+instruction_name
      
    if cmd_hash=={}:
      return "ERROR: no code generated"

    shutil.move('prog_rom.vhd', os.path.dirname(asm_name)+'/prog_rom.vhd')
    return sim(cmd_hash, mem_controller({}, active, activeCallback)) 


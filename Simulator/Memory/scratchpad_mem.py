class scratchpad_mem(object):
  def __init__(self, dic):
    self.mem = [0 for i in xrange(256)]
    for key,value in dic: 
      self.mem[key] = value&0x3FF
      
  def __getitem__(self, key):
    return self.mem[key]
    
  def __setitem__(self, key, value):
    self.mem[key] = value & 0x3FF
    
class register_file(object):
  
  def __init__(self):
    self.mem = [0 for i in range(32)]
    
  def __getitem__(self, key):
    return self.mem[key]
    
  def __setitem__(self, key, value):
    self.mem[key] = value & 0xFF
    











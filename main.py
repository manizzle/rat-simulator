from GUI.Editor import editor
import wx
import imp, os, sys, traceback

version = '0.70'

def main_is_frozen():
  return (hasattr(sys, "frozen") or # new py2exe
          hasattr(sys, "importers") # old py2exe
          or imp.is_frozen("__main__")) # tools/freeze
          
def get_main_dir():
  if main_is_frozen():
    return os.path.dirname(sys.executable)
  return os.getcwd()
          
if main_is_frozen():
    sys.stderr = open('errLog.txt','w')
    sys.stdout = sys.stderr
    pass
try:
  os.chdir(get_main_dir())
      
  app = wx.App(False)
  app.SetTopWindow(editor(version))
  app.GetTopWindow().Show()
  app.MainLoop()
except Exception as e:
  traceback.print_exc()
  sys.exit()

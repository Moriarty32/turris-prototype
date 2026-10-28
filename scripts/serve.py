from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit,unquote
import sys
ROOT=Path(__file__).resolve().parents[1]/'dist'
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  path=unquote(urlsplit(path).path)
  prefix='/turris-prototype'
  if path==prefix:path='/'
  elif path.startswith(prefix+'/'):path=path[len(prefix):]
  target=(ROOT/path.lstrip('/')).resolve()
  if not target.is_relative_to(ROOT.resolve()):return str(ROOT/'404.html')
  return str(target)
 def log_message(self,*args):pass
port=int(sys.argv[1]) if len(sys.argv)>1 else 4173
print(f'Local: http://127.0.0.1:{port}/turris-prototype/',flush=True)
ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()


import argparse
from pathlib import Path
from .api.server import serve, ENGINE
def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="cmd")
    s=sp.add_parser("serve"); s.add_argument("--host",default="127.0.0.1"); s.add_argument("--port",type=int,default=18321)
    sp.add_parser("status")
    sp.add_parser("owner-token")
    a=p.parse_args()
    if a.cmd=="serve": return serve(a.host,a.port)
    if a.cmd=="owner-token": print(ENGINE.token()); return
    import json; print(json.dumps(ENGINE.status(),indent=2))
if __name__=="__main__": main()

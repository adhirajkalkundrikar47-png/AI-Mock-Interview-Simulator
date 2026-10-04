"""Real HTTP tests against the dependency-free Java adapter. No third-party Python dependencies."""
import json, os, pathlib, subprocess, tempfile, time, urllib.request, urllib.error, http.cookiejar
ROOT=pathlib.Path(__file__).resolve().parents[1]
PORT=18081
BASE=f'http://127.0.0.1:{PORT}'
def client():return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
def call(c,path,data=None,origin=BASE):
 raw=None if data is None else json.dumps(data).encode()
 r=urllib.request.Request(BASE+'/api'+path,data=raw,headers={'Content-Type':'application/json','Origin':origin})
 try:
  with c.open(r,timeout=40) as resp:return resp.status,json.load(resp)
 except urllib.error.HTTPError as e:return e.code,json.load(e)
def check(condition,label):
 assert condition,label
 print('PASS:',label)
with tempfile.TemporaryDirectory() as tmp:
 build=pathlib.Path(tmp)/'classes';build.mkdir()
 subprocess.run(['java','com.sun.tools.javac.Main','--release','17','-d',str(build),*[str(p) for p in (ROOT/'src/main/java/com/interview').glob('*.java')]],check=True)
 env=dict(os.environ,PORT=str(PORT),DATA_DIR=tmp+'/data',AI_API_KEY='')
 def start():
  p=subprocess.Popen(['java','-cp',str(build),'com.interview.LocalServer'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL)
  for _ in range(100):
   try:
    if call(client(),'/health')[0]==200:return p
   except Exception:pass
   time.sleep(.05)
  p.terminate();raise RuntimeError('Server did not start')
 proc=start()
 try:
  a,b=client(),client()
  for asset in ['', 'app.js', 'style.css', 'favicon.svg']:
   with urllib.request.urlopen(BASE+'/'+asset) as response:
    check(response.status==200 and len(response.read())>0, 'serves '+(asset or 'index.html'))
  check(call(a,'/sessions')[0]==401,'anonymous history denied')
  account={'name':'Integration Learner','email':'one@example.com','password':'test-password-123'}
  check(call(a,'/auth/register',account,origin='https://evil.example')[0]==403,'cross-origin mutation denied')
  check(call(a,'/auth/register',account)[0]==200,'registration')
  check(call(a,'/me')[1]['name']=='Integration Learner','authenticated identity')
  status,s=call(a,'/sessions',{'role':'Web developer','level':'Beginner','mode':'baseline'});check(status==201 and len(s['questions'])==5,'five-question session')
  sid=s['id'];qid=s['questions'][0]['id']
  payload={'questionId':qid,'key':'integration-key-0001','answer':'The server must validate data because a client can bypass browser checks. Reject invalid values.'}
  check(call(a,f'/sessions/{sid}/answers',dict(payload,answer='x'))[0]==400,'short answer rejected')
  status,s=call(a,f'/sessions/{sid}/answers',payload);check(status==200 and s['answers'][0]['status']=='READY','answer persisted and evaluated')
  check(s['answers'][0]['feedback']['mode']=='Rule-based hints','baseline clearly labelled')
  check(len(call(a,f'/sessions/{sid}/answers',payload)[1]['answers'])==1,'duplicate request does not duplicate answer')
  check(call(a,f'/sessions/{sid}/answers',dict(payload,answer='A different answer with conflicting content.'))[0]==409,'idempotency conflict')
  check(call(b,'/auth/register',dict(account,email='two@example.com'))[0]==200,'second account')
  check(call(b,f'/sessions/{sid}')[0]==404,'cross-account read denied')
  check(call(b,f'/sessions/{sid}/answers',payload)[0]==404,'cross-account write denied')
  for i,q in enumerate(s['questions'][1:],1):
   status,s=call(a,f'/sessions/{sid}/answers',{'questionId':q['id'],'key':'integration-key-000'+str(i+1),'answer':'I would explain the main concept, provide a concrete example and check the relevant assumptions.'})
   check(status==200,f'answer {i+1}')
  check(s['status']=='COMPLETED' and len(s['answers'])==5,'session completion')
  check(len(call(a,'/sessions')[1])==1,'history')
  check(call(a,'/auth/logout',{})[0]==200 and call(a,'/me')[0]==401,'logout invalidates access')
  proc.terminate();proc.wait();proc=start()
  check(call(a,'/auth/login',account)[0]==200,'login after restart')
  check(call(a,f'/sessions/{sid}')[1]['status']=='COMPLETED','history persists after process restart')
  check(call(a,'/sessions',{'role':'Java developer','level':'Intermediate','mode':'ai'})[0]==400,'unconfigured AI cannot masquerade as AI feedback')
 finally:proc.terminate();proc.wait()
print('All integration tests passed.')

# Exercise the real AI adapter against a controlled local provider stub.
# This verifies response validation and recovery, not a commercial model's quality.
import http.server, threading
class Provider(http.server.BaseHTTPRequestHandler):
 mode='invalid'
 def do_POST(self):
  request=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  assert 'candidate_answer' in request['messages'][1]['content']
  content='not valid JSON' if Provider.mode=='invalid' else json.dumps({'strength':'You identified the topic.','gap':'Explain the reason.','next':'Add a concrete example.'})
  data=json.dumps({'choices':[{'message':{'content':content}}]}).encode()
  self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
provider=http.server.HTTPServer(('127.0.0.1',0),Provider)
threading.Thread(target=provider.serve_forever,daemon=True).start()
with tempfile.TemporaryDirectory() as tmp:
 build=pathlib.Path(tmp)/'classes';build.mkdir()
 subprocess.run(['java','com.sun.tools.javac.Main','--release','17','-d',str(build),*[str(p) for p in (ROOT/'src/main/java/com/interview').glob('*.java')]],check=True)
 env=dict(os.environ,PORT=str(PORT),DATA_DIR=tmp+'/data',AI_API_KEY='test-only-not-a-real-secret',AI_ENDPOINT=f'http://localhost:{provider.server_port}/chat')
 proc=start()
 try:
  c=client();call(c,'/auth/register',{'name':'AI test','email':'ai@example.com','password':'test-password-123'})
  status,s=call(c,'/sessions',{'role':'Java developer','level':'Beginner','mode':'ai'})
  check(status==201,'AI mode available with server configuration')
  sid=s['id'];payload={'questionId':s['questions'][0]['id'],'key':'ai-integration-key-01','answer':'I would explain a contract and how a class implements that contract with an instance.'}
  status,s=call(c,f'/sessions/{sid}/answers',payload)
  check(status==200 and s['answers'][0]['status']=='FAILED','malformed AI output rejected')
  check(s['answers'][0]['answer']==payload['answer'],'answer survives evaluator failure')
  Provider.mode='valid'
  status,s=call(c,f'/sessions/{sid}/retry',{'key':payload['key']})
  check(status==200 and s['answers'][0]['status']=='READY','failed evaluation recovers on retry')
  check(s['answers'][0]['feedback']['mode']=='AI-assisted feedback','AI feedback labelled correctly')
  check(call(c,f'/sessions/{sid}/retry',{'key':payload['key']})[0]==409,'ready feedback cannot be charged for a duplicate retry')
 finally:proc.terminate();proc.wait();provider.shutdown()
print('AI adapter tests passed (controlled provider stub).')

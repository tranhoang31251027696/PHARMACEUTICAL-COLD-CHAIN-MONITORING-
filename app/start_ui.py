"""Serve the dashboard and a local, independently checked regression API."""
from pathlib import Path
import argparse, http.server, json, socketserver, sys, os, urllib.request, urllib.error, webbrowser

ROOT = Path(__file__).resolve().parent
DIRECTORY = ROOT / 'NETLIFY_DASHBOARD'
REMOTE = os.environ.get('COLDCHAIN_MODEL_API', 'https://coldchain-backend-jq65.onrender.com').rstrip('/')
MAX_BODY = 20 * 1024 * 1024
sys.path.insert(0, str(ROOT / 'backend'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        if self.path == '/api/local-health':
            try:
                import numpy
                available, error = True, None
            except ImportError:
                available, error = False, 'Install requirements-ui.txt to enable exact regression checking'
            self.send_json({'service': 'coldchain-local', 'regression_available': available,
                            'max_regression_rows': 2000, 'error': error,
                            'scope': 'Local research adapter, not a production authentication service'})
        elif self.path.split('?', 1)[0] in ('/health', '/api/fefo', '/api/batches', '/api/products', '/api/alerts') or self.path.startswith(('/api/predictions/', '/api/sensor/')):
            try:
                with urllib.request.urlopen(REMOTE+self.path, timeout=70) as response:
                    return self.send_json(json.loads(response.read()), response.status)
            except urllib.error.HTTPError as e:
                try: data = json.loads(e.read())
                except Exception: data = {'detail':f'Model/data backend HTTP {e.code}'}
                return self.send_json(data, e.code)
            except (OSError, ValueError) as e:
                return self.send_json({'detail':'Historical data backend unavailable: '+str(e)}, 502)
        elif self.path in ('/sample/sensor.csv', '/sample/fefo.csv', '/sample/regression.csv'):
            names = {'sensor.csv':'sample_sensor_BATCH-01004.csv', 'fefo.csv':'sample_fefo_batches.csv',
                     'regression.csv':'sample_regression.csv'}
            p = ROOT/'SAMPLE_DATASETS'/names[self.path.rsplit('/', 1)[1]]
            raw = p.read_bytes(); self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)
        else:
            super().do_GET()

    def do_POST(self):
        if self.headers.get('Origin'):
            from urllib.parse import urlsplit
            origin = urlsplit(self.headers['Origin'])
            if origin.netloc != self.headers.get('Host') or origin.scheme != 'http':
                return self.send_json({'detail':'Cross-origin local requests are refused'}, 403)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_BODY:
                return self.send_json({'detail':'JSON body is empty or exceeds 20 MiB'}, 413)
            if 'application/json' not in self.headers.get('Content-Type', ''):
                return self.send_json({'detail':'Expected application/json'}, 415)
            raw = self.rfile.read(size)
            body = json.loads(raw)
            if self.path in ('/api/regression', '/api/check-certificate'):
                from regression_service import diagnose
                return self.send_json(diagnose(body, check_only=self.path.endswith('check-certificate')))
            if self.path == '/api/live-model-pair':
                from live_models import predict_pair
                return self.send_json(predict_pair(body))
            if self.path == '/predict':
                # Only this fixed inference endpoint is proxied; callers cannot choose a URL.
                req = urllib.request.Request(REMOTE+'/predict', data=raw,
                       headers={'Content-Type':'application/json'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=80) as response:
                        return self.send_json(json.loads(response.read()), response.status)
                except urllib.error.HTTPError as e:
                    try: data = json.loads(e.read())
                    except Exception: data = {'detail':f'Model backend HTTP {e.code}'}
                    return self.send_json(data, e.code)
                except (OSError, TimeoutError) as e:
                    return self.send_json({'detail':'Model backend unavailable; inference was not verified: '+str(e)}, 502)
            return self.send_json({'detail':'Unknown endpoint'}, 404)
        except (ValueError, TypeError, KeyError, AssertionError, IndexError, OverflowError, ZeroDivisionError) as e:
            return self.send_json({'detail':str(e) or 'Certificate rejected by independent checker',
                                   'verified':False}, 400)
        except ImportError:
            return self.send_json({'detail':'Local research dependencies are unavailable; install requirements-ui.txt',
                                   'verified':False}, 503)
        except Exception:
            return self.send_json({'detail':'Local computation failed; no verified verdict issued',
                                   'verified':False}, 500)

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def main():
    if not __debug__:
        raise RuntimeError('Do not run this service with python -O: checker assertions are required')
    try:
        import numpy
    except ImportError:
        candidate = ROOT.parent/'BACKUP/Q1_revision_v5/env/Scripts/python.exe'
        if candidate.is_file() and Path(sys.executable).resolve() != candidate.resolve():
            os.execv(str(candidate), [str(candidate), str(Path(__file__).resolve()), *sys.argv[1:]])
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    for port in dict.fromkeys([args.port, 8080, 8088, 8888, 3000]):
        try: server = Server(('127.0.0.1', port), Handler)
        except OSError: continue
        url = f'http://127.0.0.1:{port}'
        print('ColdChain UI: '+url, flush=True)
        print('Uploads drive the app for this browser session. Auto-inference sends sensor histories to the configured backend; disable it before upload for local analysis only.', flush=True)
        if not args.no_browser: webbrowser.open(url)
        try: server.serve_forever()
        except KeyboardInterrupt: pass
        finally: server.server_close()
        return
    raise RuntimeError('No available local port')

if __name__ == '__main__': main()

"""Integration tests: real producer/checker over loopback, no remote model calls."""
from pathlib import Path
import sys, unittest, threading, urllib.request, urllib.error, json, copy, hashlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import start_ui

class LocalAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = start_ui.Server(('127.0.0.1', 0), start_ui.Handler)
        cls.base = 'http://127.0.0.1:' + str(cls.server.server_port)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True); cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(timeout=3)

    def post(self, payload, path='/api/regression', origin=None):
        headers = {'Content-Type': 'application/json'}
        if origin: headers['Origin'] = origin
        request = urllib.request.Request(self.base+path, json.dumps(payload).encode(), headers, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def payload(self):
        return dict(labels=[1,0,1], reference_scores=[.9,.5,.2], actual_scores=[.1,.5,.9],
                    ids=['A','B','C'], lo='0.30', hi='0.90',
                    query=dict(semantics='rational', kind='finite', values=['0.5','0.8','0.9']))

    def test_divergence_and_query_agreement(self):
        status, data = self.post(self.payload())
        self.assertEqual(status, 200); self.assertEqual(data['status'], 'DIVERGENT')
        self.assertTrue(data['verification']['verified'])
        self.assertEqual(data['query_result']['affected'], data['boolean_result']['affected'])

    def test_equivalence(self):
        p = self.payload(); p['actual_scores'] = p['reference_scores']
        status, data = self.post(p)
        self.assertEqual(status, 200); self.assertEqual(data['status'], 'EQUIVALENT')

    def test_endpoint_only_psc_zero(self):
        p = dict(labels=[1,0], reference_scores=[1.,0.], actual_scores=[1.,0.], ids=['A','B'],
                 lo='0.5', hi='1', new_precision='strict',
                 query=dict(semantics='rational', kind='lattice', lo='0.5', hi='1', left_closed=True, right_closed=True, decimal_places=2))
        status, data = self.post(p)
        self.assertEqual(status, 200); self.assertEqual(data['status'], 'DIVERGENT')
        self.assertEqual(data['certificate']['psc_exact'], '0'); self.assertTrue(data['query_result']['affected'])

    def test_certificate_replay_and_tamper(self):
        _, data = self.post(self.payload()); wrapper = data['download']
        status, replay = self.post(wrapper, '/api/check-certificate')
        self.assertEqual(status, 200); self.assertTrue(replay['verified'])
        wrapper = copy.deepcopy(wrapper); wrapper['certificate']['equivalent'] = True
        status, rejected = self.post(wrapper, '/api/check-certificate')
        self.assertEqual(status, 400); self.assertFalse(rejected['verified'])

    def test_invalid_inputs_refused(self):
        for key, value in [('labels',[2,0,1]), ('ids',['A','A','C']), ('new_ids',['X','B','C']),
                           ('lo',.3), ('reference_scores',[float('nan'),.5,.2])]:
            with self.subTest(key=key):
                p = self.payload(); p[key] = value
                self.assertEqual(self.post(p)[0], 400)

    def test_local_cross_origin_refused(self):
        self.assertEqual(self.post(self.payload(), origin='http://unrelated.invalid')[0], 403)

    def test_imported_research_bytes_unchanged(self):
        root = Path(__file__).resolve().parents[1]/'backend/engine'
        m = json.loads((root/'SOURCE_MANIFEST.json').read_text(encoding='utf-8'))
        for n, digest in m['sha256'].items():
            self.assertEqual(hashlib.sha256((root/n).read_bytes()).hexdigest(), digest, n)

if __name__ == '__main__': unittest.main()

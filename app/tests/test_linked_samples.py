"""Replay the linked demo against real frozen models and independent checker."""
import csv, hashlib, json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from live_models import predict_pair
from regression_service import diagnose

class LinkedSamplesTest(unittest.TestCase):
    def test_cached_scores_replay_on_the_same_sensor_and_inventory(self):
        samples = ROOT / 'NETLIFY_DASHBOARD' / 'samples'
        cache = json.loads((samples / 'sample_linked_predictions.json').read_text(encoding='utf-8'))
        with (samples / 'sample_linked_inventory.csv').open(encoding='utf-8-sig') as f:
            inventory_ids = {r['Batch_ID'] for r in csv.DictReader(f)}
        for filename, groups in cache.items():
            with (samples / filename).open(encoding='utf-8-sig') as f:
                raw = list(csv.DictReader(f))
            for batch, stored in groups.items():
                with self.subTest(file=filename, batch=batch):
                    self.assertIn(batch, inventory_ids)
                    self.assertEqual(stored['live_prediction']['sensor_file_sha256'], hashlib.sha256((samples / filename).read_bytes()).hexdigest())
                    rows = [dict(Batch_ID=batch, Timestamp=r['Timestamp'], calibrated_temp=float(r.get('calibrated_temp') or r.get('actual_temp') or r['Temperature']), Humidity=float(r.get('Humidity') or 60), Shipment_Mode=r.get('Shipment_Mode') or 'Air') for r in raw if r['Batch_ID'] == batch]
                    fresh = predict_pair(dict(readings=rows, history_complete=True))
                    self.assertEqual(fresh['payload'], stored['payload'])
                    result = diagnose(stored['payload'])
                    self.assertTrue(result['verified'])
                    self.assertTrue(result['verification']['verified'])

if __name__ == '__main__':
    unittest.main()

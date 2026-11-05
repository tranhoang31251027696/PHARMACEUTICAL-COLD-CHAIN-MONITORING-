import sys,unittest,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from live_models import predict_pair
class LiveModelsTest(unittest.TestCase):
 def rows(self):
  import datetime
  return [dict(Batch_ID='NEW',Timestamp=(datetime.datetime(2026,1,1)+datetime.timedelta(hours=i)).isoformat(),calibrated_temp=5+(i%7)*.3,Humidity=60,Shipment_Mode='Air') for i in range(48)]
 def test_fresh_predictions_and_input_sensitivity(self):
  rows=self.rows();a=predict_pair(dict(readings=rows,history_complete=True))
  self.assertEqual(a['count'],39);self.assertEqual(len(a['live_prediction']['models']),2)
  altered=copy.deepcopy(rows)
  for r in altered:r['calibrated_temp']=2.1
  b=predict_pair(dict(readings=altered,history_complete=True))
  self.assertNotEqual(a['payload']['reference_scores'],b['payload']['reference_scores'])
  self.assertNotEqual(a['live_prediction']['input_sha256'],b['live_prediction']['input_sha256'])
  self.assertTrue(all(0<=p<=1 for p in a['payload']['actual_scores']))
 def test_requires_complete_regular_history(self):
  with self.assertRaises(ValueError):predict_pair(dict(readings=self.rows(),history_complete=False))
  rows=self.rows();del rows[8]
  with self.assertRaises(ValueError):predict_pair(dict(readings=rows,history_complete=True))
 def test_future_changes_do_not_change_past_scores(self):
  rows=self.rows();a=predict_pair(dict(readings=rows,history_complete=True));rows[-1]['calibrated_temp']=10
  b=predict_pair(dict(readings=rows,history_complete=True))
  self.assertEqual(a['payload']['reference_scores'],b['payload']['reference_scores'])
  self.assertEqual(a['payload']['actual_scores'],b['payload']['actual_scores'])
if __name__=='__main__':unittest.main()

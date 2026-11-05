const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const R = require(path.join(root, 'NETLIFY_DASHBOARD/coldchain-runtime.js'));
for (const [name, kind, count] of [
  ['sample_sensor_BATCH-01004.csv', 'sensor', 336],
  ['sample_sensor_multi_batch.csv', 'sensor', 888],
  ['sample_fefo_batches.csv', 'inventory', 50],
  ['sample_regression.csv', 'regression', 2000]
]) {
  const d = R.normalize(fs.readFileSync(path.join(root, 'SAMPLE_DATASETS', name), 'utf8'), { defaultShipment: 'Air', defaultHumidity: 60 });
  assert.equal(d.kind, kind); assert.equal(d.count, count);
}
assert.equal(R.parseCSV('a,b,c\nA,,C\n').rows[0][1], '');
const regression = R.normalize(fs.readFileSync(path.join(root, 'SAMPLE_DATASETS/sample_regression.csv'), 'utf8'));
assert.deepEqual(regression.modelNames, ['XGBoost thermal (6h)', 'XGBoost thermal + Arrhenius (6h)']);
assert.equal(regression.payload.labels.reduce((sum, label) => sum + label, 0), 18);
assert.deepEqual(R.normalize('id,y,old_score,new_score\nx,1,.8,.9').modelNames, [null, null]);
assert.throws(() => R.normalize('id,y,old_score,new_score,reference_model\nx,1,.8,.9,A\nz,0,.7,.6,B'), /same model/);
assert.equal(R.parseCSV('a,b\n"x,y","two\nlines"\n').rows[0][1], 'two\nlines');
assert.equal(R.parseCSV('\uFEFFa;b\r\n"x;y";2\r\n').delimiter, ';');
assert.equal(R.parseCSV('a\tb\r1\t2\r').delimiter, '\t');
assert.throws(() => R.parseCSV('a,a\n1,2'), /unique|Duplicate/);
assert.throws(() => R.parseCSV('a,b\n"unfinished,2'), /unclosed/);
assert.throws(() => R.parseCSV('a,b\n1,2,3'), /3 cells/);
assert.throws(() => R.normalize('id,y,old_score,new_score\nx,1,,.3'), /finite/);
assert.throws(() => R.normalize('id,y,old_score,new_score\nx,2,.4,.3'), /0 or 1/);
assert.throws(() => R.normalize('id,y,old_score,new_score\nx,1,.4,.3\nx,0,.2,.1'), /unique|Duplicate/);
assert.throws(() => R.normalize('Timestamp,calibrated_temp,Humidity\n2026-02-30,5,60', { defaultShipment: 'Air' }), /Invalid date or time/);
const zero = R.normalize('Timestamp,calibrated_temp,Humidity\n2026-01-01,5,0', { defaultShipment: 'Air' });
assert.equal(zero.batches['UPLOADED-BATCH'][0].Humidity, 0);
const inv = R.normalize('product_id,batch_id,dynamic_expiry_date\nP,B,2027-01-01 00:00:00.000000002\nP,A,2027-01-01 00:00:00.000000001\nP,C,2027-01-01 00:00:00.000000001');
assert.deepEqual(inv.rows.map(x => x.FEFO_Rank), [1, 1, 2]);
assert.equal(inv.rows[0].Product_ID, 'P');
assert.equal(R.arrhenius(5).ratio, 1); assert(R.arrhenius(8).ratio > 1);
assert.throws(() => R.arrhenius(-274));
assert.throws(() => R.modelTimestamp('2026-01-01T00:00:00Z', false), /timezone/);
assert.equal(R.modelTimestamp('2026-01-01T07:00:00+07:00', true), '2026-01-01 00:00:00.000');
console.log('PASS: shipped datasets, CSV edge cases, validation, FEFO dense ties, Arrhenius and explicit timezone conversion');

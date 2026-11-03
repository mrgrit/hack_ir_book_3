import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_dataset import check
from prepare_round import prepare,validate_args
from profile_labeling import summarize,analyze


class OfflineTests(unittest.TestCase):
    def test_interval_diagnostic_does_not_claim_seconds(self):
        r={'day_cnt':2,'log_line':4,'log_len':100,'mean_tg':360,'log_start':datetime(2019,1,1),'log_end':datetime(2019,1,2)}
        out=summarize([r])
        self.assertEqual(out['interval_unit_diagnostics']['span_over_gap_log_line']['near_60_ratio_count'],1)
        self.assertIn('unconfirmed',out['gap_unit'])

    def test_snapshot_order_is_not_caller_order(self):
        a=Path('labeling_2019-05-26.xlsx');b=Path('labeling_2019-05-30.xlsx')
        def reader(path,policy):
            return ([{'ip':'private-identity','day_cnt':1 if path==a else 20,'log_end':datetime(2019,5,26 if path==a else 30)}], {'file':path.name})
        with patch('profile_labeling.read_snapshot',side_effect=reader):
            x=analyze([b,a],'last');y=analyze([a,b],'last')
        self.assertEqual(x,y);self.assertEqual(x['latest_per_source']['class_counts'],{'persistent':1})
        self.assertNotIn('private-identity',json.dumps(x))

    def test_invalid_or_short_runs_fail_before_generation(self):
        with tempfile.TemporaryDirectory() as t:
            a=argparse.Namespace(days=7,scale=0.005,run_id='test',round='r01',anchor='2026-11-01',out=Path(t)/'new')
            with self.assertRaises(ValueError):validate_args(a)
            a.days=90;a.scale=float('nan')
            with self.assertRaises(ValueError):validate_args(a)
            a.scale=0.005;a.run_id='../../shared'
            with self.assertRaises(ValueError):validate_args(a)

    @unittest.skipUnless(os.environ.get('BOOK3_SOURCE'),'Set BOOK3_SOURCE for integration checks')
    def test_determinism_order_truth_and_no_network(self):
        source=Path(os.environ['BOOK3_SOURCE'])
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            def args(out,rnd='r01'):
                return argparse.Namespace(source=source,round=rnd,anchor='2026-11-01',days=90,scale=0.005,run_id='test',out=root/out)
            with patch('socket.create_connection',side_effect=AssertionError('network forbidden')):
                first=prepare(args('a'));second=prepare(args('b'))
                self.assertEqual(first,second)
                self.assertGreater(first['input_time_inversions'],0)
                self.assertTrue(check(root/'a')['chronological'])
                self.assertEqual(first['files'],second['files'])
                with self.assertRaises(FileExistsError):prepare(args('a'))
                r08=prepare(args('r08','r08'))
                self.assertEqual(r08['scenario_outside_window_before_upstream_filter']['at_or_after_end'],10)
                self.assertEqual(check(root/'r08')['events'],r08['total'])
            f=root/'a'/'events.bulk.ndjson'
            with f.open('a',encoding='utf-8') as o:o.write('{}\n')
            with self.assertRaisesRegex(ValueError,'Hash mismatch'):check(root/'a')


if __name__=='__main__':unittest.main(verbosity=2)

import unittest, time, sys, random 
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_glm, h2o_hosts, h2o_import as h2i, h2o_jobs, h2o_exec as h2e

DO_POLL = False
class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        localhost = h2o.decide_if_localhost()
        if (localhost):
            h2o.build_cloud(1,java_heap_GB=4, base_port=54323)
        else:
            h2o_hosts.build_cloud_with_hosts(base_port=54323)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_frame_split(self):
        h2o.beta_features = True

        csvFilename = 'covtype.data'
        csvPathname = 'standard/' + csvFilename
        hex_key = "covtype.hex"

        parseResult = h2i.import_parse(bucket='home-0xdiag-datasets', path=csvPathname, hex_key=hex_key, schema='local', timeoutSecs=20)

        print "Just split away and see if anything blows up"
        splitMe = hex_key
        inspect = h2o_cmd.runInspect(key=splitMe)
        origNumRows = inspect['numRows']
        origNumCols = inspect['numCols']
        for s in range(20):
            inspect = h2o_cmd.runInspect(key=splitMe)
            numRows = inspect['numRows']
            numCols = inspect['numCols']
            fs = h2o.nodes[0].frame_split(source=splitMe, ratios=0.5)
            split0_key = fs['split_keys'][0]
            split1_key = fs['split_keys'][1]
            split0_rows = fs['split_rows'][0]
            split1_rows = fs['split_rows'][1]
            split0_ratio = fs['split_ratios'][0]
            split1_ratio = fs['split_ratios'][1]
            print "Iteration", s, "split0_rows:", split0_rows, "split1_rows:", split1_rows
            splitMe = split1_key
            # split should be within 1 row accuracy. let's say within 20 for now
            self.assertLess(abs(split1_rows - split0_rows), 2)
            self.assertEqual(numRows, (split1_rows + split0_rows))
            self.assertEqual(numCols, origNumCols)
            if split0_rows <= 2:
                break

if __name__ == '__main__':
    h2o.unit_main()

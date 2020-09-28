from ..main import Program
import json
import unittest


class MainTests(unittest.TestCase):
    def setUp(self):

        p = r"C:\Users\dimansf\Documents\projects\raspil_rt\raspil_rt\tests\resources\json1.txt"

        with open(p) as f:
            result = json.loads(f.read())
            print(len(result['store']))
            self.pp = Program(result['orders'], result['store'],
                              result['optimize'], result['scladMax'], result['widthSaw'])

    def tearDown(self):
        pass

    def test_main(self):
        self.pp.main()
        print(self.pp.map_result)

import unittest
import simpy
import numpy as np
from models import source_model

class ModelTest(unittest.TestCase):

    def setUp(self):
        self.env = simpy.Environment()
        Q = np.array([[0.1,0.2,0.3,0.4], [0.25,0.25,0.25,0.25], [0.15, 0.25, 0.35, 0.25], [0,0.3,0.3,0.4]])
        Lambda = np.array([0.5, 1.0, 1.5, 2.0])
        self.src = source_model.MMPPModel(Q, Lambda)
        pass

    def tearDown(self):
        pass

    def test_transition(self):
        rec = dict()
        for i in range(100000):
            if self.src.cur_state not in rec.keys():
                rec[self.src.cur_state] = 1
            else:
                rec[self.src.cur_state] += 1
            self.src.get_interval()
        print([item / 100000 for (key,item) in rec.items()])
        epsilon = np.ones((len(rec.keys()))) * 0.001
        pi = np.array([.25,.25,.25,.25])
        last = pi
        while True:
            last = pi
            pi = np.dot(pi, self.src.Q)
            if np.all((last - pi) < epsilon):
                break
        print(pi)

if __name__ == '__main__':
    unittest.main()

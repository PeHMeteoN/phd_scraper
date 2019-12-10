import unittest
import pandas as pd
import senh_hist as sh


class SimpleTest(unittest.TestCase):
    df = "./test_157317.csv"
    sh.download_data(code = '157317', output=df)
    df_dataset = pd.read_csv(df)
    mean_values = df_dataset.mean()
    
    def test_prec(self):
        self.assertAlmostEqual(mean_values[0], 1.13143064, places=5)
    def test_tn(self):
        self.assertAlmostEqual(mean_values[1], 20.941465, places=5)
    def test_tx(self):
        self.assertAlmostEqual(mean_values[2], 0.782993, places=5)

if __name__ == '__main__':
    unittest.main()
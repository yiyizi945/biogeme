import os
import unittest
import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme import models
from biogeme.expressions import (
    Beta,
    bioDraws,
    log,
    MonteCarlo,
    PanelLikelihoodTrajectory,
)

myPath = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(f'{myPath}/swissmetro.dat', sep='\t')
database = db.Database('swissmetro', df)

database.panel('ID')

# The Pandas data structure is available as database.data. Use all the
# Pandas functions to invesigate the database
# print(database.data.describe())

globals().update(database.variables)

exclude = ((PURPOSE != 1) * (PURPOSE != 3) + (CHOICE == 0)) > 0
database.remove(exclude)

ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_SM = Beta('ASC_SM', 0, None, None, 1)
B_TIME = Beta('B_TIME', 0, None, None, 0)
B_COST = Beta('B_COST', 0, None, None, 0)

SIGMA_CAR = Beta('SIGMA_CAR', 0, None, None, 0)
SIGMA_SM = Beta('SIGMA_SM', 0, None, None, 1)
SIGMA_TRAIN = Beta('SIGMA_TRAIN', 0, None, None, 0)


# Define a random parameter, normally distirbuted, designed to be used
# for Monte-Carlo simulation
EC_CAR = SIGMA_CAR * bioDraws('EC_CAR', 'NORMAL')
EC_SM = SIGMA_SM * bioDraws('EC_SM', 'NORMAL')
EC_TRAIN = SIGMA_TRAIN * bioDraws('EC_TRAIN', 'NORMAL')


SM_COST = SM_CO * (GA == 0)
TRAIN_COST = TRAIN_CO * (GA == 0)

TRAIN_TT_SCALED = database.DefineVariable('TRAIN_TT_SCALED', TRAIN_TT / 100.0)
TRAIN_COST_SCALED = database.DefineVariable(
    'TRAIN_COST_SCALED', TRAIN_COST / 100
)
SM_TT_SCALED = database.DefineVariable('SM_TT_SCALED', SM_TT / 100.0)
SM_COST_SCALED = database.DefineVariable('SM_COST_SCALED', SM_COST / 100)
CAR_TT_SCALED = database.DefineVariable('CAR_TT_SCALED', CAR_TT / 100)
CAR_CO_SCALED = database.DefineVariable('CAR_CO_SCALED', CAR_CO / 100)

V1 = (
    ASC_TRAIN
    + B_TIME * TRAIN_TT_SCALED
    + B_COST * TRAIN_COST_SCALED
    + EC_TRAIN
)
V2 = ASC_SM + B_TIME * SM_TT_SCALED + B_COST * SM_COST_SCALED + EC_SM
V3 = ASC_CAR + B_TIME * CAR_TT_SCALED + B_COST * CAR_CO_SCALED + EC_CAR

# Associate utility functions with the numbering of alternatives
V = {1: V1, 2: V2, 3: V3}


# Associate the availability conditions with the alternatives
CAR_AV_SP = database.DefineVariable('CAR_AV_SP', CAR_AV * (SP != 0))
TRAIN_AV_SP = database.DefineVariable('TRAIN_AV_SP', TRAIN_AV * (SP != 0))

av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

obsprob = models.logit(V, av, CHOICE)
condprobIndiv = PanelLikelihoodTrajectory(obsprob)
logprob = log(MonteCarlo(condprobIndiv))


class test_13(unittest.TestCase):
    def testEstimation(self):
        biogeme = bio.BIOGEME(database, logprob, numberOfDraws=5, seed=10)
        biogeme.saveIterations = False
        biogeme.generateHtml = False
        biogeme.generatePickle = False
        results = biogeme.estimate()
        self.assertAlmostEqual(results.data.logLike, -4634.307424865441, 2)


if __name__ == '__main__':
    unittest.main()

from prophet import Prophet
import pandas as pd
from datetime import datetime
from Day import *
import os

# class suppress_stdout_stderr(object):
#     '''
#     A context manager for doing a "deep suppression" of stdout and stderr in
#     Python, i.e. will suppress all print, even if the print originates in a
#     compiled C/Fortran sub-function.
#        This will not suppress raised exceptions, since exceptions are printed
#     to stderr just before a script exits, and after the context manager has
#     exited (at least, I think that is why it lets exceptions through).

#     '''
#     def __init__(self):
#         # Open a pair of null files
#         self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
#         # Save the actual stdout (1) and stderr (2) file descriptors.
#         self.save_fds = (os.dup(1), os.dup(2))

#     def __enter__(self):
#         # Assign the null pointers to stdout and stderr.
#         os.dup2(self.null_fds[0], 1)
#         os.dup2(self.null_fds[1], 2)

#     def __exit__(self, *_):
#         # Re-assign the real stdout/stderr back to (1) and (2)
#         os.dup2(self.save_fds[0], 1)
#         os.dup2(self.save_fds[1], 2)
#         # Close the null files
#         os.close(self.null_fds[0])
#         os.close(self.null_fds[1])

class ProphetDemandEstimator:


    @staticmethod
    def getModel(item,typeDoc, startDate = datetime(2021,1,1)):

        # with suppress_stdout_stderr():
        df = item.itemHistory.dfs[typeDoc]
        df = df[(df['date']>=startDate)]
        d = {'ds':list(df['date']),'y':list(df['sale'])}
        df = pd.DataFrame(d)
        df.reset_index(level=0, inplace=True)
        prophet_basic = Prophet()
        prophet_basic.fit(df)
        return prophet_basic

    @staticmethod
    def estimate(prophet_basic,months):

        # with suppress_stdout_stderr():
        today = Day.getToday()

        if type(months) == list:
            ans = []
            for month in months:
                future = prophet_basic.make_future_dataframe(periods=30 * month)
                forecast = prophet_basic.predict(future)
                ans += [forecast[(forecast['ds']>today)]['yhat'].sum()]
            return ans
        else:
            future = prophet_basic.make_future_dataframe(periods=30 * months)
            forecast = prophet_basic.predict(future)
            return forecast[(forecast['ds']>today)]['yhat'].sum()




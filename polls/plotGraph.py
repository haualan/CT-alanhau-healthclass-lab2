import plotly.plotly as py
from plotly.graph_objs import *
import FatBitAPI, ohmageData
import numpy as np

def plotGraph():
  # gather fitbit data
  fitBitTS = FatBitAPI.getFloorsTimeSeries()

  dt = np.dtype([('dates', 'datetime64[D]'), ('flrs', np.int8)])
  TS = np.array(fitBitTS, dtype=dt)
  # print TS
  fb_dates = TS['dates']
  fb_flrs = TS['flrs']
  # print dates, flrs 

  # gather PAM ohmage data
  a = ohmageData.ohmageDataClass()
  negative_affect, positive_affect, pam_datetimes = a.parse_pam(a.getDataPoints(schema_namespace = 'omh', schema_name = 'pam'))


  # gather Mobility data from omh
  mobilty_walking_distance_in_km, mobilty_dates = a.parse_mobility_daily_summary(a.getDataPoints(schema_namespace = 'cornell', schema_name = 'mobility-daily-summary'))


  # prep Time Series for plot
  fitBit_trace = Scatter(
      x=fb_dates,
      y=fb_flrs,
      name = 'fitBit Floors Climbed'
  )
  # data = Data([trace0])

  pam_neg_trace = Scatter(
      x=pam_datetimes,
      y=negative_affect,
      name = 'PAM negative affect'
  )

  pam_pos_trace = Scatter(
      x=pam_datetimes,
      y=positive_affect,
      name = 'PAM positive affect'
  )

  mobility_daily_trace = Scatter(
      x=mobilty_dates,
      y=mobilty_walking_distance_in_km,
      name = 'Mobility daily walking distance in km'
  )



  data = Data([ fitBit_trace, mobility_daily_trace, pam_neg_trace, pam_pos_trace ])

  # print data

  unique_url = py.plot(data, filename = 'basic-line', auto_open=False)
  # print unique_url
  return unique_url

if __name__ == "__main__":
  
  # b = FatBitAPI.getFloorsTimeSeries()
  # print b
  url = plotGraph()
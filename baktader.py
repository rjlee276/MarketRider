from __future__ import (absolute_import, division, print_function, unicode_literals)
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.analyzers as btanalyzers
import datetime
import os.path
import sys
from strategies.trendfollowing import TrendFollowingStrategy
from strategies.trendfollowing_rsi import TrendFollowingStrategyRSI
import pandas as pd


if __name__ == '__main__':
  cerebro = bt.Cerebro()

  # Add strategies to engine!
  cerebro.addstrategy(TrendFollowingStrategy)

  modpath = os.getcwd()
  datapath = os.path.join(modpath, 'data/BTC-USD.csv')

  data = btfeeds.YahooFinanceCSVData(
    dataname=datapath,
    fromdate = datetime.datetime(2014, 11, 1),
    todate = datetime.datetime(2023, 12, 31),
    reverse=False)

  cerebro.adddata(data)

  cerebro.broker.setcash(500000.0)

  # fixed sizer according to stake (always buy 1 share)
  # TODO make this variable by applying position sizing
  # cerebro.addsizer(bt.sizers.FixedSize, stake=1)

  cerebro.broker.setcommission(commission=0.001)

  # Analyzers to determine how well a strategy performs
  cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
  cerebro.addanalyzer(btanalyzers.Returns, _name='myreturns')
  cerebro.addanalyzer(btanalyzers.AnnualReturn, _name='myannualreturns')
  cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')

  print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

  back = cerebro.run(maxcpus=1)

  # Access and print the results of each analyzer
  for strategy in back:
      print('Results for Strategy:', strategy.name)

      # Sharpe Ratio
      sharpe_ratio = strategy.analyzers.mysharpe.get_analysis()['sharperatio']
      print('Sharpe Ratio:', sharpe_ratio)

      # Returns
      returns = strategy.analyzers.myreturns.get_analysis()['rnorm100']
      print('Returns:', returns)

      # Annual Returns
      annual_returns = strategy.analyzers.myannualreturns.get_analysis()
      for key, value in annual_returns.items():
          print('Annual Returns:', key, value)

      # Drawdown
      drawdown = strategy.analyzers.mydrawdown.get_analysis()
      for key, value in drawdown.items():
          print('Drawdown:', key, value)
      print('\n\n')


  print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

  cerebro.plot()
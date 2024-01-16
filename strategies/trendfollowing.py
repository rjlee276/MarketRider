import backtrader as bt


class TrendFollowingStrategy(bt.Strategy):

  # Prev: 26, 38 for short and long periods
  params = (
    ('short_period', 27),
    ('long_period', 30),
    ('print', False),
    ('stoploss', 2),
    ('trail', False),
    ('risk_perc', 1)
  )

  def __init__(self):
    self.dataclose = self.datas[0].close

    self.name = "Trend Following Strategy"

    self.order = None
    self.stop_loss_order = None
    self.stop_loss_price = None
    self.stoploss = self.params.stoploss / 100

    self.short_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.short_period)
    self.long_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.long_period)


  # logging function to print out the date and close price of the security
  def log(self, txt, dt=None, doprint=False):
    
    if self.params.print or doprint:
      dt = dt or self.datas[0].datetime.date(0)
      print('%s, %s' % (dt.isoformat(), txt))
      print('Position Size: %s' % self.position.size)

  def next(self):

    # check if order is pending
    if self.order:
      return

    # if not in market already (will have to tweak this to allow for multiple positions)
    if not self.position.size > 0:
      if self.short_sma > self.long_sma:
        
        cash = self.broker.get_cash()
        risk_amount = cash * (self.params.risk_perc / 100)

        # calculate number of shares to buy
        stop_price = self.dataclose[0] * (1.0 - self.stoploss)
        risk_per_share = self.dataclose[0] - stop_price
        size = risk_amount / risk_per_share

        self.log('BUY CREATE, %.2f, SIZE: %.2f' % (self.dataclose[0], size))
        self.order = self.buy(size=size)

    # if in market
    else:
      if self.short_sma < self.long_sma:
        self.log('SELL CREATE, %.2f' % self.dataclose[0])
        self.order = self.close()
      
  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      # Buy/Sell order submitted/accepted to/by broker - Nothing to do
      return
    
    # Check if an order has been completed
    # Broker could reject order if not enough cash
    if order.status in [order.Completed]:
      
      if order.isbuy():
        self.log('BUY EXECUTED, Size: %.2f, Price: %.2f, Cost: %.2f, Comm: %.2f' % (order.executed.size, order.executed.price, order.executed.value, order.executed.comm))
        self.buyprice = order.executed.price
        self.buycomm = order.executed.comm

        stop_price = self.buyprice * (1.0 - self.stoploss)

        # ===================RISK MANAGEMENT====================
        if self.params.trail:
          self.stop_loss_order = self.sell(exectype=bt.Order.StopTrail, trailamount=self.params.trail)
        else:
          self.stop_loss_order = self.sell(exectype=bt.Order.Stop, price=stop_price, size=self.position.size)
          self.stop_loss_price = stop_price

      else: # sell order executed
        self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
    
      self.bar_executed = len(self)

      
    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

    self.order = None

  def stop(self):
    self.log('(Short Period %2d, Long Period %2d) ENDING VALUE: %.2f' % (self.params.short_period, self.params.long_period, self.broker.getvalue()), doprint=True)
    # self.log('(Risk %2d, Stoploss %2d) ENDING VALUE: %.2f' % (self.params.risk_perc, self.params.stoploss, self.broker.getvalue()), doprint=True)


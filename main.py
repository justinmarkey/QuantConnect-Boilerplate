from QuantConnect.Data.UniverseSelection import *
from QuantConnect.Indicators import *

class MainAlgo(QCAlgorithm):

    def Initialize(self): # == __init__(self)
        self.SetStartDate(2010, 1, 1)
        self.SetEndDate(2021, 1, 1)
        self.SetCash(1000000)
        self.rsi = RelativeStrengthIndex()
        self.bb = BollingerBand()
        self.lowerbb = LowerBollingerBand()
        self.upperbb = UpperBollingerBand()
        self.AddUniverse(self.CoarseFilter, self.FineFilter)
        self.UniverseSettings.filterFineData = True
        self.UniverseSettings.Resolution = Resolution.Hour
        self.lastDay = -1
        self.Fine = {}

    def CoarseFilter(self, algorithm, coarse):
        if algorithm.Time.day == self.lastDay: 
            return Universe.Unchanged
        else:
            coarse = [c for c in coarse if c.HasFundamentalData and c.Volume > 2e5 and c.Price > 5] #only allows Price above 5 and volume above 200k, will delete anything without funddata
            course = sorted(coarse, key=lambda c: c.Volume, reverse=True) #sort highest volume on top in 0 position
            return [c.Symbol for c in course]

    def FineFilter(self, fine):
        '''
        data is forked to finefilter for further filtering. Use this to get into the nittygritty filtering and selection
        '''
        fine = [f for f in fine if f.MarketCap > 25e9 #25 bil market cap
            and f.CompanyReference.CountryId == "USA"
        for f in fine:
            fine.append(rsi(f))
            fine.append(lowerbb(f))

        fine = [f for f in fine if rsi < 30 #sort with newly appended rsi and lowerbb calculation
            and f.Price < lowerbb]
        fine = sorted(fine, key=lambda f: f.Volume, reverse = True)
        self.Fine = [f.Symbol for f in fine]
        fine = [f.Symbol for f in fine][:30] #get 30 best symbols
        self.Debug(fine) #print
        return fine #return as list of symbols

    def ShouldBuy(self):
        list_shouldBuy = FineFilter()
        for i in list_shouldBuy:
            if i == self.PortfolioInvested:
                list_shouldBuy.remove(i)
            else:
                return list_shouldBuy

    def CalcRSIinPortfolio(self):
        rsivalues = []
        for i in self.Portfolio:
            c = rsi(i)
            rsivalues.append(c)
        return rsivalues

    def ShouldSell(self):
        list_shouldSell = []
        rsivalues = CalcRSI()
        for i in self.Portfolio:
            if rsivalues(i) >= 75:
                list_shouldSell.append(i)
                return list_shouldSell
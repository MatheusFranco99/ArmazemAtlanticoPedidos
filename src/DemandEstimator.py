from Day import *


class DemandEstimator:

    day1 = Day.getMonthsAgo(6)
    day2 = Day.getMonthsAgo(3)
    day3 = Day.getToday()

    day1Str = Day.getMonthsAgo(6).strftime("%d/%m/%Y")
    day2Str = Day.getMonthsAgo(3).strftime("%d/%m/%Y")
    day3Str = Day.getToday().strftime("%d/%m/%Y")

    @staticmethod
    def estimate(item,typeDoc):

        m1 = item.getDemand(DemandEstimator.day1,DemandEstimator.day3,typeDoc)/6
        m2 = item.getDemand(DemandEstimator.day2,DemandEstimator.day3,typeDoc)/3
        return (m1 + m2)/2


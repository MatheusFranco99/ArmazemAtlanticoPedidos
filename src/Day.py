from datetime import datetime, timedelta


class Day:

    @staticmethod
    def getToday():
        today = datetime.today()
        today = today.replace(hour=0,minute=0,second=0,microsecond=0)
        return today
    
    @staticmethod
    def getLastYearToday():
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day.replace(year=day.year-1)
        return day
    
    @staticmethod
    def getLastYear1MonthLater():
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day.replace(year=day.year-1)
        day = day + timedelta(days = 30)
        return day

    @staticmethod
    def getLastYear2MonthsLater():
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day.replace(year=day.year-1)
        day = day + timedelta(days = 60)
        return day
    
    @staticmethod
    def getLastMonthSameDay():
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day - timedelta(days = 30)
        return day

    @staticmethod
    def getLastLastMonthSameDay():
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day - timedelta(days = 60)
        return day


    @staticmethod
    def getMonthsAgo(months):
        day = datetime.today()
        day = day.replace(hour=0,minute=0,second=0,microsecond=0)
        day = day - timedelta(days = months * 30)
        return day    

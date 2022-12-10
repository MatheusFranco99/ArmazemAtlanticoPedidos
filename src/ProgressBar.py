import colorama

class ProgressBar:

    def __init__(self,n = 10):
        self.n = n
        self.i = 0
        self.printPB(self.i,self.n)
    
    def step(self, step = 1):
        self.i += step
        self.printPB(self.i,self.n)


    def printPB(self,progress, total, color = colorama.Fore.YELLOW):
        percent = int(100*(progress / float(total)))
        bar = chr(9608) * percent + '-' * (100-percent)
        end = '\r'
        if (progress == total):
            color = colorama.Fore.GREEN
            end = '\n'
        print(color + f"\r|{bar}| {percent:.2f}%", end=end)
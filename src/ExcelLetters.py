

class ExcelLetters:



    @staticmethod
    def increase(letter):
        lastLetter = letter[-1]
        if lastLetter != 'Z':
            new_letter = chr(ord(lastLetter)+1)
            return letter[:-1] + new_letter
        else:
            for i in range(len(letter)-2,-1,-1):
                if(letter[i] != 'Z'):
                    new_letter = chr(ord(letter[i])+1)
                    return letter[:i] + new_letter + 'A'*(len(letter)-1-i)
            return 'A'*(len(letter)+1)
    
    @staticmethod
    def increaseN(letter,n):
        ans = letter
        for i in range(n):
            ans = ExcelLetters.increase(ans)
        return ans
    
    @staticmethod
    def getNumber(letter):
        ans = 0
        exp = 0
        for i in range(len(letter)-1,-1,-1):
            ans += (ord(letter[i]) - ord('A') + 1) * pow(26,exp)
            exp = exp + 1
        ans = ans - 1
        return ans
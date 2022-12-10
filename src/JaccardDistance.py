import re

class JaccardDistance:

    @staticmethod
    def getBigrams(s):
        return s.split()
        # s = s.replace('  ',' ').replace('-',' ').replace('/',' ')
        # tokens = re.split('(\d+)',s)
        # return tokens
        # s = s.replace(' ','').replace('-','')
        # ans = []
        # for i in range(1,len(s)):
        #     ans += [s[i-1:i]]
        # return ans


    @staticmethod
    def jaccard(s1,s2):
        bigrams1 = JaccardDistance.getBigrams(s1.lower())
        bigrams2 = JaccardDistance.getBigrams(s2.lower())
        union = set(bigrams1 + bigrams2)
        intersection = []
        for b in bigrams1:
            if b in bigrams2:
                intersection += [b]
        
        intersection = set(intersection)
        # intersection_len_sum = 0
        # union_len_sum = 0
        # for elm in intersection:
        #     intersection_len_sum += len(elm)
        # for elm in union:
        #     union_len_sum += len(elm)
        return len(intersection) / len(union)
        # return intersection_len_sum / union_len_sum
    
    @staticmethod
    def distance(s1,s2):
        if (type(s2) == list):
            ans = []
            for ss in s2:
                ans += [JaccardDistance.jaccard(s1,ss)]
            return ans
        else:
            return JaccardDistance.jaccard(s1,s2)

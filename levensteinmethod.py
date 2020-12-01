# -*- coding: UTF-8 -*-
import sys
import glob
import hashlib
import Levenshtein
import numpy
import binascii
import re

if __name__ == '__build__':
    raise Exception

def canonize(source):
        count_iter = 0
        stop_symbols = '.,!?:;-\n\r()'

        stop_words = (u'i', u'а', u'благо',
            u'буде', u'в додаток', u'щоб',
            u'навіть', u'ледь', u'благо',
            u'якщо' , u'зате', u'навіщо',
            u'або', u'бо',u'отже', u'не',
            u'але', u'проте', u'тому', u'це',
            u'чому', u'притому', u'причому',
            u'нехай ', u'немов', u'теж',
            u'тільки', u'щоб', u'що', u'хоча', u'точно',
            u'без', u'в', u'для',
            u'за', u'из', u'к', u'на',
            u'над', u'о', u'об', u'от',
            u'по', u'под', u'перед', u'при',
            u'про', u'с', u'у', u'через', u'так', 'шось'
            )

        #c =  [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)]
        c = []
        rt = source.lower().split('\n')
        for i in stop_words:
            count_iter += 1
            for k,s  in enumerate(rt):
                count_iter += 1
                if i == s:
                    del rt[k]
        str_without_stops = " ".join(rt)
        t = re.split("[\.\,\?\!\:\;]", str_without_stops)
        for g,h in enumerate(t):
            count_iter += 1
            if h == "":
                del t[g]

        for g,h in enumerate(t):
            count_iter += 1
            if h == "":
                del t[g]

        return t, count_iter

def compaire (source1,source2):
    count_iter = 0
    tmean = []
    sum = 0
    silen = 0
    silen1 = len(source1)
    silen2 = len(source2)
    if silen1 < silen2:
        silen = silen1
    else:
        silen = silen2
    for i in range(silen):
        count_iter += 1
        s = []
        for r in source2:
            count_iter += 1
            sd = Levenshtein.ratio(source1[i], source2[i])
            s.append(sd)
        t = numpy.mean(s)
        tmean.append(t)
    sum = 0
    for i in tmean:
        count_iter += 1
        sum += i

    return sum/len(tmean), count_iter

def return_sim_procents(text1, text2):
    total_iter = 0
    cmp1, iter1 = canonize(text1)
    cmp2, iter2 = canonize(text2)
    total_iter += iter1
    total_iter += iter2
    print("Схожесть документов по Levenstein Distance: ", compaire(cmp1,cmp2))
    proc, iters = compaire(cmp1, cmp2)
    total_iter += iters
    return proc * 100, total_iter, len(cmp2)


#a = return_sim_procents("це я не зумів Зупинити себе, тебе... Сьогодні Сьогодні так вив, без тебе сумую Сумую без тебе, накинь шось на себе Явы  выфыам вфвф ", "це я не зумів Зупинити себе, тебе... Сьогодні Сьогодні так вив, без тебе сумую Сумую без тебе, накинь шось на себе Я налию собі, я налию це я не зумів Зупинити себе, тебе... Сьогодні Сьогодні так вив, без тебе сумую Сумую без тебе, накинь шось на себе Я налию собі, я налию ")
#print (a)


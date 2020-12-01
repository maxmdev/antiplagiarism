# -*- coding: UTF-8 -*-
import sys
import glob
import hashlib
import binascii

if __name__ == '__build__':
    raise Exception

def canonize(source):
        stop_symbols = '.,!?:;-\n\r()'

        stop_words = (u'i', u'а', u'благо',
            u'буде', u'в додаток', u'щоб',
            u'навіть', u'ледь', u'благо',
            u'якщо' , u'зате', u'навіщо',
            u'або', u'бо',u'отже'
            u'але', u'проте', u'тому',
            u'чому', u'притому', u'причому',
            u'нехай ', u'немов', u'теж',
            u'тільки', u'щоб', u'що', u'хоча', u'точно',
            u'без', u'в', u'для',
            u'за', u'из', u'к', u'на',
            u'над', u'о', u'об', u'от',
            u'по', u'под', u'перед', u'при',
            u'про', u'с', u'у', u'через'
            )

        c =  [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in stop_words)]
        string_for_slice = "".join([i for i in c if len(i) >3 ])
        #print(string_for_slice)
        lis = []
        out = []
        for i,e  in enumerate(string_for_slice):
            if i % 3 == 0:
                a = string_for_slice[i:i+3]
                lis.append(a)
        #print (lis)
        return lis

def genmoodle_n(source, wordsLen):
    import binascii
    wordsLen = wordsLen #2 #длина шингла
    out = []
    source = canonize(source)
    for i in range(len(source)-(wordsLen-1)):
         #out.append (binascii.crc32(' '.join( [x for x in source[i:i+wordsLen]] ).encode('utf-8')))
         out.append(hashlib.md5(' '.join([x for x in source[i:i + wordsLen]]).encode('utf-8')).hexdigest())
    return "\"wordsSliceLenght_{}\": ".format(wordsLen)  + str(out).replace("\'", "\"")


def genmoodle(source):
    count_iter = 0
    shingleLen = 3
    out = []
    for i in range(len(source)-(shingleLen-1)):
        count_iter += 1
        #out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] ).encode('utf-8')))
        out.append(hashlib.md5(' '.join([x for x in source[i:i + shingleLen]]).encode('utf-8')).hexdigest())

    return out, count_iter

def compaire (source1,source2):
    count_iter = 0
    same = 0
    for i in range(len(source1)):
        count_iter += 1
        if source1[i] in source2:
            same = same + 1

    return same/float(len(source1)), count_iter

def return_sim_procents(text1, text2):
    count_iter_total = 0
    cmp1, iter1 = genmoodle(canonize(text1))
    cmp2, iter2 = genmoodle(canonize(text2))
    count_iter_total += iter1
    count_iter_total += iter2
    print("Схожесть документов по Moodle Crot: ", compaire(cmp1,cmp2))
    l, count_iter = compaire(cmp1, cmp2)
    count_iter_total += count_iter
    l = l * 100
    print(l)
    if int(l) > 100:
        l = 100
    return l, count_iter_total, len(cmp2)
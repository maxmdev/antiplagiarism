# -*- coding: UTF-8 -*-
import sys
import glob
import hashlib

if __name__ == '__build__':
    raise Exception

count_iter = 0

def canonize(source, sorting):
        stop_symbols = '.,!?:;-\n\r()'

        stop_words_union = (
            u'i', u'а', u'благо',
            u'буде', u'в додаток', u'щоб',
            u'навіть', u'ледь', u'благо',
            u'якщо' , u'зате', u'навіщо',
            u'або', u'бо',u'отже'
            u'але', u'проте', u'тому',
            u'чому', u'притому', u'причому',
            u'нехай ', u'немов', u'теж',
            u'тільки', u'щоб', u'що', u'хоча', u'точно'
        )

        stop_words_pretext = (
        u'без', u'в', u'для',
        u'за', u'из', u'к', u'на',
        u'над', u'о', u'об', u'от',
        u'по', u'под', u'перед', u'при',
        u'про', u'с', u'у', u'через'
        )

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

        if sorting == "":
            filter =stop_words
        elif sorting == "pretext":
            filter = stop_words_pretext
        elif sorting == "union":
            filter = stop_words_union
        return ( [x for x in [y.strip(stop_symbols) for y in source.lower().split()] if x and (x not in sorting)] )


def canonize_with_sorted(source, sorting):
    p = canonize(source, sorting)
    return sorted(p)


'''
get_shingle_n(source, n) - function for input in database shingles on any base
'''
def genshingle_n(source, shingleLen):
    import binascii
    count_iter = 0
    shingleLen = shingleLen #2 #длина шингла
    out = []
    source = canonize(source, "")
    for i in range(len(source)-(shingleLen-1)):
         count_iter += 1
         #out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] ).encode('utf-8')))
         out.append(hashlib.md5(' '.join([x for x in source[i:i + shingleLen]]).encode('utf-8')).hexdigest())
    return "\"shinglesLenght_{}\": ".format(shingleLen)  + str(out).replace("\'", "\"")


def genshingle(source):
    import binascii
    count_iter = 0
    shingleLen = 4 #2 #длина шингла
    out = []
    for i in range(len(source)-(shingleLen-1)):
        count_iter += 1
        #out.append (binascii.crc32(' '.join( [x for x in source[i:i+shingleLen]] ).encode('utf-8')))
        out.append(hashlib.md5(' '.join([x for x in source[i:i + shingleLen]]).encode('utf-8')).hexdigest())
    return out, count_iter

def compaire (source1,source2):
    count_iter = 0
    same = 0
    len_norm = 0
    len1 = len(source1)
    len2 = len(source2)
    if len1 < len2:
        len_norm = len1
    else:
        len_norm = len2
    for i in range(len_norm):
        count_iter += 1
        if source1[i] in source2:
            same = same + 1

    #return same*2/float(len(source1) + len(source2))
    return same/float(len(source1)), count_iter

def return_sim_procents(text1, text2, sorting):
    count_iter_total = 0
    cmp1, iter1 = genshingle(canonize(text1, sorting))
    cmp2, iter2 = genshingle(canonize(text2, sorting))
    count_iter_total += iter1
    count_iter_total += iter2
    print("Схожесть документов по шинглу: ", compaire(cmp1,cmp2))
    l, count_iter = compaire(cmp1, cmp2)
    count_iter_total += count_iter
    l = l *100
    print (l)
    if int(l) >100:
        l =100
    return l, count_iter_total, len(cmp2)
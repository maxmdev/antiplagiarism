def get_frequency_from_file(filename):
    inFile = open(filename,  'r', encoding='utf8')
    n = []
    for l in inFile:
        n += l.strip().split()

    words = dict()
    for w in n:
        if w in words:
            words[w] += 1
        else:
            words[w] = 0

    MyList = list(words)
    #print(MyList)
    i = 0
    for w in words:
        i += 1
        MyList[i - 1] = (words[w], w)

    MegaList = sorted(MyList, key=lambda x: x[0], reverse=True)
    #print (*MegaList)
    return MegaList

c = get_frequency_from_file('database/txt/example.txt')
print ('\n\n',c)
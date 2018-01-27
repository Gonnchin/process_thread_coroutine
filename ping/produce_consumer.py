
def consumer():
    re = ''
    while True:
        n = yield re
        # if not n:
        #     return
        print "consumer: %s" % n
        re = '200ok'


def produce(c):
    c.send(None)
    n = 0
    while n <= 5:
        n += 1
        print "produce %s" % n
        re = c.send(n)
        print "statue %s" % re
    c.close()


c = consumer()
produce(c)
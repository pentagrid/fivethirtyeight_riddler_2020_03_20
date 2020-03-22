price = 100
day = 0

while 1:
    #morning
    price = price * 0.9
    #evening
    price = price * 1.1
    if price < 50:
        break
    day = day + 1

print "the evening solution is on day " + str(day)

price = 100
day = 0

while 1:
    #morning
    price = price * 0.9
    if price < 50:
        break
    #evening
    price = price * 1.1
    if price < 50:
        break
    day = day + 1

print "the morning solution is on day " + str(day)
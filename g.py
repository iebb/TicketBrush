# coding: utf-8
from PIL import Image
import math
import requests, grequests
import pytesseract
import random
from StringIO import StringIO

BATCH = 50


def dx(u):
    return int(math.sin(u * 3.1416 * 2 + 0.7) * 8 + u * 5)


def un(img):
    w, h = img.size
    white = (255, 255, 255)
    black = (0, 0, 0)
    undis = Image.new("RGB", (w, h))
    for x in range(w):
        for y in range(h):
            distort = dx(1. * y / h)
            color = im.getpixel([(x - distort, y), (0, 0)][x - distort < 0 or x - distort >= w])
            undis.putpixel((x, y), [black, white][sum(color) > 600])
    return undis


def mobile():
    return '13' + str(random.randrange(4, 10)) + ''.join(str(random.choice(range(10))) for _ in range(8))

success = total = 0

Sesspool = []
for i in range(BATCH):
    Sesspool.append(requests.Session())

while success < 114514:
    recog = ''
    GPool = []
    for i in range(BATCH):
        GPool.append(grequests.get(
            "http://act.ll.sdo.com/Act20171127/AuthorCode.aspx?method=queryReserveNum", session=Sesspool[i]
        ))
    Gresult = grequests.map(GPool)
    GPool2 = []
    for i in range(BATCH):
        file = StringIO()
        file.write(Gresult[i].content)
        im = Image.open(file)
        io = un(im)
        recog = pytesseract.image_to_string(io, config='-psm 7')
        if len(recog) == 4:
            GPool2.append(grequests.post(
                "http://act.ll.sdo.com/Act20171127/Server/Reserves.ashx?method=submit&code=%s&mobile=%s"
                % (recog, mobile())
                , session=Sesspool[i]
            ))
    Gresult2 = grequests.map(GPool2)
    for r2 in Gresult2:
        if r2.json()["Code"] == 0:
            success += 1
        total += 1
    print "> %d/%d %.3f%%" % (success, total, 100. * success / total)

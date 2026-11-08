import zlib, struct, os
W,H=48,40
def encode_png(w,h,pixels):
    def chunk(t,body):
        c=t+body
        return struct.pack(">I",len(body))+c+struct.pack(">I",zlib.crc32(c)&0xffffffff)
    raw=bytearray()
    stride=w*4
    for y in range(h):
        raw.append(0); raw.extend(pixels[y*stride:(y+1)*stride])
    ihdr=struct.pack(">IIBBBBB",w,h,8,6,0,0,0)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b"")
def canvas():
    return bytearray(b"\x00\x00\x00\x00"*W*H)
def setpx(buf,x,y,col,a=255):
    if 0<=x<W and 0<=y<H:
        i=(y*W+x)*4; buf[i:i+4]=bytes([col[0],col[1],col[2],a])
def rect(buf,x0,y0,x1,y1,col,a=255):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): setpx(buf,x,y,col,a)

# Cura AoE1 (imagen 1): calvo, estola azul con borde, tunica marron, reliquia + baculo
robe=(150,116,70); robeD=(115,86,50); robeDD=(85,62,34)
stole=(52,84,164); stoleL=(200,210,235)
skin=(232,176,138); skinD=(200,140,100); shine=(245,205,170)
ink=(26,18,8); dark=(43,31,16)
wood=(139,105,60); woodD=(100,72,38)
relic=(110,82,50); relicD=(80,58,32); relicL=(160,125,75)
gold=(220,180,80)

def draw_priest(buf,pose="down",blink=False):
    # pies
    rect(buf,20,35,24,36,robeDD); rect(buf,24,35,28,36,robeDD)
    # tunica
    rect(buf,17,17,31,34,dark)
    rect(buf,18,18,30,33,robe)
    rect(buf,18,18,30,20,robeD)
    rect(buf,23,18,25,33,robeD)
    # estola azul con borde claro (hombros -> pecho)
    rect(buf,19,18,22,33,stole); rect(buf,26,18,29,33,stole)
    rect(buf,19,18,19,33,stoleL); rect(buf,29,18,29,33,stoleL)
    rect(buf,19,18,22,19,(70,105,190)); rect(buf,26,18,29,19,(70,105,190))
    # brazo izq sostiene reliquia (caja)
    rect(buf,10,20,17,30,dark); rect(buf,11,21,16,29,relic)
    rect(buf,11,21,16,22,relicL); rect(buf,13,23,15,27,relicD)
    rect(buf,13,24,15,26,(60,42,22))
    rect(buf,10,30,17,32,skin)   # manos bajo la caja
    # baculo lado der
    if pose=="mid":
        sx0,sx1,sy0,sy1=37,38,3,35
        rect(buf,31,15,35,18,skin)
        rect(buf,31,18,34,24,dark); rect(buf,32,19,33,23,robe)
    if pose=="up":
        sx0,sx1,sy0,sy1=37,38,0,33
        for (x,y) in [(34,1),(42,1),(35,5),(41,5),(36,8),(40,8)]: setpx(buf,x,y,gold)
        rect(buf,31,6,35,9,skin)
        rect(buf,31,9,34,20,dark); rect(buf,32,10,33,19,robe)
    else:
        sx0,sx1,sy0,sy1=36,37,6,37
        rect(buf,32,27,35,30,skin)
        rect(buf,31,20,34,27,dark); rect(buf,32,21,33,26,robe)
    rect(buf,sx0,sy0,sx1,sy1,wood)
    for y in range(sy0,sy1+1,3): setpx(buf,sx0,y,woodD)
    setpx(buf,sx0,sy0,(170,135,80)); setpx(buf,sx1,sy0,(170,135,80))
    # cabeza calva
    rect(buf,20,8,28,19,skin)
    rect(buf,21,8,27,10,shine)    # brillo calva
    rect(buf,20,11,21,18,skinD); rect(buf,27,11,28,18,skinD)
    rect(buf,20,8,28,9,(225,165,125))
    if blink:
        rect(buf,22,13,23,13,skinD); rect(buf,25,13,26,13,skinD)
    else:
        rect(buf,22,13,23,13,ink); rect(buf,25,13,26,13,ink)
    rect(buf,23,15,25,15,skinD)
    rect(buf,23,17,25,17,(165,95,75))

FONT={
 "W":["#.#","#.#","#.#","###","#.#"],
 "O":["###","#.#","#.#","#.#","###"],
 "L":["#..","#..","#..","#..","###"],
}
def text(buf,word,x0,y0,col,outline=None):
    x=x0
    for ch in word:
        g=FONT[ch]
        for dy,row in enumerate(g):
            for dx,c in enumerate(row):
                if c=="#":
                    if outline: setpx(buf,x+dx,y0+dy,outline)
                    setpx(buf,x+dx,y0+dy,col)
        x+=4

base="gentle-emote-arcade/emotes/aoe"
jobs=[
 ("think/think_01.png","down",False,None),("think/think_02.png","mid",False,None),
 ("think/think_03.png","up",False,None),("think/think_04.png","up",False,"WOLOLO"),
]
for rel,pose,blink,word in jobs:
    p=os.path.join(base,rel)
    buf=canvas(); draw_priest(buf,pose=pose,blink=blink)
    if word: text(buf,word,8,0,gold,outline=dark)
    open(p,"wb").write(encode_png(W,H,buf))
    print("ok",rel)

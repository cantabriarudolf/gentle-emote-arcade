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

# Paleta monje AoE2: habito marron, capucha, cinto de soga
habit=(133,99,58); habitD=(99,71,40); habitDD=(72,51,28)
hoodL=(150,114,70)
skin=(232,176,138); skinD=(200,140,100); shade=(186,128,92)
ink=(26,18,8); dark=(43,31,16)
rope=(210,190,140)
wood=(110,80,45); woodD=(80,56,30); woodL=(150,115,70)
gold=(220,180,80); goldL=(255,220,130)

def draw_monk(buf,pose="down",blink=False):
    # ---- pies (sandalias) ----
    rect(buf,20,35,24,36,(90,65,40)); rect(buf,24,35,28,36,(90,65,40))
    setpx(buf,21,36,skinD); setpx(buf,26,36,skinD)
    # ---- habito con contorno ----
    rect(buf,17,17,31,34,dark)
    rect(buf,18,18,30,33,habit)
    rect(buf,18,18,30,21,habitD)            # sombra de la capucha sobre el pecho
    rect(buf,18,28,21,33,habitD); rect(buf,27,28,30,33,habitD)  # pliegues bajos
    rect(buf,23,18,25,33,habitD)            # pliegue central
    # ---- cinto de soga con nudo ----
    rect(buf,18,24,30,26,rope)
    rect(buf,18,24,30,24,(230,210,160))
    rect(buf,24,26,26,29,rope); rect(buf,25,29,27,30,rope)  # nudo colgando
    # ---- brazo izq (manga ancha) ----
    rect(buf,14,19,17,29,dark); rect(buf,15,20,16,28,habit)
    rect(buf,14,29,17,31,skin)              # mano izq
    # ---- brazo der al baculo ----
    if pose=="up":
        rect(buf,31,7,34,19,dark); rect(buf,32,8,33,18,habit)  # manga levantada
        rect(buf,31,5,34,8,skin)                               # mano agarra alto
        sx0,sx1,sy0,sy1=37,38,0,33
        cx0,cx1,cy0,cy1=32,42,1,3
        for (x,y) in [(30,0),(44,0),(29,5),(45,5),(34,7),(41,7),(30,9),(44,9)]: setpx(buf,x,y,goldL)
        for (x,y) in [(33,4),(40,4)]: setpx(buf,x,y,gold)
    else:
        rect(buf,31,19,34,27,dark); rect(buf,32,20,33,26,habit)
        rect(buf,32,27,35,30,skin)          # mano envuelve el baculo
        sx0,sx1,sy0,sy1=36,37,3,37
        cx0,cx1,cy0,cy1=31,42,4,6
    # ---- baculo de madera con cruz ----
    rect(buf,sx0,sy0,sx1,sy1,wood)
    for y in range(sy0,sy1+1,3): setpx(buf,sx0,y,woodD)  # vetas
    rect(buf,sx0,sy0,sx1,sy0,woodL)          # tope iluminado
    rect(buf,cx0,cy0,cx1,cy1,wood); rect(buf,cx0,cy0,cx1,cy0,woodL)
    rect(buf,cx0+4,cy0-2,cx1-4,cy1+2,gold)   # refuerzo dorado central
    # ---- capucha ----
    rect(buf,16,4,32,22,dark)
    rect(buf,17,5,31,21,habit)
    rect(buf,17,5,31,8,habitD)              # sombra superior
    rect(buf,17,5,18,21,habitDD); rect(buf,30,5,31,21,habitDD)
    rect(buf,21,3,27,5,habit)               # punta
    rect(buf,23,3,25,4,hoodL)
    # ---- cara ----
    rect(buf,20,9,28,19,skin)
    rect(buf,20,9,28,10,shade)              # sombra capucha
    rect(buf,20,14,21,19,skinD); rect(buf,27,14,28,19,skinD)
    if blink:
        rect(buf,22,14,23,14,skinD); rect(buf,25,14,26,14,skinD)
    else:
        rect(buf,22,14,23,14,ink); rect(buf,25,14,26,14,ink)
        rect(buf,22,13,23,13,(110,80,50)); rect(buf,25,13,26,13,(110,80,50))
    setpx(buf,24,16,skinD)
    rect(buf,23,18,25,18,(165,95,75))

base="gentle-emote-arcade/emotes/aoe"
jobs=[
 ("think/think_01.png","down",False),("think/think_02.png","up",False),
 ("idle/idle.png","down",False),("idle/idle_blink.png","down",True),
 ("hi/hi_01.png","up",False),("hi/hi_02.png","up",True),
]
for rel,pose,blink in jobs:
    p=os.path.join(base,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    buf=canvas(); draw_monk(buf,pose=pose,blink=blink)
    open(p,"wb").write(encode_png(W,H,buf))
    print("ok",rel)

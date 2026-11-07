import zlib, struct, os

W,H=48,40
def encode_png(w,h,pixels):
    # pixels: bytearray RGBA row-major
    def chunk(t,body):
        c=t+body
        return struct.pack(">I",len(body))+c+struct.pack(">I",zlib.crc32(c)&0xffffffff)
    raw=bytearray()
    stride=w*4
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y*stride:(y+1)*stride])
    ihdr=struct.pack(">IIBBBBB",w,h,8,6,0,0,0)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b"")

def canvas():
    return bytearray(W*H*4) # transparent

def setpx(buf,x,y,r,g,b,a=255):
    if 0<=x<W and 0<=y<H:
        i=(y*W+x)*4; buf[i:i+4]=bytes([r,g,b,a])
def rect(buf,x0,y0,x1,y1,col):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): setpx(buf,x,y,*col)

# palette
outline=(43,31,16); hat=(138,106,59); hatD=(107,79,38); skin=(232,176,138); skinD=(200,140,100)
tunic=(122,90,46); tunicD=(94,68,32); pants=(74,56,32); dark=(26,18,8); boot=(60,40,20)

def draw_villager(blink=False):
    buf=canvas()
    # legs/boots
    rect(buf,21,30,23,35,pants); rect(buf,25,30,27,35,pants)
    rect(buf,20,35,24,36,boot); rect(buf,24,35,28,36,boot)
    # body tunic
    rect(buf,20,19,28,30,tunic)
    rect(buf,20,19,28,21,tunicD) # shoulders shade
    rect(buf,23,19,25,30,tunicD) # center shade line
    rect(buf,20,26,28,27,(80,55,25)) # belt
    rect(buf,23,26,25,27,boot) # buckle
    # arms
    rect(buf,17,20,20,28,tunic); rect(buf,28,20,31,28,tunic)
    rect(buf,17,28,20,30,skin); rect(buf,28,28,31,30,skin) # hands
    # head
    rect(buf,21,11,27,19,skin)
    rect(buf,21,11,21,19,skinD); rect(buf,27,11,27,19,skinD)
    # hat
    rect(buf,22,5,26,7,hatD)
    rect(buf,20,7,28,9,hat)
    rect(buf,18,9,30,11,hatD) # brim
    rect(buf,18,9,30,9,hat)
    # eyes
    if blink:
        rect(buf,22,14,23,14,skinD); rect(buf,25,14,26,14,skinD)
    else:
        rect(buf,22,14,23,15,dark); rect(buf,25,14,26,15,dark)
    # mouth
    rect(buf,23,17,25,17,skinD)
    return buf

base=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"..","emotes","aoe","idle")
os.makedirs(base,exist_ok=True)
open(os.path.join(base,"idle.png"),"wb").write(encode_png(W,H,draw_villager(False)))
open(os.path.join(base,"idle_blink.png"),"wb").write(encode_png(W,H,draw_villager(True)))
print("done",os.listdir(base))

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
def canvas(): return bytearray(W*H*4)
def setpx(buf,x,y,col):
    if 0<=x<W and 0<=y<H:
        i=(y*W+x)*4; buf[i:i+4]=bytes([col[0],col[1],col[2],255])
def rect(buf,x0,y0,x1,y1,col):
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): setpx(buf,x,y,col)
def circle(buf,cx,cy,r,col):
    for y in range(cy-r,cy+r+1):
        for x in range(cx-r,cx+r+1):
            if (x-cx)**2+(y-cy)**2<=r*r: setpx(buf,x,y,col)

# palettes
V=dict(hat=(138,106,59),hatD=(107,79,38),tunic=(122,90,46),tunicD=(94,68,32),skin=(232,176,138),skinD=(200,140,100),pants=(74,56,32),boot=(60,40,20))
M=dict(hat=(240,240,230),hatD=(210,210,200),tunic=(240,240,230),tunicD=(180,180,170),skin=(232,176,138),skinD=(200,140,100),pants=(180,180,170),boot=(120,120,130))
K=dict(hat=(80,80,90),hatD=(50,50,60),tunic=(60,60,70),tunicD=(40,40,50),skin=(200,150,110),skinD=(170,120,80),pants=(70,70,80),boot=(50,50,60))
outline=(43,31,16); dark=(26,18,8); gold=(220,180,80); red=(200,60,60); green=(60,180,80); blue=(60,120,200); magenta=(255,0,255)

def draw_villager(buf,pal,pose="idle",blink=False,mouth=1,shrink=False,fallen=False,arm_up=False,yolo=False):
    yoff=4 if shrink else 0
    if fallen:
        # fallen body
        rect(buf,8,26,40,30,pal['tunic']); rect(buf,10,28,38,29,pal['tunicD'])
        rect(buf,30,20,36,26,pal['skin']); rect(buf,32,21,34,22,dark)
        rect(buf,38,14,40,24,(180,180,190)); rect(buf,36,12,40,14,(180,180,190))
        if yolo: rect(buf,28,22,36,24,magenta)
        return
    # legs
    rect(buf,21,30-yoff,23,35-yoff,pal['pants']); rect(buf,25,30-yoff,27,35-yoff,pal['pants'])
    rect(buf,20,35-yoff,24,36-yoff,pal['boot']); rect(buf,24,35-yoff,28,36-yoff,pal['boot'])
    # body
    rect(buf,20,19-yoff,28,30-yoff,pal['tunic']); rect(buf,20,19-yoff,28,21-yoff,pal['tunicD'])
    rect(buf,20,26-yoff,28,27-yoff,(80,55,25)); rect(buf,23,26-yoff,25,27-yoff,pal['boot'])
    # arms
    if arm_up:
        rect(buf,28,8-yoff,31,20-yoff,pal['tunic']); rect(buf,28,6-yoff,31,8-yoff,pal['skin'])
    else:
        rect(buf,17,20-yoff,20,28-yoff,pal['tunic']); rect(buf,28,20-yoff,31,28-yoff,pal['tunic'])
        rect(buf,17,28-yoff,20,30-yoff,pal['skin']); rect(buf,28,28-yoff,31,30-yoff,pal['skin'])
    # head
    circle(buf,24,15-yoff,4,pal['skin'])
    rect(buf,21,11-yoff,27,19-yoff,pal['skin'])
    # hat (villager straw hat)
    rect(buf,20,7-yoff,28,9-yoff,pal['hat']); rect(buf,18,9-yoff,30,11-yoff,pal['hatD'])
    rect(buf,22,5-yoff,26,7-yoff,pal['hatD'])
    # monk hood
    if pal==M:
        rect(buf,20,6-yoff,28,12-yoff,pal['hat']); rect(buf,21,12-yoff,27,14-yoff,pal['hatD'])
    # soldier helmet
    if pal==K:
        rect(buf,19,7-yoff,29,11-yoff,pal['hat']); rect(buf,20,11-yoff,28,12-yoff,pal['hatD'])
        rect(buf,23,5-yoff,25,7-yoff,pal['hatD'])
    # eyes
    if blink:
        setpx(buf,22,14-yoff,(200,140,100)); setpx(buf,25,14-yoff,(200,140,100))
    else:
        setpx(buf,22,14-yoff,dark); setpx(buf,23,14-yoff,dark); setpx(buf,25,14-yoff,dark); setpx(buf,26,14-yoff,dark)
    # mouth
    mw={0:1,1:3,2:5,3:7}.get(mouth,3)
    for x in range(24-mw//2,24+mw//2+1): setpx(buf,x,17-yoff,(200,140,100))
    if yolo:
        rect(buf,20,13-yoff,28,14-yoff,magenta)

def decorate(buf,state,pal):
    if state=="think":
        rect(buf,32,4,34,6,(255,255,150)); rect(buf,33,7,33,9,(255,200,50))
        rect(buf,32,10,34,12,(255,200,50))
    if state=="read":
        rect(buf,32,18,36,22,(160,120,80)); circle(buf,34,20,3,(200,230,255))
    if state=="write":
        rect(buf,32,16,38,18,(160,120,80)); rect(buf,36,18,38,26,(120,90,50))
    if state=="tool":
        rect(buf,32,20,42,23,(100,70,40)); rect(buf,40,23,42,28,(80,50,30))
    if state=="ask":
        rect(buf,32,6,40,14,(255,255,255)); rect(buf,32,6,40,6,dark); rect(buf,36,8,37,10,dark); rect(buf,38,8,39,10,dark)
    if state=="success":
        rect(buf,32,20,36,24,green); rect(buf,33,21,35,23,(255,255,255))
    if state=="judge":
        rect(buf,32,14,38,16,(120,80,40)); rect(buf,36,16,38,22,(90,60,30))
    if state=="review":
        rect(buf,32,18,38,22,(255,255,255)); rect(buf,34,20,38,21,red)
    if state=="jira":
        rect(buf,30,2,36,6,(200,200,210)); rect(buf,32,6,34,12,(200,80,60)); rect(buf,33,1,33,2,(255,200,50))
    if state=="jobs":
        rect(buf,32,22,36,26,(80,200,80)); rect(buf,32,22,36,23,(50,150,50))
    if state in ("yolo","super-yolo"):
        rect(buf,20,13,28,14,magenta)
        rect(buf,32,4,36,6,(200,200,210)); rect(buf,33,6,35,10,(255,100,50))
        if state=="super-yolo": rect(buf,38,2,42,6,(255,220,80))
    if state=="remember":
        rect(buf,32,22,42,28,(160,160,170)); rect(buf,34,24,38,26,(120,120,130))
    if state=="grandma":
        rect(buf,32,20,36,24,(220,120,160)); rect(buf,33,21,35,23,(255,180,200))
    if state=="explore":
        rect(buf,32,16,36,20,(255,220,100)); rect(buf,33,17,35,19,(255,180,50))
    if state=="build":
        rect(buf,32,18,38,20,(255,180,80)); rect(buf,34,20,36,22,(255,100,50))
    if state=="verify":
        rect(buf,32,18,36,26,(80,140,200)); rect(buf,33,19,35,25,(255,255,255))
    if state=="delegate":
        rect(buf,32,24,36,28,(240,240,230)); rect(buf,33,25,35,27,(200,200,210))
    if state=="compact":
        rect(buf,32,8,36,12,(255,255,255)); rect(buf,33,9,35,11,(200,200,210))
    if state=="hi":
        rect(buf,32,2,36,4,(255,220,80)); rect(buf,33,4,35,6,(255,180,50))
    if state=="failure":
        rect(buf,30,28,40,30,red); rect(buf,32,26,34,28,(180,180,190))
    if state=="bye":
        rect(buf,32,2,36,4,(255,220,80))
    if state=="jobs":
        rect(buf,32,2,36,4,(80,200,80))

# state -> (palette, kwargs)
states={
 "hi":(V,dict(arm_up=True)), "think":(M,{}), "talk":(V,dict(mouth=2)), "read":(K,{}),
 "write":(V,{}), "tool":(K,{}), "ask":(V,{}), "success":(M,{}), "failure":(V,dict(fallen=True)),
 "compact":(M,dict(shrink=True)), "delegate":(M,{}), "explore":(K,{}), "build":(V,{}),
 "verify":(K,{}), "judge":(M,{}), "review":(M,{}), "jira":(V,{}), "jobs":(V,{}),
 "yolo":(V,dict(yolo=True)), "super-yolo":(V,dict(yolo=True)), "remember":(M,{}),
 "grandma":(V,{}), "bye":(V,dict(arm_up=True)),
}
base_dir="gentle-emote-arcade/emotes/aoe"
for state,(pal,kw) in states.items():
    d=os.path.join(base_dir,state); os.makedirs(d,exist_ok=True)
    buf=canvas(); draw_villager(buf,pal,pose=state,blink=False,**kw); decorate(buf,state,pal)
    open(os.path.join(d,state+".png"),"wb").write(encode_png(W,H,buf))
    if state=="talk":
        for name,mw in [("talk_close",0),("talk_small",1),("talk_mid",2),("talk_wide",3)]:
            b=canvas(); draw_villager(b,V,pose="talk",mouth=mw); open(os.path.join(d,name+".png"),"wb").write(encode_png(W,H,b))
    print(state)
# idle
d=os.path.join(base_dir,"idle"); os.makedirs(d,exist_ok=True)
b=canvas(); draw_villager(b,V,pose="idle",blink=False); open(os.path.join(d,"idle.png"),"wb").write(encode_png(W,H,b))
b=canvas(); draw_villager(b,V,pose="idle",blink=True); open(os.path.join(d,"idle_blink.png"),"wb").write(encode_png(W,H,b))
print("idle done")

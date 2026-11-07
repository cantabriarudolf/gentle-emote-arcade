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

# palettes
V=dict(hat=(138,106,59),hatD=(107,79,38),tunic=(122,90,46),tunicD=(94,68,32),skin=(232,176,138))
M=dict(hat=(240,240,230),hatD=(210,210,200),tunic=(240,240,230),tunicD=(180,180,170),skin=(232,176,138)) # monk white
K=dict(hat=(80,80,90),hatD=(50,50,60),tunic=(60,60,70),tunicD=(40,40,50),skin=(200,150,110)) # soldier gray
outline=(43,31,16); pants=(74,56,32); dark=(26,18,8); boot=(60,40,20); magenta=(255,0,255)

def base(buf,pal,blink=False, mouth=1, shrink=False, fallen=False, arm_up=False):
    skin=pal['skin']
    if fallen:
        rect(buf,10,28,38,32,pal['tunic']); rect(buf,12,30,36,31,pal['tunicD'])
        rect(buf,30,24,36,28,skin) # head sideways
        rect(buf,32,25,34,26,dark)
        rect(buf,38,18,40,28,(180,180,190)) # sword
        return
    yoff=4 if shrink else 0
    # legs
    rect(buf,21,30-yoff,23,35-yoff,pants); rect(buf,25,30-yoff,27,35-yoff,pants)
    rect(buf,20,35-yoff,24,36-yoff,boot); rect(buf,24,35-yoff,28,36-yoff,boot)
    # body
    rect(buf,20,19-yoff,28,30-yoff,pal['tunic']); rect(buf,20,19-yoff,28,21-yoff,pal['tunicD'])
    rect(buf,20,26-yoff,28,27-yoff,(80,55,25))
    # arms
    if arm_up:
        rect(buf,28,10-yoff,31,20-yoff,pal['tunic']); rect(buf,28,8-yoff,31,10-yoff,skin)
    else:
        rect(buf,17,20-yoff,20,28-yoff,pal['tunic']); rect(buf,28,20-yoff,31,28-yoff,pal['tunic'])
        rect(buf,17,28-yoff,20,30-yoff,skin); rect(buf,28,28-yoff,31,30-yoff,skin)
    # head
    rect(buf,21,11-yoff,27,19-yoff,skin)
    # hat
    if pal==M:
        rect(buf,21,7-yoff,27,11-yoff,pal['hat']); rect(buf,20,11-yoff,28,12-yoff,pal['hatD'])
    else:
        rect(buf,22,5-yoff,26,7-yoff,pal['hatD']); rect(buf,20,7-yoff,28,9-yoff,pal['hat']); rect(buf,18,9-yoff,30,11-yoff,pal['hatD'])
    # eyes
    if blink:
        rect(buf,22,14-yoff,23,14-yoff,(200,140,100)); rect(buf,25,14-yoff,26,14-yoff,(200,140,100))
    else:
        rect(buf,22,14-yoff,23,15-yoff,dark); rect(buf,25,14-yoff,26,15-yoff,dark)
    # mouth
    mw={0:1,1:3,2:4,3:5}.get(mouth,3)
    rect(buf,24-mw//2,17-yoff,24+mw//2,17-yoff,(200,140,100))

def decorate(buf,state):
    if state=="think": rect(buf,32,5,34,7,(255,255,150)); rect(buf,33,8,33,10,(255,200,50)) # bulb
    if state=="read": rect(buf,32,18,36,22,(160,120,80)); setpx(buf,34,20,(200,230,255)) # magnifier
    if state=="write": rect(buf,32,16,38,18,(160,120,80)); rect(buf,36,18,38,26,(120,90,50)) # hammer
    if state=="tool": rect(buf,32,20,42,23,(100,70,40)); rect(buf,40,23,42,28,(80,50,30)) # ram
    if state=="ask": rect(buf,32,8,40,14,(255,255,255)); rect(buf,32,8,40,8,dark); rect(buf,36,10,37,12,dark) # bubble
    if state=="success": rect(buf,32,20,36,24,(50,200,80)) # check bg
    if state=="judge": rect(buf,32,14,38,16,(120,80,40)); rect(buf,36,16,38,22,(90,60,30)) # gavel
    if state=="review": rect(buf,32,18,38,22,(255,255,255)); rect(buf,34,20,38,21,(255,0,0)) # scroll+pen
    if state=="jira": rect(buf,30,4,36,6,(200,200,210)); rect(buf,32,6,34,12,(200,80,60)) # rocket
    if state=="jobs": rect(buf,32,22,36,26,(80,200,80)); rect(buf,32,22,36,23,(50,150,50)) # mate/bar
    if state in ("yolo","super-yolo"):
        rect(buf,21,13,27,15,magenta) # headband/sunglasses strip
        rect(buf,32,4,36,6,(200,200,210)); rect(buf,33,6,35,10,(255,100,50)) # rocket
        if state=="super-yolo": rect(buf,38,2,42,6,(255,220,80)) # sun
    if state=="remember": rect(buf,32,22,42,28,(160,160,170)) # elephant blob
    if state=="grandma": rect(buf,32,20,36,24,(220,120,160)) # yarn
    if state=="explore": rect(buf,32,16,36,20,(255,220,100)) # torch
    if state=="build": rect(buf,32,18,38,20,(255,180,80)) # weld
    if state=="verify": rect(buf,32,18,36,26,(80,140,200)) # shield
    if state=="delegate": rect(buf,32,24,36,28,(240,240,230)) # second monk
    if state=="compact": rect(buf,32,8,36,12,(255,255,255))

states={
 "hi":(V,dict(arm_up=True)), "think":(M,{}), "talk":(V,dict(mouth=2)), "read":(K,{}),
 "write":(V,{}), "tool":(K,{}), "ask":(V,{}), "success":(M,{}), "failure":(V,dict(fallen=True)),
 "compact":(M,dict(shrink=True)), "delegate":(M,{}), "explore":(K,{}), "build":(V,{}),
 "verify":(K,{}), "judge":(M,{}), "review":(M,{}), "jira":(V,{}), "jobs":(V,{}),
 "yolo":(V,{}), "super-yolo":(V,{}), "remember":(M,{}), "grandma":(V,{}),
 "bye":(V,dict(arm_up=True)),
}
base_dir="gentle-emote-arcade/emotes/aoe"
for state,(pal,kw) in states.items():
    d=os.path.join(base_dir,state); os.makedirs(d,exist_ok=True)
    buf=canvas(); base(buf,pal,**kw); decorate(buf,state)
    open(os.path.join(d,state+".png"),"wb").write(encode_png(W,H,buf))
    if state=="talk":
        for name,mw in [("talk_close",0),("talk_small",1),("talk_mid",2),("talk_wide",3)]:
            b=canvas(); base(b,V,mouth=mw); open(os.path.join(d,name+".png"),"wb").write(encode_png(W,H,b))
    print(state)
# idle already exists, keep it (do not overwrite) - ensure blink exists
print("done")

"""Genera los estados del monje/cura de AoE para gentle-emote-arcade.

6 estados x 2 poses, 48x40 RGBA, fondo transparente, solo stdlib:

  delegate  cura  repartiendo: 01 baculo en alto (wololo), 02 senalando
  judge     cura  mazo:        01 mazo arriba, 02 mazo apoyado
  review    cura  escriba:     01 pluma escribiendo, 02 pluma levantada
  remember  monje susurro:     01 mano en la boca, 02 mano afuera + ondas
  compact   monje:             01 tamano normal, 02 achicado (misma tunica)
  verify    monje escudo:      01 sello arriba, 02 sello estampado

think/ ya esta entregado por gen_priest.py: no se regenera ni se toca.
El cura (calvo, estola azul) sale con la misma silueta que think/; el monje
(habito marron con capucha) con la misma que hi/.
"""
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

def paste_scaled(dst,src,num=3,den=4,ground=37):
    """Pega src achicado num/den y anclado al piso. Samplea el pixel mas
    opaco de cada bloque para no perder el contorno (compact_02)."""
    dw=W*num//den; dh=H*num//den
    ox=(W-dw)//2; oy=ground-dh+1
    for dy in range(dh):
        sy0=dy*den//num; sy1=max(sy0+1,(dy+1)*den//num)
        for dx in range(dw):
            sx0=dx*den//num; sx1=max(sx0+1,(dx+1)*den//num)
            best=None; bestA=0
            for sy in range(sy0,min(sy1,H)):
                for sx in range(sx0,min(sx1,W)):
                    i=(sy*W+sx)*4
                    if src[i+3]>bestA:
                        bestA=src[i+3]; best=(src[i],src[i+1],src[i+2])
            if best is not None: setpx(dst,ox+dx,oy+dy,best)

# ---- paleta cura (gen_priest): calvo, estola azul, tunica marron ----
robe=(150,116,70); robeD=(115,86,50); robeDD=(85,62,34)
stole=(52,84,164); stoleL=(200,210,235); stoleD=(70,105,190)
skin=(232,176,138); skinD=(200,140,100); shine=(245,205,170)
shade=(186,128,92)
ink=(26,18,8); dark=(43,31,16); lip=(165,95,75)
wood=(139,105,60); woodD=(100,72,38); woodL=(170,135,80)
gold=(220,180,80); goldL=(255,220,130)
relic=(110,82,50); relicD=(80,58,32); relicL=(160,125,75)
red=(200,60,60); redL=(240,120,110); redD=(150,40,42)
parch=(238,230,206); parchD=(206,196,168); parchInk=(120,100,80)
green=(60,170,90); greenL=(120,220,140); steel=(150,152,162)

# ---- paleta monje (gen_monk): habito marron, capucha, cinto de soga ----
habit=(133,99,58); habitD=(99,71,40); habitDD=(72,51,28); hoodL=(150,114,70)
rope=(210,190,140); ropeL=(230,210,160); sandal=(90,65,40)
shieldC=(80,140,200); shieldL=(150,190,230); shieldW=(235,240,245)

# ===================== CURA (calvo, estola azul) =====================
def cura_torso(buf):
    rect(buf,20,35,24,36,robeDD); rect(buf,24,35,28,36,robeDD)
    rect(buf,17,17,31,34,dark)
    rect(buf,18,18,30,33,robe)
    rect(buf,18,18,30,20,robeD)
    rect(buf,23,18,25,33,robeD)
    rect(buf,19,18,22,33,stole); rect(buf,26,18,29,33,stole)
    rect(buf,19,18,19,33,stoleL); rect(buf,29,18,29,33,stoleL)
    rect(buf,19,18,22,19,stoleD); rect(buf,26,18,29,19,stoleD)

def cura_head(buf):
    rect(buf,20,8,28,19,skin)
    rect(buf,21,8,27,10,shine)
    rect(buf,20,11,21,18,skinD); rect(buf,27,11,28,18,skinD)
    rect(buf,20,8,28,9,(225,165,125))
    rect(buf,22,13,23,13,ink); rect(buf,25,13,26,13,ink)
    rect(buf,23,15,25,15,skinD)
    rect(buf,23,17,25,17,lip)

# brazo izquierdo
def cura_arm_relic(buf):
    rect(buf,10,20,17,30,dark); rect(buf,11,21,16,29,relic)
    rect(buf,11,21,16,22,relicL); rect(buf,13,23,15,27,relicD)
    rect(buf,13,24,15,26,(60,42,22))
    rect(buf,10,30,17,32,skin)

def cura_arm_down(buf):
    rect(buf,14,19,17,29,dark); rect(buf,15,20,16,28,robe)
    rect(buf,14,29,17,31,skin)

def cura_arm_point(buf):
    rect(buf,10,20,17,26,dark); rect(buf,11,21,16,25,robe)
    rect(buf,8,21,11,25,robeD)    # cuna de la manga
    rect(buf,5,22,9,24,skin)      # mano
    rect(buf,3,22,5,23,skin)      # dedo indice
    setpx(buf,3,22,shine)
    setpx(buf,5,24,skinD)

def cura_arm_parchment(buf):
    """Brazo izq sosteniendo el pergamino del escriba."""
    rect(buf,14,23,17,28,dark); rect(buf,15,24,16,27,robe)
    rect(buf,12,26,25,34,dark)                # borde (deja ver los pies en y35)
    rect(buf,13,27,24,33,parch)               # hoja
    rect(buf,13,27,24,27,parchD)
    rect(buf,15,29,21,29,parchInk)            # renglones
    rect(buf,15,31,20,31,parchInk)
    rect(buf,20,31,23,33,(150,60,60))         # sello de cera
    rect(buf,13,24,16,27,skin)                # mano sobre el borde
    setpx(buf,13,27,skinD)

# brazo derecho + prop
def staff(buf,x,y0,y1):
    rect(buf,x,y0,x+1,y1,wood)
    for y in range(y0,y1+1,3): setpx(buf,x,y,woodD)
    setpx(buf,x,y0,woodL); setpx(buf,x+1,y0,woodL)

def cura_arm_staff_up(buf):
    rect(buf,32,9,36,19,dark); rect(buf,33,10,35,18,robe)   # manga arriba
    rect(buf,32,5,37,9,skin)                  # puno que agarra el baculo
    rect(buf,32,9,37,9,skinD)
    staff(buf,37,0,33)                        # baculo en alto
    for (x,y) in [(40,2),(43,4),(41,7),(44,10),(40,13),(42,16)]: setpx(buf,x,y,gold)
    for (x,y) in [(39,3),(42,6),(43,12),(39,9),(33,0),(39,18)]: setpx(buf,x,y,goldL)

def cura_arm_staff_down(buf):
    rect(buf,31,19,34,27,dark); rect(buf,32,20,33,26,robe)
    rect(buf,32,27,37,30,skin)
    setpx(buf,37,30,skinD)
    staff(buf,36,4,37)

def cura_arm_gavel_up(buf):
    rect(buf,29,1,41,6,dark)                  # cabeza del mazo
    rect(buf,30,2,40,5,wood)
    rect(buf,30,2,40,2,woodL)
    rect(buf,30,3,31,5,woodD); rect(buf,39,3,40,5,woodD)
    rect(buf,33,6,36,9,dark); rect(buf,34,6,35,8,wood)    # mango a la vista
    rect(buf,32,9,37,13,skin)                 # mano
    rect(buf,32,13,37,13,skinD)
    rect(buf,32,13,35,21,dark); rect(buf,33,14,34,20,robe)  # manga

def cura_arm_gavel_down(buf):
    rect(buf,31,19,34,27,dark); rect(buf,32,20,33,26,robe)
    rect(buf,31,27,37,31,skin)                # mano
    rect(buf,31,31,37,31,skinD)
    rect(buf,35,31,36,35,wood)                # mango
    setpx(buf,35,33,woodD)
    rect(buf,30,34,42,38,dark)                # cabeza apoyada en el piso
    rect(buf,31,35,41,37,wood)
    rect(buf,31,35,41,35,woodL)
    rect(buf,31,36,32,37,woodD); rect(buf,40,36,41,37,woodD)

def plume(buf,x,y):
    """Plumon rojo. (x,y) es la punta; crece hacia abajo-izquierda."""
    rect(buf,x,y,x,y,red)
    rect(buf,x-1,y+1,x,y+1,red)
    rect(buf,x-2,y+2,x+1,y+2,red)
    rect(buf,x-3,y+3,x+1,y+3,red)
    rect(buf,x-3,y+4,x,y+4,red)
    rect(buf,x-3,y+5,x-1,y+5,red)
    rect(buf,x-4,y+6,x-2,y+6,red)
    rect(buf,x-4,y+7,x-3,y+7,red)
    setpx(buf,x,y+1,redL); setpx(buf,x-1,y+2,redL)
    setpx(buf,x-1,y+3,redL); setpx(buf,x-2,y+4,redL)
    setpx(buf,x-2,y+5,redL); setpx(buf,x-3,y+6,redL)
    setpx(buf,x+1,y+3,redD); setpx(buf,x,y+4,redD); setpx(buf,x-1,y+5,redD)

def cura_arm_quill_write(buf):
    # cana: punta sobre el pergamino (24,28) -> plumon (35,14)
    for i in range(12): setpx(buf,24+i,28-i,woodD)
    plume(buf,35,14)
    rect(buf,29,19,33,25,dark); rect(buf,30,20,32,24,robe)  # manga
    rect(buf,26,23,31,26,skin)                # mano
    rect(buf,26,26,31,26,skinD)
    setpx(buf,23,29,ink)                      # tinta recien puesta

def cura_arm_quill_up(buf):
    for i in range(9): setpx(buf,28+i,17-i,woodD)   # cana levantada
    plume(buf,38,3)
    rect(buf,32,12,35,21,dark); rect(buf,33,13,34,20,robe)  # manga
    rect(buf,31,8,36,12,skin)                 # mano en alto
    rect(buf,31,12,36,12,skinD)

def delegate_01():
    buf=canvas(); cura_torso(buf); cura_arm_relic(buf); cura_arm_staff_up(buf); cura_head(buf)
    return buf

def delegate_02():
    buf=canvas(); cura_torso(buf); cura_arm_point(buf); cura_arm_staff_down(buf); cura_head(buf)
    return buf

def judge_01():
    buf=canvas(); cura_torso(buf); cura_arm_down(buf); cura_arm_gavel_up(buf); cura_head(buf)
    return buf

def judge_02():
    buf=canvas(); cura_torso(buf); cura_arm_down(buf); cura_arm_gavel_down(buf); cura_head(buf)
    return buf

def review_01():
    buf=canvas(); cura_torso(buf); cura_arm_parchment(buf); cura_arm_quill_write(buf); cura_head(buf)
    return buf

def review_02():
    buf=canvas(); cura_torso(buf)
    cura_arm_parchment(buf)
    cura_arm_quill_up(buf); cura_head(buf)
    return buf

# ===================== MONJE (capucha marron) =====================
def monje_torso(buf):
    rect(buf,20,35,24,36,sandal); rect(buf,24,35,28,36,sandal)
    setpx(buf,21,36,skinD); setpx(buf,26,36,skinD)
    rect(buf,17,17,31,34,dark)
    rect(buf,18,18,30,33,habit)
    rect(buf,18,18,30,21,habitD)
    rect(buf,18,28,21,33,habitD); rect(buf,27,28,30,33,habitD)
    rect(buf,23,18,25,33,habitD)
    rect(buf,18,24,30,26,rope)
    rect(buf,18,24,30,24,ropeL)
    rect(buf,24,26,26,29,rope); rect(buf,25,29,27,30,rope)

def monje_hood(buf):
    rect(buf,16,4,32,22,dark)
    rect(buf,17,5,31,21,habit)
    rect(buf,17,5,31,8,habitD)
    rect(buf,17,5,18,21,habitDD); rect(buf,30,5,31,21,habitDD)
    rect(buf,21,3,27,5,habit)
    rect(buf,23,3,25,4,hoodL)

def monje_face(buf,blink=False):
    rect(buf,20,9,28,19,skin)
    rect(buf,20,9,28,10,shade)
    rect(buf,20,14,21,19,skinD); rect(buf,27,14,28,19,skinD)
    if blink:
        rect(buf,22,14,23,14,skinD); rect(buf,25,14,26,14,skinD)
    else:
        rect(buf,22,14,23,14,ink); rect(buf,25,14,26,14,ink)
        rect(buf,22,13,23,13,(110,80,50)); rect(buf,25,13,26,13,(110,80,50))
    setpx(buf,24,16,skinD)
    rect(buf,23,18,25,18,lip)

def monje_arm_left_down(buf):
    rect(buf,14,19,17,29,dark); rect(buf,15,20,16,28,habit)
    rect(buf,14,29,17,31,skin)

def monje_arm_right_down(buf):
    rect(buf,31,19,34,27,dark); rect(buf,32,20,33,26,habit)
    rect(buf,32,27,35,30,skin)

def monje_shield(buf):
    """Escudo en el brazo izquierdo (verify)."""
    rect(buf,12,19,17,28,dark); rect(buf,13,20,16,27,habit)
    rect(buf,13,27,17,29,skin)
    rect(buf,6,15,15,30,dark)                 # escudo
    rect(buf,7,16,14,29,shieldC)
    rect(buf,7,16,14,17,shieldL)
    rect(buf,7,28,14,29,(60,110,170))
    rect(buf,9,19,12,26,shieldW)              # blason
    rect(buf,7,22,14,23,shieldW)
    setpx(buf,8,16,shieldL); setpx(buf,13,16,shieldL)

def monje_seal_up(buf):
    rect(buf,33,10,36,19,dark); rect(buf,34,11,35,18,habit)  # manga
    rect(buf,33,6,38,9,skin)                  # mano
    rect(buf,33,9,38,9,skinD)
    rect(buf,35,2,37,6,woodD)                 # mango
    rect(buf,35,2,37,2,gold)
    rect(buf,32,10,39,11,dark)                # bloque del sello
    rect(buf,33,10,38,11,steel)
    rect(buf,33,12,38,13,green)               # almohadilla
    rect(buf,33,13,38,13,greenL)

def monje_seal_down(buf):
    rect(buf,32,19,36,27,dark); rect(buf,33,20,35,26,habit)
    rect(buf,32,27,38,31,skin)                # mano
    rect(buf,32,31,38,31,skinD)
    rect(buf,35,31,37,34,woodD)               # mango
    rect(buf,32,34,40,35,steel)               # bloque
    rect(buf,31,36,41,37,green)               # almohadilla estampando
    rect(buf,31,36,41,36,greenL)
    rect(buf,29,38,35,38,(90,190,110))        # marca en el piso
    rect(buf,37,38,42,38,(90,190,110))

def monje_whisper_in(buf):
    """Mano ahuecada tapando la boca."""
    rect(buf,29,20,33,26,dark); rect(buf,30,21,32,25,habit)
    rect(buf,24,15,29,20,skin)                # mano en la boca
    rect(buf,24,15,29,15,skinD)
    rect(buf,24,20,29,20,skinD)
    rect(buf,26,16,26,19,skinD)               # dedo
    setpx(buf,30,16,skin); setpx(buf,30,19,skinD)

def monje_whisper_out(buf):
    """Mano corrida + ondas del susurro."""
    rect(buf,30,19,34,26,dark); rect(buf,31,20,33,25,habit)
    rect(buf,29,14,34,19,skin)                # mano abierta
    rect(buf,29,14,34,14,skinD)
    rect(buf,31,15,31,18,skinD)
    rect(buf,29,19,34,19,skinD)
    setpx(buf,35,16,skin); setpx(buf,35,18,skinD)
    for (x,y) in [(37,12),(38,13),(38,14),(37,15)]: setpx(buf,x,y,gold)
    for (x,y) in [(40,9),(41,10),(41,11),(41,12),(40,13)]: setpx(buf,x,y,gold)

def relicario(buf, cx, cy, brillo):
    """Relicario dorado con cruz; brillo suma destellos."""
    rect(buf, cx - 3, cy - 4, cx + 3, cy + 4, (150, 110, 45))
    rect(buf, cx - 2, cy - 3, cx + 2, cy + 3, gold)
    rect(buf, cx - 2, cy - 3, cx + 2, cy - 2, goldL)
    rect(buf, cx - 1, cy - 1, cx + 1, cy + 2, (150, 110, 45))
    setpx(buf, cx, cy, goldL)
    setpx(buf, cx, cy - 1, (255, 240, 180))
    pts = ((-5, -5), (5, -5), (-6, 0), (6, 0), (-5, 5), (5, 5)) if brillo else ((-5, -5), (5, -5))
    for (dx, dy) in pts:
        setpx(buf, cx + dx, cy + dy, goldL)


def nicho(buf, cx, cy):
    """Hornacina de piedra con arco para entronizar la reliquia."""
    rect(buf, cx - 7, cy - 9, cx + 7, cy + 8, dark)
    rect(buf, cx - 6, cy - 8, cx + 6, cy + 7, (52, 42, 28))
    rect(buf, cx - 5, cy - 7, cx + 5, cy + 6, (36, 28, 18))
    for dx, w in ((-4, 9), (-3, 7), (-2, 5), (-1, 3)):
        pass
    for i, dx in enumerate((4, 3, 2, 1)):
        y = cy - 8 - i
        if y >= 0:
            for x in range(cx - dx, cx + dx + 1):
                setpx(buf, x, y, (52, 42, 28))


def remember_01():
    buf=canvas(); monje_torso(buf); monje_hood(buf); monje_face(buf)
    monje_arm_left_down(buf); monje_arm_right_down(buf)
    relicario(buf, 38, 24, False)
    return buf

def remember_02():
    buf=canvas(); monje_torso(buf); monje_hood(buf); monje_face(buf)
    monje_arm_left_down(buf); monje_arm_right_down(buf)
    nicho(buf, 38, 24)
    relicario(buf, 38, 25, True)
    return buf

def compact_01():
    buf=canvas()
    rect(buf, 9, 9, 39, 33, dark)
    rect(buf, 10, 10, 38, 32, parch)
    for y in (14, 18, 22, 26):
        rect(buf, 14, y, 34, y, parchInk)
    rect(buf, 14, 30, 22, 30, parchInk)
    rect(buf, 4, 18, 8, 24, skin)
    rect(buf, 40, 18, 44, 24, skin)
    setpx(buf, 4, 21, skinD); setpx(buf, 44, 21, skinD)
    return buf

def compact_02():
    buf=canvas()
    rect(buf, 5, 18, 8, 22, woodD)
    rect(buf, 40, 18, 43, 22, woodD)
    rect(buf, 8, 14, 40, 26, dark)
    rect(buf, 9, 15, 39, 25, parch)
    rect(buf, 9, 18, 39, 18, parchD)
    rect(buf, 9, 22, 39, 22, parchD)
    rect(buf, 22, 24, 28, 30, dark)
    rect(buf, 23, 25, 27, 29, green)
    rect(buf, 23, 25, 27, 25, greenL)
    for (x, y) in ((24, 27), (25, 28), (26, 27), (27, 26), (28, 25)):
        setpx(buf, x, y, steel)
        setpx(buf, x, y + 1, steel)
    rect(buf, 22, 30, 23, 36, red)
    rect(buf, 26, 30, 27, 36, redD)
    return buf

TRAZO1 = ((30, 19), (31, 20), (32, 21), (33, 22), (34, 23))
TRAZO2 = ((34, 23), (35, 22), (36, 21), (37, 20), (38, 19), (39, 18))

def escudo_grande(buf):
    rect(buf, 26, 12, 44, 30, dark)
    rect(buf, 27, 13, 43, 29, shieldC)
    hline = None
    for x in range(27, 44):
        setpx(buf, x, 13, shieldL)
    for (y, x0, x1) in ((30, 29, 41), (31, 31, 39), (32, 33, 37), (33, 34, 36)):
        for x in range(x0, x1 + 1):
            setpx(buf, x, y, shieldC)
        setpx(buf, x0 - 1, y, dark); setpx(buf, x1 + 1, y, dark)

def tilde(buf, trazos, col):
    for x, y in trazos:
        setpx(buf, x, y, col)
        setpx(buf, x, y + 1, col)

def verify_01():
    buf=canvas(); monje_torso(buf); monje_hood(buf); monje_face(buf)
    monje_shield(buf); monje_seal_up(buf)
    escudo_grande(buf)
    tilde(buf, TRAZO1, green)
    return buf

def verify_02():
    buf=canvas(); monje_torso(buf); monje_hood(buf); monje_face(buf)
    monje_shield(buf); monje_seal_down(buf)
    escudo_grande(buf)
    tilde(buf, TRAZO1 + TRAZO2, greenL)
    for (x, y) in ((29, 15), (41, 24), (31, 27)):
        setpx(buf, x, y, shieldW)
    return buf

# ===================== salida + verificacion =====================
BASE=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..","emotes","aoe"))

FRAMES=[
 ("delegate","delegate_01.png",delegate_01),("delegate","delegate_02.png",delegate_02),
 ("judge","judge_01.png",judge_01),("judge","judge_02.png",judge_02),
 ("review","review_01.png",review_01),("review","review_02.png",review_02),
 ("remember","remember_01.png",remember_01),("remember","remember_02.png",remember_02),
 ("compact","compact_01.png",compact_01),("compact","compact_02.png",compact_02),
 ("verify","verify_01.png",verify_01),("verify","verify_02.png",verify_02),
]

def verify_png(path):
    """IHDR obligatorio + transparencia real leida del archivo escrito."""
    data=open(path,"rb").read()
    assert data[:8]==b"\x89PNG\r\n\x1a\n", path
    assert struct.unpack(">I",data[8:12])[0]==13 and data[12:16]==b"IHDR", path
    w,h,depth,ctype,comp,filt,inter=struct.unpack(">IIBBBBB",data[16:29])
    assert (w,h,depth,ctype,comp,filt,inter)==(W,H,8,6,0,0,0), (path,w,h,depth,ctype,comp,filt,inter)
    assert data[29:33]==struct.pack(">I",zlib.crc32(data[12:29])&0xffffffff), path
    assert data[-8:-4]==b"IEND", path
    idat=b""; i=8
    while i<len(data):
        ln=struct.unpack(">I",data[i:i+4])[0]; t=data[i+4:i+8]
        if t==b"IDAT": idat+=data[i+8:i+8+ln]
        i+=12+ln
    raw=zlib.decompress(idat); stride=W*4
    assert len(raw)==(stride+1)*H, path
    clear=solid=0
    for y in range(H):
        assert raw[y*(stride+1)]==0, path
        row=raw[y*(stride+1)+1:y*(stride+1)+1+stride]
        for x in range(W):
            a=row[x*4+3]
            clear+= a==0
            solid+= a==255
    assert clear>0 and solid>0, (path,"fondo/figura")
    return w,h,depth,ctype,inter,clear,solid

written=[]
for carpeta,nombre,build in FRAMES:
    buf=build(); assert len(buf)==W*H*4
    d=os.path.join(BASE,carpeta); os.makedirs(d,exist_ok=True)
    p=os.path.join(d,nombre)
    open(p,"wb").write(encode_png(W,H,buf))
    w,h,depth,ctype,inter,clear,solid=verify_png(p)
    rel=carpeta+"/"+nombre
    written.append(rel)
    print("ok %-22s %dx%d bd%d ct%d il%d  alfa0=%-4d opaco=%d"%(rel,w,h,depth,ctype,inter,clear,solid))

print("\n%d frames:"%len(written))
for rel in written: print("  emotes/aoe/"+rel)

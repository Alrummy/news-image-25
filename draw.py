from PIL import Image, ImageDraw, ImageFont
import os, math

W = H = 1024
PAPER = (246, 240, 224)
PANEL = (250, 246, 234)
INK = (28, 30, 29)
MUTED = (94, 91, 82)
RED = (177, 47, 38)
PALE = (224, 216, 197)
SEA = (214, 224, 219)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(path, size): return ImageFont.truetype(path, size)

im = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(im)

# Fine newsprint border and masthead
for inset, color, width in [(18, INK, 2), (24, PALE, 1)]:
    d.rectangle((inset, inset, W-inset, H-inset), outline=color, width=width)
d.text((42, 22), "THE WORLD", font=font(SERIF, 62), fill=INK)
d.text((46, 91), "WEDNESDAY 25 NOVEMBER 2026", font=font(BOLD, 18), fill=RED)
d.line((42, 119, 982, 119), fill=INK, width=3)
d.text((800, 97), "GLOBAL BRIEF  /  05", font=font(BOLD, 12), fill=MUTED)

# Text helpers
def wrap(text, f, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = word if not line else line + " " + word
        if d.textbbox((0, 0), trial, font=f)[2] <= max_width:
            line = trial
        else:
            if line: lines.append(line)
            line = word
    if line: lines.append(line)
    return lines

def fit_lines(text, max_width, max_height, start=24, minimum=16, path=BOLD, spacing=3):
    for size in range(start, minimum-1, -1):
        f = font(path, size)
        lines = wrap(text, f, max_width)
        h = len(lines) * (size + spacing)
        if h <= max_height:
            return f, lines
    f = font(path, minimum)
    return f, wrap(text, f, max_width)

def draw_paragraph(x, y, lines, f, fill, spacing=3):
    step = f.size + spacing
    for line in lines:
        d.text((x, y), line, font=f, fill=fill)
        y += step
    return y

def panel_box(box, num, category):
    x1,y1,x2,y2 = box
    d.rounded_rectangle(box, radius=8, fill=PANEL, outline=INK, width=2)
    d.rounded_rectangle((x1+11,y1+11,x1+43,y1+43), radius=4, fill=RED)
    nf = font(BOLD, 19)
    bb = d.textbbox((0,0), str(num), font=nf)
    d.text((x1+27-(bb[2]-bb[0])/2, y1+14), str(num), font=nf, fill=PAPER)
    d.text((x1+54,y1+16), category, font=font(BOLD, 14), fill=RED)
    d.line((x1+14,y1+52,x2-14,y1+52), fill=PALE, width=2)

def draw_headline(text, x, y, width, max_h, start=25, minimum=18):
    f, lines = fit_lines(text, width, max_h, start, minimum, BOLD, 2)
    return draw_paragraph(x,y,lines,f,INK,2), f.size, lines

# Story 1 — wide lead panel
box=(38,132,986,365)
panel_box(box,1,"STRAIT OF HORMUZ")
draw_headline("TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ",55,196,625,91,35,27)
detail="Iran's IRGC says both vessels exploded and caught fire on an unauthorized route."
df=font(SANS,18)
draw_paragraph(56,294,wrap(detail,df,618),df,MUTED,4)
# Sea scene on right
sx, sy = 716, 190
d.rounded_rectangle((sx,sy,sx+245,sy+145), radius=6, fill=SEA)
# horizon and wave marks
d.line((sx+8,sy+77,sx+237,sy+77), fill=(154,174,170), width=2)
for yy in (95,116,134):
    for xx in (sx+12,sx+75,sx+143,sx+204):
        d.arc((xx,sy+yy-5,xx+28,sy+yy+5), 190, 345, fill=(104,135,134), width=2)
def tanker(x,y,scale=1,fire=False):
    # long deck and hull silhouette
    pts=[(x,y+35*scale),(x+104*scale,y+35*scale),(x+91*scale,y+52*scale),(x+16*scale,y+52*scale)]
    d.polygon(pts, fill=INK)
    d.rectangle((x+25*scale,y+21*scale,x+39*scale,y+35*scale), fill=INK)
    d.rectangle((x+38*scale,y+25*scale,x+50*scale,y+35*scale), fill=INK)
    d.rectangle((x+56*scale,y+27*scale,x+69*scale,y+35*scale), fill=INK)
    d.line((x+18*scale,y+19*scale,x+18*scale,y+34*scale), fill=INK, width=max(1,int(2*scale)))
    if fire:
        cx=x+78*scale; cy=y+12*scale
        d.polygon([(cx,cy+22*scale),(cx-7*scale,cy+7*scale),(cx,cy),(cx+5*scale,cy+11*scale),(cx+10*scale,cy+4*scale),(cx+13*scale,cy+22*scale)],fill=RED)
        d.ellipse((cx-2*scale,cy+14*scale,cx+8*scale,cy+28*scale),fill=(232,126,49))
tanker(sx+18,sy+48,.85,False)
tanker(sx+124,sy+83,.82,True)

# Four lower stories in two columns
cards=[
 ((38,378,506,671),2,"U.S. COURTS","HUAWEI CONVICTED IN U.S. CRIMINAL TRIAL","A federal court found the Chinese tech giant guilty of stealing trade secrets and bank fraud.","court"),
 ((518,378,986,671),3,"SPACE","PAKISTAN'S FIRST ASTRONAUT REACHES CHINA'S SPACE STATION","Shenzhou-24 docks carrying the first foreign astronaut to China's station.","space"),
 ((38,684,506,977),4,"PACIFIC","AUSTRALIA AND SOLOMON ISLANDS SIGN SECURITY TREATY","The pact bars any foreign military or security base on the Solomon Islands.","pacific"),
 ((518,684,986,977),5,"RIYADH","HOUTHIS STRIKE RIYADH'S TALLEST TOWER","Eleven wounded in the capital; Houthis also claim an attack on Saudi Arabia's largest oil refinery.","riyadh"),
]

def draw_court(x,y,w,h):
    # courthouse facade with pediment, columns, steps and gavel
    d.rectangle((x,y,x+w,y+h), fill=(235,229,212), outline=PALE, width=1)
    d.polygon([(x+18,y+48),(x+w//2,y+12),(x+w-18,y+48)], fill=INK)
    d.rectangle((x+25,y+48,x+w-25,y+58), fill=INK)
    for cx in (x+38,x+68,x+98,x+128):
        d.rectangle((cx,y+60,cx+12,y+126), fill=(250,246,234), outline=INK, width=2)
    d.rectangle((x+24,y+126,x+w-22,y+137), fill=INK)
    d.rectangle((x+14,y+138,x+w-12,y+147), fill=INK)
    # red seal
    d.ellipse((x+w-42,y+16,x+w-20,y+38), fill=RED)

def draw_space(x,y,w,h):
    d.rectangle((x,y,x+w,y+h), fill=(31,42,58))
    for px,py in ((x+22,y+22),(x+130,y+27),(x+48,y+118),(x+148,y+87)):
        d.ellipse((px,py,px+3,py+3),fill=PAPER)
    # station body & solar panels
    d.rectangle((x+55,y+65,x+145,y+82), fill=(224,218,198), outline=INK, width=2)
    d.rectangle((x+79,y+47,x+104,y+99), fill=(224,218,198), outline=INK, width=2)
    for xx in (x+15,x+145):
        d.rectangle((xx,y+57,xx+35,y+90), fill=(89,125,148), outline=(210,209,192), width=2)
        for k in (1,2): d.line((xx+k*11,y+59,xx+k*11,y+88), fill=(199,211,202), width=1)
        d.line((xx+2,y+73,xx+33,y+73), fill=(199,211,202), width=1)
    # capsule approaching
    d.polygon([(x+158,y+106),(x+176,y+96),(x+188,y+105),(x+185,y+123),(x+169,y+128)], fill=RED, outline=PAPER)
    d.line((x+149,y+112,x+164,y+112), fill=PAPER, width=2)

def draw_pacific(x,y,w,h):
    d.rectangle((x,y,x+w,y+h), fill=(220,231,225))
    # islands
    d.polygon([(x+12,y+104),(x+31,y+85),(x+56,y+92),(x+72,y+71),(x+91,y+78),(x+104,y+105),(x+88,y+119),(x+47,y+124)], fill=(81,111,83))
    d.polygon([(x+118,y+100),(x+139,y+82),(x+159,y+92),(x+174,y+72),(x+198,y+89),(x+213,y+115),(x+187,y+126),(x+149,y+120)], fill=(81,111,83))
    # linking treaty shield
    cx=x+w//2; cy=y+48
    d.polygon([(cx,cy-30),(cx+25,cy-20),(cx+22,cy+7),(cx,cy+24),(cx-22,cy+7),(cx-25,cy-20)], fill=PANEL, outline=RED)
    d.line((cx-11,cy-2,cx-2,cy+7,cx+14,cy-11), fill=RED, width=4)
    d.text((x+13,y+9),"AU",font=font(BOLD,13),fill=INK)
    d.text((x+w-42,y+9),"SI",font=font(BOLD,13),fill=INK)

def draw_riyadh(x,y,w,h):
    d.rectangle((x,y,x+w,y+h), fill=(237,225,207))
    # skyline
    d.rectangle((x+10,y+88,x+52,y+142),fill=(89,87,77))
    d.rectangle((x+57,y+69,x+92,y+142),fill=(116,105,88))
    d.rectangle((x+99,y+24,x+137,y+142),fill=INK)
    d.polygon([(x+99,y+24),(x+118,y+7),(x+137,y+24)],fill=INK)
    d.line((x+118,y+7,x+118,y+0),fill=INK,width=3)
    for yy in (42,58,74,90,106,122):
        d.line((x+106,y+yy,x+130,y+yy),fill=(209,185,139),width=2)
    d.rectangle((x+145,y+84,x+183,y+142),fill=(101,95,81))
    d.rectangle((x+190,y+99,x+220,y+142),fill=(121,105,85))
    # impact burst
    cx,cy=x+158,y+47
    for ang in range(0,360,45):
        ex=cx+int(18*math.cos(math.radians(ang))); ey=cy+int(18*math.sin(math.radians(ang)))
        d.line((cx,cy,ex,ey),fill=RED,width=3)
    d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=RED)
    d.ellipse((x+16,y+118,x+29,y+131),fill=RED)

scene_fns={"court":draw_court,"space":draw_space,"pacific":draw_pacific,"riyadh":draw_riyadh}
for box,num,cat,headline,detail,scene in cards:
    panel_box(box,num,cat)
    x1,y1,x2,y2=box
    # Story text column with dedicated illustration box to its right
    ix=x1+292; iy=y1+91; iw=151; ih=151
    scene_fns[scene](ix,iy,iw,ih)
    tx=x1+16; tw=258
    bottom, size, hl=draw_headline(headline,tx,y1+65,tw,103,24,18)
    # detail in compact readable type; fit within lower-left text region
    detail_font=font(SANS,14)
    lines=wrap(detail,detail_font,tw)
    max_lines=max(1,(y2-14-max(bottom+8,y1+178))//18)
    if len(lines)>max_lines:
        for fs in range(14,11,-1):
            trialf=font(SANS,fs); trial=wrap(detail,trialf,tw)
            if len(trial)<=max_lines:
                detail_font,lines=trialf,trial; break
    draw_paragraph(tx,max(bottom+7,y1+174),lines,detail_font,MUTED,3)

# Footer
# thin rule and centered credit
d.line((42,989,982,989),fill=INK,width=2)
footer="make.fun daily news image — 25 November 2026"
ff=font(SANS,13); fw=d.textbbox((0,0),footer,font=ff)[2]
d.text(((W-fw)/2,993),footer,font=ff,fill=MUTED)

out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"entry.png")
im.save(out,format="PNG",optimize=True)
print(out)

"""brand_overlays.py OUTDIR FONTDIR LOGO_PNG [--caption "Line1|Line2" NAME Y] [--tag "Text" NAME] [--endcard]
MOPC Network styles measured from approved bumper reels (9:16, 1080x1920).
Fonts: Montserrat[wght].ttf from cdn.jsdelivr.net/gh/google/fonts@main/ofl/montserrat/ ; logo: rasterised MOPC_Logo_Colour.svg (cairosvg)."""
import sys
from PIL import Image, ImageDraw, ImageFont
a=sys.argv; out,fd,logo=a[1],a[2],a[3]; W,H=1080,1920
PUR=(120,77,158); NAVY=(40,64,120); GREEN=(137,187,59); BG=(241,242,245)
def font(sz): f=ImageFont.truetype(f'{fd}/Montserrat.ttf',sz); f.set_variation_by_name(b'Bold'); return f
def centred(d,t,f,cy,fill,x=None):
    bb=d.textbbox((0,0),t,font=f); tw=d.textlength(t,font=f); d.text((x if x is not None else (W-tw)/2, cy-(bb[1]+bb[3])/2),t,font=f,fill=fill)
for i in [j for j,x in enumerate(a) if x=='--caption']:
    lines=a[i+1].split('|'); name=a[i+2]; y0=int(a[i+3])
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); f=font(64); lh=112
    for k,t in enumerate(lines):
        tw=d.textlength(t,font=f); x0=(W-tw)/2-38; y=y0+k*(lh+14)
        d.rounded_rectangle([x0,y,x0+tw+76,y+lh],radius=20,fill=PUR); centred(d,t,f,y+lh/2,'white')
    im.save(f'{out}/{name}.png')
for i in [j for j,x in enumerate(a) if x=='--tag']:
    t,name=a[i+1],a[i+2]
    im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); f=font(40); tw=d.textlength(t,font=f)
    d.rounded_rectangle([80,300,80+tw+48,376],radius=10,fill='white'); centred(d,t,f,338,NAVY,x=104); im.save(f'{out}/{name}.png')
if '--endcard' in a:
    im=Image.new('RGB',(W,H),BG); lg=Image.open(logo).convert('RGBA'); lg=lg.resize((540,int(lg.height*540/lg.width)),Image.LANCZOS)
    im.paste(lg,((W-540)//2,766),lg); d=ImageDraw.Draw(im); d.rounded_rectangle([280,1032,799,1151],radius=60,fill=GREEN)
    centred(d,'Check your address.',font(41),1091,'white'); im.save(f'{out}/endcard_mopc.png')

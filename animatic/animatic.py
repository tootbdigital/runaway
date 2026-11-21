import math, subprocess, wave, struct, sys
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,BPM=1280,720,24,90
BEAT=60/BPM; LINE=4*BEAT  # 1 linha de letra = 4 batidas (~2,7 s)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fL=ImageFont.truetype(FB,50); fS=ImageFont.truetype(FB,26); fT=ImageFont.truetype(FB,84)
BLUE=(91,184,245); PINK=(247,168,201)
COL={"red":(235,64,52),"yellow":(250,204,20),"green":(70,180,80),"none":(255,255,255)}
CHORUS=[("Que cor é essa, Tutila?","Tuti"),("É a cor que a gente vê!","Tutila"),
        ("Que cor é essa, Tuti?","Tutila"),("Vem comigo aprender!","both")]
def verse(l,c): return [(l[0],"Tuti",c),(l[1],"Tuti",c),(l[2],"Tutila",c),(l[3],"both",c)]
V1=verse(["Tuti viu uma maçã","Redondinha e bem doce","Tutila diz: é vermelha!","Vermelho, vermelho, viva!"],"red")
V2=verse(["Brilha lá no céu azul","Um sol que nos aquece","Tutila diz: é amarelo!","Amarelo, amarelo, viva!"],"yellow")
V3=verse(["Pula a rã na folha","Pula e se diverte","Tutila diz: é verde!","Verde, verde, viva!"],"green")
CH=[(t,w,"none") for t,w in CHORUS]
lines=[("Tuti e Tutila","both","none"),("Que cor é essa?","both","none")]
lines+=V1+CH+V2+CH+V3+CH+[("Muito bem! Até o próximo!","both","none")]
total=len(lines)*LINE
def tuti(d,x,y,col,s,smile=True):
    d.ellipse([x-95*s,y-60*s,x-25*s,y+30*s],fill=col,outline=(40,40,60),width=4)
    d.ellipse([x+25*s,y-60*s,x+95*s,y+30*s],fill=col,outline=(40,40,60),width=4)
    d.ellipse([x-70*s,y-70*s,x+70*s,y+70*s],fill=col,outline=(40,40,60),width=5)
    for ex in (-26,26):
        d.ellipse([x+ex*s-14*s,y-24*s-14*s,x+ex*s+14*s,y-24*s+14*s],fill="white",outline=(40,40,60),width=3)
        d.ellipse([x+ex*s-6*s,y-24*s-6*s,x+ex*s+6*s,y-24*s+6*s],fill=(30,30,50))
    d.rounded_rectangle([x-16*s,y-2*s,x+16*s,y+90*s],radius=16*s,fill=col,outline=(40,40,60),width=4)
    d.arc([x-30*s,y+14*s,x+30*s,y+50*s],20,160,fill=(40,40,60),width=3) if smile else None
def frame(t):
    idx=min(int(t//LINE),len(lines)-1); txt,who,c=lines[idx]
    ph=(t%BEAT)/BEAT; bounce=abs(math.sin(ph*math.pi))  # sobe no tempo
    im=Image.new("RGB",(W,H),(255,248,225)); d=ImageDraw.Draw(im)
    d.rectangle([0,560,W,H],fill=(200,235,190))
    # objeto da lição
    if c!="none":
        r=70+10*bounce; d.ellipse([W/2-r,250-r,W/2+r,250+r],fill=COL[c],outline=(40,40,60),width=5)
    else:
        d.text((W/2,200),"Cores!" if idx<2 else "",font=fT,fill=(120,90,160),anchor="mm")
    act=lambda n: who in (n,"both")
    for n,x,col in (("Tuti",330,BLUE),("Tutila",950,PINK)):
        s=1.35+(0.12*bounce if act(n) else 0); y=470-(30*bounce if act(n) else 0)
        tuti(d,x,y,col,s); d.text((x,590),n,font=fS,fill=(70,70,90),anchor="mm")
    d.rounded_rectangle([60,630,W-60,700],radius=20,fill=(255,255,255),outline=(40,40,60),width=3)
    d.text((W/2,665),txt,font=fL,fill=(40,40,60),anchor="mm")
    d.text((20,15),f"ANIMATIC  linha {idx+1}/{len(lines)}  ·  placeholder 2D, personagens e cores a definir na bíblia",font=fS,fill=(130,130,150))
    return im
# áudio de marcação: clique a cada batida (mais agudo no 1 do compasso) + nota-guia suave por linha
sr=22050; n=int(total*sr); buf=[0.0]*n
def tone(t0,f,dur,amp):
    i0=int(t0*sr)
    for i in range(int(dur*sr)):
        if i0+i>=n: break
        buf[i0+i]+=amp*math.sin(2*math.pi*f*i/sr)*math.exp(-6*i/(dur*sr))
for b in range(int(total/BEAT)): tone(b*BEAT,1200 if b%4==0 else 800,0.08,0.35)
with wave.open("/tmp/claude-0/click.wav","wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
    w.writeframes(b"".join(struct.pack("<h",int(max(-1,min(1,v))*32000)) for v in buf))
out=sys.argv[1]
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
  "-i","/tmp/claude-0/click.wav","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-shortest",out],stdin=subprocess.PIPE)
for f in range(int(total*FPS)): p.stdin.write(frame(f/FPS).tobytes())
p.stdin.close(); p.wait(); print("ok",total)

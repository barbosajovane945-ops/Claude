#!/usr/bin/env python3
"""Gera index.html com as 22 cenas do roteiro (9:16, 720x1280), controladas por window.render(t)."""
import html, re, sys, pathlib

# (inicio, fim, legenda — *palavra* fica amarela, prop, texto do medidor, rótulo do medidor)
SCENES = [
    (0, 4, "ACORDOU NUMA MANSÃO.", "room", None, None),
    (4, 8, "A PORTA ESTÁ *TRANCADA*.", "corridor", None, None),
    (8, 13, "SEU CÉREBRO GASTA *20%*.", "xray", "20%", "ENERGIA"),
    (13, 17, "O VÍRUS ESPALHOU *RÁPIDO*.", "vitrine", None, None),
    (17, 22, "SEM AR, O CÉREBRO SOFRE EM *POUCOS MINUTOS*.", "timer", None, None),
    (22, 26, "ELE ESTÁ *ATRÁS* DE VOCÊ.", "zombie", None, None),
    (26, 31, "O CORAÇÃO PASSA DE *150 BATIDAS*.", "speed", "150 BPM", "CORAÇÃO"),
    (31, 35, "CADA MÃO TEM *27 OSSOS*.", "hand", "27", "OSSOS"),
    (35, 40, "A ARMA TEM *8 BALAS*.", "gun", "8", "BALAS"),
    (40, 44, "O LABORATÓRIO FICA *EMBAIXO*.", "tubes", None, None),
    (44, 49, "CADA DEGRAU *DÓI MAIS*.", "stairs", "×2", "TENSÃO"),
    (49, 53, "ALGO PULOU DO *TETO*.", "shadow", None, None),
    (53, 58, "É HORA DE *AGIR*.", "target", None, None),
    (58, 63, "O TIRO *ACERTOU*.", "boom", None, None),
    (63, 67, "A PORTA *ABRIU*.", "metaldoor", None, None),
    (67, 72, "OS PULMÕES TÊM CERCA DE *300 MILHÕES* DE PEQUENOS SACOS.", "lungs", "300 MI", "ALVÉOLOS"),
    (72, 77, "O CORPO CANSA *RÁPIDO*.", "tired", "×3", "CANSAÇO"),
    (77, 82, "A SENHA ESTÁ NO *DIÁRIO*.", "safe", None, None),
    (82, 87, "A SAÍDA ESTÁ *PERTO*.", "vault", None, None),
    (87, 92, "VOCÊ *SOBREVIVEU*.", "stars", None, None),
    (92, 97, "NEM TUDO *TERMINOU*.", "eye", None, None),
    (97, 100, "COMENTA O DESFECHO E ESCOLHE O *PRÓXIMO TEMA*.", "none", None, None),
]

# Cada prop é HTML simples; animações são aplicadas em JS via data-anim.
PROPS = {
    "none": "",
    "room": '<div class="arch" style="left:150px;top:260px"></div><div class="arch" style="left:420px;top:260px"></div>',
    "corridor": '<div class="wall"></div><div class="lamp" data-anim="flick"></div><div class="floor"></div>',
    "xray": '<div class="xray" data-anim="pulse"><div class="brain"></div></div>',
    "vitrine": '<div class="case"></div><div class="crack c1"></div><div class="crack c2"></div>',
    "timer": '<div class="clock" data-anim="shrink"><span id="timerText">4:00</span></div>',
    "zombie": '<div class="zb" data-anim="creep"><div class="zhead"></div><div class="zbody"></div><div class="eye e1"></div><div class="eye e2"></div></div>',
    "speed": '<div class="sl s1"></div><div class="sl s2"></div><div class="sl s3"></div><div class="sl s4"></div>',
    "hand": '<div class="hand" data-anim="pulse"><div class="fg"></div><div class="fg"></div><div class="fg"></div><div class="fg"></div><div class="fg"></div></div>',
    "gun": '<div class="pistol"></div><div class="ring" data-anim="pulse"></div>',
    "tubes": '<div class="tube t1"></div><div class="tube t2"></div><div class="tube t3"></div><div class="tube t4"></div>',
    "stairs": '<div class="stairs"></div>',
    "shadow": '<div class="shadow" data-anim="drift"></div>',
    "target": '<div class="cross" data-anim="pulse"></div>',
    "boom": '<div class="burst" data-anim="boom"></div>',
    "metaldoor": '<div class="mdoor" data-anim="rattle"></div><div class="redlight" data-anim="flick"></div>',
    "lungs": '<div class="lung l1"></div><div class="lung l2"></div>',
    "tired": '<div class="sweat" data-anim="drip"></div>',
    "safe": '<div class="safe"><div class="dial" data-anim="spin"></div></div>',
    "vault": '<div class="gold" data-anim="pulse"></div>',
    "stars": '<div class="moon"></div><div class="star st1"></div><div class="star st2"></div><div class="star st3"></div><div class="star st4"></div>',
    "eye": '<div class="window"></div><div class="yeye" data-anim="flick"></div>',
}

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#000}
#stage{position:relative;width:720px;height:1280px;overflow:hidden;
  background:radial-gradient(circle at 50% 40%,#17377a 0%,#0a1c44 55%,#050d22 100%)}
#grid{position:absolute;inset:0;background-image:linear-gradient(rgba(120,170,255,.16) 2px,transparent 2px),
  linear-gradient(90deg,rgba(120,170,255,.16) 2px,transparent 2px);background-size:72px 72px}
.scene{position:absolute;inset:0;display:none}
.abs{position:absolute}
/* personagem */
#char{position:absolute;left:300px;top:640px;width:120px;height:330px}
#char .head{position:absolute;left:30px;top:0;width:60px;height:60px;border-radius:50%;background:#f1c27d}
#char .hair{position:absolute;left:28px;top:-4px;width:64px;height:30px;border-radius:32px 32px 0 0;background:#3a2412}
#char .shirt{position:absolute;left:12px;top:64px;width:96px;height:120px;border-radius:10px;background:#f2f2f2;
  color:#0a1c44;font:900 34px Arial Black,Arial,sans-serif;display:flex;align-items:center;justify-content:center;letter-spacing:2px}
#char .arm{position:absolute;top:70px;width:18px;height:110px;border-radius:9px;background:#f2f2f2}
#char .a1{left:-4px}#char .a2{left:106px}
#char .leg{position:absolute;top:184px;width:30px;height:120px;border-radius:12px;background:#1d2a4a}
#char .l1{left:30px}#char .l2{left:62px}
/* medidor e legenda */
#meter{position:absolute;left:460px;top:90px;width:220px;padding:14px 10px;border:4px solid #ffd400;border-radius:12px;
  background:rgba(5,13,34,.85);text-align:center;color:#fff;display:none}
#meter .v{font:900 52px Arial Black,Arial,sans-serif;color:#ffd400;line-height:1.1}
#meter .l{font:700 22px Arial,sans-serif;letter-spacing:2px}
#cap{position:absolute;left:40px;right:40px;top:960px;text-align:center;color:#fff;
  font:900 46px Arial Black,Arial,sans-serif;text-transform:uppercase;line-height:1.2;text-shadow:0 4px 0 #000,0 0 18px rgba(0,0,0,.6)}
#cap .k{color:#ffd400}
#fade{position:absolute;inset:0;background:#000;opacity:0;pointer-events:none}
/* props */
.arch{position:absolute;width:120px;height:260px;border-radius:60px 60px 0 0;background:#0e2250;border:4px solid #2c4f96;top:260px}
.wall{position:absolute;left:0;top:200px;width:720px;height:360px;background:linear-gradient(#3b2a1e,#2a1d14)}
.floor{position:absolute;left:0;top:560px;width:720px;height:80px;background:#4a3524}
.lamp{position:absolute;left:300px;top:250px;width:70px;height:70px;border-radius:50%;background:#ffe27a;box-shadow:0 0 60px 20px rgba(255,220,120,.6)}
.xray{position:absolute;left:210px;top:260px;width:300px;height:300px;border-radius:50%;background:radial-gradient(#7fd3ff,#1b5fd6 70%);box-shadow:0 0 80px #4fc3ff}
.brain{position:absolute;left:60px;top:70px;width:180px;height:160px;border-radius:50%;border:8px solid #d6f2ff;background:rgba(255,255,255,.12)}
.case{position:absolute;left:180px;top:300px;width:360px;height:280px;border:6px solid #9bd3ff;background:rgba(120,190,255,.12)}
.crack{position:absolute;height:6px;background:#fff;transform-origin:left center}
.c1{left:260px;top:380px;width:180px;transform:rotate(25deg)}
.c2{left:300px;top:420px;width:140px;transform:rotate(-40deg)}
.clock{position:absolute;left:220px;top:250px;width:280px;height:280px;border-radius:50%;background:#0b1a3a;border:14px solid #ffd400;
  display:flex;align-items:center;justify-content:center;font:900 90px Arial Black,Arial,sans-serif;color:#fff}
.zb{position:absolute;left:200px;top:260px;width:320px;height:360px}
.zhead{position:absolute;left:110px;top:0;width:100px;height:110px;border-radius:50%;background:#050810}
.zbody{position:absolute;left:70px;top:110px;width:180px;height:250px;border-radius:40px 40px 10px 10px;background:#050810}
.eye{position:absolute;top:50px;width:20px;height:12px;border-radius:50%;background:#ffd400;box-shadow:0 0 18px #ffd400}
.e1{left:138px}.e2{left:182px}
.sl{position:absolute;left:0;width:720px;height:6px;background:rgba(255,255,255,.7)}
.s1{top:300px}.s2{top:420px;width:500px}.s3{top:700px;width:600px}.s4{top:820px;width:400px}
.hand{position:absolute;left:210px;top:340px;width:300px;height:280px}
.fg{position:absolute;bottom:0;width:36px;height:200px;border-radius:18px;background:#7fe0ff;box-shadow:0 0 30px #4fc3ff}
.fg:nth-child(1){left:20px;transform:rotate(-30deg)}.fg:nth-child(2){left:85px;transform:rotate(-12deg)}
.fg:nth-child(3){left:150px}.fg:nth-child(4){left:215px;transform:rotate(12deg)}.fg:nth-child(5){left:250px;height:150px;transform:rotate(30deg)}
.pistol{position:absolute;left:180px;top:400px;width:300px;height:70px;border-radius:8px;background:#2a2f3a;border:4px solid #55606f}
.ring{position:absolute;left:150px;top:330px;width:380px;height:220px;border-radius:50%;border:10px solid rgba(120,200,255,.8);box-shadow:0 0 40px #4fc3ff}
.tube{position:absolute;top:260px;width:70px;height:320px;border-radius:35px;background:rgba(80,255,140,.55);border:4px solid #7dffb0}
.t1{left:90px}.t2{left:250px;height:280px}.t3{left:410px;height:340px}.t4{left:570px;height:300px}
.stairs{position:absolute;left:0;top:560px;width:720px;height:260px;
  background:repeating-linear-gradient(-20deg,#3a2a1f 0 40px,#5a4330 40px 80px)}
.shadow{position:absolute;left:260px;top:220px;width:200px;height:120px;border-radius:50%;background:rgba(0,0,0,.85);filter:blur(4px)}
.cross{position:absolute;left:260px;top:300px;width:200px;height:200px;border-radius:50%;border:8px solid #ff3b3b;box-shadow:0 0 30px #ff3b3b}
.cross:after{content:"";position:absolute;left:92px;top:0;width:8px;height:200px;background:#ff3b3b}
.burst{position:absolute;left:160px;top:250px;width:400px;height:400px;border-radius:50%;
  background:radial-gradient(#fff 0,#ffb020 25%,#ff6a1a 45%,#2c7cff 70%,transparent 72%)}
.mdoor{position:absolute;left:170px;top:240px;width:380px;height:440px;background:#4b5563;border:10px solid #2d333d}
.redlight{position:absolute;left:330px;top:220px;width:60px;height:60px;border-radius:50%;background:#ff2a2a;box-shadow:0 0 60px #ff2a2a}
.lung{position:absolute;top:300px;width:200px;height:300px;border-radius:50% 50% 40% 40%;background:radial-gradient(#9fd8ff,#2c6fd1);box-shadow:0 0 50px #4fc3ff}
.l1{left:110px}.l2{left:410px}
.sweat{position:absolute;left:310px;top:300px;width:30px;height:40px;border-radius:50% 50% 50% 50%;background:#8fd8ff}
.safe{position:absolute;left:200px;top:300px;width:320px;height:320px;border-radius:14px;background:#5a6270;border:12px solid #2d333d}
.dial{position:absolute;left:90px;top:90px;width:120px;height:120px;border-radius:50%;border:12px solid #ffd400;background:#333}
.gold{position:absolute;left:0;top:220px;width:720px;height:520px;background:radial-gradient(circle at 50% 50%,rgba(255,215,90,.9),rgba(255,215,90,0) 60%)}
.moon{position:absolute;left:520px;top:200px;width:110px;height:110px;border-radius:50%;background:#fff6c8;box-shadow:0 0 50px #fff6c8}
.star{position:absolute;width:6px;height:6px;border-radius:50%;background:#fff}
.st1{left:120px;top:240px}.st2{left:300px;top:330px}.st3{left:90px;top:440px}.st4{left:620px;top:420px}
.window{position:absolute;left:200px;top:260px;width:320px;height:360px;background:#06101f;border:12px solid #3a4658}
.yeye{position:absolute;left:300px;top:380px;width:120px;height:50px;border-radius:50%;background:#ffd400;box-shadow:0 0 60px #ffd400}
"""

def caption_html(text):
    # *palavra* -> span amarelo (escape do resto)
    parts = re.split(r"\*(.+?)\*", text)
    out = []
    for i, p in enumerate(parts):
        out.append(f'<span class="k">{html.escape(p)}</span>' if i % 2 else html.escape(p))
    return "".join(out)

def build():
    scenes_html = []
    for idx, (s, e, cap, prop, mval, mlab) in enumerate(SCENES):
        scenes_html.append(
            f'<div class="scene" data-start="{s}" data-end="{e}" id="s{idx}">{PROPS[prop]}</div>'
        )
    js_scenes = ",".join(f"[{s},{e}]" for s, e, *_ in SCENES)
    caps = [caption_html(c) for _, _, c, *_ in SCENES]
    meters = [(m, l) for *_, m, l in [(s, e, c, p, mv, ml) for s, e, c, p, mv, ml in SCENES]]
    meters = [(mv, ml) for _, _, _, _, mv, ml in SCENES]
    import json
    doc = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Cena</title>
<style>{CSS}</style></head>
<body>
<div id="stage">
  <div id="grid"></div>
  {''.join(scenes_html)}
  <div id="char" data-anim="bob">
    <div class="hair"></div><div class="head"></div>
    <div class="arm a1"></div><div class="arm a2"></div>
    <div class="shirt">CLD</div>
    <div class="leg l1"></div><div class="leg l2"></div>
  </div>
  <div id="meter"><div class="v" id="mv"></div><div class="l" id="ml"></div></div>
  <div id="cap"></div>
  <div id="fade"></div>
</div>
<script>
const SCENES = [{js_scenes}];
const CAPS = {json.dumps(caps, ensure_ascii=False)};
const METERS = {json.dumps(meters, ensure_ascii=False)};
const TIMER_START = 240; // 4:00, em segundos, contagem regressiva na cena 5
window.render = function(t) {{
  let idx = SCENES.findIndex(([s,e]) => t >= s && t < e);
  if (idx < 0) idx = SCENES.length - 1;
  const [s, e] = SCENES[idx];
  const lt = t - s, dur = e - s;
  document.querySelectorAll('.scene').forEach((el, i) => el.style.display = i === idx ? 'block' : 'none');
  // fade entre cenas
  const fadeIn = Math.min(1, lt / 0.25), fadeOut = Math.min(1, (dur - lt) / 0.25);
  document.getElementById('fade').style.opacity = 1 - Math.min(fadeIn, fadeOut);
  // legenda
  document.getElementById('cap').innerHTML = CAPS[idx];
  // medidor
  const [mv, ml] = METERS[idx];
  const meter = document.getElementById('meter');
  if (mv) {{
    meter.style.display = 'block';
    document.getElementById('mv').textContent = mv;
    document.getElementById('ml').textContent = ml;
  }} else meter.style.display = 'none';
  // animações genéricas dentro da cena
  const scene = document.querySelectorAll('.scene')[idx];
  scene.querySelectorAll('[data-anim]').forEach(el => {{
    const a = el.dataset.anim;
    if (a === 'flick') el.style.opacity = 0.55 + 0.45 * (Math.sin(t * 40) > -0.3 ? 1 : 0.2);
    if (a === 'pulse') el.style.transform = `scale(${{1 + 0.05 * Math.sin(t * 6)}})`;
    if (a === 'shrink') el.style.transform = `scale(${{1 - 0.08 * lt / dur}})`;
    if (a === 'creep') el.style.transform = `translateY(${{Math.sin(t * 3) * 6}}px) scale(${{1 + lt * 0.01}})`;
    if (a === 'drift') el.style.transform = `translateX(${{Math.sin(t * 1.5) * 60}}px)`;
    if (a === 'boom') el.style.transform = `scale(${{Math.min(1, lt * 3)}})`;
    if (a === 'rattle') el.style.transform = `translateX(${{Math.sin(t * 60) * 3}}px)`;
    if (a === 'spin') el.style.transform = `rotate(${{t * 120}}deg)`;
    if (a === 'drip') el.style.transform = `translateY(${{(lt * 80) % 120}}px)`;
  }});
  if (idx === 4) {{
    const left = Math.round(TIMER_START - 60 * lt / dur);
    const m = Math.floor(left / 60), sec = String(left % 60).padStart(2, '0');
    document.getElementById('timerText').textContent = `${{m}}:${{sec}}`;
  }}
  // personagem: balanço suave
  const ch = document.getElementById('char');
  ch.style.transform = `translateY(${{Math.sin(t * 5) * 8}}px)`;
}};
window.render(0);
</script></body></html>"""
    return doc

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1])
    out.write_text(build(), encoding="utf-8")
    print("ok", out)

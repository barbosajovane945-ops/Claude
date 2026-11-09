import json, math
R, P, A0 = 4.0, 90.0, -40.0
import os
LIN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)) if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linhas.json')) else '/home/user/Claude/estudio/espaco/projetos/sol_apagado', 'linhas.json')))
FALA = {l['id']: l for l in LIN['linhas']}
def tp(ref):   # "C1", "C1.2" ou "C1:acaba" -> segundos (os mesmos tempos da voz)
    if ':' in ref:
        f, w = ref.split(':'); return next(p['t0'] for pd in FALA[f]['pedacos'] for p in pd['palavras'] if p['t'].lower().startswith(w))
    if '.' in ref:
        f, k = ref.split('.'); return FALA[f]['pedacos'][int(k) - 1]['t0']
    return FALA[ref]['t0']
TC, TD = tp("C1.2"), tp("D1")      # sai da curva; a Terra se abre
def pos(t):
    a = math.radians(A0 + 360*t/P); return [R*math.cos(a), 0, R*math.sin(a)], a
p0, a = pos(TC)
v = [-math.sin(a), 0, math.cos(a)]
spd = 2*math.pi*R/P
pf = [p0[i] + v[i]*spd*(TD-TC) for i in range(3)]
r3 = lambda p: [round(x, 3) for x in p]
sa = [p0[i] + v[i]*0.7 for i in range(3)]; sb = [p0[i] + v[i]*2.6 for i in range(3)]
sm = [(sa[i]+sb[i])/2 for i in range(3)]
RT = 0.5
cam = lambda **k: {"roll": 90, "so_altura": True, "mm": 35, **k}
objetos = {
 "sol": {"corpo": "estrelaG", "pos": [0,0,0], "raio": 0.9, "halo": 3,
         "brilho": [{"de": "A1.2:apagasse", "ate": "A1.2:apagasse+0.5", "para": 0.05}], "fundo": True},
 "terra": {"corpo": "terra", "raio": RT, "girar": 0.25,
           "orbita": {"em": "sol", "raio": R, "periodo": P, "fase": A0/360},
           "movimentos": [{"de": "C1.2", "ate": "D1", "para": r3(pf), "curva": "linear"}],
           "sai": "direto", "mostrar": [["inicio", "D1+0.15"]]},
 "orbita": {"tipo": "orbita", "em": "sol", "raio": R, "tracejada": True, "destaque": True, "fundo": True,
            "mostrar": [["inicio", "D1"]]},
 "pulso": {"tipo": "brilho", "pos": [0,0,0], "raio": 0.35, "cor": "#FFD166", "opacidade": 0.9,
           "movimentos": [{"de": "A1.2:apagasse", "ate": "C1:acaba", "para": "terra", "curva": "linear"}],
           "entra": "direto", "sai": "direto", "mostrar": [["A1.2:apagasse", "C1:acaba"]], "fundo": True},
 "luzSol": {"tipo": "luz", "de": "pulso", "para": "terra", "raio_ini": 0.55, "raio_fim": 0.6,
            "cor": "#FFD98A", "opacidade": 0.55, "entra": "direto", "sai": "direto",
            "mostrar": [["inicio", "C1:acaba"]], "fundo": True},
 "seta": {"tipo": "seta", "de": r3(sa), "para": r3(sb), "pos": r3(sm), "raio": 1.0, "largura": 0.06,
          "cor": "#FFD166", "desenha": ["C1.2", "C1.2.fim"], "mostrar": [["C1.2", "C2.fim"]]},
 "breu": {"tipo": "brilho", "pos": [0, -2200, -500], "raio": 0.01, "opacidade": 0},
 "praia": {"tipo": "praia", "pos": [0, -2000, 0], "luar": "luaCeu", "ambiente": 0.16, "lampada": False,
           "regua": {"x": 400, "z": -300, "altura": 1}, "mostrar": [["L1-0.05", "D1"]], "entra": "direto", "sai": "direto"},
 "luaCeu": {"corpo": "lua", "pos": [9, -1984, -70], "raio": 2.6, "girar": 0, "entra": "direto", "sai": "direto", "mostrar": [["L1-0.05", "L1:apaga.fim"]]},
 "corte": {"tipo": "corte", "modo": "terra", "pos": r3(pf), "raio": RT*1.05, "entra": "direto",
           "abre": ["D1+0.1", "D1.1.fim"],
           "destaque": [{"nome": "nucleo", "de": "D1.2:calor", "ate": "D1.3", "camadas": [0, 1]},
                        {"nome": "oceano", "de": "D1.3:segura", "ate": "D2.fim", "camadas": [4, 4]}],
           "mostrar": [["D1", None]]},
}
G = ["sol", "terra"]

import math as m
def az(t): return round(40 - 4*t, 1)
def sph(azd, eld):
    a, e = m.radians(azd), m.radians(eld)
    return [m.sin(a)*m.cos(e), m.sin(e), m.cos(a)*m.cos(e)]
def contraluz(azd, eld):   # luz vindo de trás da Terra (só uma borda fina acesa)
    c = sph(azd + 35, eld - 10); return [round(-x, 3) for x in c]
T = {k: tp(k) for k in ["B1", "B3", "D1"]}
planos = [
 {"de": "inicio", "novo": "o Sol embaixo, a Terra em cima, a luz entre os dois; o Sol apaga", "longo": True,
  "compo": {"x": 0.5, "y": 0.34},
  "camera": {"de": cam(enquadrar=G, ocupa=0.62, az=az(0), el=30), "para": cam(enquadrar=G, ocupa=0.62, az=az(T["B1"]), el=30), "curva": "meio"}},
 {"de": "B1", "continuo": True, "longo": True, "novo": "o fim da luz sobe devagar até a Terra", "compo": {"x": 0.5, "y": 0.34},
  "camera": {"de": cam(enquadrar=G, ocupa=0.62, az=az(T["B1"]), el=30), "para": cam(enquadrar=G, ocupa=0.66, az=az(T["B3"]), el=24), "curva": "meio"}},
 {"de": "B3", "continuo": True, "longo": True, "faixa": False, "novo": "a câmera abre: a órbita inteira em volta do Sol apagado", "compo": {"x": 0.5, "y": 0.42},
  "camera": {"de": cam(enquadrar=G, ocupa=0.66, az=az(T["B3"]), el=24), "para": cam(enquadrar=["orbita"], ocupa=0.5, az=az(T["B3"]) - 3, el=50), "curva": "meio"}},
 {"de": "C1:acaba", "continuo": True, "longo": True, "faixa": False, "luz": contraluz(az(T["B3"]) - 3, 50), "novo": "a Terra escurece e sai pela seta, em linha reta", "compo": {"x": 0.5, "y": 0.42},
  "camera": {"de": cam(enquadrar=["orbita"], ocupa=0.5, az=az(T["B3"]) - 3, el=50), "para": cam(enquadrar=["orbita", "terra"], ocupa=0.5, az=az(T["B3"]) - 8, el=48), "curva": "meio"}},


 {"de": "L1", "novo": "do chão: a Lua no céu deixa o mar prateado, e apaga", "longo": True, "luz": "camera", "borrao": False,
  "camera": {"de": {"em": "praia", "pos": [0, 2.6, 15], "alvo": [6, 9, -60], "mm": 24}, "para": {"em": "praia", "pos": [0.3, 2.5, 14], "alvo": [4, 7, -60], "mm": 24}, "curva": "meio"}},
 {"de": "M1", "continuo": True, "longo": True, "luz": "camera", "borrao": False, "novo": "a câmera vira para o horizonte: a manhã não chega",
  "camera": {"de": {"em": "praia", "pos": [0.3, 2.5, 14], "alvo": [4, 7, -60], "mm": 24}, "para": {"em": "praia", "pos": [0.4, 2.5, 13.5], "alvo": [-30, 3.0, -50], "mm": 24}, "curva": "meio"}},
 {"de": "C2", "continuo": True, "longo": True, "luz": "camera", "borrao": False, "novo": "de volta ao mar escuro: céu preto, só estrelas",
  "camera": {"de": {"em": "praia", "pos": [0.4, 2.5, 13.5], "alvo": [-30, 3.0, -50], "mm": 24}, "para": {"em": "praia", "pos": [0.3, 2.4, 13], "alvo": [0, 2.6, -40], "mm": 24}, "curva": "meio"}},
 {"de": "C3", "continuo": True, "longo": True, "luz": "camera", "borrao": False, "novo": "o mar para de mexer e a geada cobre a areia",
  "camera": {"de": {"em": "praia", "pos": [0.3, 2.4, 13], "alvo": [0, 2.6, -40], "mm": 24}, "para": {"em": "praia", "pos": [0.8, 1.9, 10], "alvo": [0, 0.6, -40], "mm": 24}, "curva": "meio"}},
 {"de": "C4", "continuo": True, "longo": True, "luz": "camera", "borrao": False, "novo": "o mar inteiro virou gelo; a câmera levanta para o céu vazio",
  "camera": {"de": {"em": "praia", "pos": [0.8, 1.9, 10], "alvo": [0, 0.6, -40], "mm": 24}, "para": {"em": "praia", "pos": [1.0, 2.6, 8.5], "alvo": [0, 7, -40], "mm": 24}, "curva": "meio"}},
 {"de": "D1", "continuo": True, "longo": True, "heroi": "corte", "luz": "camera", "novo": "a Terra se abre: o núcleo quente e o mar por baixo do gelo", "compo": {"x": 0.46, "y": 0.33},
  "camera": {"de": cam(enquadrar=["corte"], ocupa=0.42, az=az(T["B3"]) + 24, el=24), "para": cam(enquadrar=["corte"], ocupa=0.44, az=az(T["B3"]) + 36, el=22), "curva": "meio"}},
 {"de": "Q1", "continuo": True, "longo": True, "heroi": "corte", "luz": "camera", "novo": "a câmera continua andando em volta", "compo": {"x": 0.46, "y": 0.33},
  "camera": {"de": cam(enquadrar=["corte"], ocupa=0.44, az=az(T["B3"]) + 36, el=22), "para": cam(enquadrar=["corte"], ocupa=0.4, az=az(T["B3"]) + 54, el=26), "curva": "meio"}},
]
eventos = [
 {"tipo": "clarao", "em": "A1.2:apagasse", "alvo": "sol", "forca": 0.6, "dur": 0.5},
 {"tipo": "som", "em": "A1.2:apagasse", "nota": "grave"},
 {"tipo": "som", "em": "A2.2", "nota": "plim"},
 {"tipo": "som", "em": "C1:acaba", "nota": "grave"},
 {"tipo": "som", "em": "L1:apaga", "nota": "tique"},
 {"tipo": "som", "em": "C2.2:frio", "nota": "plim"},
 {"tipo": "som", "em": "C4.2:setenta", "nota": "grave"},
 {"tipo": "som", "em": "D1.2:calor", "nota": "tique"},
 {"tipo": "som", "em": "Q1", "nota": "plim"},
]
plano = {"titulo": "E se o Sol apagasse?", "estilo": "vivo", "cauda": 1.7, "luz": {"de": "sol"},
         "extra": "extra.js", "objetos": objetos, "planos": planos, "eventos": eventos}
json.dump(plano, open('plano.json', 'w'), ensure_ascii=False, indent=1)
print("p0", r3(p0), "pf", r3(pf))

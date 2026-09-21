"""
╔══════════════════════════════════════════════════════════════════╗
║     CORRECTEUR PYTHON INTERACTIF — BARÈME GENEVOIS /6           ║
║     Concepts : for · while · fonctions · turtle · listes        ║
╠══════════════════════════════════════════════════════════════════╣
║  RÉPARTITION DES POINTS (par exercice, 12 pts) :                ║
║   EXÉCUTION  ·····  2 pts  — tourne sans erreur                 ║
║   AFFICHAGE  ····· 5 pts  — résultats corrects (+ de poids)    ║
║   FORMULE    ·····  3 pts  — algorithme / logique juste         ║
║   STRUCTURE  ·····  2 pts  — boucle, def, style                 ║
║                                                                   ║
║  QUESTIONS COMPOSÉES → feedback par sous-partie (a · b · c)    ║
║  FORMULE BARÈME : Note = (pts/max) × 5 + 1  arrondi 0.5        ║
╠══════════════════════════════════════════════════════════════════╣
║  UTILISATION :                                                    ║
║   Mode interactif : python correcteur_interactif.py             ║
║   Mode script     : remplis la section CONFIG en bas            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import math, io, sys, re, textwrap
from contextlib import redirect_stdout


# ══════════════════════════════════════════════════════════════════
#  SPY TURTLE
# ══════════════════════════════════════════════════════════════════

class TurtleSpy:
    def __init__(self):
        self._calls, self._segments = [], []
        self._x = self._y = self._angle = 0.0
        self._pen_down = True

    def _mv(self, d):
        if self._pen_down:
            x2 = self._x + d * math.cos(math.radians(self._angle))
            y2 = self._y + d * math.sin(math.radians(self._angle))
            self._segments.append((round(self._x,2), round(self._y,2),
                                    round(x2,2), round(y2,2), round(d,2)))
            self._x, self._y = x2, y2
        else:
            self._x += d * math.cos(math.radians(self._angle))
            self._y += d * math.sin(math.radians(self._angle))

    def forward(self, d):   self._calls.append(("forward",d));   self._mv(d)
    def fd(self, d):        self.forward(d)
    def backward(self, d):  self._calls.append(("backward",d));  self._mv(-d)
    def bk(self, d):        self.backward(d)
    def right(self, a):     self._calls.append(("right",a));     self._angle -= a
    def rt(self, a):        self.right(a)
    def left(self, a):      self._calls.append(("left",a));      self._angle += a
    def lt(self, a):        self.left(a)
    def penup(self):        self._calls.append(("penup",));      self._pen_down = False
    def pu(self):           self.penup()
    def up(self):           self.penup()
    def pendown(self):      self._calls.append(("pendown",));    self._pen_down = True
    def pd(self):           self.pendown()
    def down(self):         self.pendown()
    def setheading(self,a): self._calls.append(("setheading",a)); self._angle = a
    def seth(self,a):       self.setheading(a)
    def goto(self, x, y=None):
        if y is None and hasattr(x,'__iter__'): x,y=x
        self._calls.append(("goto",x,y))
        if self._pen_down:
            self._segments.append((round(self._x,2),round(self._y,2),
                                    round(x,2),round(y,2),None))
        self._x, self._y = x, y
    def setpos(self,x,y=None):      self.goto(x,y)
    def setposition(self,x,y=None): self.goto(x,y)
    def home(self):
        self._calls.append(("home",)); self._x=self._y=0.; self._angle=0.
    def color(self,*a):     self._calls.append(("color",a))
    def pencolor(self,*a):  self._calls.append(("pencolor",a))
    def fillcolor(self,*a): self._calls.append(("fillcolor",a))
    def begin_fill(self):   self._calls.append(("begin_fill",))
    def end_fill(self):     self._calls.append(("end_fill",))
    def speed(self,s):      self._calls.append(("speed",s))
    def hideturtle(self):   self._calls.append(("hideturtle",))
    def ht(self):           self.hideturtle()
    def showturtle(self):   self._calls.append(("showturtle",))
    def st(self):           self.showturtle()
    def write(self,*a,**k): self._calls.append(("write",a))
    def done(self): pass
    def exitonclick(self): pass
    def mainloop(self): pass
    def setup(self,*a,**k): pass
    def title(self,*a): pass
    def bgcolor(self,*a): pass
    def Screen(self): return self
    def tracer(self,*a): pass
    def update(self): pass
    def reset(self): self.__init__()
    def clear(self): pass
    def position(self): return (self._x, self._y)
    def pos(self): return self.position()
    def xcor(self): return self._x
    def ycor(self): return self._y
    def heading(self): return self._angle % 360

    # ── stats ─────────────────────────────────────────────────
    def nb(self, name):     return sum(1 for c in self._calls if c[0]==name)
    def nb_forward(self):   return self.nb("forward")
    def segment_lengths(self): return [s[4] for s in self._segments if s[4] is not None]
    def unique_lengths(self):  return set(round(l,1) for l in self.segment_lengths() if l and l>0)
    def turns_of(self, deg, tol=1):
        return sum(1 for c in self._calls if c[0] in ("right","left") and abs(c[1]-deg)<tol)
    def is_closed(self, tol=4): return math.hypot(self._x, self._y) < tol
    def nb_penup(self):     return self.nb("penup")
    def has_color(self):
        return any(c[0] in ("color","pencolor","fillcolor") for c in self._calls)
    def total_segments(self): return len(self._segments)


# ══════════════════════════════════════════════════════════════════
#  MOTEUR D'EXÉCUTION
# ══════════════════════════════════════════════════════════════════

def executer(code, input_vals=None, extra=None):
    """
    Exécute le code élève.
    input_vals : list[str] — réponses successives à input()
    Retourne (succes, sortie, spy, erreur)
    """
    spy = TurtleSpy()
    input_vals = list(input_vals or [])
    input_idx  = [0]

    def fake_input(*a):
        if input_idx[0] < len(input_vals):
            v = input_vals[input_idx[0]]; input_idx[0] += 1; return v
        return ""

    ns = {
        "__builtins__": __builtins__,
        "turtle": spy, "t": spy,
        "forward": spy.forward, "fd": spy.fd,
        "backward": spy.backward, "bk": spy.bk,
        "right": spy.right, "rt": spy.rt,
        "left": spy.left, "lt": spy.lt,
        "goto": spy.goto, "setpos": spy.setpos,
        "setheading": spy.setheading, "seth": spy.seth,
        "penup": spy.penup, "pu": spy.pu, "up": spy.up,
        "pendown": spy.pendown, "pd": spy.pd, "down": spy.down,
        "speed": spy.speed, "color": spy.color,
        "pencolor": spy.pencolor, "fillcolor": spy.fillcolor,
        "begin_fill": spy.begin_fill, "end_fill": spy.end_fill,
        "hideturtle": spy.hideturtle, "ht": spy.ht,
        "showturtle": spy.showturtle, "st": spy.st,
        "home": spy.home, "done": spy.done,
        "exitonclick": spy.exitonclick, "mainloop": spy.mainloop,
        "Screen": spy.Screen, "write": spy.write,
        "range": range, "print": print, "len": len,
        "input": fake_input,
        "int": int, "float": float, "str": str, "bool": bool,
        "list": list, "tuple": tuple, "dict": dict, "set": set,
        "abs": abs, "round": round, "sum": sum, "min": min, "max": max,
        "sorted": sorted, "reversed": reversed,
        "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
        "math": math, "isinstance": isinstance, "type": type,
    }
    if extra: ns.update(extra)
    sys.modules["turtle"] = spy  # type: ignore
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(code, "<eleve>", "exec"), ns)
        return True, buf.getvalue(), spy, ""
    except Exception as e:
        return False, buf.getvalue(), spy, f"{type(e).__name__}: {e}"
    finally:
        sys.modules.pop("turtle", None)


# ══════════════════════════════════════════════════════════════════
#  BARÈME GENEVOIS
# ══════════════════════════════════════════════════════════════════

def note_g(pts, pts_max):
    if pts_max == 0: return 1.0
    return round(max(1., min(6., (pts/pts_max)*5+1)) * 2) / 2

def mention(n):
    for s, m in [(5.5,"Excellent ★★★"),(5.0,"Très bien ★★"),(4.5,"Bien ★"),
                 (4.0,"Suffisant ✓"),(3.0,"Insuffisant ✗"),(0,"Très insuffisant ✗✗")]:
        if n >= s: return m
    return "Très insuffisant ✗✗"

def barre(pts, pts_max, w=20):
    if pts_max == 0: return "░"*w
    f = pts/pts_max
    return "█"*round(f*w) + "░"*(w-round(f*w))


# ══════════════════════════════════════════════════════════════════
#  CLASSES CRITÈRE & SOUS-PARTIE
# ══════════════════════════════════════════════════════════════════

class Critere:
    CATS = {"exe":"EXÉCUTION","aff":"AFFICHAGE","for":"FORMULE  ","str":"STRUCTURE"}

    def __init__(self, label, pts_max, cat="str"):
        self.label, self.pts_max, self.cat = label, pts_max, cat
        self.pts, self.detail = 0, ""

    def ok(self, detail=""):
        self.pts = self.pts_max; self.detail = detail; return self

    def ko(self, detail=""):
        self.pts = 0; self.detail = detail; return self

    def partiel(self, p, detail=""):
        self.pts = min(p, self.pts_max); self.detail = detail; return self

    def __str__(self):
        icone = "✓" if self.pts == self.pts_max else ("~" if self.pts > 0 else "✗")
        cat   = self.CATS.get(self.cat, self.cat[:3].upper())
        d     = f"  → {self.detail}" if self.detail else ""
        return f"  {icone} [{cat}][{self.pts}/{self.pts_max}] {self.label}{d}"


class SousPartie:
    """
    Sous-partie d'une question composée (a, b, c...).
    Peut contenir plusieurs critères.
    """
    def __init__(self, lettre, titre, pts_max):
        self.lettre  = lettre
        self.titre   = titre
        self.pts_max = pts_max
        self.criteres: list[Critere] = []
        self.feedback = ""

    def pts(self):
        return sum(c.pts for c in self.criteres)

    def rapport(self, indent="    "):
        note_sp = note_g(self.pts(), self.pts_max)
        lignes  = []
        lignes.append(f"{indent}({self.lettre}) {self.titre}  "
                      f"[{self.pts()}/{self.pts_max}] → {note_sp}/6")
        for c in self.criteres:
            lignes.append(indent + str(c))
        if self.feedback:
            lignes.append(f"{indent}  💬 {self.feedback}")
        return "\n".join(lignes)


# ══════════════════════════════════════════════════════════════════
#  UTILITAIRES
# ══════════════════════════════════════════════════════════════════

def norm(t):     return re.sub(r'\s+',' ', str(t).strip().lower())
def contient(s, *mots): return all(norm(m) in norm(s) for m in mots)
def egale(s, a):         return norm(s) == norm(a)
def utilise(code, *mots): return all(m in code for m in mots)
def nb_for(code):   return len(re.findall(r'\bfor\b', code))
def nb_while(code): return len(re.findall(r'\bwhile\b', code))
def nb_def(code):   return len(re.findall(r'\bdef\b', code))
def nums(s):         return [float(x) for x in re.findall(r'-?\d+\.?\d*', s)]
def lignes(s):       return [l.strip() for l in s.strip().splitlines() if l.strip()]


# ══════════════════════════════════════════════════════════════════
#  BIBLIOTHÈQUE DE CONCEPTS
# ══════════════════════════════════════════════════════════════════
# Chaque concept expose une fonction eval_*(code, succes, sortie, spy, erreur)
# → retourne list[Critere | SousPartie]
# Répartition : EXE=2  AFF=5  FOR=3  STR=2  (total 12)

# ──────────────────────────────────────────────────────────────────
# CONCEPT : BOUCLE FOR — Table de multiplication
# ──────────────────────────────────────────────────────────────────
ENONCE_FOR = """
Écris un programme qui :
  a) Demande un entier N à l'utilisateur
  b) Affiche la table de multiplication de N (de N×1 à N×10)
     Format : "N x i = résultat"
  c) Affiche à la fin : "Somme = X" (somme des 10 résultats)
"""

def eval_for(code, succes, sortie, spy, erreur, input_vals=None):
    N = int((input_vals or ["7"])[0])
    attendus = [N*i for i in range(1,11)]
    somme    = sum(attendus)
    ls       = lignes(sortie)
    c        = []

    # ── (a) EXÉCUTION ─────────────────────────────
    sp_a = SousPartie("a", "Exécution sans erreur", 2)
    cr = Critere("Code tourne sans erreur", 2, "exe")
    cr.ok() if succes else cr.ko(erreur)
    sp_a.criteres.append(cr)
    if not succes:
        sp_a.feedback = "Corrige d'abord l'erreur pour débloquer les autres points."
    c.append(sp_a)

    # ── (b) AFFICHAGE table ────────────────────────
    sp_b = SousPartie("b", "Table affichée correctement", 7)
    cr1 = Critere("10 lignes de multiplication affichées", 2, "aff")
    lignes_table = [l for l in ls if "x" in l or "×" in l or "*" in l]
    cr1.ok(f"{len(lignes_table)}/10") if len(lignes_table) >= 10 else \
        cr1.partiel(len(lignes_table)//5, f"{len(lignes_table)}/10 lignes")
    sp_b.criteres.append(cr1)

    cr2 = Critere("Résultats numériques tous corrects (N×1 à N×10)", 3, "aff")
    trouvés = nums(sortie)
    corrects = sum(1 for a in attendus if a in [round(x) for x in trouvés])
    if corrects == 10: cr2.ok("parfait")
    elif corrects >= 5: cr2.partiel(1, f"{corrects}/10 corrects")
    else: cr2.ko(f"{corrects}/10 corrects")
    sp_b.criteres.append(cr2)

    cr3 = Critere("Format lisible (N x i = résultat)", 2, "aff")
    ok_fmt = any(re.search(r'\d+\s*[x×\*]\s*\d+\s*=\s*\d+', l) for l in ls)
    cr3.ok() if ok_fmt else cr3.ko("format attendu : N x i = résultat")
    sp_b.criteres.append(cr3)

    if corrects < 10:
        sp_b.feedback = (f"Vérifie la formule : le résultat de {N}×{10} doit être {N*10}. "
                         f"Utilise n * i dans la boucle.")
    c.append(sp_b)

    # ── (c) AFFICHAGE somme ────────────────────────
    sp_c = SousPartie("c", "Somme affichée en fin", 3)
    cr4 = Critere(f"Affiche 'Somme = {somme}'", 2, "aff")
    if somme in [round(x) for x in nums(sortie)] and \
       any("somme" in l.lower() or "sum" in l.lower() or "total" in l.lower() for l in ls):
        cr4.ok(f"Somme={somme} trouvée")
    else:
        cr4.ko(f"Somme {somme} absente ou mal libellée")
    sp_c.criteres.append(cr4)

    cr5 = Critere("Accumulateur utilisé pour la somme", 1, "for")
    ok_acc = bool(re.search(r'\b(total|somme|s|acc)\s*[+]?=', code)) or "+=" in code
    cr5.ok() if ok_acc else cr5.ko("variable accumulatrice manquante")
    sp_c.criteres.append(cr5)

    if not (somme in [round(x) for x in nums(sortie)]):
        sp_c.feedback = (f"Initialise un accumulateur à 0 avant la boucle, "
                         f"puis ajoute chaque résultat.")
    c.append(sp_c)

    # ── FORMULE + STRUCTURE (hors sous-parties) ───
    sp_d = SousPartie("d", "Formule & Structure", 3)
    cr6 = Critere("Boucle for avec range(1, 11)", 1, "str")
    cr6.ok() if (nb_for(code)>=1 and ("range(1" in code or "range(1," in code)) \
        else cr6.ko("range(1, 11) attendu")
    sp_d.criteres.append(cr6)

    cr7 = Critere("Variable N issue de input()", 1, "str")
    cr7.ok() if "input" in code else cr7.ko("input() absent")
    sp_d.criteres.append(cr7)

    cr8 = Critere("Multiplication N*i dans la boucle", 1, "for")
    cr8.ok() if "*" in code else cr8.ko("opérateur * absent")
    sp_d.criteres.append(cr8)

    c.append(sp_d)
    return c


# ──────────────────────────────────────────────────────────────────
# CONCEPT : BOUCLE WHILE — Compteur / saisie validée
# ──────────────────────────────────────────────────────────────────
ENONCE_WHILE = """
Écris un programme qui :
  a) Demande un nombre positif à l'utilisateur (répète jusqu'à obtenir un nb > 0)
  b) Affiche le compte à rebours de ce nombre jusqu'à 0
  c) Affiche "Décollage !" à la fin
"""

def eval_while(code, succes, sortie, spy, erreur, input_vals=None):
    vals = input_vals or ["-3", "0", "5"]
    ls   = lignes(sortie)
    c    = []

    sp_a = SousPartie("a", "Exécution sans erreur", 2)
    cr = Critere("Code tourne sans erreur", 2, "exe")
    cr.ok() if succes else cr.ko(erreur)
    if not succes:
        sp_a.feedback = "Vérifie la syntaxe de ta boucle while et les indentations."
    sp_a.criteres.append(cr); c.append(sp_a)

    sp_b = SousPartie("b", "Validation de la saisie (while ≤ 0)", 4)
    cr1 = Critere("Boucle while utilisée pour valider la saisie", 2, "aff")
    cr1.ok() if nb_while(code) >= 1 else cr1.ko("while absent")
    sp_b.criteres.append(cr1)

    cr2 = Critere("Saisie négative rejetée (redemande)", 2, "aff")
    ok2 = nb_while(code) >= 1 and (">" in code or "<=" in code)
    cr2.ok() if ok2 else cr2.ko("condition de rejet absente")
    if not ok2:
        sp_b.feedback = ("Utilise : while n <= 0 : n = int(input(...))  "
                         "pour forcer un nombre positif.")
    sp_b.criteres.append(cr2); c.append(sp_b)

    sp_c = SousPartie("c", "Compte à rebours affiché", 4)
    decompte = [l for l in ls if re.match(r'^\d+$', l)]
    cr3 = Critere("Compte à rebours complet de N à 0", 3, "aff")
    # cherche si les nombres 5,4,3,2,1,0 apparaissent en ordre décroissant
    seq = [int(x) for x in decompte if x.isdigit()]
    is_desc = all(seq[i] > seq[i+1] for i in range(len(seq)-1)) if len(seq)>1 else False
    if seq and is_desc and 0 in seq:
        cr3.ok(f"Séquence : {seq[:6]}...")
    elif seq:
        cr3.partiel(1, f"Séquence partielle ou désordonnée : {seq}")
    else:
        cr3.ko("Aucun nombre affiché")
    sp_c.criteres.append(cr3)

    cr4 = Critere("'Décollage !' affiché à la fin", 1, "aff")
    ok4 = any(contient(l, "décollage") or contient(l, "decollage") for l in ls)
    cr4.ok() if ok4 else cr4.ko("texte 'Décollage !' absent")
    sp_c.criteres.append(cr4)

    if not (seq and is_desc):
        sp_c.feedback = ("Utilise une seconde boucle while (ou for) : "
                         "while n >= 0 : print(n); n -= 1")
    c.append(sp_c)

    sp_d = SousPartie("d", "Structure du code", 2)
    cr5 = Critere("Au moins 1 boucle while (+ 1 autre while ou for)", 1, "str")
    cr5.ok() if nb_while(code)>=1 else cr5.ko()
    sp_d.criteres.append(cr5)

    cr6 = Critere("input() utilisé", 1, "str")
    cr6.ok() if "input" in code else cr6.ko()
    sp_d.criteres.append(cr6); c.append(sp_d)
    return c


# ──────────────────────────────────────────────────────────────────
# CONCEPT : FONCTIONS
# ──────────────────────────────────────────────────────────────────
ENONCE_FONCTIONS = """
Écris un programme avec les fonctions suivantes :
  a) est_pair(n)   → retourne True si n est pair, False sinon
     Affiche le résultat pour n=4 et n=7
  b) factorielle(n) → calcule n! avec une boucle (pas de récursion)
     Affiche 5! et 0!
  c) maximum(liste)  → retourne le plus grand élément sans utiliser max()
     Teste avec [3, 7, 2, 9, 1]
"""

def eval_fonctions(code, succes, sortie, spy, erreur, input_vals=None):
    ls = lignes(sortie)
    c  = []

    sp_a = SousPartie("a", "Exécution sans erreur", 2)
    cr = Critere("Code tourne sans erreur", 2, "exe")
    cr.ok() if succes else cr.ko(erreur)
    if not succes:
        sp_a.feedback = "Vérifie que chaque def est bien indenté et que les return sont présents."
    sp_a.criteres.append(cr); c.append(sp_a)

    # ── (b) est_pair ──────────────────────────────
    sp_b = SousPartie("b", "Fonction est_pair(n)", 4)
    cr1 = Critere("Fonction est_pair() définie avec def", 1, "str")
    cr1.ok() if re.search(r'\bdef\s+est_pair\b', code) else cr1.ko("def est_pair() absent")
    sp_b.criteres.append(cr1)

    cr2 = Critere("Modulo % 2 utilisé (ou & 1)", 1, "for")
    cr2.ok() if ("% 2" in code or "%2" in code or "& 1" in code) else cr2.ko()
    sp_b.criteres.append(cr2)

    cr3 = Critere("Résultat est_pair(4)=True et est_pair(7)=False affiché", 2, "aff")
    has_true  = any(contient(l,"true")  for l in ls)
    has_false = any(contient(l,"false") for l in ls)
    if has_true and has_false: cr3.ok()
    elif has_true or has_false: cr3.partiel(1, "un seul cas affiché")
    else: cr3.ko("True/False absents")
    if not (has_true and has_false):
        sp_b.feedback = ("Appelle est_pair(4) → affiche True, est_pair(7) → affiche False. "
                         "Vérifie que tu print() le résultat.")
    sp_b.criteres.append(cr3); c.append(sp_b)

    # ── (c) factorielle ──────────────────────────
    sp_c = SousPartie("c", "Fonction factorielle(n)", 5)
    cr4 = Critere("Fonction factorielle() définie avec def", 1, "str")
    cr4.ok() if re.search(r'\bdef\s+factorielle\b', code) else cr4.ko()
    sp_c.criteres.append(cr4)

    cr5 = Critere("Boucle for ou while utilisée (pas de récursion)", 1, "for")
    has_loop = re.search(r'\bdef\s+factorielle', code) and (nb_for(code)>=1 or nb_while(code)>=1)
    cr5.ok() if has_loop else cr5.ko("boucle absente dans la fonction")
    sp_c.criteres.append(cr5)

    ns_out = nums(sortie)
    cr6 = Critere("5! = 120 affiché", 2, "aff")
    cr6.ok("120 trouvé") if 120.0 in ns_out else cr6.ko("120 absent dans la sortie")
    sp_c.criteres.append(cr6)

    cr7 = Critere("0! = 1 affiché", 1, "aff")
    cr7.ok() if (1.0 in ns_out or "1" in sortie) else cr7.ko("1 (=0!) absent")
    sp_c.criteres.append(cr7)

    if 120.0 not in ns_out:
        sp_c.feedback = ("factorielle(5) doit retourner 120. "
                         "Initialise resultat=1 puis multiplie dans la boucle. "
                         "N'oublie pas de gérer le cas n=0 (retourne 1).")
    c.append(sp_c)

    # ── (d) maximum ──────────────────────────────
    sp_d = SousPartie("d", "Fonction maximum(liste)", 4)
    cr8 = Critere("Fonction maximum() définie avec def", 1, "str")
    cr8.ok() if re.search(r'\bdef\s+maximum\b', code) else cr8.ko()
    sp_d.criteres.append(cr8)

    cr9 = Critere("max() interdit — utilise une boucle", 1, "for")
    uses_builtin_max = bool(re.search(r'(?<!\w)max\s*\(', code))
    def_max_pos = code.find("def maximum")
    # autorise max() seulement avant la def (comparaison) — heuristique simple
    cr9.ok() if not uses_builtin_max else cr9.ko("max() interdit, utilise une boucle")
    sp_d.criteres.append(cr9)

    cr10 = Critere("Résultat maximum([3,7,2,9,1]) = 9 affiché", 2, "aff")
    cr10.ok("9 trouvé") if 9.0 in ns_out else cr10.ko("9 absent dans la sortie")
    sp_d.criteres.append(cr10)

    if 9.0 not in ns_out:
        sp_d.feedback = ("Initialise maxi = liste[0], puis parcours la liste : "
                         "si element > maxi → maxi = element. Retourne maxi.")
    c.append(sp_d)
    return c


# ──────────────────────────────────────────────────────────────────
# CONCEPT : TURTLE — Formes avec for
# ──────────────────────────────────────────────────────────────────
ENONCE_TURTLE = """
Écris un programme turtle qui :
  a) Dessine un carré de côté 100 avec une boucle for (4 côtés)
  b) Lève le crayon, avance de 150, puis dessine un triangle équilatéral (côté 80)
  c) Ajoute au moins une couleur différente pour chaque forme
"""

def eval_turtle(code, succes, sortie, spy, erreur, input_vals=None):
    c = []

    sp_a = SousPartie("a", "Exécution sans erreur", 2)
    cr = Critere("Code tourne sans erreur", 2, "exe")
    cr.ok() if succes else cr.ko(erreur)
    sp_a.criteres.append(cr); c.append(sp_a)

    segs = spy.segment_lengths()
    total_segs = spy.total_segments()
    nb_pu  = spy.nb_penup()

    # ── (b) carré ────────────────────────────────
    sp_b = SousPartie("b", "Carré de côté 100", 4)
    cr1 = Critere("4 segments de longueur 100 (côtés du carré)", 2, "aff")
    seg100 = [s for s in segs if abs(s-100)<2]
    cr1.ok(f"{len(seg100)} segment(s) de 100px") if len(seg100)>=4 \
        else cr1.partiel(len(seg100)//2, f"seulement {len(seg100)}/4 trouvés")
    sp_b.criteres.append(cr1)

    cr2 = Critere("Angles de 90° (right(90) ou left(90))", 1, "aff")
    t90 = spy.turns_of(90)
    cr2.ok(f"{t90} virage(s) à 90°") if t90>=4 else cr2.ko(f"{t90}/4 virages à 90°")
    sp_b.criteres.append(cr2)

    cr3 = Critere("Boucle for range(4) utilisée", 1, "str")
    cr3.ok() if (nb_for(code)>=1 and "range(4)" in code) else \
        cr3.ko("for range(4) attendu pour le carré")
    sp_b.criteres.append(cr3)

    if len(seg100)<4:
        sp_b.feedback = ("for i in range(4): forward(100); right(90) "
                         "dessine un carré de côté 100.")
    c.append(sp_b)

    # ── (c) déplacement + triangle ───────────────
    sp_c = SousPartie("c", "Déplacement + triangle équilatéral (côté 80)", 3)
    cr4 = Critere("Levée de crayon entre les formes (penup)", 1, "aff")
    cr4.ok() if nb_pu >= 1 else cr4.ko("penup() absent")
    sp_c.criteres.append(cr4)

    seg80  = [s for s in segs if abs(s-80)<2]
    cr5 = Critere("3 segments de longueur 80 (triangle)", 2, "aff")
    cr5.ok(f"{len(seg80)} trouvés") if len(seg80)>=3 \
        else cr5.partiel(len(seg80)//2, f"{len(seg80)}/3 trouvés")
    sp_c.criteres.append(cr5)

    if len(seg80)<3:
        sp_c.feedback = ("Triangle équilatéral : for i in range(3): "
                         "forward(80); left(120)  (angle extérieur = 120°).")
    c.append(sp_c)

    # ── (d) couleurs ─────────────────────────────
    sp_d = SousPartie("d", "Couleurs (au moins 2 différentes)", 3)
    nb_color = sum(1 for c2 in spy._calls if c2[0] in ("color","pencolor","fillcolor"))
    cr6 = Critere("color() ou pencolor() appelé ≥ 2 fois", 2, "aff")
    cr6.ok(f"{nb_color} appels couleur") if nb_color>=2 \
        else cr6.partiel(1 if nb_color==1 else 0,
                         f"{nb_color} appel(s) couleur")
    sp_d.criteres.append(cr6)

    cr7 = Critere("Couleurs différentes pour chaque forme", 1, "for")
    colors_used = [c2[1] for c2 in spy._calls if c2[0] in ("color","pencolor")]
    ok7 = len(set(str(x) for x in colors_used)) >= 2
    cr7.ok() if ok7 else cr7.ko("mêmes couleurs ou une seule couleur")
    sp_d.criteres.append(cr7)
    c.append(sp_d)
    return c


# ──────────────────────────────────────────────────────────────────
# CONCEPT : LISTES — traitement avec boucle
# ──────────────────────────────────────────────────────────────────
ENONCE_LISTES = """
Écris un programme qui :
  a) Crée une liste de 6 notes [12, 8, 17, 5, 15, 9]
  b) Calcule et affiche la moyenne avec une boucle for
  c) Affiche les notes > 10 avec un message "Reçu : X"
  d) Trie la liste et affiche-la du plus petit au plus grand
"""

def eval_listes(code, succes, sortie, spy, erreur, input_vals=None):
    ls = lignes(sortie)
    c  = []
    notes = [12, 8, 17, 5, 15, 9]
    moy   = sum(notes)/len(notes)

    sp_a = SousPartie("a", "Exécution sans erreur", 2)
    cr = Critere("Code tourne sans erreur", 2, "exe")
    cr.ok() if succes else cr.ko(erreur)
    sp_a.criteres.append(cr); c.append(sp_a)

    sp_b = SousPartie("b", "Liste définie + moyenne calculée", 4)
    cr1 = Critere("Liste [12,8,17,5,15,9] définie", 1, "str")
    cr1.ok() if all(str(n) in code for n in notes) else \
        cr1.ko("certains éléments manquent")
    sp_b.criteres.append(cr1)

    ns = nums(sortie)
    cr2 = Critere(f"Moyenne = {moy:.1f} affichée", 2, "aff")
    ok2 = any(abs(x - moy)<0.1 for x in ns)
    cr2.ok(f"moyenne {moy:.1f} trouvée") if ok2 else \
        cr2.ko(f"{moy:.1f} absent (nombres vus: {ns[:5]})")
    sp_b.criteres.append(cr2)

    cr3 = Critere("Boucle for et accumulateur pour la somme (pas sum())", 1, "for")
    ok3 = nb_for(code)>=1 and "+=" in code
    cr3.ok() if ok3 else cr3.ko("boucle+accumulateur attendus")
    sp_b.criteres.append(cr3)

    if not ok2:
        sp_b.feedback = ("Somme = 0; for n in liste: somme += n; "
                         "moy = somme / len(liste) → doit donner 11.0.")
    c.append(sp_b)

    sp_c = SousPartie("c", "Affiche les notes > 10 avec 'Reçu : X'", 3)
    recus_attendus = [n for n in notes if n > 10]  # 12, 17, 15
    cr4 = Critere(f"Notes > 10 filtrées : {recus_attendus}", 2, "aff")
    recus_trouves = [round(x) for x in ns if x > 10]
    ok4 = all(n in recus_trouves for n in recus_attendus)
    cr4.ok() if ok4 else cr4.partiel(1 if any(n in recus_trouves for n in recus_attendus) else 0,
                                      f"trouvés: {recus_trouves}")
    sp_c.criteres.append(cr4)

    cr5 = Critere("Mot 'Reçu' dans la sortie", 1, "aff")
    cr5.ok() if any("recu" in l.lower() or "reçu" in l.lower() for l in ls) \
        else cr5.ko("'Reçu' absent")
    sp_c.criteres.append(cr5)

    if not ok4:
        sp_c.feedback = ("for n in liste: if n > 10: print('Reçu :', n)")
    c.append(sp_c)

    sp_d = SousPartie("d", "Liste triée affichée", 3)
    triee = sorted(notes)
    cr6 = Critere(f"Sortie contient {triee}", 2, "aff")
    ns_int = [round(x) for x in ns]
    ok6 = all(n in ns_int for n in triee)
    cr6.ok() if ok6 else cr6.ko(f"liste triée {triee} non retrouvée")
    sp_d.criteres.append(cr6)

    cr7 = Critere("sorted() ou .sort() utilisé", 1, "str")
    cr7.ok() if ("sorted" in code or ".sort()" in code) else \
        cr7.ko("sorted() ou .sort() attendu")
    sp_d.criteres.append(cr7)
    c.append(sp_d)
    return c


# ══════════════════════════════════════════════════════════════════
#  CATALOGUE DES CONCEPTS DISPONIBLES
# ══════════════════════════════════════════════════════════════════

CONCEPTS = {
    "1": {
        "nom":    "Boucle for — Table de multiplication",
        "enonce": ENONCE_FOR,
        "eval":   eval_for,
        "inputs": ["7"],
    },
    "2": {
        "nom":    "Boucle while — Validation + compte à rebours",
        "enonce": ENONCE_WHILE,
        "eval":   eval_while,
        "inputs": ["-3", "0", "5"],
    },
    "3": {
        "nom":    "Fonctions — est_pair / factorielle / maximum",
        "enonce": ENONCE_FONCTIONS,
        "eval":   eval_fonctions,
        "inputs": [],
    },
    "4": {
        "nom":    "Turtle — Carré + triangle + couleurs",
        "enonce": ENONCE_TURTLE,
        "eval":   eval_turtle,
        "inputs": [],
    },
    "5": {
        "nom":    "Listes — Moyenne / filtre / tri",
        "enonce": ENONCE_LISTES,
        "eval":   eval_listes,
        "inputs": [],
    },
}


# ══════════════════════════════════════════════════════════════════
#  RAPPORT COMPLET
# ══════════════════════════════════════════════════════════════════

def rapport(nom, corrections):
    """
    corrections : list[ (nom_concept, list[SousPartie]) ]
    """
    total_pts = 0
    total_max = 0

    print()
    print("═" * 68)
    print(f"  RAPPORT D'ÉVALUATION — {nom.upper()}")
    print(f"  Python | Barème Genevois /6")
    print("═" * 68)

    recap_cats = {"exe":0,"aff":0,"for":0,"str":0}
    recap_max  = {"exe":0,"aff":0,"for":0,"str":0}

    for nom_concept, sous_parties in corrections:
        pts_ex  = sum(sp.pts()     for sp in sous_parties)
        max_ex  = sum(sp.pts_max   for sp in sous_parties)
        note_ex = note_g(pts_ex, max_ex)
        total_pts += pts_ex
        total_max += max_ex

        print(f"\n  ┌─ {nom_concept}")
        print(f"  │  Points : {pts_ex}/{max_ex}  →  {barre(pts_ex,max_ex,16)}  {note_ex}/6  {mention(note_ex)}")
        print("  │")
        for sp in sous_parties:
            print(sp.rapport("  │  "))
            for cr in sp.criteres:
                recap_cats[cr.cat] += cr.pts
                recap_max[cr.cat]  += cr.pts_max
        print("  └" + "─"*60)

    note_fin = note_g(total_pts, total_max)

    print()
    print("═" * 68)
    print("  RÉCAPITULATIF PAR CATÉGORIE")
    print("  " + "─"*60)
    cats_info = [
        ("exe", "EXÉCUTION  (sans erreur)           "),
        ("aff", "AFFICHAGE  (résultats corrects) ★  "),
        ("for", "FORMULE    (algorithme juste)       "),
        ("str", "STRUCTURE  (boucle, def, style)     "),
    ]
    for cat, label in cats_info:
        sp = recap_cats[cat]; sm = recap_max[cat]
        n  = note_g(sp, sm) if sm else 1.0
        print(f"  {label}  {barre(sp,sm,15)}  {sp}/{sm}  ({n}/6)")

    print("═" * 68)
    print(f"  TOTAL  : {total_pts}/{total_max} points")
    print(f"  NOTE   : {note_fin} / 6   —  {mention(note_fin)}")
    print("═" * 68)

    # grille
    print("\n  GRILLE BARÈME GENEVOIS :")
    print("  " + "─"*50)
    for n, pct, m in [(6.0,"100%","Excellent"),(5.5,"90%","Très bien"),
                       (5.0,"80%","Bien"),(4.5,"70%","Assez bien"),
                       (4.0,"60%","Suffisant"),(3.5,"50%","Insuffisant"),
                       (3.0,"40%","Insuffisant"),(2.0,"20%","Faible"),(1.0,"0%","Très faible")]:
        m2 = "  ◀ NOTE FINALE" if abs(n-note_fin)<0.3 else ""
        print(f"  {n:.1f}/6  {'█'*round((n-1)/5*12):<12} ({pct:>4})  {m}{m2}")
    print()

    # FEEDBACK GLOBAL
    pts_pct = total_pts/total_max if total_max else 0
    print("  FEEDBACK GLOBAL :")
    print("  " + "─"*50)
    if pts_pct >= 0.90:
        print("  Excellent travail. Maîtrise complète des concepts.")
    elif pts_pct >= 0.70:
        print("  Bon travail. Quelques détails à peaufiner.")
        low = [l for c,l in cats_info if recap_max[c] and nota(recap_cats[c],recap_max[c]) < 4.5]
        if low: print(f"  Axe d'amélioration : {low[0].strip()}")
    elif pts_pct >= 0.50:
        print("  Résultats insuffisants. Révise les points marqués ✗.")
        low = [l for c,l in cats_info if recap_max[c] and nota(recap_cats[c],recap_max[c]) < 4.0]
        for l in low[:2]: print(f"  → {l.strip()}")
    else:
        print("  Travail insuffisant. Revoir les bases et les erreurs signalées.")
        print("  Consulte les 💬 feedbacks par sous-partie ci-dessus.")
    print()
    return note_fin

def nota(p, m): return note_g(p, m)


# ══════════════════════════════════════════════════════════════════
#  INTERFACE INTERACTIVE
# ══════════════════════════════════════════════════════════════════

def lire_code(invite):
    """Lecture multi-ligne : termine sur une ligne vide."""
    print(invite)
    print("  (Colle le code élève, puis appuie sur ENTRÉE deux fois)")
    lignes_code = []
    while True:
        ligne = input()
        if ligne == "" and lignes_code and lignes_code[-1] == "":
            break
        lignes_code.append(ligne)
    return "\n".join(lignes_code[:-1])  # retire la dernière ligne vide


def mode_interactif():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       CORRECTEUR PYTHON INTERACTIF — BARÈME /6          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    nom = input("\n  Nom de l'élève : ").strip() or "Élève"

    print("\n  CONCEPTS DISPONIBLES :")
    for k, v in CONCEPTS.items():
        print(f"    [{k}] {v['nom']}")
    print()

    choix = input("  Concepts à corriger (ex: 1 3 5 ou 'tous') : ").strip()
    if choix.lower() in ("tous", "all", ""):
        selected = list(CONCEPTS.keys())
    else:
        selected = [c.strip() for c in choix.split() if c.strip() in CONCEPTS]

    if not selected:
        print("  Aucun concept sélectionné. Fin.")
        return

    corrections = []
    for cle in selected:
        concept = CONCEPTS[cle]
        print()
        print("─" * 62)
        print(f"  CONCEPT : {concept['nom']}")
        print("─" * 62)
        print(f"\n  ÉNONCÉ :{concept['enonce']}")

        code = lire_code(f"\n  CODE ÉLÈVE ({concept['nom']}) :")
        if not code.strip():
            print("  ⚠ Aucun code saisi — exercice ignoré.")
            continue

        succes, sortie, spy, erreur = executer(code, concept["inputs"])
        sous_parties = concept["eval"](code, succes, sortie, spy, erreur, concept["inputs"])
        corrections.append((concept["nom"], sous_parties))

    if corrections:
        rapport(nom, corrections)


# ══════════════════════════════════════════════════════════════════
#  MODE SCRIPT — Remplis ici pour une correction sans saisie
# ══════════════════════════════════════════════════════════════════

NOM_ELEVE = "Élève Test"

# Concepts à corriger : "1" for, "2" while, "3" fonctions, "4" turtle, "5" listes
CONCEPTS_SELECTIONNES = ["1", "3", "4"]

CODES_ELEVES = {
    "1": """
n = int(input("Table de : "))
total = 0
for i in range(1, 11):
    res = n * i
    print(n, "x", i, "=", res)
    total += res
print("Somme =", total)
""",
    "3": """
def est_pair(n):
    return n % 2 == 0

def factorielle(n):
    if n == 0:
        return 1
    res = 1
    for i in range(1, n + 1):
        res *= i
    return res

def maximum(liste):
    maxi = liste[0]
    for x in liste:
        if x > maxi:
            maxi = x
    return maxi

print(est_pair(4))
print(est_pair(7))
print("5! =", factorielle(5))
print("0! =", factorielle(0))
print("Max :", maximum([3, 7, 2, 9, 1]))
""",
    "4": """
import turtle

turtle.color("blue")
for i in range(4):
    turtle.forward(100)
    turtle.right(90)

turtle.penup()
turtle.forward(150)
turtle.pendown()

turtle.color("red")
for i in range(3):
    turtle.forward(80)
    turtle.left(120)

turtle.done()
""",
}


def mode_script():
    corrections = []
    for cle in CONCEPTS_SELECTIONNES:
        if cle not in CONCEPTS or cle not in CODES_ELEVES:
            continue
        concept = CONCEPTS[cle]
        code    = textwrap.dedent(CODES_ELEVES[cle]).strip()
        succes, sortie, spy, erreur = executer(code, concept["inputs"])
        sous_parties = concept["eval"](code, succes, sortie, spy, erreur, concept["inputs"])
        corrections.append((concept["nom"], sous_parties))

    if corrections:
        rapport(NOM_ELEVE, corrections)


# ══════════════════════════════════════════════════════════════════
#  LANCEMENT
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    if "--script" in sys.argv or not sys.stdin.isatty():
        # Mode script (test automatique ou redirection stdin)
        mode_script()
    else:
        mode_interactif()

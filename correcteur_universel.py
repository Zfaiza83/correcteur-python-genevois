"""
╔══════════════════════════════════════════════════════════════╗
║        CORRECTEUR UNIVERSEL PYTHON — BARÈME GENEVOIS         ║
║              Note finale sur 6  |  Tout type de code         ║
╠══════════════════════════════════════════════════════════════╣
║  Distribution des points par exercice :                       ║
║   • EXÉCUTION  — le code tourne sans erreur                  ║
║   • AFFICHAGE  — les prints sont corrects                    ║
║   • FORMULE    — l'algorithme / le calcul est juste          ║
║   • STRUCTURE  — boucle, variables, style                    ║
║                                                               ║
║  Formule barème genevois : Note = (pts/max) × 5 + 1          ║
║  Arrondi au 0.5                                               ║
╠══════════════════════════════════════════════════════════════╣
║  TYPES PRIS EN CHARGE :                                       ║
║   turtle, calcul, boucle for/while, chaînes, listes,         ║
║   fonctions, entrées/sorties, tout autre type Python          ║
╚══════════════════════════════════════════════════════════════╝

UTILISATION :
  1. Descends jusqu'à la section  ▼ ZONE EXERCICES ▼
  2. Pour chaque exercice : remplis CODE, EXPECTED_OUTPUT,
     et les fonctions de validation.
  3. Lance : python correcteur_universel.py
"""

import math
import io
import sys
import types
import re
from contextlib import redirect_stdout


# ══════════════════════════════════════════════════════════════
#  SPY TURTLE  (intercepte les appels turtle sans fenêtre)
# ══════════════════════════════════════════════════════════════

class TurtleSpy:
    def __init__(self):
        self._calls = []
        self._x = 0.0
        self._y = 0.0
        self._angle = 0.0
        self._pen_down = True
        self._segments = []

    def _move(self, d):
        if self._pen_down:
            x2 = self._x + d * math.cos(math.radians(self._angle))
            y2 = self._y + d * math.sin(math.radians(self._angle))
            self._segments.append((round(self._x,2), round(self._y,2),
                                    round(x2,2), round(y2,2), round(d,2)))
            self._x, self._y = x2, y2
        else:
            self._x += d * math.cos(math.radians(self._angle))
            self._y += d * math.sin(math.radians(self._angle))

    def forward(self, d):
        self._calls.append(("forward", d)); self._move(d)
    def fd(self, d): self.forward(d)
    def backward(self, d):
        self._calls.append(("backward", d)); self._move(-d)
    def bk(self, d): self.backward(d)
    def right(self, a):
        self._calls.append(("right", a)); self._angle -= a
    def rt(self, a): self.right(a)
    def left(self, a):
        self._calls.append(("left", a)); self._angle += a
    def lt(self, a): self.left(a)
    def penup(self):
        self._calls.append(("penup",)); self._pen_down = False
    def pu(self): self.penup()
    def up(self): self.penup()
    def pendown(self):
        self._calls.append(("pendown",)); self._pen_down = True
    def pd(self): self.pendown()
    def down(self): self.pendown()
    def goto(self, x, y=None):
        if y is None and hasattr(x,'__iter__'): x,y=x
        self._calls.append(("goto",x,y))
        if self._pen_down:
            self._segments.append((round(self._x,2),round(self._y,2),
                                    round(x,2),round(y,2),None))
        self._x,self._y = x,y
    def setpos(self,x,y=None): self.goto(x,y)
    def setposition(self,x,y=None): self.goto(x,y)
    def setheading(self,a):
        self._calls.append(("setheading",a)); self._angle=a
    def seth(self,a): self.setheading(a)
    def home(self):
        self._calls.append(("home",)); self._x=self._y=0.; self._angle=0.
    def color(self,*a): self._calls.append(("color",a))
    def pencolor(self,*a): self._calls.append(("pencolor",a))
    def fillcolor(self,*a): self._calls.append(("fillcolor",a))
    def begin_fill(self): self._calls.append(("begin_fill",))
    def end_fill(self): self._calls.append(("end_fill",))
    def speed(self,s): self._calls.append(("speed",s))
    def hideturtle(self): self._calls.append(("hideturtle",))
    def ht(self): self.hideturtle()
    def showturtle(self): self._calls.append(("showturtle",))
    def st(self): self.showturtle()
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

    # ── stats ──────────────────────────────────────────────
    def nb_call(self, name):
        return sum(1 for c in self._calls if c[0]==name)
    def nb_forward(self): return self.nb_call("forward")
    def nb_right(self): return self.nb_call("right")
    def nb_left(self): return self.nb_call("left")
    def total_segments(self): return len(self._segments)
    def segment_lengths(self):
        return [s[4] for s in self._segments if s[4] is not None]
    def unique_lengths(self):
        return set(round(l,1) for l in self.segment_lengths() if l and l>0)
    def turns_of(self, deg, tol=1):
        return sum(1 for c in self._calls
                   if c[0] in ("right","left") and abs(c[1]-deg)<tol)
    def is_closed(self, tol=3):
        return math.hypot(self._x, self._y) < tol
    def nb_penup(self): return self.nb_call("penup")
    def has_color(self):
        return any(c[0] in ("color","pencolor","fillcolor") for c in self._calls)


# ══════════════════════════════════════════════════════════════
#  MOTEUR D'EXÉCUTION
# ══════════════════════════════════════════════════════════════

def _build_ns(spy=None, input_val="", extra=None):
    """Construit le namespace d'exécution."""
    spy = spy or TurtleSpy()
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
        "input": lambda *a: input_val,
        "int": int, "float": float, "str": str, "bool": bool,
        "list": list, "tuple": tuple, "dict": dict, "set": set,
        "abs": abs, "round": round, "sum": sum, "min": min, "max": max,
        "sorted": sorted, "enumerate": enumerate, "zip": zip,
        "math": math,
    }
    if extra:
        ns.update(extra)
    return ns, spy


def executer(code_str, input_val="", extra=None):
    """
    Exécute le code élève.
    Retourne (succes, sortie, spy, erreur)
    """
    ns, spy = _build_ns(input_val=input_val, extra=extra)
    sys.modules["turtle"] = spy          # type: ignore
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(code_str, "<eleve>", "exec"), ns)
        return True, buf.getvalue(), spy, ""
    except Exception as e:
        return False, buf.getvalue(), spy, f"{type(e).__name__}: {e}"
    finally:
        sys.modules.pop("turtle", None)


# ══════════════════════════════════════════════════════════════
#  BARÈME GENEVOIS
# ══════════════════════════════════════════════════════════════

def note_genevois(pts, pts_max):
    """Note /6 arrondie au 0.5."""
    if pts_max == 0: return 1.0
    raw = (pts / pts_max) * 5 + 1
    return round(max(1.0, min(6.0, raw)) * 2) / 2

def mention(note):
    seuils = [(5.5,"Excellent ★★★"),(5.0,"Très bien ★★"),(4.5,"Bien ★"),
              (4.0,"Suffisant ✓"),(3.0,"Insuffisant ✗"),(0,"Très insuffisant ✗✗")]
    for s, m in seuils:
        if note >= s: return m
    return "Très insuffisant ✗✗"


# ══════════════════════════════════════════════════════════════
#  CLASSES DE CRITÈRES
# ══════════════════════════════════════════════════════════════

class Critere:
    """Un critère de notation avec son label et ses points."""
    def __init__(self, label, pts_max, categorie="structure"):
        self.label = label
        self.pts_max = pts_max
        self.categorie = categorie   # execution | affichage | formule | structure
        self.pts_obtenus = 0
        self.ok = False
        self.detail = ""

    def valider(self, ok, detail=""):
        self.ok = ok
        self.pts_obtenus = self.pts_max if ok else 0
        self.detail = detail
        return self

    def partiel(self, pts, detail=""):
        self.pts_obtenus = min(pts, self.pts_max)
        self.ok = pts >= self.pts_max
        self.detail = detail
        return self

    def ligne(self):
        icone = "✓" if self.ok else ("~" if self.pts_obtenus > 0 else "✗")
        cat = f"[{self.categorie[:3].upper()}]"
        return (f"  {icone} {cat} [{self.pts_obtenus}/{self.pts_max}] "
                f"{self.label}"
                + (f"  → {self.detail}" if self.detail else ""))


class Exercice:
    """
    Définit un exercice et le corrige.

    Paramètres :
      titre       — nom affiché
      criteres    — liste de Critere (définit le total de points)
      evaluateur  — fonction(code, succes, sortie, spy) → list[Critere]
      input_val   — valeur simulée pour input()
      extra       — dict injecté dans le namespace
    """
    def __init__(self, titre, evaluateur, input_val="", extra=None):
        self.titre = titre
        self.evaluateur = evaluateur
        self.input_val = input_val
        self.extra = extra

    def corriger(self, code):
        succes, sortie, spy, erreur = executer(code, self.input_val, self.extra)
        criteres = self.evaluateur(code, succes, sortie, spy, erreur)
        pts = sum(c.pts_obtenus for c in criteres)
        pts_max = sum(c.pts_max for c in criteres)
        return pts, pts_max, criteres, succes, erreur


# ══════════════════════════════════════════════════════════════
#  FONCTIONS UTILITAIRES POUR LES VALIDATEURS
# ══════════════════════════════════════════════════════════════

def normaliser(texte):
    """Normalise la sortie pour comparaison (espaces, casse)."""
    return re.sub(r'\s+', ' ', str(texte).strip().lower())

def sortie_contient(sortie, *mots):
    """Vérifie que chaque mot apparaît dans la sortie."""
    s = normaliser(sortie)
    return all(normaliser(m) in s for m in mots)

def sortie_egale(sortie, attendu):
    """Comparaison exacte normalisée."""
    return normaliser(sortie) == normaliser(attendu)

def code_utilise(code, *mots_cles):
    """Vérifie la présence de mots-clés dans le code source."""
    return all(m in code for m in mots_cles)

def compter_boucles_for(code):
    return len(re.findall(r'\bfor\b', code))

def compter_boucles_while(code):
    return len(re.findall(r'\bwhile\b', code))

def compter_prints(code):
    return len(re.findall(r'\bprint\s*\(', code))

def extraire_nombres(sortie):
    """Extrait tous les nombres d'une sortie texte."""
    return [float(x) for x in re.findall(r'-?\d+\.?\d*', sortie)]

def lignes_sortie(sortie):
    return [l.strip() for l in sortie.strip().splitlines() if l.strip()]


# ══════════════════════════════════════════════════════════════
#  ▼▼▼  ZONE EXERCICES — MODIFIE ICI  ▼▼▼
# ══════════════════════════════════════════════════════════════
#
#  Pour chaque exercice, définis :
#   1. CODE_EXn  — le code de l'élève
#   2. def eval_exn(code, succes, sortie, spy, erreur)
#        → retourne une list[Critere] avec .valider() ou .partiel()
#
#  Répartition conseillée des points :
#   EXÉCUTION  2 pts  — tourne sans erreur
#   AFFICHAGE  3 pts  — print corrects
#   FORMULE    3 pts  — algorithme / calcul juste
#   STRUCTURE  2 pts  — boucle, variable, style
#   TOTAL      10 pts par exercice (adapte librement)
#
# ─────────────────────────────────────────────────────────────

# ╔══════════════════════════╗
# ║  EX1 — Table de multiplication avec for  (10 pts)
# ╚══════════════════════════╝
#  L'élève doit afficher la table de N (ex: table de 7)
#  Format attendu :  7 x 1 = 7  /  7 x 2 = 14  … 7 x 10 = 70

CODE_EX1 = """
n = 7
for i in range(1, 11):
    print(n, "x", i, "=", n * i)
"""

def eval_ex1(code, succes, sortie, spy, erreur):
    c = []

    # ── EXÉCUTION (2 pts) ──────────────────────────────────
    ex = Critere("Code s'exécute sans erreur", 2, "execution")
    c.append(ex.valider(succes, erreur if not succes else ""))

    # ── AFFICHAGE (3 pts) ──────────────────────────────────
    lignes = lignes_sortie(sortie)

    af1 = Critere("10 lignes affichées (une par multiplication)", 1, "affichage")
    c.append(af1.valider(len(lignes) == 10, f"{len(lignes)} ligne(s) trouvée(s)"))

    af2 = Critere("Première ligne contient 7 x 1 = 7", 1, "affichage")
    ok2 = len(lignes) > 0 and sortie_contient(lignes[0], "7", "1", "7")
    c.append(af2.valider(ok2, lignes[0] if lignes else "aucune sortie"))

    af3 = Critere("Dernière ligne contient 7 x 10 = 70", 1, "affichage")
    ok3 = len(lignes) >= 10 and sortie_contient(lignes[-1], "7", "10", "70")
    c.append(af3.valider(ok3, lignes[-1] if lignes else "aucune sortie"))

    # ── FORMULE (3 pts) ────────────────────────────────────
    nombres = extraire_nombres(sortie)
    resultats = nombres[2::3] if len(nombres) >= 3 else []  # 3e colonne
    attendus = [7*i for i in range(1, 11)]

    fo1 = Critere("Résultats numériques corrects (7×1 à 7×10)", 2, "formule")
    corrects = sum(1 for r,a in zip(resultats, attendus) if abs(r-a)<0.01)
    if corrects == 10:
        fo1.valider(True, "tous corrects")
    else:
        fo1.partiel(corrects // 5, f"{corrects}/10 corrects")
    c.append(fo1)

    fo2 = Critere("Multiplication utilisée (* ou formule équivalente)", 1, "formule")
    c.append(fo2.valider("*" in code or "mul" in code,
                          "opérateur * trouvé" if "*" in code else "absent"))

    # ── STRUCTURE (2 pts) ──────────────────────────────────
    st1 = Critere("Boucle for utilisée", 1, "structure")
    c.append(st1.valider(compter_boucles_for(code) >= 1))

    st2 = Critere("range(1, 11) ou range(1, 10+1)", 1, "structure")
    ok_r = "range(1, 11)" in code or "range(1,11)" in code or "range(1, 10+1)" in code
    c.append(st2.valider(ok_r, "range(1,11) attendu"))

    return c


# ╔══════════════════════════╗
# ║  EX2 — Répétition d'un motif avec for  (10 pts)
# ╚══════════════════════════╝
#  Affiche N fois un motif (ex: "*** Python ***")
#  + numéroter chaque ligne

CODE_EX2 = """
motif = "*** Python ***"
n = 5
for i in range(1, n + 1):
    print(i, "-", motif)
"""

def eval_ex2(code, succes, sortie, spy, erreur):
    c = []

    # ── EXÉCUTION (2 pts) ──────────────────────────────────
    ex = Critere("Code s'exécute sans erreur", 2, "execution")
    c.append(ex.valider(succes, erreur if not succes else ""))

    # ── AFFICHAGE (3 pts) ──────────────────────────────────
    lignes = lignes_sortie(sortie)

    af1 = Critere("5 lignes affichées", 1, "affichage")
    c.append(af1.valider(len(lignes) == 5, f"{len(lignes)} ligne(s)"))

    af2 = Critere("Le motif apparaît dans chaque ligne", 1, "affichage")
    motif = "python"
    ok2 = all(motif in l.lower() or "***" in l for l in lignes) if lignes else False
    c.append(af2.valider(ok2))

    af3 = Critere("Numérotation 1 à 5 présente", 1, "affichage")
    nums = [extraire_nombres(l) for l in lignes]
    ok3 = all(i+1 in [round(x) for x in (nums[i] if i<len(nums) else [])]
              for i in range(5)) if len(lignes)==5 else False
    c.append(af3.valider(ok3, "numéros 1-5 attendus"))

    # ── FORMULE (3 pts) ────────────────────────────────────
    fo1 = Critere("Variable pour le motif utilisée (pas du texte brut répété)", 1, "formule")
    has_var = bool(re.search(r'\w+\s*=\s*["\']', code))
    c.append(fo1.valider(has_var))

    fo2 = Critere("Variable pour N (pas hard-codé dans range)", 2, "formule")
    # cherche un pattern type "n = 5" puis "range(...n...)"
    has_n_var = bool(re.search(r'\bn\s*=\s*\d+', code, re.IGNORECASE)) or \
                bool(re.search(r'nb|nombre|fois|repetitions?\s*=', code, re.IGNORECASE))
    c.append(fo2.valider(has_n_var, "variable n= trouvée" if has_n_var else "n non défini"))

    # ── STRUCTURE (2 pts) ──────────────────────────────────
    st1 = Critere("Boucle for avec range()", 1, "structure")
    c.append(st1.valider(compter_boucles_for(code)>=1 and "range" in code))

    st2 = Critere("range commence à 1 (numérotation correcte)", 1, "structure")
    ok_r = "range(1" in code or "range(1," in code
    c.append(st2.valider(ok_r, "range(1,...) attendu"))

    return c


# ╔══════════════════════════╗
# ║  EX3 — Somme des N premiers entiers avec for  (10 pts)
# ╚══════════════════════════╝
#  Calcule 1+2+3+...+N et affiche le résultat
#  N saisi par l'utilisateur (ex: N=10 → 55)

CODE_EX3 = """
n = int(input("Entrer N : "))
total = 0
for i in range(1, n + 1):
    total = total + i
print("La somme de 1 à", n, "est :", total)
"""

def eval_ex3(code, succes, sortie, spy, erreur):
    c = []

    # ── EXÉCUTION (2 pts) ──────────────────────────────────
    ex = Critere("Code s'exécute sans erreur", 2, "execution")
    c.append(ex.valider(succes, erreur if not succes else ""))

    # ── AFFICHAGE (3 pts) ──────────────────────────────────
    af1 = Critere("Un résultat numérique affiché", 1, "affichage")
    nombres = extraire_nombres(sortie)
    c.append(af1.valider(len(nombres) >= 1, f"nombres trouvés: {nombres}"))

    af2 = Critere("Résultat = 55 (somme 1 à 10)", 2, "affichage")
    ok2 = 55.0 in nombres or 55 in [round(x) for x in nombres]
    c.append(af2.valider(ok2, f"sortie: {sortie.strip()}"))

    # ── FORMULE (3 pts) ────────────────────────────────────
    fo1 = Critere("Accumulateur initialisé à 0 avant la boucle", 1, "formule")
    ok_acc = bool(re.search(r'\b(total|somme|s|acc)\s*=\s*0', code))
    c.append(fo1.valider(ok_acc))

    fo2 = Critere("Accumulation dans la boucle (total += i ou total = total + i)", 2, "formule")
    ok_acc2 = "+=" in code or re.search(r'\w+\s*=\s*\w+\s*\+\s*\w+', code) is not None
    c.append(fo2.valider(bool(ok_acc2)))

    # ── STRUCTURE (2 pts) ──────────────────────────────────
    st1 = Critere("Boucle for utilisée", 1, "structure")
    c.append(st1.valider(compter_boucles_for(code) >= 1))

    st2 = Critere("input() utilisé pour saisir N", 1, "structure")
    c.append(st2.valider("input" in code))

    return c


# ╔══════════════════════════╗
# ║  EX4 — Dessin carré avec turtle + for  (10 pts)
# ╚══════════════════════════╝
#  Dessine un carré de côté 100 avec une boucle for

CODE_EX4 = """
import turtle

for i in range(4):
    turtle.forward(100)
    turtle.right(90)

turtle.done()
"""

def eval_ex4(code, succes, sortie, spy, erreur):
    c = []

    # ── EXÉCUTION (2 pts) ──────────────────────────────────
    ex = Critere("Code s'exécute sans erreur", 2, "execution")
    c.append(ex.valider(succes, erreur if not succes else ""))

    # ── AFFICHAGE (visuel turtle, 3 pts) ──────────────────
    af1 = Critere("4 segments dessinés (4 côtés)", 2, "affichage")
    nb_seg = spy.total_segments()
    c.append(af1.valider(nb_seg >= 4, f"{nb_seg} segment(s)"))

    af2 = Critere("Carré fermé (tortue revient au départ ±3px)", 1, "affichage")
    c.append(af2.valider(spy.is_closed(), f"dist={math.hypot(spy._x,spy._y):.1f}px"))

    # ── FORMULE (3 pts) ────────────────────────────────────
    fo1 = Critere("Angles de 90° (right(90) ou left(90))", 2, "formule")
    t90 = spy.turns_of(90)
    c.append(fo1.valider(t90 >= 4, f"{t90} virage(s) à 90°"))

    fo2 = Critere("Segments de même longueur (côtés égaux)", 1, "formule")
    ul = spy.unique_lengths()
    c.append(fo2.valider(len(ul) == 1, f"longueurs: {ul}"))

    # ── STRUCTURE (2 pts) ──────────────────────────────────
    st1 = Critere("Boucle for avec range(4)", 1, "structure")
    c.append(st1.valider(compter_boucles_for(code)>=1 and "range(4)" in code))

    st2 = Critere("import turtle présent", 1, "structure")
    c.append(st2.valider("import turtle" in code or "import turtle" in code))

    return c


# ╔══════════════════════════╗
# ║  EX5 — FizzBuzz 1 à 20  (10 pts)
# ╚══════════════════════════╝
#  for i in 1..20 : Fizz si div/3, Buzz si div/5, FizzBuzz si div/15

CODE_EX5 = """
for i in range(1, 21):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
"""

def eval_ex5(code, succes, sortie, spy, erreur):
    c = []

    # ── EXÉCUTION (2 pts) ──────────────────────────────────
    ex = Critere("Code s'exécute sans erreur", 2, "execution")
    c.append(ex.valider(succes, erreur if not succes else ""))

    # ── AFFICHAGE (3 pts) ──────────────────────────────────
    lignes = lignes_sortie(sortie)
    attendu = []
    for i in range(1, 21):
        if i%15==0: attendu.append("fizzbuzz")
        elif i%3==0: attendu.append("fizz")
        elif i%5==0: attendu.append("buzz")
        else: attendu.append(str(i))

    af1 = Critere("20 lignes affichées", 1, "affichage")
    c.append(af1.valider(len(lignes)==20, f"{len(lignes)} lignes"))

    corrects = sum(1 for l,a in zip([x.lower() for x in lignes], attendu) if l==a)
    af2 = Critere("Toutes les lignes correctes (20/20)", 2, "affichage")
    if corrects == 20:
        af2.valider(True, "parfait")
    else:
        af2.partiel(corrects // 10, f"{corrects}/20 lignes correctes")
    c.append(af2)

    # ── FORMULE (3 pts) ────────────────────────────────────
    fo1 = Critere("Modulo % utilisé", 1, "formule")
    c.append(fo1.valider("%" in code))

    fo2 = Critere("Cas FizzBuzz (divisible par 15) traité en premier", 2, "formule")
    # le cas 15 doit apparaître avant les cas 3 et 5
    pos15 = code.find("15")
    pos3  = code.find("% 3") if "% 3" in code else code.find("%3")
    pos5  = code.find("% 5") if "% 5" in code else code.find("%5")
    ok15 = pos15 != -1 and (pos15 < pos3 or pos3 == -1)
    c.append(fo2.valider(ok15, "15 avant 3" if ok15 else "ordre incorrect"))

    # ── STRUCTURE (2 pts) ──────────────────────────────────
    st1 = Critere("Boucle for avec range(1, 21)", 1, "structure")
    c.append(st1.valider(compter_boucles_for(code)>=1 and
                          ("range(1, 21)" in code or "range(1,21)" in code)))

    st2 = Critere("if / elif / else utilisés", 1, "structure")
    c.append(st2.valider("elif" in code and "else" in code))

    return c


# ══════════════════════════════════════════════════════════════
#  CONFIGURATION : exercices à corriger
# ══════════════════════════════════════════════════════════════

NOM_ELEVE = "Élève Test"

EXERCICES = [
    (Exercice("EX1 — Table de multiplication (for)",      eval_ex1, input_val=""), CODE_EX1),
    (Exercice("EX2 — Répétition d'un motif (for)",        eval_ex2, input_val=""), CODE_EX2),
    (Exercice("EX3 — Somme 1 à N (for + accumulateur)",   eval_ex3, input_val="10"), CODE_EX3),
    (Exercice("EX4 — Carré turtle (for + turtle)",        eval_ex4, input_val=""), CODE_EX4),
    (Exercice("EX5 — FizzBuzz 1 à 20 (for + if/elif)",   eval_ex5, input_val=""), CODE_EX5),
]


# ══════════════════════════════════════════════════════════════
#  RAPPORT
# ══════════════════════════════════════════════════════════════

CATEGORIES = {
    "execution": "EXÉCUTION",
    "affichage": "AFFICHAGE",
    "formule":   "FORMULE  ",
    "structure": "STRUCTURE",
}

def rapport(nom, exercices_codes):
    resultats = []
    for ex, code in exercices_codes:
        pts, pts_max, criteres, _, _ = ex.corriger(code)
        resultats.append((ex.titre, pts, pts_max, criteres))

    total_pts = sum(r[1] for r in resultats)
    total_max = sum(r[2] for r in resultats)
    note_fin  = note_genevois(total_pts, total_max)

    print("=" * 65)
    print(f"  RAPPORT D'ÉVALUATION — {nom.upper()}")
    print(f"  Python + Boucle for | Barème Genevois /6")
    print("=" * 65)

    for titre, pts, pts_max, criteres in resultats:
        note_ex = note_genevois(pts, pts_max)
        print(f"\n  {titre}")
        print(f"  Points : {pts}/{pts_max}  →  Note : {note_ex}/6  {mention(note_ex)}")
        print("  " + "─" * 55)

        # Grouper par catégorie pour la lisibilité
        for cat_key, cat_label in CATEGORIES.items():
            groupe = [cr for cr in criteres if cr.categorie == cat_key]
            if not groupe: continue
            sous_pts   = sum(cr.pts_obtenus for cr in groupe)
            sous_max   = sum(cr.pts_max for cr in groupe)
            print(f"\n  [{cat_label}  {sous_pts}/{sous_max}]")
            for cr in groupe:
                print("  " + cr.ligne())

    # ── Récap global ──────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"  RÉCAPITULATIF PAR CATÉGORIE")
    print("  " + "─" * 55)
    for cat_key, cat_label in CATEGORIES.items():
        all_cr = [cr for _,_,_,crit in resultats for cr in crit if cr.categorie == cat_key]
        sp = sum(cr.pts_obtenus for cr in all_cr)
        sm = sum(cr.pts_max for cr in all_cr)
        barre = "█" * int(sp/sm*20) + "░" * (20 - int(sp/sm*20)) if sm else "░"*20
        print(f"  {cat_label}  {barre}  {sp}/{sm}")

    print("=" * 65)
    print(f"  TOTAL   : {total_pts}/{total_max} points")
    print(f"  NOTE    : {note_fin} / 6   —  {mention(note_fin)}")
    print("=" * 65)

    # ── Grille barème genevois ────────────────────────────
    print("\n  GRILLE BARÈME GENEVOIS :")
    print("  ─────────────────────────────────────────")
    grille = [
        (6.0,"100%","Excellent"),   (5.5,"90%","Très bien"),
        (5.0,"80%","Bien"),         (4.5,"70%","Assez bien"),
        (4.0,"60%","Suffisant"),    (3.5,"50%","Insuffisant"),
        (3.0,"40%","Insuffisant"),  (2.0,"20%","Faible"),
        (1.0,"0%", "Très faible"),
    ]
    for n, pct, m in grille:
        marker = "  ◀ TU ES ICI" if abs(n - note_fin) < 0.3 else ""
        barre = "█" * round((n-1)/5*10)
        print(f"  {n:.1f}/6  {barre:<10}  ({pct:>4})  {m}{marker}")
    print()

    return note_fin


# ══════════════════════════════════════════════════════════════
#  LANCEMENT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nCorrection en cours...\n")
    rapport(NOM_ELEVE, EXERCICES)

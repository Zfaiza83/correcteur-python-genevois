"""
=============================================================
  ÉVALUATEUR AUTOMATIQUE — TURTLE + BOUCLES
  Barème Genevois  |  Note finale sur 6
=============================================================
  Formule : Note = (points_obtenus / points_max) × 5 + 1
  Arrondi au 0.5 le plus proche
=============================================================

EXERCICES :
  EX1 — Carré avec for        (6 pts)
  EX2 — Polygone régulier     (8 pts)
  EX3 — Spirale avec while    (8 pts)
  EX4 — Répétition de formes  (8 pts)
  EX5 — Figure combinée       (10 pts)

UTILISATION :
  1. Colle le code de l'élève dans chaque section CODE_ELEVE.
  2. Lance : python bareme_turtle_genevois.py
  3. Le rapport s'affiche dans la console.
=============================================================
"""

import math
import io
import sys
import types
from contextlib import redirect_stdout

# ──────────────────────────────────────────────────────────
#  MOTEUR DE CORRECTION : on intercepte les appels turtle
# ──────────────────────────────────────────────────────────

class TurtleSpy:
    """Remplace le module turtle pour enregistrer les appels."""

    def __init__(self):
        self._calls = []
        self._x = 0.0
        self._y = 0.0
        self._angle = 0.0
        self._pen_down = True
        self._color = "black"
        self._speed_val = 3
        self._segments = []          # liste de segments dessinés

    # ── déplacements ──────────────────────────────────────
    def forward(self, d):
        self._calls.append(("forward", d))
        if self._pen_down:
            x2 = self._x + d * math.cos(math.radians(self._angle))
            y2 = self._y + d * math.sin(math.radians(self._angle))
            self._segments.append((round(self._x, 2), round(self._y, 2),
                                   round(x2, 2), round(y2, 2),
                                   round(d, 2)))
            self._x, self._y = x2, y2
        else:
            self._x += d * math.cos(math.radians(self._angle))
            self._y += d * math.sin(math.radians(self._angle))

    fd = forward

    def backward(self, d):
        self._calls.append(("backward", d))
        self.forward(-d)

    bk = backward

    def right(self, a):
        self._calls.append(("right", a))
        self._angle -= a

    rt = right

    def left(self, a):
        self._calls.append(("left", a))
        self._angle += a

    lt = left

    def goto(self, x, y=None):
        if y is None and hasattr(x, '__iter__'):
            x, y = x
        self._calls.append(("goto", x, y))
        if self._pen_down:
            self._segments.append((round(self._x, 2), round(self._y, 2),
                                   round(x, 2), round(y, 2), None))
        self._x, self._y = x, y

    setpos = goto
    setposition = goto

    def setheading(self, a):
        self._calls.append(("setheading", a))
        self._angle = a

    seth = setheading

    def penup(self):
        self._calls.append(("penup",))
        self._pen_down = False

    pu = penup
    up = penup

    def pendown(self):
        self._calls.append(("pendown",))
        self._pen_down = True

    pd = pendown
    down = pendown

    def color(self, *args):
        self._calls.append(("color", args))
        if args:
            self._color = args[0]

    def pencolor(self, *args):
        self._calls.append(("pencolor", args))

    def fillcolor(self, *args):
        self._calls.append(("fillcolor", args))

    def begin_fill(self):
        self._calls.append(("begin_fill",))

    def end_fill(self):
        self._calls.append(("end_fill",))

    def speed(self, s):
        self._calls.append(("speed", s))
        self._speed_val = s

    def hideturtle(self):
        self._calls.append(("hideturtle",))

    def showturtle(self):
        self._calls.append(("showturtle",))

    ht = hideturtle
    st = showturtle

    def home(self):
        self._calls.append(("home",))
        self._x, self._y = 0.0, 0.0
        self._angle = 0.0

    def reset(self):
        self.__init__()

    def clear(self):
        self._calls.append(("clear",))

    def position(self):
        return (self._x, self._y)

    def pos(self):
        return self.position()

    def xcor(self):
        return self._x

    def ycor(self):
        return self._y

    def heading(self):
        return self._angle % 360

    def done(self):
        pass

    def exitonclick(self):
        pass

    def mainloop(self):
        pass

    def setup(self, *a, **k):
        pass

    def title(self, *a):
        pass

    def bgcolor(self, *a):
        pass

    def Screen(self):
        return self

    def tracer(self, *a):
        pass

    def update(self):
        pass

    def write(self, *a, **k):
        self._calls.append(("write", a))

    # ── stats utiles ──────────────────────────────────────
    def nb_forward(self):
        return sum(1 for c in self._calls if c[0] == "forward")

    def nb_right(self):
        return sum(1 for c in self._calls if c[0] == "right")

    def nb_left(self):
        return sum(1 for c in self._calls if c[0] == "left")

    def total_segments(self):
        return len(self._segments)

    def segment_lengths(self):
        return [s[4] for s in self._segments if s[4] is not None]

    def unique_lengths(self):
        return set(round(l, 1) for l in self.segment_lengths() if l and l > 0)

    def has_loop(self, code_str):
        return "for " in code_str or "while " in code_str

    def has_for(self, code_str):
        return "for " in code_str

    def has_while(self, code_str):
        return "while " in code_str

    def used_range(self, code_str):
        return "range" in code_str


# ──────────────────────────────────────────────────────────
#  BARÈME GENEVOIS
# ──────────────────────────────────────────────────────────

def note_genevois(points, points_max):
    """Convertit points/max en note /6 (arrondi au 0.5)."""
    if points_max == 0:
        return 1.0
    raw = (points / points_max) * 5 + 1
    raw = max(1.0, min(6.0, raw))
    return round(raw * 2) / 2          # arrondi au 0.5


def mention(note):
    if note >= 5.5:
        return "Excellent ★★★"
    elif note >= 5.0:
        return "Très bien ★★"
    elif note >= 4.5:
        return "Bien ★"
    elif note >= 4.0:
        return "Suffisant ✓"
    elif note >= 3.0:
        return "Insuffisant ✗"
    else:
        return "Très insuffisant ✗✗"


# ──────────────────────────────────────────────────────────
#  EXÉCUTEUR SÉCURISÉ
# ──────────────────────────────────────────────────────────

def _build_namespace(spy, input_fn=None):
    """Construit le namespace d'exécution avec le spy turtle."""
    if input_fn is None:
        input_fn = lambda *a: ""
    return {
        "turtle": spy,
        "t": spy,
        "__builtins__": __builtins__,
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
        "range": range, "print": print,
        "input": input_fn,
        "int": int, "float": float, "str": str, "math": math,
    }


def run_code(code_str, spy):
    """Exécute le code élève en injectant le spy turtle."""
    namespace = _build_namespace(spy)
    # Injecte le spy comme module turtle dans sys.modules
    sys.modules["turtle"] = spy          # type: ignore
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(code_str, "<eleve>", "exec"), namespace)
        return True, buf.getvalue()
    except Exception as e:
        return False, str(e)
    finally:
        sys.modules.pop("turtle", None)


# ══════════════════════════════════════════════════════════
#  EXERCICES — BARÈME DÉTAILLÉ
# ══════════════════════════════════════════════════════════

def evaluer_ex1(code):
    """
    EX1 — Carré avec une boucle for  (6 pts)
    ─────────────────────────────────────────
    Critères :
      [2] Utilise une boucle for
      [1] range(4) ou équivalent
      [1] forward() d'une valeur fixe
      [1] right(90) ou left(90)
      [1] Le carré est fermé (retour au point de départ ±2px)
    """
    spy = TurtleSpy()
    ok, err = run_code(code, spy)

    detail = []
    pts = 0

    # [2] for loop
    if spy.has_for(code):
        pts += 2
        detail.append("  ✓ [2/2] Boucle for présente")
    else:
        detail.append("  ✗ [0/2] Pas de boucle for")

    # [1] range(4)
    iterations = code.count("range(4)") + code.count("range( 4 )")
    # compte aussi les boucles répétées 4 fois d'une autre manière
    if "range(4)" in code or "4)" in code:
        pts += 1
        detail.append("  ✓ [1/1] range(4) ou 4 itérations")
    else:
        detail.append("  ✗ [0/1] range(4) manquant ou incorrect")

    # [1] forward
    if spy.nb_forward() >= 4:
        pts += 1
        detail.append(f"  ✓ [1/1] forward() appelé {spy.nb_forward()} fois")
    else:
        detail.append(f"  ✗ [0/1] forward() appelé {spy.nb_forward()} fois (besoin ≥ 4)")

    # [1] right/left 90°
    turns_90 = sum(1 for c in spy._calls
                   if c[0] in ("right", "left") and abs(c[1] - 90) < 1)
    if turns_90 >= 4:
        pts += 1
        detail.append(f"  ✓ [1/1] Virage 90° détecté {turns_90} fois")
    else:
        detail.append(f"  ✗ [0/1] Virage 90° manquant ({turns_90} détecté)")

    # [1] carré fermé
    dist = math.hypot(spy._x, spy._y)
    if dist < 3:
        pts += 1
        detail.append(f"  ✓ [1/1] Carré fermé (retour au départ, dist={dist:.2f})")
    elif ok:
        detail.append(f"  ✗ [0/1] Carré non fermé (dist={dist:.2f})")

    if not ok:
        detail.append(f"  ⚠ Erreur d'exécution : {err}")

    return pts, 6, detail


def evaluer_ex2(code):
    """
    EX2 — Polygone régulier à N côtés  (8 pts)
    ─────────────────────────────────────────────
    L'élève doit demander N à l'utilisateur et dessiner le polygone.
    Critères :
      [2] Boucle for avec range(n) ou range(N)
      [1] Variable pour le nombre de côtés
      [2] Angle = 360/N utilisé
      [2] N segments de même longueur dessinés
      [1] Polygone fermé (±3px)
    """
    # On simule N=6 (hexagone) pour la correction
    code_test = code.replace("input(", "_fake_input(")
    spy = TurtleSpy()

    # Injecte input() simulé (N=6)
    full_code = "N = 6\nn = 6\n" + code_test.replace("int(input(", "int(_fake_input(")
    spy2 = TurtleSpy()
    namespace_extra = {"_fake_input": lambda *a: "6", "N": 6, "n": 6}

    ok, err = run_code(
        "N = 6\nn = 6\n" + code.replace("input(", "lambda *a:'6'  #"),
        spy2
    )
    # Réessai propre
    spy3 = TurtleSpy()
    ok, err = run_code(code, spy3)  # avec input vide → N = ""

    spy = TurtleSpy()
    # Patch input pour renvoyer 6
    modified = code
    ok, err = run_code_with_input(modified, spy, "6")

    detail = []
    pts = 0

    # [2] boucle for
    if spy.has_for(code):
        pts += 2
        detail.append("  ✓ [2/2] Boucle for présente")
    else:
        detail.append("  ✗ [0/2] Pas de boucle for")

    # [1] variable pour N
    has_var = any(v in code for v in ["n =", "N =", "n=", "N=", "cotes", "nb_cotes",
                                       "nombre", "sides", "nbcotes"])
    if has_var or "input" in code:
        pts += 1
        detail.append("  ✓ [1/1] Variable N ou saisie utilisateur")
    else:
        detail.append("  ✗ [0/1] Pas de variable pour le nombre de côtés")

    # [2] angle 360/N
    has_angle_expr = "360" in code and ("/" in code or "//" in code)
    if has_angle_expr:
        pts += 2
        detail.append("  ✓ [2/2] Angle calculé comme 360/N")
    elif "60" in code or "90" in code:
        pts += 1
        detail.append("  ~ [1/2] Angle fixe (pas calculé dynamiquement)")
    else:
        detail.append("  ✗ [0/2] Angle 360/N absent")

    # [2] segments de même longueur
    lengths = spy.segment_lengths()
    if len(lengths) >= 3:
        unique = set(round(l, 0) for l in lengths)
        if len(unique) == 1:
            pts += 2
            detail.append(f"  ✓ [2/2] {len(lengths)} segments égaux de {lengths[0]:.0f}px")
        else:
            pts += 1
            detail.append(f"  ~ [1/2] Segments inégaux : {unique}")
    else:
        detail.append(f"  ✗ [0/2] Moins de 3 segments ({len(lengths)} détectés)")

    # [1] fermé
    dist = math.hypot(spy._x, spy._y)
    if dist < 5:
        pts += 1
        detail.append(f"  ✓ [1/1] Polygone fermé (dist={dist:.2f})")
    else:
        detail.append(f"  ✗ [0/1] Polygone non fermé (dist={dist:.2f})")

    if not ok:
        detail.append(f"  ⚠ Erreur d'exécution : {err}")

    return pts, 8, detail


def run_code_with_input(code_str, spy, input_value="6"):
    """Exécute le code en simulant input() → renvoie input_value."""
    namespace = _build_namespace(spy, input_fn=lambda *a: input_value)
    sys.modules["turtle"] = spy          # type: ignore
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(code_str, "<eleve>", "exec"), namespace)
        return True, buf.getvalue()
    except Exception as e:
        return False, str(e)
    finally:
        sys.modules.pop("turtle", None)


def evaluer_ex3(code):
    """
    EX3 — Spirale avec une boucle while  (8 pts)
    ──────────────────────────────────────────────
    Critères :
      [2] Boucle while présente
      [1] Condition de sortie (compteur ou longueur max)
      [2] Longueur croissante à chaque tour
      [2] Virage constant (angle fixe à chaque itération)
      [1] Au moins 8 segments dessinés
    """
    spy = TurtleSpy()
    ok, err = run_code(code, spy)

    detail = []
    pts = 0

    # [2] while
    if spy.has_while(code):
        pts += 2
        detail.append("  ✓ [2/2] Boucle while présente")
    else:
        detail.append("  ✗ [0/2] Pas de boucle while")

    # [1] condition de sortie
    has_condition = (
        "<" in code or ">" in code or "<=" in code or ">=" in code
    ) and "while" in code
    if has_condition:
        pts += 1
        detail.append("  ✓ [1/1] Condition de sortie détectée")
    else:
        detail.append("  ✗ [0/1] Condition de sortie manquante")

    # [2] longueurs croissantes
    lengths = spy.segment_lengths()
    if len(lengths) >= 3:
        is_growing = all(lengths[i] <= lengths[i+1] + 0.5
                         for i in range(len(lengths)-1))
        if is_growing and max(lengths) > min(lengths):
            pts += 2
            detail.append(f"  ✓ [2/2] Longueurs croissantes ({min(lengths):.1f}→{max(lengths):.1f})")
        else:
            pts += 1
            detail.append(f"  ~ [1/2] Longueurs non uniformément croissantes")
    else:
        detail.append(f"  ✗ [0/2] Pas assez de segments ({len(lengths)})")

    # [2] virage constant
    turns = [c[1] for c in spy._calls if c[0] in ("right", "left")]
    if turns:
        unique_turns = set(round(t, 0) for t in turns)
        if len(unique_turns) == 1:
            pts += 2
            detail.append(f"  ✓ [2/2] Angle constant de {turns[0]:.0f}°")
        else:
            pts += 1
            detail.append(f"  ~ [1/2] Angles variables : {unique_turns}")
    else:
        detail.append("  ✗ [0/2] Aucun virage détecté")

    # [1] au moins 8 segments
    if len(lengths) >= 8:
        pts += 1
        detail.append(f"  ✓ [1/1] {len(lengths)} segments dessinés (≥8)")
    else:
        detail.append(f"  ✗ [0/1] Seulement {len(lengths)} segments (<8)")

    if not ok:
        detail.append(f"  ⚠ Erreur d'exécution : {err}")

    return pts, 8, detail


def evaluer_ex4(code):
    """
    EX4 — Répétition de formes (plusieurs carrés/triangles)  (8 pts)
    ─────────────────────────────────────────────────────────────────
    Critères :
      [2] Double boucle (boucle imbriquée ou 2 boucles)
      [2] Au moins 3 formes identiques dessinées
      [1] Déplacement entre les formes (penup/pendown ou goto)
      [2] Formes régulières (segments égaux par forme)
      [1] Code structuré (variable ou fonction pour la forme)
    """
    spy = TurtleSpy()
    ok, err = run_code(code, spy)

    detail = []
    pts = 0

    # [2] double boucle ou 2 boucles
    nb_for = code.count("for ")
    nb_while = code.count("while ")
    total_loops = nb_for + nb_while
    if total_loops >= 2:
        pts += 2
        detail.append(f"  ✓ [2/2] {total_loops} boucle(s) détectée(s)")
    elif total_loops == 1:
        pts += 1
        detail.append(f"  ~ [1/2] 1 seule boucle (double boucle attendue)")
    else:
        detail.append("  ✗ [0/2] Aucune boucle")

    # [2] au moins 3 formes (heuristique : penup appelé ≥2 fois)
    nb_penup = sum(1 for c in spy._calls if c[0] == "penup")
    # Ou segmentation par position
    if nb_penup >= 2:
        pts += 2
        detail.append(f"  ✓ [2/2] {nb_penup} levées de crayon → formes séparées")
    elif len(spy._segments) >= 9:   # au moins 3 formes de 3 côtés
        pts += 2
        detail.append(f"  ✓ [2/2] {len(spy._segments)} segments → 3+ formes probables")
    elif nb_penup == 1:
        pts += 1
        detail.append(f"  ~ [1/2] 1 levée de crayon seulement")
    else:
        detail.append(f"  ✗ [0/2] Pas de séparation entre formes")

    # [1] déplacement entre formes
    has_move = (
        "penup" in code or "pu(" in code or
        "goto" in code or "setpos" in code or
        "forward" in code.lower()
    )
    if nb_penup >= 1:
        pts += 1
        detail.append("  ✓ [1/1] Déplacement entre formes détecté")
    else:
        detail.append("  ✗ [0/1] Pas de déplacement entre formes")

    # [2] formes régulières
    lengths = spy.segment_lengths()
    if lengths:
        unique = set(round(l, 0) for l in lengths)
        if len(unique) <= 2:   # max 2 longueurs différentes (forme + déplacement)
            pts += 2
            detail.append(f"  ✓ [2/2] Longueurs régulières : {unique}")
        else:
            pts += 1
            detail.append(f"  ~ [1/2] Longueurs variées : {unique}")
    else:
        detail.append("  ✗ [0/2] Aucun segment détecté")

    # [1] variable ou fonction
    has_structure = (
        "def " in code or
        any(v in code for v in ["taille", "cote", "longueur", "size", "l =",
                                  "n =", "N =", "nb"])
    )
    if has_structure:
        pts += 1
        detail.append("  ✓ [1/1] Variable ou fonction utilisée")
    else:
        detail.append("  ✗ [0/1] Pas de variable/fonction pour la taille")

    if not ok:
        detail.append(f"  ⚠ Erreur d'exécution : {err}")

    return pts, 8, detail


def evaluer_ex5(code):
    """
    EX5 — Figure combinée (spirale carrée ou étoile)  (10 pts)
    ────────────────────────────────────────────────────────────
    Critères :
      [2] Boucle principale correcte
      [2] Variation progressive (longueur ou angle)
      [2] Au moins 20 segments dessinés
      [2] Retour partiel au centre (effet spirale) ou symétrie
      [1] Couleurs ou style (color/pencolor utilisé)
      [1] Code lisible (commentaires ou nommage)
    """
    spy = TurtleSpy()
    ok, err = run_code(code, spy)

    detail = []
    pts = 0

    # [2] boucle principale
    if spy.has_for(code) or spy.has_while(code):
        pts += 2
        detail.append("  ✓ [2/2] Boucle principale présente")
    else:
        detail.append("  ✗ [0/2] Aucune boucle")

    # [2] variation progressive
    lengths = spy.segment_lengths()
    if len(lengths) >= 5:
        diffs = [lengths[i+1] - lengths[i] for i in range(len(lengths)-1)]
        same_sign = all(d >= -0.5 for d in diffs) or all(d <= 0.5 for d in diffs)
        if same_sign and max(lengths) - min(lengths) > 5:
            pts += 2
            detail.append(f"  ✓ [2/2] Progression régulière ({min(lengths):.0f}→{max(lengths):.0f})")
        elif max(lengths) - min(lengths) > 2:
            pts += 1
            detail.append(f"  ~ [1/2] Légère variation des longueurs")
        else:
            detail.append("  ✗ [0/2] Pas de variation progressive")
    else:
        detail.append(f"  ✗ [0/2] Pas assez de segments ({len(lengths)})")

    # [2] au moins 20 segments
    if len(lengths) >= 20:
        pts += 2
        detail.append(f"  ✓ [2/2] {len(lengths)} segments (≥20)")
    elif len(lengths) >= 10:
        pts += 1
        detail.append(f"  ~ [1/2] {len(lengths)} segments (entre 10 et 19)")
    else:
        detail.append(f"  ✗ [0/2] {len(lengths)} segments (<10)")

    # [2] effet spirale (éloignement depuis l'origine)
    if len(spy._segments) >= 5:
        dists = [math.hypot(s[2], s[3]) for s in spy._segments]
        if max(dists) > 30:
            pts += 2
            detail.append(f"  ✓ [2/2] Effet spirale (dist max={max(dists):.0f}px)")
        else:
            pts += 1
            detail.append(f"  ~ [1/2] Faible éloignement (dist max={max(dists):.0f}px)")
    else:
        detail.append("  ✗ [0/2] Figure trop petite")

    # [1] couleurs
    has_color = any(c[0] in ("color", "pencolor", "fillcolor") for c in spy._calls)
    if has_color or "color" in code:
        pts += 1
        detail.append("  ✓ [1/1] Couleur utilisée")
    else:
        detail.append("  ✗ [0/1] Pas de couleur")

    # [1] commentaires ou nommage
    has_comments = "#" in code
    has_good_names = any(v in code for v in [
        "longueur", "taille", "angle", "tour", "cote", "nb", "step", "size"
    ])
    if has_comments or has_good_names:
        pts += 1
        detail.append("  ✓ [1/1] Commentaires ou nommage lisible")
    else:
        detail.append("  ✗ [0/1] Pas de commentaires ni nommage clair")

    if not ok:
        detail.append(f"  ⚠ Erreur d'exécution : {err}")

    return pts, 10, detail


# ══════════════════════════════════════════════════════════
#  RAPPORT FINAL
# ══════════════════════════════════════════════════════════

def rapport(nom_eleve, resultats):
    """Affiche le rapport complet et retourne la note finale."""
    total_pts = sum(r[0] for r in resultats)
    total_max = sum(r[1] for r in resultats)
    note = note_genevois(total_pts, total_max)

    lignes = []
    lignes.append("=" * 62)
    lignes.append(f"  RAPPORT D'ÉVALUATION — {nom_eleve.upper()}")
    lignes.append(f"  Turtle Python + Boucles | Barème Genevois")
    lignes.append("=" * 62)

    titres = [
        "EX1 — Carré avec for",
        "EX2 — Polygone régulier",
        "EX3 — Spirale avec while",
        "EX4 — Répétition de formes",
        "EX5 — Figure combinée",
    ]

    for i, (pts, max_pts, detail) in enumerate(resultats):
        note_ex = note_genevois(pts, max_pts)
        lignes.append("")
        lignes.append(f"  {titres[i]}")
        lignes.append(f"  Points : {pts}/{max_pts}  →  Note partielle : {note_ex}/6")
        lignes.append("  " + "─" * 50)
        for ligne in detail:
            lignes.append("  " + ligne)

    lignes.append("")
    lignes.append("=" * 62)
    lignes.append(f"  TOTAL : {total_pts}/{total_max} points")
    lignes.append(f"  NOTE FINALE : {note} / 6   —  {mention(note)}")
    lignes.append("=" * 62)
    lignes.append("")

    # Grille barème genevois
    lignes.append("  GRILLE BARÈME GENEVOIS (rappel) :")
    lignes.append("  ─────────────────────────────────")
    grille = [
        (6.0, "100%", "Excellent"),
        (5.5, "90%",  "Très bien"),
        (5.0, "80%",  "Bien"),
        (4.5, "70%",  "Assez bien"),
        (4.0, "60%",  "Suffisant"),
        (3.5, "50%",  "Insuffisant"),
        (3.0, "40%",  "Insuffisant"),
        (2.0, "20%",  "Faible"),
        (1.0, "0%",   "Très faible"),
    ]
    for n, pct, m in grille:
        marker = " ◀" if abs(n - note) < 0.3 else ""
        lignes.append(f"  {n:.1f}/6  ({pct:>4})  {m}{marker}")
    lignes.append("")

    print("\n".join(lignes))
    return note


# ══════════════════════════════════════════════════════════
#  ▼▼▼  ZONE ÉLÈVE — COLLE LE CODE ICI  ▼▼▼
# ══════════════════════════════════════════════════════════

# ─── Informations élève ───────────────────────────────────
NOM_ELEVE = "Élève Test"

# ─── EX1 : Carré avec une boucle for ─────────────────────
CODE_EX1 = """
import turtle

for i in range(4):
    turtle.forward(100)
    turtle.right(90)

turtle.done()
"""

# ─── EX2 : Polygone régulier à N côtés ───────────────────
CODE_EX2 = """
import turtle

n = int(input("Nombre de côtés : "))
angle = 360 / n

for i in range(n):
    turtle.forward(100)
    turtle.right(angle)

turtle.done()
"""

# ─── EX3 : Spirale avec une boucle while ─────────────────
CODE_EX3 = """
import turtle

longueur = 5
while longueur < 200:
    turtle.forward(longueur)
    turtle.right(91)
    longueur += 5

turtle.done()
"""

# ─── EX4 : Répétition de 4 carrés ───────────────────────
CODE_EX4 = """
import turtle

taille = 80

for forme in range(4):
    for cote in range(4):
        turtle.forward(taille)
        turtle.right(90)
    turtle.penup()
    turtle.forward(taille + 10)
    turtle.pendown()

turtle.done()
"""

# ─── EX5 : Spirale carrée colorée ────────────────────────
CODE_EX5 = """
import turtle

couleurs = ["red", "blue", "green", "orange"]
longueur = 5

# Dessine une spirale carrée
for i in range(60):
    turtle.color(couleurs[i % 4])
    turtle.forward(longueur)
    turtle.right(91)
    longueur += 3

turtle.hideturtle()
turtle.done()
"""

# ══════════════════════════════════════════════════════════
#  LANCEMENT DE LA CORRECTION
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nCorrection en cours...\n")

    resultats = [
        evaluer_ex1(CODE_EX1),
        evaluer_ex2(CODE_EX2),
        evaluer_ex3(CODE_EX3),
        evaluer_ex4(CODE_EX4),
        evaluer_ex5(CODE_EX5),
    ]

    rapport(NOM_ELEVE, resultats)

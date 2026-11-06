"""Gemeinsame Fixtures: vier Mini-Instanzen (Kapazität 10), eine je Ausgang, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b).

Handrechnung (FFD = größte zuerst, jedes Paket in den ersten Container mit genug Platz):

* mini_l1 (5, 5, 4, 3, 3), Summe 20: L1 = 2. FFD: 5 + 5 füllt C1; 4 -> C2; 3 -> C2 (7); 3 -> C2 (10): 2 Container = L1. Ausgang 'l1'.
* mini_l2 (6, 6, 6, 2), Summe 20: L1 = 2. L2 bei alpha = 0: J2 = {6, 6, 6} (drei Container, freier Platz 4 + 4 + 4 = 12), J3 = {2} mit Summe 2 <= 12, also
  0 zusätzliche: L(0) = 3. FFD: drei Container für die Sechsen, die 2 kommt in C1: 3 Container = L2 > L1. Ausgang 'l2'.
* mini_offen_optimal (4, 4, 4, 4, 3), Summe 19: L1 = 2, L2 = 2 (kein Paket über 5). FFD: 4 + 4 in C1 (8); die dritte 4 in C2; die vierte 4 in C2 (8); die 3 passt weder in C1 (11)
  noch in C2 (11): C3. FFD = 3. Optimum 3: zwei Container bräuchten eine Teilmenge mit Summe 9 oder 10 (der Rest muss <= 10 sein), die Summen sind aber 3, 4, 7, 8, 11, 12, 15, 16, 19.
  Ausgang 'offen_optimal'.
* mini_offen_nicht_optimal (4, 4, 3, 3, 3, 3), Summe 20: L1 = 2, L2 = 2. FFD: 4 + 4 in C1 (8); die erste 3 in C2; die zweite 3 in C2 (6); die dritte 3 in C2 (9); die vierte 3 passt
  weder in C1 (11) noch in C2 (12): C3. FFD = 3. Optimum 2: {4, 3, 3} und {4, 3, 3}. Ausgang 'offen_nicht_optimal', die Schranke L2 ist scharf.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sbw_scenario import Instance  # noqa: E402


@pytest.fixture
def mini_l1():
    return Instance((5, 5, 4, 3, 3), 10)


@pytest.fixture
def mini_l2():
    return Instance((6, 6, 6, 2), 10)


@pytest.fixture
def mini_offen_optimal():
    return Instance((4, 4, 4, 4, 3), 10)


@pytest.fixture
def mini_offen_nicht_optimal():
    return Instance((4, 4, 3, 3, 3, 3), 10)

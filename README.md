# Marketplace - Cosmin-Răzvan VANCEA - 333CA

Organizare
-

Tema este împărțită pe 3 module: producer, consumer și marketplace.

Modulele producer și consumer sunt simple:
- **Producer** rezervă un loc în marketplace, primește o listă de produse și le
  *publică* la infinit în locul rezervat. Dacă un produs nu poate fi adăugat
  (coada este plină), atunci acesta se va aștepta un timp și se va reîncerca
  operațiunea (polling).
- **Consumer** rezervă un coș de cumpărături în marketplace și primește o listă de
  produse pe care trebuie să le adauge în coș sau să le scoată din coș. La fel ca
  mai sus, dacă un produs nu poate fi adăugat în coș (produsul nu există) sau
  nu poate fi scos din coș (coada de unde a fost luat este plină), atunci se va
  aștepta un timp și se va reîncerca operațiunea (polling).

În modulul **marketplace** au loc toate operațiunile importante. La înregistrarea
unui nou producător, i se alocă un `Lock` și un contor care ține evidența
numărului de produse publicate de fiecare producător. Lock-ul permite modificarea
atomică a acestui contor.

- Atât pentru simplitate, cât și ca o optimizare, marketplace-ul are un singur
  buffer (`_store`) unde ține produsele publicate, plus un dicționar
  (`_product_to_producer`) care face corespondența dintre fiecare produs publicat
  și producătorul acestuia. (necesar la adăgarea sau ștergerea de produse din
  coș - la adăguare trebuie scăzut contorul; la ștergere trebuie crescut)
- Consider că este mai optim deoarece la adăguarea unui produs în coș pot profita
  de faptul că operațiunea de `remove` este atomică[1] în Python, iar astfel scap
  de un loc unde ar fi trebuit sa folosesc Lock pentru a sincroniza căutarea și
  ștergerea din n cozi (n = numărul de producători înregistrați).
- Tocmai din acest motiv consider că implementarea este una eficientă.

*[1] Atomicitatea operației `remove` se poate observa și examinând bytecode-ul
generat întrucât ștergerea se face într-o singura instrucțiune bytecode (`CALL_METHOD`)*
```commandline
>>> import dis
>>> def remove(list, elem):
...     list.remove(elem)
...
>>> dis.dis(remove)
  2           0 LOAD_FAST                0 (list)
              2 LOAD_METHOD              0 (remove)
              4 LOAD_FAST                1 (elem)
              6 CALL_METHOD              1
              8 POP_TOP
             10 LOAD_CONST               0 (None)
             12 RETURN_VALUE
```

Restul informațiilor legate de implementare sunt destul de evidente și cred că
se înteleg ușor din cod și comentarii.

Implementare
-

Întregul enunț a fost implementat. Ca lipsuri (deși nu le pot numi neapărat așa)
consider că tema ar fi putut folosi wait & notify în loc de polling la adăugarea
și scoaterea de produse, iar astfel am fi avut ocazia de a experimenta cu mai
multe metode de sincronizare.

Nu am întâmpinat dificultăți la implementare, au existat câteva nelămuriri în
legătura cu cerința, dar au fost rezolvate rapid pe forum.

Resurse utilizate
-

- [How to verify if one step is Atomic in Python](https://stackoverflow.com/questions/17990334/how-to-verify-if-one-step-is-atomic-operation-in-python-or-now)
- [List remove is thread safe](https://blog.finxter.com/python-list-remove/)
- [Thread safe operations](https://web.archive.org/web/20201108091210/http://effbot.org/pyfaq/what-kinds-of-global-value-mutation-are-thread-safe.htm)
- [Labs](https://ocw.cs.pub.ro/courses/asc)

Git
-

Repository privat pe [GitHub](https://github.com/cvancea/marketplace/).
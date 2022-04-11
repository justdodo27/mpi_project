# Lotniskowce

S samolotów oraz L lotniskowców każdy z różną liczbą Ni stanowisk postojowych; S > suma(Ni). Na każdym lotniskowcu znajduje się tylko jeden pas startowy, z którego korzystają zarówno samoloty startujące jak i lądujące. Pas może być używany tylko w trybie wyłącznym. Samolot ubiega się o dowolny spośród aktualnie wolnych pasów startowych. Napisać program dla procesu samolotu. Pasy i miejsca postojowe należy traktować jako zasoby. 

## Algorytm
Tagi:
- Rezerwacja
- Lądowanie
- Start

Zmienne:
- S - liczba samolotów
- L - liczba lotniskowców
- Ni - liczba stanowisk na i-tym lotniskowcu
- k - rozmiar samolotou (k <= MIN(Ni) *warunek zapewni możliwość wylądowania na kązdym lotniskowcu*)
- t - zegar procesu

**Działanie algorytmu**:
- Na poczatku programu, każdy z procesów ustawia czas procesu na 0.
- Mniejszy czas to wyższy priorytet.
- W przypadku takich samych czasów decyduje kolejność ID procesów.
- Czasy procesów zmieniają się następująco:
    - Przy wysłaniu wiadomości zwiększa czas procesu o 1
    - Przy odebraniu wiadomości ustawia swój czas procesu na MAX(czas lokalny, czas nadesłany) + 1
- Procesy przechowują dwie lokalne listy, w których przechowują ID procesów, którym odmówiły odpowiednio stanowiska lub pasu startowego.
- Gdy samolot opuści lotniskowiec odpowiada do wszystkich samolotów z listy.
- Jeżeli samolot odpowie innemu samolotowi *pozytywnie*, który wcześniej znajdował się na jego liście usuwa go z jego listy.
- Proces może wykonać operację dopiero po uzyskaniu odpowiedzi od innych procesów.


**Rezerwacja stanowiska**:
- Gdy samolot chce zarezerwować stanowisko na lotniskowcu:
    - Rozsyła żądanie do wszystkich samolotów z tagiem rezerwacji oraz swoim priorytetem.
    - Gdy otrzyma Ni-suma(k) >= k, gdzie suma(k) to wszystkie odpowiedzi, to rezerwuje stanowisko postojowe.
- Jeżeli samolot otrzyma prośbę o rezerwacje, na lotniskowiec o który się ubiega:
    - mając niższy priorytet od samolotu żądającego - odsyła 0
    - mając wyższy priorytet od samolotu żądającego - odsyła k i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o rezerwację na lotniskowiec, na którym się znajduje lub ma rezerwację, odsyła k i zapisuje go do listy
- Jeżeli samolot otrzyma prośbę o rezerwację na lotniskowiec, o który się nie ubiega, odsyła 0

**Lądowanie na lotniskowcu**:
- Gdy samolot chce lądować na lotniskowcu:
    - Jeżeli samolot otrzymał rezerwacje rozsyła żądanie do wszystkich samolotów z tagiem lądowania oraz swoim priorytetem.
    - Gdy otrzyma S-1 zgód, zajmuje sekcje krytyczną i ląduje.
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowiec na który chce wylądować:
    - mając niższy priorytet od samolotu żądającego - odsyła True
    - mając wyższy priorytet od samolotu żądającego - odsyła False i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu o który się nie ubiega odsyła True
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu na którym się znajduje, odsyła True
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu na którym chce startować odsyła False i zapisuje samolot do swojej listy
- Jeżeli samolot wyląduje zwalnia pas startowy i rozsyła odpowiedzi do procesów z listy.

**Startowanie z lotniskowca**:
- Gdy samolot chce startować z lotniskowca:
    - Rozsyła żądanie do wszystkich samolotów z tagiem startowania oraz swoim priorytetem.
    - Gdy otrzyma S-1 zgód, zajmuje sekcje krytyczną i startuje.
- Jęzeli samolot otrzyma prośbę o start, na lotniskowcu na którym chcę startować:
    - mając niższy priorytet od smaolotu żądającego - odsyła True
    - mając wyższy priorytet od samolotu żądającego - odsyła False i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o start, na lotniskowcu na którym się nie znajduje, ani o który się nie ubiega, odsyła True
- Jeżeli samolot otrzyma prośbę o start, na lotniskowcu na który chcę wylądować odsyła True
- Jeżeli samolot wystartuje zwalnia pas startowy i rozsyła odpowiedzi do procesów z listy.

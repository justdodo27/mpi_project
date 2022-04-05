# Lotniskowce

S samolotów oraz L lotniskowców każdy z różną liczbą Ni stanowisk postojowych; S > suma(Ni). Na każdym lotniskowcu znajduje się tylko jeden pas startowy, z którego korzystają zarówno samoloty startujące jak i lądujące. Pas może być używany tylko w trybie wyłącznym. Samolot ubiega się o dowolny spośród aktualnie wolnych pasów startowych. Napisać program dla procesu samolotu. Pasy i miejsca postojowe należy traktować jako zasoby. 

## Algorytm
Tagi:
- Rezerwacja
- Lądowanie
- Start

## TODO
- jak pyta o rezerwacje nie dostaje odmowy zgody tlyko liczbe zajetych przez nie miejsc miejsc
- priorytety nie zegar systemowy cos innego

**Działanie algorytmu**:
- Na poczatku programu, każdy z procesów pobiera czas z zegara.
- Mniejszy czas to wyższy priorytet.
- W przypadku takich samych czasów decyduje kolejność ID procesów.
- Podczas każdej nowej czynności proces pobiera nowy czas
- Procesy przechowują dwie lokalne listy, w których przechowują ID procesów, którym odmówiły odpowiednio stanowiska lub pasu startowego.
- Gdy samolot opuści lotniskowiec odpowiada zgodą do wszystkich samolotów z listy zgodą.
- Jeżeli samolot odpowie innemu samolotowi zgodą, który wcześniej znajdował się na jego liście usuwa go z jego listy.


**Rezerwacja stanowiska**:
- Gdy samolot chce zarezerwować stanowisko na lotniskowcu:
    - Rozsyła żądanie do wszystkich samolotów z tagiem rezerwacji oraz swoim priorytetem.
    - Gdy otrzyma minimum S-Ni zgód, rezerwuje stanowisko postojowe i zmniejsza się liczba stanowisk.
- Jeżeli samolot otrzyma prośbę o rezerwacje, na lotniskowiec o który się ubiega:
    - mając niższy priorytet od samolotu żądającego - odpowiada zgoda
    - mając wyższy priorytet od samolotu żądającego - odpowiada odmowa i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o rezerwację na lotniskowiec, na którym się znajduje lub ma rezerwację, odpowiada odmową i zapisuje go do listy
- Jeżeli samolot otrzyma prośbę o rezerwację na lotniskowiec, o który się nie ubiega, odpowiada zgodą

**Lądowanie na lotniskowcu**:
- Gdy samolot chce lądować na lotniskowcu:
    - Jeżeli samolot otrzymał rezerwacje rozsyła żądanie do wszystkich samolotów z tagiem lądowania oraz swoim priorytetem.
    - Gdy otrzyma minimum S-1 zgód, zajmuje sekcje krytyczną i ląduje.
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowiec na który chce wylądować:
    - mając niższy priorytet od samolotu żądającego - odpowiada zgoda
    - mając wyższy priorytet od samolotu żądającego - odpowiada odmowa i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu o który się nie ubiega odpowiada zgodą
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu na którym się znajduje, odpowiada zgodą
- Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu na którym chce startować odpowiada odmową i zapisuje samolot do swojej listy
- Jeżeli samolot wyląduje zwalnia pas startowy i rozsyła zgody do procesów z listy.

**Startowanie z lotniskowca**:
- Gdy samolot chce startować z lotniskowca:
    - Rozsyła żądanie do wszystkich samolotów z tagiem startowania oraz swoim priorytetem.
    - Gdy otrzyma minimum S-1 zgód, zajmuje sekcje krytyczną i startuje.
- Jęzeli samolot otrzyma prośbę o start, na lotniskowcu na którym chcę startować:
    - mając niższy priorytet od smaolotu żądającego - odpowiada zgoda
    - mając wyższy priorytet od samolotu żądającego - odpowiada odmowa i zapisuje go do swojej listy
- Jeżeli samolot otrzyma prośbę o start, na lotniskowcu na którym się nie znajduje, ani o który się nie ubiega, odpowiada zgodą
- Jeżeli samolot otrzyma prośbę o start, na lotniskowcu na który chcę wylądować odpowiada zgodą
- Jeżeli samolot wystartuje zwalnia pas startowt i rozsyła zgody do procesów z listy.

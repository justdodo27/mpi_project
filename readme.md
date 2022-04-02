# Lotniskowce

S samolotów oraz L lotniskowców każdy z różną liczbą Ni stanowisk postojowych; S > suma(Ni). Na każdym lotniskowcu znajduje się tylko jeden pas startowy, z którego korzystają zarówno samoloty startujące jak i lądujące. Pas może być używany tylko w trybie wyłącznym. Samolot ubiega się o dowolny spośród aktualnie wolnych pasów startowych. Napisać program dla procesu samolotu. Pasy i miejsca postojowe należy traktować jako zasoby. 

## Algorytm
- Na poczatku programu, każdy z procesów otrzymuje priorytet na podstawie swojego ID.
- Gdy samolot chce lądować na lotniskowcu:
    - Rozsyła żądanie do wszystkich samolotów z tagiem lądowania oraz swoim priorytetem.
    - Gdy otrzyma minimum S-Ni zgód, zajmuje sekcje krytyczną i ląduje.
    - Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowiec o który się ubiega:
        - mając niższy priorytet od smaolotu żądającego - odpowiada zgoda
        - mając wyższy priorytet od samolotu żądającego - odpowiada odmowa i zapisuje go do swojej listy
    - Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu o który się nie ubiega zawsze odpowiada zgoda
    - Jeżeli samolot otrzyma prośbę o lądowanie, na lotniskowcu na którym się znajduje zawsze odpowiada odmową i zapisuje samolot do swojej listy
- Gdy samolot chce startować z lotniskowca:
    - Rozsyła żądanie do wszystkich samolotów z tagiem startowania oraz swoim priorytetem.
    - ...
- Gdy samolot opuści lotniskowiec odpowiada zgodą do wszystkich samolotów z listy zgodą.
- Jeżeli samolot odpowie innemu samolotowi zgodą, który wcześniej znajdował się na jego liście usuwa go z jego listy.
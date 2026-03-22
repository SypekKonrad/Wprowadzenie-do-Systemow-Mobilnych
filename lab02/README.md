Zaimplementowano symulator stacji bazowej obsługujący zgłoszenia przychodzące zgodnie z procesem Poissona (odstępy między zgłoszeniami mają rozkład wykładniczy). Długości rozmów generowane są z rozkładu Gaussa z uwzględnieniem minimalnej i maksymalnej długości rozmowy.

System składa się z określonej liczby kanałów oraz kolejki o zadanej długości. W każdym kroku symulacji (1 sekunda) nowe zgłoszenia są przydzielane do wolnych kanałów, kierowane do kolejki lub odrzucane w przypadku jej przepełnienia.


### Uruchomienie

```aiignore
python3 -m venv venv
source venv/bin/activate
pip install -r requirements
python3 zadanie.py
```
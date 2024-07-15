# Gra w Szachy w Pythonie

## Przegląd
Ten projekt to gra w szachy napisana w Pythonie z graficznym interfejsem użytkownika (GUI) stworzonym za pomocą PyQt5. Gra pozwala graczom grać w szachy przeciwko sobie lokalnie. Obsługuje różne ustawienia czasu oraz loguje zdarzenia gry dla lepszego śledzenia i debugowania.

## Funkcje
- **Graficzny Interfejs Użytkownika:** Intuicyjny i interaktywny GUI do gry w szachy.
- **Ruchy Figur:** Obsługa standardowych ruchów szachowych z wykrywaniem kolizji.
- **Gra na Zmianę:** Wymusza naprzemienne tury między graczami.
- **Ustawienia Czasu:** Zawiera tryb Blitz i tryb inkrementalny dla gier z limitem czasu.
- **Logowanie Zdarzeń:** Loguje zdarzenia gry i działania dla śledzenia i debugowania.

## Wymagania
- Python 3.x
- PyQt5
- SQLite3

## Instalacja
1. Sklonuj repozytorium:
    ```sh
    git https://github.com/Assassin-PL/ProjektSzachy.git
    ```
2. Przejdź do katalogu projektu:
    ```sh
    cd chess-game
    ```
3. Zainstaluj wymagane pakiety:
    ```sh
    pip install pyqt5
    ```

## Użycie
1. Uruchom główny skrypt, aby rozpocząć grę:
    ```sh
    python main.py
    ```
2. Otworzy się okno gry, w którym możesz grać w szachy.

## Opis Plików
- `main.py`: Punkt wejścia aplikacji. Inicjalizuje GUI i uruchamia pętlę zdarzeń.
- `interface.py`: Zawiera główne komponenty GUI i logikę renderowania szachownicy oraz figur.
- `interfaceTest.py`: Definiuje klasę `ChessView` używaną w GUI.
- `logi.py`: Obsługuje logowanie zdarzeń gry i przekierowuje stdout do okna logów.
- `logika.py`: Zawiera główną logikę ruchów szachowych, wykrywania kolizji oraz zasad gry.
- `pionek.py`: Definiuje klasę `ChessPiece`, reprezentującą poszczególne figury szachowe i ich zachowanie.
- `read_db.py`: Zawiera funkcje do odczytu historii gry z bazy danych SQLite.
- `stale.py`: Zawiera stałe używane w całej aplikacji.
- `TCPserwer.py`: Implementuje serwer TCP do obsługi komunikacji sieciowej (nie w pełni zintegrowany).
- `klient.py`: Implementuje logikę po stronie klienta do łączenia się z serwerem TCP (nie w pełni zintegrowany).

## Ustawienia Gry
- Gra obsługuje różne ustawienia czasu:
  - **Czas Blitz:** 5 minut na gracza.
  - **Czas Inkrementu:** Dodaje dodatkowy czas po każdym ruchu.
- Te ustawienia można skonfigurować w klasie `ChessScene` w pliku `interface.py`.

## Logowanie
- Gra loguje zdarzenia i działania do oddzielnego okna, aby ułatwić śledzenie i debugowanie.
- Logi są zarządzane przez klasy `LogWindow` i `LogWorker` w pliku `logi.py`.

## Wkład w Projekt
Wkłady są mile widziane! Proszę forkować repozytorium i przesyłać pull requesty.

## Licencja
Ten projekt jest licencjonowany na podstawie licencji MIT. Zobacz plik [LICENSE](LICENSE) po więcej szczegółów.

---

### Przykładowe Użycie
Aby rozpocząć grę z domyślnymi ustawieniami, po prostu uruchom `main.py`. Przed rozpoczęciem gry możesz dostosować ustawienia w pliku `interface.py`.

```sh
python main.py

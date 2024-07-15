import sys
import asyncio
import concurrent.futures

from PyQt5.QtWidgets import QApplication

from interfaceTest import ChessView

async def example_async_function():
    await asyncio.sleep(10)  # Symulacja operacji asynchronicznej - oczekiwanie przez 1 sekundę

async def run_qt_event_loop(app):
    await asyncio.get_event_loop().run_in_executor(None, sys.exit(app.exec_()))

async def main():
    app = QApplication(sys.argv)

    # Tworzymy instancję widoku szachowego
    view = ChessView()
    view.show()

    # Uruchamiamy pętlę zdarzeń PyQt w tle
    # await asyncio.get_event_loop().run_in_executor(None, app.exec_)
    await asyncio.gather(
        example_async_function,
        run_qt_event_loop(app)
        # Tutaj możesz dodać inne funkcje asynchroniczne do wykonania równolegle
    )
    # await asyncio.get_event_loop().run_in_executor(None, sys.exit(app.exec_()))
    # Tutaj czekamy na zakończenie start_client przed zakończeniem main()

if __name__ == "__main__":
    # Inicjalizujemy aplikację PyQt
    app = QApplication(sys.argv)
    # loop = asyncio.get_running_loop()

     # Tworzymy instancję widoku szachowego

    view = ChessView()
    view.show()

    # Uruchamiamy aplikację
    sys.exit(app.exec_())
    # asyncio.run(main())

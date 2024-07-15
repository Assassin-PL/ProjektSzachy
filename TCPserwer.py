import asyncio
import socket


class TCPServer:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.clients = []  # Inicjalizacja listy klientów

    async def start_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        addr = server.sockets[0].getsockname()
        print(f'Serwując na {addr}')
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        self.clients.append((reader, writer))  # Dodajemy połączenie klienta do listy
        print(f'Połączono z {addr}')
        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    print(f'Klient {addr} zamknął połączenie')
                    break
                message = data.decode()
                print(f"Otrzymano wiadomość od {addr}: {message}")
                await self.broadcast_message(data, writer)
        except ConnectionResetError:
            print(f'Połączenie z {addr} zostało nieoczekiwanie zamknięte.')
        finally:
            print(f"Zamykanie połączenia z {addr}")
            self.clients.remove((reader, writer))  # Usuwamy połączenie klienta z listy
            writer.close()
            await writer.wait_closed()

    async def broadcast_message(self, message, sender_writer):
        for client_reader, client_writer in self.clients:
            if client_writer is not sender_writer:  # Nie wysyłamy wiadomości z powrotem do nadawcy
                try:
                    client_writer.write(message)
                    await client_writer.drain()
                except ConnectionResetError:
                    addr = client_writer.get_extra_info('peername')
                    print(f'Błąd wysyłania do {addr}; Połączenie zostało zresetowane.')
                    self.clients.remove((client_reader, client_writer))
                    client_writer.close()
                    await client_writer.wait_closed()
class TCPClient:
    def __init__(self, host='localhost', port=8888):
        self.host_name = host
        self.port = port
        self.client_socket = None

    def connect(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host_name, self.port))
        print(f"Połączono z serwerem na {self.host_name}:{self.port}")

    def send_message(self, message):
        self.client_socket.sendall(message.encode())
        print(f"Wysłano: {message}")

    def receive_message(self):
        data = self.client_socket.recv(1024)
        message = data.decode()
        print(f"Otrzymano: {message}")
        return message

    def close(self):
        print("Zamykanie połączenia")
        self.client_socket.close()


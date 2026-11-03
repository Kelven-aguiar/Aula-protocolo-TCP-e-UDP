"""Bloco 4: servidor UDP contínuo. Execute: python servidor-udp.py"""
import socket

HOST = "0.0.0.0"
PORTA = 5001  # Porta diferente da usada pelo servidor TCP.

# socket(): cria socket IPv4 e UDP (SOCK_DGRAM).
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind(): define a porta onde chegam os datagramas.
servidor.bind((HOST, PORTA))
print(f"Servidor UDP ativo na porta {PORTA}. Ctrl+C para encerrar.")

try:
    while True:
        # recvfrom(): recebe até 2048 bytes e identifica o remetente.
        dados, endereco = servidor.recvfrom(2048)
        texto = dados.decode("utf-8")

        # Cada mensagem possui um ID para confirmar a mensagem correta.
        identificador, separador, mensagem = texto.partition("|")
        if not separador:
            print("Datagrama fora do formato esperado:", texto)
            continue

        print(f"Recebido de {endereco}, ID {identificador}: {mensagem}")

        # sendto(): manda um datagrama para o IP e a porta do remetente.
        confirmacao = f"ACK:{identificador}"
        servidor.sendto(confirmacao.encode("utf-8"), endereco)

except KeyboardInterrupt:
    print("\nServidor encerrado por Ctrl+C.")
finally:
    servidor.close()

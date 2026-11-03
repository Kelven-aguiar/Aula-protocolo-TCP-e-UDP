"""Bloco 4: cliente UDP contínuo. Execute: python cliente-udp.py"""
import socket

# Troque pelo IPv4 do notebook que executa servidor-udp.py.
IP_SERVIDOR = "192.168.1.10"
PORTA = 5001

# socket(): cria socket IPv4 e UDP, sem estabelecer conexão TCP.
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente.settimeout(2)  # Não fica esperando uma resposta para sempre.

contador = 0

try:
    while True:
        mensagem = input("Você (/sair para fechar): ")
        if mensagem.lower() == "/sair":
            break
        if not mensagem:
            continue

        contador += 1
        identificador = str(contador)
        pacote = f"{identificador}|{mensagem}"

        # sendto(): envia um datagrama ao destino, sem connect().
        cliente.sendto(pacote.encode("utf-8"), (IP_SERVIDOR, PORTA))

        try:
            # recvfrom(): recebe resposta e endereço de origem.
            dados, endereco = cliente.recvfrom(2048)
            confirmacao = dados.decode("utf-8")
            if endereco == (IP_SERVIDOR, PORTA) and confirmacao == f"ACK:{identificador}":
                print("Servidor confirmou a mensagem!")
            else:
                print("Resposta inesperada:", confirmacao, "de", endereco)
        except socket.timeout:
            print("Tempo esgotado: não recebemos confirmação UDP.")

except (KeyboardInterrupt, EOFError):
    print("\nCliente encerrado.")
except OSError as erro:
    print("Erro de rede:", erro)
finally:
    cliente.close()

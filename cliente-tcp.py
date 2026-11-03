"""Bloco 4: cliente TCP com chat contínuo. Execute: python cliente-tcp.py"""
import socket

# Troque pelo IPv4 do notebook que executa servidor-tcp.py.
# Se estiver tudo no mesmo notebook, use "127.0.0.1".
IP_SERVIDOR = "192.168.1.10"
PORTA = 5000

# socket(): cria um socket IPv4 e TCP.
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # connect(): estabelece a conexão TCP com o servidor.
    cliente.settimeout(5)
    cliente.connect((IP_SERVIDOR, PORTA))
    cliente.settimeout(None)  # Chat sem limite de espera entre mensagens.
    print("Conectado! Escreva mensagens; /sair encerra o cliente.")

    # Usaremos uma linha por mensagem, delimitada por \n.
    entrada = cliente.makefile("r", encoding="utf-8")
    with entrada:
        while True:  # Mantém o chat aberto.
            mensagem = input("Você: ")
            if mensagem.lower() == "/sair":
                break
            if not mensagem:
                continue

            # sendall(): envia os bytes da mensagem ao servidor.
            cliente.sendall((mensagem + "\n").encode("utf-8"))

            # readline(): lê a resposta completa, até \n.
            resposta = entrada.readline()
            if not resposta:
                print("Servidor encerrou a conexão.")
                break
            print(resposta.rstrip("\r\n"))

except (KeyboardInterrupt, EOFError):
    print("\nCliente encerrado.")
except OSError as erro:
    print("Erro de rede:", erro)
finally:
    cliente.close()

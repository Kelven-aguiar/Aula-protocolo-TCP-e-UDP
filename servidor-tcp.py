"""Bloco 4: servidor TCP com chat contínuo. Execute: python servidor-tcp.py"""
import socket

HOST = "0.0.0.0"  # Ouve em todas as interfaces IPv4 do notebook
PORTA = 5000

# socket(): cria um socket IPv4 (AF_INET) usando TCP (SOCK_STREAM).
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind(): associa o socket ao IP local e à porta 5000.
servidor.bind((HOST, PORTA))

# listen(): começa a aguardar pedidos de conexão TCP.
servidor.listen()
print(f"Servidor TCP ativo na porta {PORTA}. Ctrl+C para encerrar.")

try:
    while True:  # Mantém o servidor disponível para novos clientes.
        print("\nAguardando cliente...")
        # accept(): espera um cliente e devolve conexão + endereço remoto.
        conexao, endereco = servidor.accept()
        print("Cliente conectado:", endereco)

        try:
            with conexao:
                # makefile lê mensagens terminadas em \n; TCP é fluxo de bytes.
                entrada = conexao.makefile("r", encoding="utf-8")
                with entrada:
                    while True:  # Mantém o chat com o cliente atual.
                        linha = entrada.readline()
                        if not linha:  # Cliente fechou a conexão.
                            break
                        mensagem = linha.rstrip("\r\n")
                        print(f"Cliente {endereco[0]}: {mensagem}")

                        # sendall(): envia todos os bytes de uma resposta.
                        resposta = f"Servidor recebeu: {mensagem}\n"
                        conexao.sendall(resposta.encode("utf-8"))
        except OSError as erro:
            print("Erro na conversa:", erro)
        print("Cliente desconectado.")

except KeyboardInterrupt:
    print("\nServidor encerrado por Ctrl+C.")
finally:
    servidor.close()  # close(): libera o socket.

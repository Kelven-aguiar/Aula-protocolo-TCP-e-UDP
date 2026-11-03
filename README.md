# Aula 7 — Criando servidores e clientes TCP e UDP com Python

Este é um **tutorial para seguir diretamente no VS Code**. Você não precisa baixar os arquivos Python prontos: **vai criar os arquivos, copiar os blocos de código e modificar os mesmos programas** conforme avança. Os quatro arquivos disponíveis neste GitHub servem apenas como referência do **Bloco 4**.

## Antes de começar — preparação

**Dividam-se em duplas.** O notebook A será o **servidor** e o notebook B será o **cliente**. Os dois devem estar no mesmo Wi-Fi. Ao final, troquem os papéis.

1. Abra o **VS Code**. Em seu computador, crie uma pasta chamada **`Servidor-Cliente-Python`**.
2. No VS Code, clique em **File → Open Folder** e abra essa pasta.
3. Em **Terminal → New Terminal**, digite `python --version`. Se não funcionar, tente `py --version`. É necessário ter o Python instalado.
4. No notebook do **servidor**, execute `ipconfig` e procure o **Endereço IPv4** do adaptador Wi-Fi. Anote-o, por exemplo `192.168.1.10`.
5. Nos arquivos dos clientes, substitua `192.168.1.10` pelo IP real do notebook servidor. Se ambos os programas forem executados no mesmo computador, use `127.0.0.1`.

**Conheça as funções:** `socket()` cria o socket; `bind()` define IP/porta locais; `listen()` prepara a espera por conexões TCP; `accept()` aceita um cliente; `connect()` inicia a conexão TCP; `sendall()` envia bytes pelo TCP; `recvfrom()` e `sendto()` recebem e enviam datagramas UDP. O `while True` mantém o programa em funcionamento até sair do laço.

> **Como usar este tutorial:** todos os blocos Python têm **código completo, com indentação**. Nos passos de atualização, observe os comentários `# NOVO - BLOCO 5` e **substitua o conteúdo inteiro do arquivo** pelo bloco logo abaixo de **"Ficando assim o código:"**. Dessa maneira, você não precisa adivinhar onde colocar cada linha.

---

# Bloco 4 — Comunicação TCP e UDP

## Passo 1 — Criar servidor TCP

1. Na pasta `Servidor-Cliente-Python`, clique em **New File**.
2. Nomeie o arquivo exatamente **`servidor-tcp.py`**.
3. Copie **todo** o código abaixo e cole nele:

```python
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
```

**Entenda o código:** `AF_INET` significa IPv4; `SOCK_STREAM` significa TCP; `0.0.0.0` permite receber conexões por interfaces IPv4 locais; `5000` é a porta; `listen()` aguarda; `accept()` aceita a conexão; `sendall()` devolve a resposta. O servidor atende um cliente por vez, mas continua aberto esperando o próximo.

**Executar:** no notebook A, no terminal da pasta, digite:

```powershell
python servidor-tcp.py
```

**Resultado esperado:** `Servidor TCP ativo na porta 5000` e `Aguardando cliente...`. **Deixe o terminal aberto.**

## Passo 2 — Criar cliente TCP

1. No notebook B, abra a mesma pasta no VS Code.
2. Crie **`cliente-tcp.py`**.
3. Copie e cole o código inteiro abaixo.
4. **Troque o valor de `IP_SERVIDOR` pelo IPv4 do notebook A.**

```python
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
```

**Executar no notebook B:**

```powershell
python cliente-tcp.py
```

**Teste:** digite `Olá, servidor!`, pressione Enter e veja `Servidor recebeu: Olá, servidor!`. Envie outras mensagens. Digite `/sair` para fechar somente o cliente. O servidor continua esperando novas conexões. `Ctrl+C` encerra o servidor.

**Por que há `\n` nos dados?** TCP é um fluxo de bytes, não uma sequência de mensagens prontas. Por isso usamos uma quebra de linha para marcar o fim de cada mensagem, e `readline()` para recebê-la.

## Passo 3 — Criar servidor UDP

1. No notebook A, crie **`servidor-udp.py`**.
2. Copie todo o código abaixo:

```python
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
```

**Executar no notebook A, em outro terminal:**

```powershell
python servidor-udp.py
```

**Observe:** o servidor UDP utiliza a porta **5001** e não usa `listen()` nem `accept()`. Ele recebe datagramas diretamente com `recvfrom()`.

## Passo 4 — Criar cliente UDP

1. No notebook B, crie **`cliente-udp.py`**.
2. Copie todo o código abaixo. Ajuste o `IP_SERVIDOR`.

```python
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
```

**Executar no notebook B:**

```powershell
python cliente-udp.py
```

Digite `Olá, servidor!`. O cliente deverá exibir `Servidor confirmou a mensagem!`. Esse **ACK** foi criado pelo nosso código; **UDP não garante entrega por conta própria**. O ID da mensagem ajuda a reconhecer a confirmação correta.

**Discussão:** por que o cliente UDP não usa `connect()`? Quais funções aparecem no servidor TCP e não no UDP?

### Passo 5 — Troca de papéis

O aluno B vira servidor e o aluno A vira cliente. No novo servidor, execute `ipconfig` para descobrir o IPv4; atualize os dois arquivos do cliente e repita um teste TCP e outro UDP. Na rede escolar, se os notebooks estiverem isolados, use `127.0.0.1` com cliente e servidor no mesmo notebook.

---

# Bloco 5 — Diagnóstico, velocidade e recuperação

**Vamos continuar nos mesmos quatro arquivos.** Nos códigos a seguir, as partes novas estão identificadas como `# NOVO - BLOCO 5`. Lembre-se de executar somente **um servidor de cada protocolo/porta** por vez; reinicie o servidor após alterar o arquivo.

## Passo 6 — Usar ping, tracert e verificar a porta

No **cliente**, abra outro terminal PowerShell e substitua o IP abaixo pelo IP real do servidor:

```powershell
ipconfig
ping 192.168.1.10
tracert 192.168.1.10
Test-NetConnection 192.168.1.10 -Port 5000
```

- `ping`: observa respostas ICMP e tempo de ida e volta; **não verifica o programa Python**.
- `tracert`: tenta mostrar os roteadores intermediários; na mesma sub-rede pode não haver saltos. Para ver mais saltos, experimente `tracert 8.8.8.8`.
- `Test-NetConnection`: testa se a **porta TCP 5000** aceita conexão; `TcpTestSucceeded: True` indica sucesso. **Não testa UDP**.
- No notebook servidor, `netstat -ano -p tcp | findstr :5000` mostra a porta TCP; `netstat -ano -p udp | findstr :5001` mostra a porta UDP.

**Experimento:** encerre `servidor-tcp.py` com `Ctrl+C`. O `ping` pode continuar funcionando, enquanto o teste da porta 5000 falha. Isso demonstra a diferença entre o computador responder e a aplicação estar disponível.

**Outro problema:** com o servidor TCP ativo na porta 5000, mude temporariamente a porta no `cliente-tcp.py` para `6000`. Observe o erro e depois volte para `5000`.

> Firewalls podem bloquear ICMP independentemente de TCP/UDP. Não desative configurações de segurança da escola sem orientação.

## Passo 7 — Simular lentidão TCP

Abra `servidor-tcp.py`. **Acrescente** `import time` após `import socket` e `time.sleep(2)` depois de imprimir a mensagem do cliente, antes de responder. Essas linhas criam dois segundos de atraso **no programa**, não na rede.

**Ficando assim o código:**

```python
"""Bloco 4: servidor TCP com chat contínuo. Execute: python servidor-tcp.py"""
import socket

# NOVO - BLOCO 5: permite simular atraso de resposta
import time

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

                        # NOVO - BLOCO 5: resposta propositalmente lenta
                        time.sleep(2)

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
```

**Teste:** reinicie o servidor e o cliente. Envie `Olá!` e observe a resposta demorar aproximadamente dois segundos. Para continuar, vamos substituir esse código no próximo passo, removendo o atraso.

## Passo 8 — Medir a taxa de transferência TCP

Vamos transferir **1.000.000 de bytes** e aguardar a confirmação do servidor. Taxa aproximada em Mbps = bytes × 8 ÷ segundos ÷ 1.000.000.

**No `servidor-tcp.py`:** remova a simulação de lentidão e adicione o tratamento de mensagens que começam com `TESTE:`. O servidor contará os bytes recebidos e devolverá `RECEBIDOS:<quantidade>`.

**Ficando assim o código do servidor TCP:**

```python
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
                        # NOVO - BLOCO 5: responde a um teste de velocidade
                        if mensagem.startswith("TESTE:"):
                            quantidade = len(mensagem[6:].encode("utf-8"))
                            print(f"Recebidos {quantidade} bytes para teste.")
                            conexao.sendall(f"RECEBIDOS:{quantidade}\n".encode("utf-8"))
                            continue

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
```

**No `cliente-tcp.py`:** acrescente `import time` e a opção `/velocidade`, que envia a carga, espera a confirmação e calcula Mbps.

**Ficando assim o código do cliente TCP:**

```python
"""Bloco 4: cliente TCP com chat contínuo. Execute: python cliente-tcp.py"""
import socket

# NOVO - BLOCO 5: cronômetro para medir a taxa efetiva
import time

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

            # NOVO - BLOCO 5: digite /velocidade no chat
            if mensagem == "/velocidade":
                carga = "A" * 1_000_000
                inicio = time.perf_counter()
                cliente.sendall(("TESTE:" + carga + "\n").encode("utf-8"))
                confirmacao = entrada.readline().strip()
                duracao = time.perf_counter() - inicio

                if confirmacao == "RECEBIDOS:1000000":
                    mbps = (1_000_000 * 8) / (duracao * 1_000_000)
                    print(f"Tempo total: {duracao:.3f} segundos")
                    print(f"Taxa efetiva aproximada: {mbps:.2f} Mbps")
                else:
                    print("Falha na confirmação:", confirmacao)
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
```

**Teste:** reinicie servidor e cliente TCP; no chat do cliente, digite **`/velocidade`**. Observe `Tempo total` e `Taxa efetiva aproximada`. Trata-se de um teste didático com confirmação, não da velocidade máxima do Wi-Fi. O tempo inclui ida/volta e processamento.

## Passo 9 — Simular perda de mensagens UDP

Agora o servidor UDP **descartará a primeira tentativa** de cada mensagem, sem enviar ACK. A perda é simulada **no código da aplicação**, não no sinal Wi-Fi.

No `servidor-udp.py`, acrescente os conjuntos `descartados` e `processados`, que identificam mensagens pelo endereço do cliente e ID. Depois de receber o datagrama, se for a primeira tentativa, use `continue` para ignorá-lo; se for retransmissão, confirme sem processar duas vezes.

**Ficando assim o código do servidor UDP:**

```python
"""Bloco 4: servidor UDP contínuo. Execute: python servidor-udp.py"""
import socket

HOST = "0.0.0.0"
PORTA = 5001  # Porta diferente da usada pelo servidor TCP.

# NOVO - BLOCO 5: identifica a primeira tentativa de cada mensagem
descartados = set()

# NOVO - BLOCO 5: evita processar a mesma mensagem mais de uma vez
processados = set()

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

        # NOVO - BLOCO 5: usa origem + ID como identificador
        chave = (endereco, identificador)

        # Descarta propositalmente a primeira tentativa
        if chave not in descartados:
            descartados.add(chave)
            print(f"PERDA SIMULADA: mensagem ID {identificador}")
            continue

        if chave not in processados:
            processados.add(chave)
            print(f"MENSAGEM RECUPERADA: ID {identificador}: {mensagem}")
        else:
            print(f"DUPLICATA: ID {identificador}; reenviando ACK")

        # sendto(): manda um datagrama para o IP e a porta do remetente.
        confirmacao = f"ACK:{identificador}"
        servidor.sendto(confirmacao.encode("utf-8"), endereco)

except KeyboardInterrupt:
    print("\nServidor encerrado por Ctrl+C.")
finally:
    servidor.close()
```

**Teste intermediário:** reinicie o servidor UDP e execute o cliente UDP ainda no código do Bloco 4. Envie uma mensagem: o servidor mostra `PERDA SIMULADA` e o cliente termina com timeout, sem confirmação. É exatamente esse problema que resolveremos no próximo passo.

## Passo 10 — Recuperar mensagens UDP com timeout e retransmissão

No `cliente-udp.py`, substitua o envio único por um laço que tenta **até três vezes**. Se não chegar `ACK:<ID>` em 2 segundos, reenvie **a mesma mensagem com o mesmo ID**.

**Ficando assim o código do cliente UDP:**

```python
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

        # NOVO - BLOCO 5: reenvia o mesmo datagrama até 3 vezes
        confirmado = False

        for tentativa in range(1, 4):
            print(f"Tentativa {tentativa} — mensagem ID {identificador}")

            # sendto(): envia o datagrama sem conexão prévia
            cliente.sendto(pacote.encode("utf-8"), (IP_SERVIDOR, PORTA))

            try:
                # recvfrom(): recebe a confirmação do servidor
                dados, endereco = cliente.recvfrom(2048)
                confirmacao = dados.decode("utf-8")

                if endereco == (IP_SERVIDOR, PORTA) and confirmacao == f"ACK:{identificador}":
                    print("Mensagem confirmada!")
                    confirmado = True
                    break

                print("Confirmação inesperada:", confirmacao)

            except socket.timeout:
                print("Timeout: servidor não confirmou. Reenviando...")

        if not confirmado:
            print("Não foi possível confirmar após 3 tentativas.")

except (KeyboardInterrupt, EOFError):
    print("\nCliente encerrado.")
except OSError as erro:
    print("Erro de rede:", erro)
finally:
    cliente.close()
```

**Teste:** reinicie os dois programas UDP e envie `Olá, servidor!`.

**Cliente esperado:**

```text
Tentativa 1 — mensagem ID 1
Timeout: servidor não confirmou. Reenviando...
Tentativa 2 — mensagem ID 1
Mensagem confirmada!
```

**Servidor esperado:**

```text
PERDA SIMULADA: mensagem ID 1
MENSAGEM RECUPERADA: ID 1: Olá, servidor!
```

A recuperação não é feita automaticamente pelo UDP: **foi implementada por nós** com identificador, ACK, timeout e retransmissão. No exemplo didático, os conjuntos ficam em memória e são zerados ao reiniciar o programa; um sistema real exigiria controles adicionais de duplicatas, autenticação e consumo de memória.

---

## Revisão final — desempenho, QoS e segurança

| Conceito | O que significa |
| --- | --- |
| **Latência** | Tempo de ida e volta; o `ping` observa RTT de ICMP. |
| **Taxa de transferência** | Dados efetivamente transferidos por segundo (Mbps). |
| **Jitter** | Variação dos tempos de chegada dos pacotes. |
| **Perda de pacotes** | Dados que não chegam ao receptor; no exercício simulamos a ausência de entrega na aplicação. |
| **QoS** | Priorização e gerenciamento do tráfego, especialmente em congestionamento. |
| **Firewall** | Pode restringir comunicações por protocolo, IP e porta. |
| **Criptografia** | TCP e UDP não criptografam por padrão; aplicações usam protocolos como TLS/QUIC para proteção. |
| **Autenticação** | Verifica a identidade de quem acessa um sistema. |
| **Controle de acesso** | Define quais clientes podem usar o serviço. |

### Solução rápida de problemas

- **`python` não funciona:** teste `py` ou confira a instalação do Python.
- **`ConnectionRefusedError`:** servidor TCP não está ouvindo no IP/porta informados.
- **`Timeout`:** verifique servidor, IP, firewall e isolamento entre os notebooks.
- **`Address already in use`:** outra execução já está usando a porta.
- **Não conecta no Wi-Fi da escola:** experimente os programas no mesmo notebook com `127.0.0.1`.
- **UDP não confirma:** verifique a porta **5001** e se o servidor UDP está executando.

**Você concluiu a aula quando conseguir:** fazer os dois chats funcionarem; identificar diferença entre teste de rede e teste de aplicação; medir taxa de transferência; simular perda UDP e recuperar a mensagem por retransmissão.

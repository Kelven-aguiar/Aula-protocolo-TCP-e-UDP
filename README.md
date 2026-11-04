# Aula 7 — Comunicação TCP e UDP em Python

Siga as três atividades na ordem, criando os arquivos no VS Code, testando as comunicações e evoluindo os mesmos programas. Os quatro arquivos `.py` do repositório são referências da **Atividade 1**; não é necessário baixá-los.

## Antes de começar — preparação

**Dividam-se em duplas.** O notebook A será o **servidor** e o notebook B será o **cliente**. Os dois devem estar no mesmo Wi-Fi.

1. Abra o **VS Code**. Em seu computador, crie uma pasta chamada **`Servidor-Cliente-Python`**.
2. No VS Code, clique em **File → Open Folder** e abra essa pasta.
3. Em **Terminal → New Terminal**, digite `python --version`. Se não funcionar, tente `py --version`. É necessário ter o Python instalado.
4. No notebook do **servidor**, execute `ipconfig` e procure o **Endereço IPv4** do adaptador Wi-Fi. Anote-o, por exemplo `192.168.1.10`.
5. Nos arquivos dos clientes, substitua `192.168.1.10` pelo IP real do notebook servidor. Se ambos os programas forem executados no mesmo computador, use `127.0.0.1`.

**Conheça as funções:** `socket()` cria o socket; `bind()` define IP/porta locais; `listen()` prepara a espera por conexões TCP; `accept()` aceita um cliente; `connect()` inicia a conexão TCP; `sendall()` envia bytes pelo TCP; `recvfrom()` e `sendto()` recebem e enviam datagramas UDP. O `while True` mantém o programa em funcionamento até sair do laço.

> **Como usar este tutorial:** todos os blocos Python têm **código completo**. Nas atualizações, observe os comentários `# NOVO - ATIVIDADE 2` e `# NOVO - ATIVIDADE 3` e **substitua o conteúdo inteiro do arquivo** pelo bloco logo abaixo de **"Ficando assim o código:"**. Dessa maneira, você não precisa adivinhar onde colocar cada linha.

---

# Atividade 1 — Criando servidores e clientes TCP e UDP

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

# Atividade 2 — Observando as diferenças reais entre TCP e UDP

**Objetivo:** observar o estabelecimento e encerramento de uma conexão TCP e comparar com o recebimento de datagramas UDP. Não vamos simular perda de pacotes.

## Passo 6 — Testar a comunicação sem servidor

1. Pare os dois servidores com `Ctrl+C`.
2. Execute `cliente-tcp.py`. Como a porta TCP não está ouvindo, a tentativa de `connect()` pode retornar conexão recusada.
3. Execute `cliente-udp.py` e envie `Olá, servidor!`. O `sendto()` pode retornar sem erro, mas não haverá confirmação do programa servidor; pode ocorrer timeout ou um erro de rede, conforme o sistema.
4. Reinicie os dois servidores.

**O que observar:** TCP exige conexão estabelecida antes de enviar. UDP permite o envio de um datagrama sem negociar uma conexão prévia; enviar não significa que alguém recebeu.

## Passo 7 — Mostrar a conexão real no servidor TCP

No arquivo `servidor-tcp.py`, acrescente os logs ao redor de `accept()` para visualizar o momento em que o cliente conecta. Acrescente também um log quando a leitura chegar ao fim (EOF).

**Trecho novo após `accept()`:**

```python
# NOVO - ATIVIDADE 2: consulta os endereços da conexão.
print("[TCP] Conexão estabelecida:", endereco)
print("[TCP] Endereço local:", conexao.getsockname())
print("[TCP] Endereço remoto:", conexao.getpeername())
```

**O que significam as duas funções novas?**

- `conexao.getsockname()`: consulta o **endereço local desta conexão**, isto é, o IP e a porta do **servidor** no notebook A. Exemplo: `('192.168.1.10', 5000)`.
- `conexao.getpeername()`: consulta o **endereço remoto desta conexão**, isto é, o IP e a porta do **cliente** no notebook B. Exemplo: `('192.168.1.11', 52340)`.

O número `52340` é uma porta de origem escolhida para a conexão do cliente e pode mudar a cada execução. **Local e remoto dependem de qual computador está executando o código**: aqui, estamos consultando os dois endereços do ponto de vista do servidor.

**Exemplo de saída no servidor:**

```text
[TCP] Conexão estabelecida: ('192.168.1.11', 52340)
[TCP] Endereço local: ('192.168.1.10', 5000)
[TCP] Endereço remoto: ('192.168.1.11', 52340)
```

**Ficando assim o código completo do `servidor-tcp.py`:**

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
        # NOVO - ATIVIDADE 2: aguarda uma conexão TCP real.
        print("\n[TCP] Aguardando em accept()...")
        # accept(): espera um cliente e devolve conexão + endereço remoto.
        conexao, endereco = servidor.accept()
        # NOVO - ATIVIDADE 2: consulta os endereços da conexão.
        print("[TCP] Conexão estabelecida:", endereco)
        print("[TCP] Endereço local:", conexao.getsockname())
        print("[TCP] Endereço remoto:", conexao.getpeername())

        try:
            with conexao:
                # makefile lê mensagens terminadas em \n; TCP é fluxo de bytes.
                entrada = conexao.makefile("r", encoding="utf-8")
                with entrada:
                    while True:  # Mantém o chat com o cliente atual.
                        linha = entrada.readline()
                        if not linha:  # Cliente encerrou o envio normalmente.
                            # NOVO - ATIVIDADE 2: fim do fluxo TCP (EOF).
                            print("[TCP] O cliente encerrou o envio de dados (EOF).")
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

Execute o servidor e depois o cliente. Observe os endereços da conexão. Digite `/sair` no cliente e veja o servidor registrar o fim do fluxo e continuar aguardando o próximo cliente.

**Importante:** o log é gerado pelo estado real do socket. O fim normal do fluxo indica que o outro lado encerrou o envio; uma interrupção de rede nem sempre é percebida imediatamente.

## Passo 8 — Mostrar os datagramas e a ausência de conexão UDP

No `servidor-udp.py`, acrescente `settimeout(8)` para observar períodos sem mensagens, e um log do endereço retornado por `recvfrom()`. **Não** há `accept()` nem evento automático de desconexão UDP.

**Trecho novo após `bind()`:**

```python
# NOVO - ATIVIDADE 2: permite observar períodos sem datagramas.
servidor.settimeout(8)
```

**Ficando assim o código completo do `servidor-udp.py`:**

```python
"""Bloco 4: servidor UDP contínuo. Execute: python servidor-udp.py"""
import socket

HOST = "0.0.0.0"
PORTA = 5001  # Porta diferente da usada pelo servidor TCP.

# socket(): cria socket IPv4 e UDP (SOCK_DGRAM).
servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind(): define a porta onde chegam os datagramas.
servidor.bind((HOST, PORTA))

# NOVO - ATIVIDADE 2: permite observar períodos sem datagramas.
servidor.settimeout(8)
print(f"Servidor UDP ativo na porta {PORTA}. Ctrl+C para encerrar.")

try:
    while True:
        # recvfrom(): recebe até 2048 bytes e identifica o remetente.
        try:
            dados, endereco = servidor.recvfrom(2048)
        except socket.timeout:
            # NOVO - ATIVIDADE 2: não existe evento de desconexão UDP.
            print("[UDP] 8 s sem datagramas; isso não prova desconexão.")
            continue

        # NOVO - ATIVIDADE 2: origem recebida com cada datagrama.
        print("[UDP] Datagrama recebido de:", endereco)
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

Execute o servidor UDP e o cliente UDP. Envie uma mensagem, depois digite `/sair` no cliente. O servidor apenas continuará esperando; após oito segundos sem datagramas, poderá mostrar um timeout. Isso **não comprova** que um cliente se desconectou.

## Passo 9 — Comparar os resultados

| Observação | TCP | UDP |
| --- | --- | --- |
| Antes da troca de dados | `connect()` e `accept()` | `sendto()` e `recvfrom()` |
| Conexão estabelecida | Pode ser observada no socket | Não há conexão TCP equivalente |
| Origem do cliente | Socket conectado tem endereço remoto | Cada `recvfrom()` informa o remetente |
| Encerramento normal do cliente | Pode gerar fim de fluxo (EOF) | Não existe aviso automático de desconexão |
| Servidor indisponível | `connect()` pode falhar | `sendto()` pode concluir sem entrega |

**Discussão:** qual protocolo é mais apropriado para enviar um arquivo que deve chegar completo? Por que algumas aplicações de tempo real utilizam UDP?

---
# Atividade 3 — Diagnóstico de rede e desempenho

**Vamos continuar nos mesmos quatro arquivos.** No teste de velocidade, as partes novas estão identificadas como `# NOVO - ATIVIDADE 3`. Lembre-se de executar somente **um servidor de cada protocolo/porta** por vez; reinicie o servidor após alterar o arquivo.

## Passo 10 — Usar ping, tracert e verificar a porta

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
- No próximo passo, vamos usar `netstat` para observar os estados dessas conexões no Windows.

**Experimento:** encerre `servidor-tcp.py` com `Ctrl+C`. O `ping` pode continuar funcionando, enquanto o teste da porta 5000 falha. Isso demonstra a diferença entre o computador responder e a aplicação estar disponível.

## Passo 11 — Verificar no Windows se o TCP está conectado

Agora vamos usar o **`netstat`**, um comando do Windows que mostra conexões e portas de rede. Vamos comparar o que aparece **antes e depois** que um cliente se conecta.

### 11.1 — Servidor TCP aguardando

1. No notebook A, execute `python servidor-tcp.py` e deixe o servidor aberto.
2. No **mesmo notebook A**, abra **outro terminal PowerShell** no VS Code. Não feche o terminal do servidor.
3. Digite:

```powershell
netstat -ano -p tcp | findstr :5000
```

Exemplo de resultado:

```text
TCP    0.0.0.0:5000       0.0.0.0:0          LISTENING       1234
```

**O que significa?** `LISTENING` indica que o servidor TCP está **aguardando conexões** na porta `5000`. O número final, como `1234`, é o identificador do processo (**PID**) e varia entre os computadores.

### 11.2 — Cliente TCP conectado

1. No notebook B, execute `python cliente-tcp.py`.
2. **Não digite `/sair`**: deixe o cliente conectado, esperando uma mensagem.
3. Volte ao segundo terminal do notebook A e execute novamente:

```powershell
netstat -ano -p tcp | findstr :5000
```

Agora poderá aparecer também:

```text
TCP    192.168.1.10:5000    192.168.1.11:52340    ESTABLISHED    1234
```

**O que significa?** `ESTABLISHED` indica que a conexão TCP foi estabelecida. A primeira coluna de endereço mostra **IP e porta do servidor**; a segunda mostra **IP e porta do cliente**. Os IPs, a porta `52340` e o PID são exemplos e podem ser diferentes.

Digite `/sair` no cliente e execute o comando novamente. Aquela conexão deixará de aparecer como `ESTABLISHED` após o encerramento, enquanto o servidor continuará em `LISTENING`.

### 11.3 — Comparar com UDP

1. Deixe `servidor-udp.py` executando no notebook A.
2. Em outro terminal do mesmo notebook, digite:

```powershell
netstat -ano -p udp | findstr :5001
```

Exemplo:

```text
UDP    0.0.0.0:5001       *:*                5678
```

**Qual é a diferença?** A porta UDP `5001` aparece, mas não existe `LISTENING` ou `ESTABLISHED` como no TCP. Isso acontece porque o UDP **não estabelece uma conexão TCP com o cliente**.

**Conclusão:** no TCP conseguimos observar o servidor aguardando (`LISTENING`) e a conexão aberta (`ESTABLISHED`). No UDP observamos o socket associado à porta, mas não esses estados de conexão.

---

## Passo 12 — Medir a taxa de transferência TCP

Vamos transferir **1.000.000 de bytes** e aguardar a confirmação do servidor. Taxa aproximada em Mbps = bytes × 8 ÷ segundos ÷ 1.000.000.

**No `servidor-tcp.py`:** adicione o tratamento de mensagens que começam com `TESTE:`. O servidor contará os bytes recebidos e devolverá `RECEBIDOS:<quantidade>`.

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
        # NOVO - ATIVIDADE 2: aguarda uma conexão TCP real.
        print("\n[TCP] Aguardando em accept()...")
        # accept(): espera um cliente e devolve conexão + endereço remoto.
        conexao, endereco = servidor.accept()
        # NOVO - ATIVIDADE 2: consulta os endereços da conexão.
        print("[TCP] Conexão estabelecida:", endereco)
        print("[TCP] Endereço local:", conexao.getsockname())
        print("[TCP] Endereço remoto:", conexao.getpeername())

        try:
            with conexao:
                # makefile lê mensagens terminadas em \n; TCP é fluxo de bytes.
                entrada = conexao.makefile("r", encoding="utf-8")
                with entrada:
                    while True:  # Mantém o chat com o cliente atual.
                        linha = entrada.readline()
                        if not linha:  # Cliente encerrou o envio normalmente.
                            # NOVO - ATIVIDADE 2: fim do fluxo TCP (EOF).
                            print("[TCP] O cliente encerrou o envio de dados (EOF).")
                            break
                        mensagem = linha.rstrip("\r\n")
                        # NOVO - ATIVIDADE 3: mede transferência de um lote de dados.
                        if mensagem.startswith("TESTE:"):
                            tamanho = len(mensagem[6:].encode("utf-8"))
                            print(f"[TCP] Teste: {tamanho} bytes recebidos.")
                            conexao.sendall(f"RECEBIDOS:{tamanho}\n".encode("utf-8"))
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

# NOVO - ATIVIDADE 3: cronômetro para medir a taxa efetiva
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

            # NOVO - ATIVIDADE 3: digite /velocidade no chat
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

## Revisão final — desempenho, QoS e segurança

| Conceito | O que significa |
| --- | --- |
| **Latência** | Tempo de ida e volta; o `ping` observa RTT de ICMP. |
| **Taxa de transferência** | Dados efetivamente transferidos por segundo (Mbps). |
| **Jitter** | Variação dos tempos de chegada dos pacotes. |
| **Perda de pacotes** | Dados que não chegam ao destino; TCP pode retransmitir segmentos perdidos, enquanto UDP não possui retransmissão automática. |
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

**Você concluiu as atividades quando conseguir:** fazer os dois chats funcionarem; distinguir teste de rede e teste de aplicação; medir a taxa de transferência TCP.

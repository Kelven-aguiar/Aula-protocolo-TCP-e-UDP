# Aula 7 — Protocolos TCP e UDP com Python

**Tutorial para os alunos — Blocos 4 e 5.** Leia e siga **na ordem**, em duplas. Você não precisa conhecer Python previamente. Tudo funciona com a biblioteca padrão do Python, sem instalar pacotes.

> **Objetivo:** criar uma comunicação real entre dois notebooks no mesmo Wi-Fi, descobrir por que ela falha, medir desempenho e programar recuperação de mensagens UDP.

## Antes de começar

**O que é um socket?** É a interface usada pelo programa para trocar dados pela rede. Pense no **IP** como o endereço do computador e na **porta** como o número da aplicação. Nosso servidor TCP usará a porta **5000** e o UDP, **5001**.

| TCP | UDP |
| --- | --- |
| Estabelece conexão antes de enviar dados | Envia datagramas sem conexão prévia |
| Entrega os bytes em ordem enquanto a conexão funciona | Não garante chegada nem ordem dos datagramas |
| Usamos `listen()`, `accept()`, `connect()` | Usamos `sendto()` e `recvfrom()` |
| Ex.: acesso web HTTPS, SSH | Ex.: jogos em tempo real, DNS tradicional |

UDP não é sempre mais rápido: depende da aplicação e da rede.

### 1. Prepare os notebooks

1. Conectem os **dois notebooks ao mesmo Wi-Fi**. Um será o **servidor (A)** e outro o **cliente (B)**.
2. Instalem o Python e o VS Code se necessário. No terminal do VS Code, confirmem com `python --version` (ou `py --version`).
3. Cliquem no botão **Code → Download ZIP** nesta página. Extraiam o ZIP e abram a pasta no VS Code. Cada computador pode baixar os mesmos quatro arquivos.
4. No notebook A, abram um terminal (`Terminal → New Terminal`) e executem `ipconfig`. Procurem o **Endereço IPv4** do adaptador **Wi-Fi** (exemplo: `192.168.1.10`).
5. No notebook B, abram `cliente_tcp.py` e `cliente_udp.py` e **substituam** o exemplo `IP_SERVIDOR = "192.168.1.10"` pelo IPv4 do notebook A. **Não usem o IP do gateway**.
6. Caso a escola isole os notebooks na rede, executem os dois programas no **mesmo notebook** e usem `IP_SERVIDOR = "127.0.0.1"` nos clientes. É o *localhost*.

**Importante:** `0.0.0.0` aparece apenas nos **servidores** para escutar nas interfaces IPv4; **não** deve ser o destino do cliente.

---

# BLOCO 4 — Construindo a comunicação

## 2. TCP: servidor

No notebook A, abram [servidor_tcp.py](servidor_tcp.py). Leiam os comentários do código, especialmente:

- `socket(AF_INET, SOCK_STREAM)`: cria o socket IPv4/TCP.
- `bind(("0.0.0.0", 5000))`: associa o socket à porta local **5000**.
- `listen()`: coloca o servidor à espera.
- `accept()`: aguarda um cliente e devolve uma conexão para conversar.
- `readline()`: recebe uma mensagem terminada em quebra de linha. **TCP transporta um fluxo de bytes**, não mensagens individuais.
- `sendall()`: envia os bytes de resposta.
- Os dois `while True`: o externo aceita novos clientes, o interno mantém o chat com um cliente. Este exemplo atende **um cliente por vez**.
- `Ctrl+C`: encerra o servidor.

No terminal do notebook A:

```powershell
python servidor_tcp.py
```

Resultado esperado:

```text
Servidor TCP ativo na porta 5000. Ctrl+C para encerrar.
Aguardando cliente...
```

**Deixem esse terminal aberto.**

## 3. TCP: cliente

No notebook B, abram [cliente_tcp.py](cliente_tcp.py). Vejam os comentários de `socket()`, `connect()`, `sendall()` e `readline()`.

Em outro terminal:

```powershell
python cliente_tcp.py
```

Escrevam `Olá, servidor!` e pressionem Enter. O cliente deverá exibir:

```text
Conectado! Escreva mensagens; /sair encerra o cliente.
Você: Olá, servidor!
Servidor recebeu: Olá, servidor!
```

Escrevam mais duas mensagens. `/sair` encerra **apenas o cliente**; o servidor volta a aguardar outro cliente. Para encerrar o servidor, usem `Ctrl+C`.

**Pergunta para discussão:** por que `connect()` precisa funcionar antes de o cliente TCP enviar dados?

## 4. UDP: servidor e cliente

No notebook A, **sem precisar fechar o servidor TCP**, abram outro terminal e executem:

```powershell
python servidor_udp.py
```

No notebook B, abram outro terminal e executem:

```powershell
python cliente_udp.py
```

Digite `Olá, servidor!`. O cliente deverá mostrar `Servidor confirmou a mensagem!`.

Leiam os comentários nos arquivos [servidor_udp.py](servidor_udp.py) e [cliente_udp.py](cliente_udp.py):

- `SOCK_DGRAM`: cria o socket UDP.
- `recvfrom()`: recebe dados **e** endereço de quem enviou.
- `sendto()`: informa o endereço de destino no próprio envio.
- `settimeout(2)`: espera até 2 segundos por uma resposta.
- `ACK:1`: é uma **confirmação criada por nosso programa**, não um recurso automático do UDP.
- `1|Olá, servidor!`: `1` é o número da mensagem, usado para reconhecer sua confirmação.

**Pergunta para discussão:** quais funções do servidor TCP não aparecem no servidor UDP? Por quê?

**Troquem de papéis:** o notebook B vira servidor e o A vira cliente. Descubram o IPv4 do novo servidor, alterem `IP_SERVIDOR` nos clientes e repitam um teste TCP e um UDP.

---

# BLOCO 5 — Diagnóstico, desempenho e recuperação

> **Agora vamos modificar os MESMOS quatro arquivos.** Os trechos adicionados estão indicados por `# NOVO - BLOCO 5`. Façam uma alteração por vez e executem novamente.

## 5. Diagnóstico: o computador responde? A aplicação responde?

Primeiro, **com o servidor TCP aberto**, no notebook B, abram outro terminal (PowerShell) e executem os comandos abaixo. Substituam o IP de exemplo pelo IP real do notebook A:

```powershell
ipconfig
ping 192.168.1.10
tracert 192.168.1.10
Test-NetConnection 192.168.1.10 -Port 5000
```

- **`ipconfig`**: mostra os endereços locais.
- **`ping`**: testa respostas **ICMP** e mostra o tempo de ida e volta (*RTT*). Não testa o programa Python.
- **`tracert`**: tenta mostrar roteadores intermediários. Na mesma sub-rede pode não haver nenhum. Experimentem também `tracert 8.8.8.8`.
- **`Test-NetConnection ... -Port 5000`**: testa se é possível estabelecer conexão **TCP** na porta 5000. Um sucesso mostra `TcpTestSucceeded : True`. Não serve para testar UDP.
- No notebook A, `netstat -ano -p tcp | findstr :5000` mostra o socket TCP em `LISTENING`; `netstat -ano -p udp | findstr :5001` mostra a porta UDP.

### Simulem três problemas

1. **Fechem o servidor TCP** com `Ctrl+C`. O `ping` **pode continuar respondendo**, mas o teste da porta 5000 deve falhar se não houver outro serviço nessa porta.
2. **Troquem a porta no cliente TCP para 6000**, com o servidor ouvindo em 5000. Tentem conectar. Depois voltem para 5000.
3. **Fechem o servidor UDP** e executem o cliente UDP. Ele pode informar ausência de confirmação após o timeout. Um `sendto()` bem-sucedido **não prova** que o servidor recebeu os dados.

Se `ping` falhar, não conclua automaticamente que TCP está bloqueado: ICMP pode ser filtrado. Firewall e isolamento entre clientes Wi-Fi também podem interferir. **Não desativem o firewall sem orientação da equipe de TI.**

## 6. Simular lentidão no TCP

Abram `servidor_tcp.py`. **Acrescentem** a importação no início:

```python
# NOVO - BLOCO 5: biblioteca para simular lentidão
import time
```

Dentro do `while True` interno, localizem:

```python
mensagem = linha.rstrip("\r\n")
print(f"Cliente {endereco[0]}: {mensagem}")
```

**Logo após essas linhas**, adicionem:

```python
# NOVO - BLOCO 5: simula servidor lento
time.sleep(2)
```

Reiniciem o servidor TCP e enviem uma mensagem. A resposta chegará aproximadamente dois segundos depois. **Isso é atraso criado pela aplicação**, não prova que a rede esteja lenta.

Depois, removam `time.sleep(2)` para a próxima etapa.

## 7. Medir a taxa de transferência TCP

Vamos transferir **1.000.000 de bytes** e medir o tempo até o servidor confirmar que recebeu tudo. A medida inclui transmissão, processamento e ida e volta da confirmação: é uma estimativa didática de **taxa efetiva de aplicação**, não da velocidade máxima do Wi-Fi.

### 7.1. Alterar `servidor_tcp.py`

No início, adicionem:

```python
# NOVO - BLOCO 5: tempo para medir a recepção
import time
```

Dentro do `while True` interno, **depois** de `mensagem = linha.rstrip("\r\n")` e **antes** do `print` normal, adicionem:

```python
# NOVO - BLOCO 5: interpreta um comando de teste de velocidade
if mensagem.startswith("TESTE:"):
    dados_teste = mensagem[6:]
    quantidade = len(dados_teste.encode("utf-8"))
    print(f"Teste de velocidade: {quantidade} bytes recebidos")
    conexao.sendall(f"RECEBIDOS:{quantidade}\n".encode("utf-8"))
    continue
```

### 7.2. Alterar `cliente_tcp.py`

No início do arquivo, adicionem:

```python
# NOVO - BLOCO 5: cronômetro de alta precisão
import time
```

No `while True` do cliente, **logo depois** de verificar `/sair` e a mensagem vazia, **antes** do `sendall` normal, adicionem:

```python
# NOVO - BLOCO 5: digite /velocidade para enviar 1 MB
if mensagem == "/velocidade":
    carga = "A" * 1_000_000
    inicio = time.perf_counter()
    cliente.sendall(("TESTE:" + carga + "\n").encode("utf-8"))
    confirmacao = entrada.readline().strip()
    duracao = time.perf_counter() - inicio

    if confirmacao == "RECEBIDOS:1000000":
        mbps = (1_000_000 * 8) / (duracao * 1_000_000)
        print(f"Tempo total: {duracao:.3f} s")
        print(f"Taxa efetiva aproximada: {mbps:.2f} Mbps")
    else:
        print("Confirmação inválida:", confirmacao)
    continue
```

Reiniciem o servidor e o cliente TCP. No chat, digitem `/velocidade`. A taxa varia conforme os notebooks, o Wi-Fi e o processamento. O teste **não** mede a latência pura da rede.

> No TCP, o código usa mensagens terminadas em `\n`, por isso o servidor consegue distinguir uma linha de texto da próxima. Para cargas maiores, uma aplicação profissional normalmente usa um protocolo próprio de enquadramento e transmissão em blocos.

## 8. Simular perda UDP e recuperar por retransmissão

**Meta:** o servidor descarta de propósito a **primeira tentativa** de cada mensagem. O cliente espera dois segundos; se não receber `ACK`, retransmite **o mesmo ID**. É uma simulação de perda **na aplicação**, não uma queda real de pacotes no Wi-Fi.

### 8.1. Alterar `servidor_udp.py`

Depois de `PORTA = 5001`, acrescentem:

```python
# NOVO - BLOCO 5: guarda (cliente, ID) descartados uma vez
descartados = set()

# NOVO - BLOCO 5: evita processar a mesma mensagem duas vezes
confirmados = set()
```

Dentro do `while True`, **depois** deste trecho já existente:

```python
if not separador:
    print("Datagrama fora do formato esperado:", texto)
    continue
```

adicionem:

```python
# NOVO - BLOCO 5: identifica a mensagem por origem e número
chave = (endereco, identificador)

# Primeira tentativa: descarta, sem mandar ACK
if chave not in descartados:
    descartados.add(chave)
    print(f"PERDA SIMULADA: ID {identificador}")
    continue

# Se uma confirmação anterior se perdeu, responder sem repetir ação
if chave in confirmados:
    print(f"REPETIÇÃO: ID {identificador}; reenviando ACK")
else:
    confirmados.add(chave)
    print(f"RECUPERADA: ID {identificador}: {mensagem}")
```

O código original continuará enviando `ACK:<ID>` ao final. Para a demonstração, esta lógica mantém as chaves na memória até encerrar o servidor. Em sistemas reais, seria necessário gerenciar tempo de retenção e memória.

### 8.2. Alterar `cliente_udp.py`

Dentro do `while True`, **substituam** o trecho que vai de `cliente.sendto(...)` até o final do `except socket.timeout` pelo código abaixo:

```python
# NOVO - BLOCO 5: retransmite até 3 vezes se não receber ACK
confirmado = False

for tentativa in range(1, 4):
    print(f"Tentativa {tentativa}, mensagem ID {identificador}")

    # Reutiliza exatamente o mesmo pacote e o mesmo ID
    cliente.sendto(pacote.encode("utf-8"), (IP_SERVIDOR, PORTA))

    try:
        dados, endereco = cliente.recvfrom(2048)
        confirmacao = dados.decode("utf-8")

        if endereco == (IP_SERVIDOR, PORTA) and confirmacao == f"ACK:{identificador}":
            print("Mensagem confirmada!")
            confirmado = True
            break

        print("Confirmação inesperada; aguardaremos nova tentativa.")

    except socket.timeout:
        print("Timeout! Sem confirmação; tentando de novo.")

if not confirmado:
    print("Falhou: nenhuma confirmação válida após 3 tentativas.")
```

**Executem primeiro o servidor UDP e depois o cliente UDP.**

Cliente esperado:

```text
Você (/sair para fechar): Olá, servidor!
Tentativa 1, mensagem ID 1
Timeout! Sem confirmação; tentando de novo.
Tentativa 2, mensagem ID 1
Mensagem confirmada!
```

Servidor esperado:

```text
PERDA SIMULADA: ID 1
RECUPERADA: ID 1: Olá, servidor!
```

**Pergunta:** quem criou a recuperação — o UDP ou o nosso programa? **Nosso programa.** A confirmação pode se perder também; por isso mantivemos o mesmo ID e uma lista de mensagens já confirmadas.

> **Atenção:** este exemplo é para sala de aula. Não implementa um protocolo UDP completo ou seguro; números de sequência persistentes, autenticação, tratamento mais robusto de ACKs e controle de memória seriam necessários em aplicações reais.

## 9. Conclusão: desempenho, QoS e segurança

| Tema | O que observar |
| --- | --- |
| Latência | `ping` mostra o tempo de ida e volta ICMP; `sleep` simula atraso de aplicação. |
| Taxa de transferência | O comando `/velocidade` mede bytes confirmados por segundo no TCP. |
| Perda e retransmissão | Nosso UDP simula perda e precisa de confirmação, timeout e nova tentativa. |
| Jitter | Variação no tempo de chegada dos pacotes, relevante para áudio e jogos. |
| QoS | Políticas de priorização de tráfego, especialmente quando há congestionamento. |
| Firewall | Pode bloquear ICMP, TCP ou UDP de formas diferentes. |
| Criptografia | TCP e UDP **não criptografam por padrão**; HTTPS usa TLS sobre TCP e QUIC usa TLS sobre UDP. |
| Autenticação | A aplicação precisa verificar com quem está se comunicando. |
| Controle de acesso | Restringir quem pode usar uma aplicação ou serviço. |

**Concluído:** vocês criaram cliente e servidor TCP/UDP, fizeram testes de conectividade, simularam lentidão, mediram taxa efetiva e implementaram retransmissão UDP.

### Se algo não funcionar

- **`ConnectionRefusedError`:** servidor TCP fechado, IP/porta errados ou serviço indisponível.
- **Timeout:** a rede, firewall, isolamento Wi-Fi ou servidor podem impedir a resposta.
- **`Address already in use`:** outra execução já utiliza a mesma porta; encerrem a anterior.
- **`python` não reconhecido:** tentem `py` ou verifiquem a instalação.
- **Wi-Fi da escola impede comunicação:** usem `127.0.0.1` nos dois programas no mesmo notebook.
- **Nenhuma resposta no UDP:** chequem porta **5001**, IP do servidor e se o servidor UDP está aberto.

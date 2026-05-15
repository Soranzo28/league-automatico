# LoL Bot

Automação de champion select para League of Legends. Aceita fila, bane, hovera e picka campeões automaticamente com base em listas de prioridade configuráveis por lane.

> Funciona apenas em filas ranqueadas (Solo/Duo e Flex).

---

## Funcionalidades

- **Auto Queue** — aceita a partida automaticamente
- **Auto Hover** — hovera o primeiro pick disponível da sua lane na fase de planejamento
- **Auto Ban** — bane o campeão de maior prioridade da lista, respeitando intenções dos aliados
- **Auto Pick** — picka o campeão de maior prioridade disponível da sua lane
- Picks configuráveis **por lane** (TOP, JG, MID, ADC, SUPP) com drag & drop para definir prioridade
- Dados do invocador (ícone, elo, nível) puxados direto do cliente do LoL
- Background do perfil exibido na tela inicial

---

## Requisitos

- Python 3.11+
- League of Legends instalado e rodando (o bot se conecta via LCU)

---

## Instalação

```bash
git clone https://github.com/seu-usuario/league-automatico.git
cd league-automatico
pip install -r requirements.txt
```


---

## Uso

```bash
python main.py
```

1. Abra o programa (pode abrir antes ou depois do LoL)
2. Configure suas listas de **Picks** e **Bans** nas abas da barra lateral
3. Marque as automações que deseja ativar (Auto Queue, Auto Ban, Auto Pick, Auto Hover)
4. Clique em **INICIAR** — o bot só age após isso
5. Clique em **PARAR** para desativar tudo

As preferências de automação e as listas de picks/bans são salvas automaticamente.

---

## Estrutura

```
league-automatico/
├── main.py   # interface gráfica principal
├── pregamemanager.py      # lógica de automação (LCU events)
├── database.py            # SQLite (campeões, picks, bans, settings)
├── populate_db.py         # sincronização com Data Dragon API
├── assets/
│   ├── champ_icons/       # ícones dos campeões
│   └── elos/              # emblemas de elo
└── lol.db                 # banco gerado automaticamente
```

---

## Aviso

Projeto pessoal, não afiliado à Riot Games. League of Legends é marca registrada da Riot Games, Inc. Este projeto não distribui nenhum ativo pertencente à Riot. O uso é de inteira responsabilidade do usuário.

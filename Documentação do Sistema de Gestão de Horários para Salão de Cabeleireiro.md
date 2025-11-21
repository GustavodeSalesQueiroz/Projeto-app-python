# Documentação do Sistema de Gestão de Horários para Salão de Cabeleireiro

**Autor:** Gustavo de Sales , Eduardo de Sales , Stefany coelho, Ryan Honorato.
**Data:** 21 de Novembro de 2025
**Versão:** 1.0

---

## 1. Proposta e Visão Geral do Projeto

O sistema de gestão de horários, desenvolvido em Python com a *framework* **Flet**, foi concebido como uma **solução pessoal e especializada** para a cabeleireira e seu salão. A proposta central é otimizar a administração da agenda, permitindo um **atendimento personalizado** e eficiente, que é a marca de um serviço de excelência.

Este sistema visa substituir métodos manuais ou planilhas genéricas, oferecendo uma interface gráfica intuitiva e focada nas necessidades específicas de um salão de beleza.

### 1.1. Objetivo Principal

O objetivo principal é fornecer uma ferramenta digital que permita:
1.  **Agendamento Rápido e Intuitivo:** Facilitar a marcação de novos horários pelo telefone ou presencialmente.
2.  **Visão Clara da Agenda:** Apresentar os agendamentos de forma organizada por data e hora.
3.  **Gestão de Status:** Permitir o acompanhamento do ciclo de vida do agendamento (Agendado, Concluído, Removido).
4.  **Personalização do Serviço:** Manter um catálogo de serviços com preços e durações pré-definidos, essenciais para o planejamento.

## 2. Análise Técnica do Sistema

O projeto é uma aplicação *desktop* desenvolvida em Python, utilizando a biblioteca **Flet** para a construção da interface gráfica de usuário (GUI).

### 2.1. Estrutura do Código

O sistema é encapsulado em uma única classe principal, `SalaoAgendamento`, que gerencia toda a lógica de negócios e persistência de dados.

| Componente | Descrição |
| :--- | :--- |
| **Tecnologia** | Python 3.x e Flet (GUI *cross-platform*). |
| **Classe Principal** | `SalaoAgendamento` (Linha 6) |
| **Persistência de Dados** | Arquivo `agendamentos.json` (Linha 9) |
| **Serviços** | Lista de dicionários com `nome`, `preco` e `duracao` (Linhas 13-22) |
| **Interface (Função)** | `main(page: ft.Page)` (Linha 99) |

### 2.2. Funcionalidades da Classe `SalaoAgendamento`

A classe implementa métodos cruciais para a gestão da agenda:

| Método | Finalidade |
| :--- | :--- |
| `__init__` | Inicializa a lista de agendamentos, carrega dados do JSON e define serviços e horários disponíveis. |
| `carregar_agendamentos` | Lê e desserializa os dados do arquivo `agendamentos.json`. |
| `salvar_agendamentos` | Serializa e salva a lista de agendamentos no arquivo JSON, garantindo a persistência dos dados. |
| `verificar_disponibilidade` | Confirma se um determinado horário em uma data específica já está ocupado por um agendamento ativo. |
| `adicionar_agendamento` | Cria um novo registro, atribui um ID e salva no arquivo. |
| `remover_agendamento` | Marca um agendamento como 'Removido' (não o exclui fisicamente, mantendo o histórico). |
| `marcar_como_concluido` | Altera o status do agendamento para 'Concluído'. |
| `obter_agendamentos_ativos` | Filtra e retorna apenas os agendamentos que não estão marcados como 'Removido'. |

### 2.3. Persistência de Dados

O sistema utiliza o formato **JSON** (`agendamentos.json`) para armazenar os dados de forma estruturada. Cada agendamento é um objeto JSON que contém os seguintes campos:

*   `id`: Identificador único do agendamento.
*   `nome`: Nome do cliente.
*   `telefone`: Telefone de contato.
*   `servico`: Nome do serviço contratado.
*   `preco`: Preço do serviço (extraído da lista de serviços).
*   `duracao`: Duração em minutos (extraída da lista de serviços).
*   `data`: Data do agendamento (formato DD/MM/AAAA).
*   `horario`: Horário do agendamento (ex: "14:30").
*   `status`: Status atual (`Agendado`, `Concluído`, `Removido`).

## 3. Manual de Uso (Interface Gráfica)

A interface é dividida em duas áreas principais: o **Formulário de Agendamento** e a **Lista de Agendamentos**.

### 3.1. Formulário de Agendamento

Esta seção é utilizada para registrar novos clientes e serviços.

| Campo | Descrição | Validação |
| :--- | :--- | :--- |
| **Nome do Cliente** | Nome completo do cliente. | Obrigatório. |
| **Telefone** | Número de telefone do cliente. | Obrigatório, deve ter 11 dígitos numéricos. |
| **Serviço** | Seleção do serviço desejado (ex: Corte Feminino, Coloração). | Obrigatório, lista pré-definida. |
| **Data** | Data do agendamento. O botão "Selecionar Data" abre um calendário. | Obrigatório, deve ser uma data futura. |
| **Horário** | Seleção do horário disponível (intervalos de 30 minutos). | Obrigatório, verifica se o horário já está ocupado. |
| **Botão "Agendar Horário"** | Registra o agendamento no sistema e atualiza a lista. | Executa todas as validações acima. |

### 3.2. Lista de Agendamentos

A lista exibe todos os agendamentos ativos, agrupados por data e ordenados por horário.

| Elemento | Descrição |
| :--- | :--- |
| **Cabeçalho de Data** | Separa visualmente os agendamentos por dia (ex: 📅 DD/MM/AAAA). |
| **Detalhes do Agendamento** | Exibe horário, nome, preço, telefone, serviço e duração. |
| **Status** | Indicado por cor e ícone: 🟠 `Agendado` (Laranja) ou 🟢 `Concluído` (Verde). |
| **Ações (Botões)** | Permite a gestão do agendamento: |
| | **✅ Marcar como concluído:** Altera o status para `Concluído`. |
| | **🗑️ Remover agendamento:** Altera o status para `Removido` (oculta da lista ativa). |

## 4. Conclusão

O sistema de gestão de horários é uma ferramenta robusta e de fácil utilização, perfeitamente alinhada à proposta de um **sistema pessoal de gestão**. Ao centralizar a agenda, o catálogo de serviços e o histórico de status, ele permite que a cabeleireira mantenha o foco no **atendimento personalizado**, garantindo que a administração do tempo seja eficiente e profissional.

A escolha do Flet como *framework* garante que a aplicação seja leve e com potencial para ser executada em diferentes plataformas (desktop), oferecendo uma solução moderna e dedicada ao sucesso do salão.

# 🔥 SkyGuard

Bot de RPA para monitoramento automatizado de queimadas no Brasil, desenvolvido como projeto da Global Solution (FIAP). O SkyGuard integra dados de satélite e clima em tempo real, gera um dashboard de acompanhamento e registra ocorrências automaticamente, apoiando a tomada de decisão em cenários de risco ambiental.

## 📌 Sobre o projeto

Incêndios florestais são um dos principais desafios ambientais do Brasil, exigindo monitoramento constante para resposta rápida. O **SkyGuard** automatiza esse processo coletando dados de focos de incêndio e condições climáticas, consolidando essas informações em um dashboard e registrando cada ocorrência relevante de forma automática — sem intervenção manual.

## 🚀 Funcionalidades

- 🛰️ **Coleta automática de dados** de focos de incêndio via API da **NASA FIRMS** (Fire Information for Resource Management System)
- 🌦️ **Integração com a API do OpenWeather** para correlacionar focos de incêndio com condições climáticas (temperatura, umidade, vento)
- 📊 **Dashboard de monitoramento** com visualização consolidada dos dados coletados
- 📋 **Registro automático** das ocorrências em Google Forms, criando um histórico estruturado
- 🤖 **Execução via UiPath (RPA)**, sem necessidade de operação manual

## 🛠️ Tecnologias utilizadas

- **UiPath Studio / Orchestrator** — orquestração e execução do robô
- **VB.NET** — tratamento e parsing das respostas das APIs
- **NASA FIRMS API** — dados de focos de incêndio em tempo real
- **OpenWeather API** — dados climáticos
- **Google Forms** — registro automatizado das ocorrências
- **HTTP Request Activities (UiPath)** — integração com as APIs externas

## ⚙️ Como funciona

1. O robô realiza requisições HTTP às APIs da NASA FIRMS e OpenWeather
2. Os dados retornados (em JSON) são tratados via expressões VB.NET para extrair as informações relevantes
3. As informações são organizadas e exibidas no dashboard de monitoramento
4. Cada ocorrência identificada é registrada automaticamente em um Google Forms, criando um log histórico

## 🧩 Desafios técnicos

- Parsing de respostas JSON das APIs usando expressões VB.NET dentro do UiPath
- Tratamento de erros e timeouts em requisições HTTP externas
- Sincronização dos dados coletados com o preenchimento automático do formulário
- Estruturação de um fluxo confiável de ponta a ponta (coleta → tratamento → dashboard → registro)

## 📦 Como executar

> Ajuste esta seção com os passos reais do seu projeto.

1. Clone o repositório
   ```bash
   git clone https://github.com/seu-usuario/skyguard.git
   ```
2. Abra o projeto no **UiPath Studio**
3. Configure suas chaves de API (NASA FIRMS e OpenWeather) no arquivo de configuração do projeto
4. Configure o link do Google Forms de destino
5. Execute o workflow principal via UiPath Studio ou publique no Orchestrator

## 🔑 Configuração de credenciais

As chaves de API e links sensíveis devem ser configurados em variáveis de ambiente ou no arquivo `config.xlsx`/`.json` do projeto (não versionado), evitando exposição de credenciais no repositório.

## 🎓 Contexto acadêmico

Projeto desenvolvido para a **Global Solution da FIAP**, com foco em automação aplicada a problemas ambientais reais do Brasil.

## 👤 Autor

**Vinicius** — Estudante de Engenharia de Software (FIAP)
[LinkedIn](#) · [GitHub](#)

## 📄 Licença

Este projeto é de uso acadêmico. Sinta-se livre para utilizá-lo como referência, com os devidos créditos.

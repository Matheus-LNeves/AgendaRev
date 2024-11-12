from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from streamlit_calendar import calendar
import json
import locale

# Configura a localidade para português do Brasil
locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

# Caminho para os arquivos JSON
eventos_file = "eventos.json"
cancelados_file = "clientes_cancelados.json"

# Carregar lista de clientes
def carregar_clientes():
    #caminho no PC Faz Capital: "C:/Users/FAZCAPITAL/OneDrive/lista de contatos.xlsx"
    #caminho no meu PC: "C:/Users/USER/OneDrive/lista de contatos.xlsx"
    file_path = "C:/Users/USER/OneDrive/lista de contatos.xlsx"
    xls = pd.ExcelFile(file_path)
    planilha2 = pd.read_excel(xls, 'Planilha2')
    nomes_encontrados = list(set(planilha2['a'].dropna().loc[planilha2['a.3'] != "Não encontrado"]))
    lista_clientes = sorted(nomes_encontrados)
    return lista_clientes

# Função para adicionar revisão no calendário
def agendar_revisao(cliente, data_inicial):
    eventos = []
    for i in range(4):
        data_evento = data_inicial + timedelta(days=i*90)
        if data_evento.weekday() >= 5:
            data_evento += timedelta(days=(7 - data_evento.weekday()))
        
        eventos.append({
            "cliente": cliente,
            "data": data_evento.strftime('%Y-%m-%d'),
            "title": cliente,
            "observacoes": "",
            "status": "Pendente"
        })
    return eventos

# Carregar eventos existentes ou criar nova estrutura
def carregar_eventos():
    try:
        with open(eventos_file, "r") as file:
            eventos = json.load(file)
        for evento in eventos:
            if "status" not in evento:
                evento["status"] = "Pendente"
            if "observacoes" not in evento:
                evento["observacoes"] = ""
    except (FileNotFoundError, json.JSONDecodeError):
        eventos = []
    return eventos

# Salvar eventos no arquivo JSON
def salvar_eventos(eventos):
    with open(eventos_file, "w") as file:
        json.dump(eventos, file)

# Carregar clientes cancelados
def carregar_cancelados():
    try:
        with open(cancelados_file, "r") as file:
            cancelados = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        cancelados = []
    return cancelados

# Salvar clientes cancelados no arquivo JSON
def salvar_cancelados(cancelados):
    with open(cancelados_file, "w") as file:
        json.dump(cancelados, file)

# Interface de usuário
st.title("Agendamento de Revisões de Carteira")
clientes = carregar_clientes()
cliente_selecionado = st.selectbox("Selecione o Cliente:", clientes)
data_revisao = st.date_input("Selecione a data da primeira revisão:", datetime.today())

# Processa o agendamento
if st.button("Agendar Revisões"):
    eventos = carregar_eventos()
    eventos_cliente = agendar_revisao(cliente_selecionado, data_revisao)
    eventos.extend(eventos_cliente)
    salvar_eventos(eventos)
    st.success("Revisões agendadas com sucesso!")

# Exibe o calendário com os eventos
st.subheader("Calendário de Revisões")
eventos_calendario = [{"title": evento["title"], "date": evento["data"]} for evento in carregar_eventos()]
calendar(events=eventos_calendario)

# Interface de eventos agendados com opção de abrir/fechar e filtrar por cliente
with st.expander("Ver Eventos Agendados", expanded=False):
    st.subheader("Filtrar Eventos por Cliente")
    cliente_para_visualizar = st.selectbox("Selecione o Cliente para Visualizar Eventos:", clientes)
    eventos = carregar_eventos()
    eventos_cliente = [evento for evento in eventos if evento["cliente"] == cliente_para_visualizar]
    
    if eventos_cliente:
        for evento in eventos_cliente:
            st.write(f"Data: {evento['data']}")
            st.write(f"Status Atual: {evento['status']}")
            evento["observacoes"] = st.text_area(f"Observações para {evento['title']} - {evento['data']}", evento["observacoes"])
            novo_status = st.selectbox(
                f"Marcar Status para {evento['title']} - {evento['data']}",
                ["Pendente", "Realizado", "Cancelado"],
                index=["Pendente", "Realizado", "Cancelado"].index(evento["status"])
            )
            evento["status"] = novo_status
            salvar_eventos(eventos)
    else:
        st.info("Nenhum evento encontrado para o cliente selecionado.")

# Exibe a lista de clientes cancelados com opção de reagendar ou remover
st.subheader("Clientes Cancelados")
clientes_cancelados = carregar_cancelados()
for cliente in clientes_cancelados:
    with st.expander(f"{cliente}", expanded=False):
        # Opção para remover cliente da lista de cancelados
        if st.button(f"Remover {cliente} dos Cancelados"):
            clientes_cancelados.remove(cliente)
            salvar_cancelados(clientes_cancelados)
            st.success(f"{cliente} foi removido da lista de cancelados.")
            continue
        
        # Opção para reagendar o cliente
        nova_data_revisao = st.date_input(f"Selecione a nova data para {cliente}:", datetime.today())
        if st.button(f"Reagendar {cliente}"):
            eventos = carregar_eventos()
            eventos_reagendados = agendar_revisao(cliente, nova_data_revisao)
            eventos.extend(eventos_reagendados)
            salvar_eventos(eventos)
            
            # Remove cliente da lista de cancelados após reagendar
            clientes_cancelados.remove(cliente)
            salvar_cancelados(clientes_cancelados)
            st.success(f"Reuniões reagendadas para {cliente}.")
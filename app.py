import streamlit as st
import pandas as pd
import pydeck as pdk
from db_sqlite import SQLiteDB
from db_mongo import MongoDB
from geoprocessamento import locais_no_raio, distancia_km

st.set_page_config(page_title="Persistência Poliglota + Geo", layout="wide")

if "sqlite_path" not in st.session_state:
    st.session_state.sqlite_path = "data.sqlite3"
if "mongo_uri" not in st.session_state:
    st.session_state.mongo_uri = "mongodb://localhost:27017"
if "mongo_db" not in st.session_state:
    st.session_state.mongo_db = "poliglota"
if "sqlite" not in st.session_state:
    st.session_state.sqlite = None
if "mongo" not in st.session_state:
    st.session_state.mongo = None

with st.sidebar:
    st.title("Conexões")
    sqlite_path = st.text_input("SQLite", st.session_state.sqlite_path)
    mongo_uri = st.text_input("MongoDB URI", st.session_state.mongo_uri, type="password")
    mongo_db = st.text_input("MongoDB Database", st.session_state.mongo_db)
    if st.button("Conectar", use_container_width=True):
        st.session_state.sqlite_path = sqlite_path
        st.session_state.mongo_uri = mongo_uri
        st.session_state.mongo_db = mongo_db
        try:
            st.session_state.sqlite = SQLiteDB(st.session_state.sqlite_path)
            st.success("SQLite ok")
        except Exception as e:
            st.session_state.sqlite = None
            st.error(f"SQLite erro: {e}")
        try:
            st.session_state.mongo = MongoDB(st.session_state.mongo_uri, st.session_state.mongo_db)
            st.success("MongoDB ok")
        except Exception as e:
            st.session_state.mongo = None
            st.error(f"MongoDB erro: {e}")

if st.session_state.sqlite is None:
    try:
        st.session_state.sqlite = SQLiteDB(st.session_state.sqlite_path)
    except Exception:
        pass
if st.session_state.mongo is None:
    try:
        st.session_state.mongo = MongoDB(st.session_state.mongo_uri, st.session_state.mongo_db)
    except Exception:
        pass

tabs = st.tabs(["Cidades e Estados", "Locais", "Consulta Integrada", "Proximidade", "Mapa"])

with tabs[0]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Cadastrar Estado")
        with st.form("form_estado", clear_on_submit=True):
            nome_estado = st.text_input("Nome do Estado")
            sigla_estado = st.text_input("Sigla", max_chars=2)
            submitted = st.form_submit_button("Salvar")
            if submitted and st.session_state.sqlite:
                ok = st.session_state.sqlite.add_estado(nome_estado, sigla_estado)
                if ok:
                    st.success("Estado salvo")
                else:
                    st.error("Não foi possível salvar")
    with c2:
        st.subheader("Cadastrar Cidade")
        estados_df = st.session_state.sqlite.list_estados() if st.session_state.sqlite else pd.DataFrame()
        estados_op = estados_df["sigla"].tolist() if not estados_df.empty else []
        with st.form("form_cidade", clear_on_submit=True):
            nome_cidade = st.text_input("Nome da Cidade")
            estado_sigla_sel = st.selectbox("Estado", estados_op)
            submitted = st.form_submit_button("Salvar")
            if submitted and st.session_state.sqlite and estado_sigla_sel:
                ok = st.session_state.sqlite.add_cidade(nome_cidade, estado_sigla_sel)
                if ok:
                    st.success("Cidade salva")
                else:
                    st.error("Não foi possível salvar")
    st.divider()
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Estados")
        df_e = st.session_state.sqlite.list_estados() if st.session_state.sqlite else pd.DataFrame()
        st.dataframe(df_e, hide_index=True, use_container_width=True)
    with colB:
        st.subheader("Cidades")
        df_c = st.session_state.sqlite.list_cidades() if st.session_state.sqlite else pd.DataFrame()
        st.dataframe(df_c, hide_index=True, use_container_width=True)

with tabs[1]:
    st.subheader("Cadastrar Local")
    cidades_lista = st.session_state.sqlite.all_cidades_nome() if st.session_state.sqlite else []
    with st.form("form_local", clear_on_submit=True):
        nome_local = st.text_input("Nome do Local")
        cidade_escolha = st.selectbox("Cidade (SQLite)", cidades_lista)
        latitude = st.number_input("Latitude", step=0.00001, format="%.5f")
        longitude = st.number_input("Longitude", step=0.00001, format="%.5f")
        descricao = st.text_area("Descrição")
        submitted = st.form_submit_button("Salvar no MongoDB")
        if submitted and st.session_state.mongo and cidade_escolha:
            cidade_nome = cidade_escolha.split(" - ")[0] if " - " in cidade_escolha else cidade_escolha
            try:
                st.session_state.mongo.add_local(nome_local, cidade_nome, latitude, longitude, descricao)
                st.success("Local salvo")
            except Exception as e:
                st.error(f"Erro: {e}")
    st.divider()
    st.subheader("Locais (MongoDB)")
    locais = st.session_state.mongo.all_locais() if st.session_state.mongo else []
    if locais:
        df = pd.DataFrame([{
            "nome_local": l.get("nome_local"),
            "cidade": l.get("cidade"),
            "latitude": l.get("coordenadas", {}).get("latitude"),
            "longitude": l.get("coordenadas", {}).get("longitude"),
            "descricao": l.get("descricao")
        } for l in locais])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Sem dados")

with tabs[2]:
    st.subheader("Consulta Integrada")
    estados_df = st.session_state.sqlite.list_estados() if st.session_state.sqlite else pd.DataFrame()
    estados_op = estados_df["sigla"].tolist() if not estados_df.empty else []
    estado_sel = st.selectbox("Estado", estados_op, key="ci_estado")
    cidades_df = st.session_state.sqlite.cidades_por_estado(estado_sel) if estado_sel and st.session_state.sqlite else pd.DataFrame()
    cidades_op = cidades_df["cidade"].tolist() if not cidades_df.empty else []
    cidade_sel = st.selectbox("Cidade", cidades_op, key="ci_cidade")
    if cidade_sel and st.session_state.mongo:
        dados = st.session_state.mongo.list_locais(cidade=cidade_sel)
        if dados:
            df = pd.DataFrame([{
                "nome_local": l.get("nome_local"),
                "cidade": l.get("cidade"),
                "latitude": l.get("coordenadas", {}).get("latitude"),
                "longitude": l.get("coordenadas", {}).get("longitude"),
                "descricao": l.get("descricao")
            } for l in dados])
            st.dataframe(df, use_container_width=True, hide_index=True)
            if "latitude" in df and "longitude" in df:
                center_lat = float(df["latitude"].mean())
                center_lon = float(df["longitude"].mean())
                r = pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=12),
                    layers=[pdk.Layer("ScatterplotLayer", data=df, get_position="[longitude, latitude]", get_radius=50)]
                )
                st.pydeck_chart(r, use_container_width=True)
        else:
            st.info("Sem locais para esta cidade")

with tabs[3]:
    st.subheader("Proximidade Geográfica")
    origem_lat = st.number_input("Latitude de origem", value=0.0, step=0.00001, format="%.5f")
    origem_lon = st.number_input("Longitude de origem", value=0.0, step=0.00001, format="%.5f")
    raio = st.number_input("Raio (km)", value=5.0, min_value=0.0, step=0.5, format="%.1f")
    if st.button("Buscar Locais Próximos"):
        locais = st.session_state.mongo.all_locais() if st.session_state.mongo else []
        resultado = locais_no_raio(locais, origem_lat, origem_lon, raio)
        if resultado:
            df = pd.DataFrame([{
                "nome_local": l.get("nome_local"),
                "cidade": l.get("cidade"),
                "latitude": l.get("coordenadas", {}).get("latitude"),
                "longitude": l.get("coordenadas", {}).get("longitude"),
                "distancia_km": l.get("distancia_km"),
                "descricao": l.get("descricao")
            } for l in resultado])
            st.dataframe(df, use_container_width=True, hide_index=True)
            center_lat = float(df["latitude"].mean())
            center_lon = float(df["longitude"].mean())
            r = pdk.Deck(
                map_style=None,
                initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=12),
                layers=[pdk.Layer("ScatterplotLayer", data=df, get_position="[longitude, latitude]", get_radius=60)]
            )
            st.pydeck_chart(r, use_container_width=True)
        else:
            st.info("Nenhum local encontrado")

with tabs[4]:
    st.subheader("Mapa de Locais")
    locais = st.session_state.mongo.all_locais() if st.session_state.mongo else []
    if locais:
        df = pd.DataFrame([{
            "nome_local": l.get("nome_local"),
            "cidade": l.get("cidade"),
            "latitude": l.get("coordenadas", {}).get("latitude"),
            "longitude": l.get("coordenadas", {}).get("longitude")
        } for l in locais])
        center_lat = float(df["latitude"].mean())
        center_lon = float(df["longitude"].mean())
        r = pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=10),
            layers=[pdk.Layer("ScatterplotLayer", data=df, get_position="[longitude, latitude]", get_radius=80)]
        )
        st.pydeck_chart(r, use_container_width=True)
    else:
        st.info("Sem dados para exibir no mapa")

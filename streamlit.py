import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Konfiguracja strony
st.set_page_config(page_title="Kursy Walut NBP", page_icon="💱", layout="wide")

# Tytuł aplikacji
st.title("💱 Kursy Walut NBP")
st.markdown("Aplikacja pobierająca dane z API Narodowego Banku Polskiego")

# Sidebar z opcjami
st.sidebar.header("Ustawienia")

# Lista popularnych walut
waluty = {
    "USD": "Dolar amerykański",
    "EUR": "Euro",
    "GBP": "Funt szterling",
    "CHF": "Frank szwajcarski",
    "JPY": "Jen japoński",
    "CZK": "Korona czeska",
    "SEK": "Korona szwedzka",
    "NOK": "Korona norweska"
}

# Wybór waluty
wybrana_waluta = st.sidebar.selectbox(
    "Wybierz walutę:",
    options=list(waluty.keys()),
    format_func=lambda x: f"{x} - {waluty[x]}"
)

# Wybór liczby dni historycznych
dni = st.sidebar.slider("Liczba dni historii:", min_value=7, max_value=90, value=30)

# Wybór typu tabeli
typ_tabeli = st.sidebar.radio("Typ tabeli NBP:", ["A", "B", "C"])

# Funkcja pobierająca aktualny kurs
@st.cache_data(ttl=3600)
def pobierz_aktualny_kurs(waluta, tabela):
    url = f"https://api.nbp.pl/api/exchangerates/rates/{tabela}/{waluta}/?format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

# Funkcja pobierająca dane historyczne
@st.cache_data(ttl=3600)
def pobierz_dane_historyczne(waluta, tabela, liczba_dni):
    url = f"https://api.nbp.pl/api/exchangerates/rates/{tabela}/{waluta}/last/{liczba_dni}/?format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return None

# Główna sekcja - aktualny kurs
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Aktualny kurs")
    dane_aktualne = pobierz_aktualny_kurs(wybrana_waluta, typ_tabeli.lower())
    
    if dane_aktualne:
        kurs = dane_aktualne['rates'][0]['mid']
        data = dane_aktualne['rates'][0]['effectiveDate']
        
        st.metric(
            label=f"{wybrana_waluta} - {waluty[wybrana_waluta]}",
            value=f"{kurs:.4f} PLN"
        )
        st.info(f"Data: {data}")
        st.caption(f"Tabela: {typ_tabeli}")

with col2:
    st.subheader("📈 Wykres historyczny")
    dane_historyczne = pobierz_dane_historyczne(wybrana_waluta, typ_tabeli.lower(), dni)
    
    if dane_historyczne:
        # Przygotowanie danych do wykresu
        df = pd.DataFrame(dane_historyczne['rates'])
        df['effectiveDate'] = pd.to_datetime(df['effectiveDate'])
        
        # Wykres liniowy
        fig = px.line(
            df,
            x='effectiveDate',
            y='mid',
            title=f"Kurs {wybrana_waluta}/PLN - ostatnie {dni} dni",
            labels={'effectiveDate': 'Data', 'mid': 'Kurs (PLN)'},
            markers=True
        )
        
        fig.update_layout(
            hovermode='x unified',
            xaxis_title="Data",
            yaxis_title="Kurs (PLN)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statystyki
        st.subheader("📉 Statystyki")
        col3, col4, col5, col6 = st.columns(4)
        
        with col3:
            st.metric("Minimum", f"{df['mid'].min():.4f} PLN")
        with col4:
            st.metric("Maximum", f"{df['mid'].max():.4f} PLN")
        with col5:
            st.metric("Średnia", f"{df['mid'].mean():.4f} PLN")
        with col6:
            zmiana = ((df['mid'].iloc[-1] - df['mid'].iloc[0]) / df['mid'].iloc[0] * 100)
            st.metric("Zmiana", f"{zmiana:.2f}%")
        
        # Tabela danych
        with st.expander("🗂️ Zobacz dane tabelaryczne"):
            df_display = df[['effectiveDate', 'mid']].copy()
            df_display.columns = ['Data', 'Kurs (PLN)']
            df_display = df_display.sort_values('Data', ascending=False)
            st.dataframe(df_display, use_container_width=True)

# Stopka
st.markdown("---")
st.markdown("**Źródło danych:** [API NBP](https://api.nbp.pl) | Dane aktualizowane codziennie przez NBP")
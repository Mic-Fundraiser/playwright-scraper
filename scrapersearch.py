import streamlit as st
from playwright.sync_api import sync_playwright
import pandas as pd

def fetch_google_results(keyword, headless=False):
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        page.goto('https://google.com')
        
        # Gestisci il consenso ai cookie se necessario
        accept_button_selector = '.QS5gu.sy4vM'
        if page.is_visible(accept_button_selector):
            page.click(accept_button_selector)
        
        # Effettua la ricerca
        search_input_selector = '.gLFyf'
        page.fill(search_input_selector, keyword)
        page.press(search_input_selector, 'Enter')
        page.wait_for_load_state("networkidle")
        
        # Estrai i risultati
        titles = page.query_selector_all('#search a h3')
        urls = [title.evaluate("e => e.closest('a').href") for title in titles]
        for title, url in zip(titles, urls):
            results.append({"Title": title.inner_text(), "URL": url})
        
        browser.close()
    return results

def highlight_rows(df1, df2):
    # Crea una colonna per l'evidenziazione basata sul match di titolo e URL
    match = []
    for index, row in df1.iterrows():
        if any((df2['Title'] == row['Title']) & (df2['URL'] == row['URL'])):
            match.append('background-color: lightgreen')
        else:
            match.append('')
    return match

def serp_comparator_app():
    st.title('Comparatore di SERP')
    
    col1, col2 = st.columns(2)
    with col1:
        keyword1 = st.text_input("Parola chiave 1", value="")
    with col2:
        keyword2 = st.text_input("Parola chiave 2", value="")
    
    if st.button("Confronta SERP"):
        if keyword1 and keyword2:
            with st.spinner("Fetching SERP results..."):
                results1 = fetch_google_results(keyword1, headless=True)
                results2 = fetch_google_results(keyword2, headless=True)
                
                df1 = pd.DataFrame(results1)
                df2 = pd.DataFrame(results2)
                
                # Applica l'evidenziazione
                df1_style = df1.style.apply(lambda x: highlight_rows(df1, df2), axis=0)
                df2_style = df2.style.apply(lambda x: highlight_rows(df2, df1), axis=0)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Risultati per: {keyword1}")
                    st.dataframe(df1_style)
                with col2:
                    st.write(f"Risultati per: {keyword2}")
                    st.dataframe(df2_style)
        else:
            st.error("Inserisci entrambe le parole chiave per il confronto.")

if __name__ == "__main__":
    serp_comparator_app()

import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Sett opp stier og hent historiske rådata fra Excel-filen din
skript_mappe = os.path.dirname(os.path.abspath(__file__))
# Filnavnet er satt til nøyaktig 'Utslippsregnskap_Oslo.xlsx'
filsti = os.path.join(skript_mappe, '..', 'data', 'Utslippsregnskap_Oslo.xlsx')

# Les hovedoversikten (Fane: 'Oversikt')
df_oversikt = pd.read_excel(filsti, sheet_name='Oversikt')

# Grupper for å finne totalen per år og beregn 2009-referanse
df_total = df_oversikt.groupby('År')['Utslipp (tonn CO₂-ekvivalenter)'].sum().reset_index().sort_values('År')
utslipp_2009 = df_total[df_total['År'] == 2009]['Utslipp (tonn CO₂-ekvivalenter)'].values[0]

siste_historiske_aar = df_total['År'].max()
siste_utslipp = df_total[df_total['År'] == siste_historiske_aar]['Utslipp (tonn CO₂-ekvivalenter)'].values[0]

# Målsetning (95 % kutt fra 2009 innen 2030)
maal_2030 = utslipp_2009 * (1 - 0.95)


# 2. GENERER GRAFENE FRA HISTORISKE DATA (Seksjon 1 & 2)

# Graf A: Historisk trend og opprinnelig målbane
maal_aar = [siste_historiske_aar, 2025, 2030]
maal_verdier = [siste_utslipp, utslipp_2009 * (1 - 0.65), maal_2030]

fig_hoved = go.Figure()
fig_hoved.add_trace(go.Scatter(x=df_total['År'], y=df_total['Utslipp (tonn CO₂-ekvivalenter)'], mode='lines+markers', name='Historiske utslipp', line=dict(color='#1f77b4', width=4)))
fig_hoved.add_trace(go.Scatter(x=maal_aar, y=maal_verdier, mode='lines+markers', name='Målbane mot 2030 (95% kutt)', line=dict(color='#2ca02c', width=3, dash='dash')))
fig_hoved.update_layout(title='<b>Oslos klimagassutslipp og veien mot 2030</b>', xaxis_title='År', yaxis_title='Tonn CO₂-ekv', template='plotly_white', hovermode='x unified')

# Graf B: Overordnet sektorgraf for siste tilgjengelige år
df_siste_aar = df_oversikt[df_oversikt['År'] == siste_historiske_aar].sort_values('Utslipp (tonn CO₂-ekvivalenter)', ascending=True)
fig_sektor = px.bar(df_siste_aar, x='Utslipp (tonn CO₂-ekvivalenter)', y='Sektor', orientation='h', title=f'<b>Hovedsektorer i Oslo ({siste_historiske_aar})</b>', template='plotly_white', color='Utslipp (tonn CO₂-ekvivalenter)', color_continuous_scale='Reds')
fig_sektor.update_layout(showlegend=False)

# Graf C: Dypdykk Veitrafikk
df_vei = pd.read_excel(filsti, sheet_name='Veitrafikk')
df_vei_trend = df_vei.groupby(['År', 'Utslippskilde'])['Utslipp (tonn CO₂-ekvivalenter)'].sum().reset_index()
fig_vei = px.line(df_vei_trend, x='År', y='Utslipp (tonn CO₂-ekvivalenter)', color='Utslippskilde', title='<b>Veitrafikk: Utvikling per kjøretøytype</b>', template='plotly_white', markers=True)

# Graf D: Dypdykk Annen mobil forbrenning
df_mobil = pd.read_excel(filsti, sheet_name='Annen mobil forbrenning')
df_mobil_trend = df_mobil.groupby(['År', 'Utslippskilde'])['Utslipp (tonn CO₂-ekvivalenter)'].sum().reset_index()
fig_mobil = px.bar(df_mobil_trend, x='År', y='Utslipp (tonn CO₂-ekvivalenter)', color='Utslippskilde', title='<b>Annen mobil forbrenning: Fordeling over tid</b>', template='plotly_white')

# Graf E: Dypdykk Energiforsyning
df_energi = pd.read_excel(filsti, sheet_name='Energiforsyning')
df_energi_trend = df_energi.groupby(['År', 'Utslippskilde'])['Utslipp (tonn CO₂-ekvivalenter)'].sum().reset_index()
fig_energi = px.area(df_energi_trend, x='År', y='Utslipp (tonn CO₂-ekvivalenter)', color='Utslippskilde', title='<b>Energiforsyning: Utvikling (Avfallsforbrenning utgjør størstedelen)</b>', template='plotly_white')


# 3. GENERER SCENARIOGRAFEN OG TILTAKSDIAGRAMMET (Seksjon 3)

aar_scenarier = [siste_historiske_aar, 2025, 2028, 2030]

# Scenario 1: Bane med vedtatte tiltak fra Klimabudsjettet
utslipp_med_tiltak = [
    siste_utslipp,
    max(0, siste_utslipp - 75000),
    max(0, siste_utslipp - 268300),
    max(0, siste_utslipp - 268300)
]

# Scenario 2: Den offisielle målbanen frem til 2030 (95% kutt)
utslipp_maalbane = [
    siste_utslipp,
    utslipp_2009 * (1 - 0.65), 
    utslipp_2009 * (1 - 0.83), 
    maal_2030                  
]

fig_scenarier = go.Figure()
fig_scenarier.add_trace(go.Scatter(x=df_total['År'], y=df_total['Utslipp (tonn CO₂-ekvivalenter)'], mode='lines+markers', name='Historiske utslipp', line=dict(color='#1f77b4', width=4)))
fig_scenarier.add_trace(go.Scatter(x=aar_scenarier, y=utslipp_med_tiltak, mode='lines+markers', name='Bane med vedtatte tiltak (Klimabudsjettet)', line=dict(color='#ff7f0e', width=3, dash='dash')))
fig_scenarier.add_trace(go.Scatter(x=aar_scenarier, y=utslipp_maalbane, mode='lines+markers', name='Offisiell målbane (95% kutt i 2030)', line=dict(color='#2ca02c', width=3, dash='dot')))
fig_scenarier.update_layout(title='<b>Klimagapet: Vedtatte tiltak vs. Offisielt mål</b>', xaxis_title='År', yaxis_title='Tonn CO₂-ekv', template='plotly_white', hovermode='x unified')

# Stolpediagram over enkelttiltak i 2028
tiltak_data = {
    'Tiltak': ['Krav til reguleringsplaner', 'Utslippsfrie lastebiler', 'Krav til kommunale byggeplasser', 'Utslippsfrie drosjer', 'Insentiver for varebiler', 'Landstrøm i Havna', 'Utslippsfrie leveranser'],
    'Effekt_2028': [35600, 18500, 18600, 11000, 9800, 8000, 9000]
}
df_tiltak = pd.DataFrame(tiltak_data).sort_values('Effekt_2028', ascending=True)
fig_tiltak_bar = px.bar(df_tiltak, x='Effekt_2028', y='Tiltak', orientation='h', title='<b>De mest effektive klimatiltakene i Oslo mot 2028</b>', template='plotly_white', color='Effekt_2028', color_continuous_scale='Greens')
fig_tiltak_bar.update_layout(showlegend=False)


# 4. KLARGJØR DEN INTERAKTIVE SIMULATORGRAFEN (Seksjon 4)
fig_sim = go.Figure()
fig_sim.add_trace(go.Scatter(x=df_total['År'], y=df_total['Utslipp (tonn CO₂-ekvivalenter)'], mode='lines+markers', name='Historiske utslipp', line=dict(color='#1f77b4', width=4)))
fig_sim.add_trace(go.Scatter(x=[2009, 2030], y=[utslipp_2009, maal_2030], mode='lines', name='Målbane mot 2030', line=dict(color='#2ca02c', width=2, dash='dot')))

# Simuleringslinjen inneholder hvert enkelt år som et eget punkt på x-aksen
sim_aar_liste = list(range(int(siste_historiske_aar), 2031))
fig_sim.add_trace(go.Scatter(x=sim_aar_liste, y=[siste_utslipp] * len(sim_aar_liste), mode='lines+markers', name='Din simulerte bane', line=dict(color='#d62728', width=4)))

fig_sim.update_layout(
    title='<b>Interaktiv Simulator: Bygg arbeidsgruppens tidslinje</b>',
    xaxis_title='År', yaxis_title='Tonn CO₂-ekv',
    template='plotly_white',
    xaxis=dict(range=[2018, 2031], dtick=1), # Tvinger ett hakk per år
    hovermode='x unified'
)


# 5. GENERER STOLPEDIAGRAM FOR NYE MULIGE VIRKEMIDLER (Seksjon 5)
nye_tiltak_data = {
    'Virkemiddel': ['CO2-avgift 2000kr', '33% bio veitrafikk', 'Dobbeltakst pers.bil', 'Dobbeltakst varebil', 'Nullutslippssone (tung)', 'Nullutslippssone (pers)', 'Avgift komm. parkering', 'Varebilpakke', 'Nasjonal pakke tung', 'Bussløyver', 'CCS husholdning', 'Hafslund CCS', 'Plastsortering', 'Tekstilgjenvinning', 'Fossilfri fjernvarme', 'Maskiner krav 2030', 'Maskiner 28% bio', 'Utenriksferger', 'Godsskip landstrøm', 'Forbud gass byggvarme'],
    'Effekt (Snitt)': [13000, 37000, 2250, 3000, 13000, 1500, 1500, 3000, 6000, 2500, 45000, 24000, 18500, 3000, 5000, 8000, 10500, 9000, 2000, 17500]
}
df_nye_tiltak = pd.DataFrame(nye_tiltak_data).sort_values('Effekt (Snitt)', ascending=True)
fig_nye_tiltak = px.bar(df_nye_tiltak, x='Effekt (Snitt)', y='Virkemiddel', orientation='h', title='<b>Potensielle nye virkemidler (Snittberegnet effekt i tonn CO₂)</b>', template='plotly_white', color='Effekt (Snitt)', color_continuous_scale='Mint')
fig_nye_tiltak.update_layout(showlegend=False)


# 6. BYGG DEN KOMPLETTE HTML-SIDEN (Med oppdatert JavaScript-motor og samlet valg)
with open("index.html", "w", encoding="utf-8") as f:
    f.write("<html><head>")
    f.write('<meta charset="utf-8">') 
    f.write("<title>Oslos Utvidede Klimadashboard og Simulator</title>")
    f.write("<style>body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f6f8; color: #333; font-size: 14px; } .container { max-width: 1200px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; } h1, h2, h3 { color: #00472e; margin-top: 10px; margin-bottom: 10px; } hr { border: 0; height: 1px; background: #ddd; margin: 20px 0; } .simulator-box { background: #f9f9f9; padding: 15px; border-radius: 6px; border: 1px solid #e0e0e0; margin-top: 15px; } .simulator-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; } .sim-seksjon { background: #fff; padding: 12px; border-radius: 6px; border: 1px solid #ddd; } .tiltak-grid { display: flex; flex-direction: column; gap: 6px; margin-top: 10px; } .tiltak-row { display: grid; grid-template-columns: 3fr 1fr; align-items: center; background: #fafafa; padding: 6px 10px; border-radius: 4px; border: 1px solid #eee; font-size: 0.88em; line-height: 1.3em; } .tiltak-row select { padding: 4px 6px; font-size: 0.9em; border-radius: 4px; border: 1px solid #ccc; cursor: pointer; } .tag-sektor { font-weight: bold; font-size: 0.8em; text-transform: uppercase; color: #555; display: block; margin-bottom: 2px; } .samlet-valg { display: flex; align-items: center; gap: 10px; background: white; padding: 10px; border-radius: 6px; border: 1px solid #ddd; margin-top: 15px; font-weight: bold; } .samlet-valg select { padding: 6px 10px; font-size: 1em; border-radius: 4px; border: 1px solid #ccc; cursor: pointer; } .sources { font-size: 0.85em; color: #555; line-height: 1.5em; } </style>")
    f.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')
    f.write("</head><body>")
    
    f.write("<div class='container'><h1>Oslos Klimadashboard: Fra Historie til Fremtid</h1></div>")
    
    # Historiske grafer (Seksjon 1, 2, 3)
    f.write("<div class='container'><h2>1. Overordnet status og historisk trend</h2>")
    f.write(fig_hoved.to_html(full_html=False, include_plotlyjs=False))
    f.write("<br>")
    f.write(fig_sektor.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    f.write("<div class='container'><h2>2. Detaljerte dypdykk i de største historiske kildene</h2>")
    f.write(fig_vei.to_html(full_html=False, include_plotlyjs=False))
    f.write(fig_mobil.to_html(full_html=False, include_plotlyjs=False))
    f.write(fig_energi.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    f.write("<div class='container'><h2>3. Fremtidsbaner, klimagap og virkemidler</h2>")
    f.write(fig_scenarier.to_html(full_html=False, include_plotlyjs=False))
    f.write("<br>")
    f.write(fig_tiltak_bar.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    
    # NYTT FIGUR: Visualisering av nye tiltak
    f.write("<div class='container'><h2>4. Visualisering av potensielle nye virkemidler</h2>")
    f.write(fig_nye_tiltak.to_html(full_html=False, include_plotlyjs=False))
    f.write("</div>")
    
    # INTERAKTIV SIMULATOR (Oppdatert)
    f.write("<div class='container' id='simulator-seksjon'><h2>5. Interaktiv simulator: Konfigurer tidslinjen</h2>")
    f.write("<p>Angi spesifikt innføringsår for vedtatte hovedtiltak. For alle potensielle nye virkemidler, bruk det samlede valget under grafen for å bestemme tidslinjen.</p>")
    f.write(fig_sim.to_html(full_html=False, include_plotlyjs=False, div_id="sim-plot-div"))
    
    f.write("<div class='simulator-box'><h3>Vedtatte tiltak:</h3><div class='tiltak-grid'>")
    
    def lag_vedtatt_rad(id_navn, tittel_tekst):
        html = f"<div class='tiltak-row'>"
        html += f"<span>{tittel_tekst}</span>"
        html += f"<select id='{id_navn}' onchange='oppdaterSimulator()'>"
        html += "<option value='inaktiv'>Inaktivt</option>"
        for aar in range(2026, 2031):
            html += f"<option value='{aar}'>Innføres i {aar}</option>"
        html += "</select></div>"
        return html

    f.write(lag_vedtatt_rad('t_klemetsrud', '<b>Karbonfangst Klemetsrud (Est. 400k tonn)</b>'))
    f.write(lag_vedtatt_rad('t_regplan', 'Krav i reguleringsplaner (35.6k tonn)'))
    f.write(lag_vedtatt_rad('t_last', 'Utslippsfrie lastebiler (18.5k tonn)'))
    f.write(lag_vedtatt_rad('t_drosje', 'Utslippsfrie drosjer (11k tonn)'))
    f.write("</div></div>")
    
    # SAMLET VALG FOR NYE VIRKEMIDLER
    f.write("<div class='samlet-valg'>")
    f.write("<label for='nye_valg'><b>Nye potensielle virkemidler (samlet pakke):</b></label>")
    f.write("<select id='nye_valg' onchange='oppdaterSimulator()'>")
    f.write("<option value='inaktiv'>Inaktiv pakke</option>")
    for aar in range(2026, 2031):
        f.write(f"<option value='{aar}'>Hele pakken fra {aar}</option>")
    f.write("</select></div>")
    
    f.write("</div>")
    
    # OPPDATERT JAVASCRIPT-MOTOR
    f.write("<script>")
    f.write(f"""
    const sisteUtslipp = {siste_utslipp};
    const sisteAar = {siste_historiske_aar};
    
    const tiltaksListeVedtatt = [
        {{ id: 't_klemetsrud', kutt: 400000 }},
        {{ id: 't_regplan',    kutt: 35600 }},
        {{ id: 't_last',       kutt: 18500 }},
        {{ id: 't_drosje',     kutt: 11000 }}
    ];
    
    const samletKuttNye = 260750; // Summen av alle snitt-kuttene i pakken
    
    function oppdaterSimulator() {{
        let simAar = [];
        let simVerdier = [];
        
        for (let a = sisteAar; a <= 2030; a++) {{
            simAar.push(a);
            
            if (a === sisteAar) {{
                simVerdier.push(sisteUtslipp);
            }} else {{
                let samletKuttDetteAar = 0;
                
                tiltaksListeVedtatt.forEach(tiltak => {{
                    let valgtInnforingsAar = document.getElementById(tiltak.id).value;
                    if (valgtInnforingsAar !== 'inaktiv' && parseInt(valgtInnforingsAar) <= a) {{
                        samletKuttDetteAar += tiltak.kutt;
                    }}
                }});
                
                let nyeValgAar = document.getElementById('nye_valg').value;
                if (nyeValgAar !== 'inaktiv' && parseInt(nyeValgAar) <= a) {{
                    samletKuttDetteAar += samletKuttNye;
                }}
                
                let beregnetUtslipp = Math.max(0, sisteUtslipp - samletKuttDetteAar);
                simVerdier.push(beregnetUtslipp);
            }}
        }}
        
        Plotly.restyle('sim-plot-div', {{
            x: [simAar],
            y: [simVerdier]
        }}, [2]);
    }}
    
    oppdaterSimulator();
    """)
    f.write("</script>")
    
    # Datakilder i bunnen
    f.write("<div class='container sources'><h2>Datakilder</h2><ul><li>miljodirektoratet.no, klimaoslo.no</li></ul></div>")
    
    f.write("</body></html>")

print("index.html er oppdatert med en figur over nye tiltak og samlet valg for å redusere trykking!")
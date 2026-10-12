"""Plotly rendering of the already aggregated tables. No CSV access."""

from html import escape
from math import ceil
import textwrap

import plotly.graph_objects as go

from src.market_metrics import MISSING
from src.schema import SURVEY_LABELS

# Compact display aliases only; original questionnaire labels remain in tables.
SHORT_LABELS = {
    "professional_services": "Professional services", "healthcare_allied": "Healthcare & allied health",
    "retail_ecommerce": "Retail & e-commerce", "trades_construction": "Trades & construction",
    "real_estate": "Real estate & property", "manufacturing_logistics": "Manufacturing & logistics",
    "education_training": "Education & training", "other": "Other",
    "customer_enquiries": "Customer enquiries", "sales_followup": "Sales follow-up",
    "appointment_scheduling": "Appointments", "manual_data_entry": "Manual data entry",
    "reporting_analysis": "Reporting & analysis", "documents_information": "Documents & information",
    "finance_invoicing": "Finance & invoicing", "staff_coordination": "Staff coordination",
    "customer_support": "Customer support", "marketing_content": "Marketing & content",
    "regular_multiple": "Regular use", "limited_tasks": "Specific tasks", "experimented": "Experimented",
    "not_using": "Not using", "unsure": "Not sure", "scale_without_staff_growth": "Grow without proportional hiring",
}


def label(field, code, short=False):
    if code == MISSING:
        return "Missing answer"
    if short and code in SHORT_LABELS:
        return SHORT_LABELS[code]
    return SURVEY_LABELS[field].get(code, code.replace("_", " ").capitalize())


def wrap_label(value, width=24):
    return "<br>".join(escape(line) for line in textwrap.wrap(value, width))


def style_chart(fig, tokens, height):
    fig.update_layout(template="none", height=height, paper_bgcolor=tokens["surface"],
                      plot_bgcolor=tokens["surface"], font=dict(family="Inter, sans-serif", size=12, color=tokens["foreground"]),
                      margin=dict(l=8, r=24, t=16, b=40),
                      hoverlabel=dict(bgcolor=tokens["surface"], font_color=tokens["foreground"]),
                      legend=dict(orientation="h", y=-.2, x=0, font_size=12))
    fig.update_xaxes(gridcolor=tokens["border"], zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor=tokens["border"], zeroline=False, automargin=True)
    return fig


def bar_chart(table, field, tokens, ordered=False):
    rows = table if ordered else table.sort_values("count", ascending=False, kind="stable")
    custom = [[label(field, r.category), r.count, r.denominator] for r in rows.itertuples()]
    text = [f"{r.count}/{r.denominator} · {r.percentage:.0f}%" if r.denominator else "No answers" for r in rows.itertuples()]
    fig = go.Figure(go.Bar(x=rows["percentage"].tolist(),
        y=[wrap_label(label(field, code, short=True)) for code in rows["category"]], orientation="h",
        marker_color=tokens["chart-1"], text=text, textposition="outside", cliponaxis=False,
        textfont_color=tokens["foreground"], customdata=custom,
        hovertemplate="%{customdata[0]}<br>%{customdata[1]} / %{customdata[2]} respondents · %{x:.1f}%<extra></extra>"))
    style_chart(fig, tokens, max(350, len(rows) * 45 + 75))
    fig.update_yaxes(autorange="reversed", tickfont_size=11)
    fig.update_xaxes(title="% of respondents who answered", range=[0, 125], tickvals=[0,25,50,75,100], ticksuffix="%")
    return fig


def survey_bar_summary(table, field):
    """Descriptive summary of the selected answers, not an inferred market claim."""
    if table.empty or not table['denominator'].gt(0).any():
        return 'No recorded answers in this selection.'
    top = table.loc[table['count'].eq(table['count'].max())]
    first = top.iloc[0]
    names = ', '.join(label(field,c,short=True) for c in top['category'].iloc[:3])
    if len(top) > 3:
        names += f' and {len(top)-3} other categories'
    lead = 'Most reported' if field == 'pain_points' else 'Largest group'
    if len(top) > 1:
        lead = 'Joint highest'
    return (f'{lead}: {names} — {first["count"]} of {first.denominator} answered responses '
            f'({first.percentage:.1f}%)' + (' each.' if len(top)>1 else '.') + ' In the current selection.')


def survey_bar_chart(table, field, tokens, ordered=False, highlight_token='survey-highlight'):
    """Fixed-scale tracks with label/value headers above each rounded bar."""
    rows = table if ordered else table.sort_values('count',ascending=False,kind='stable')
    positions = list(range(len(rows)))
    custom = [[label(field,r.category),r.count,r.denominator,r.percentage] for r in rows.itertuples()]
    hover = ('%{customdata[0]}<br>Respondents: %{customdata[1]}<br>'
             'Answered denominator: %{customdata[2]}<br>Percentage: %{customdata[3]:.1f}%<extra></extra>')
    fig = go.Figure(go.Bar(x=[100]*len(rows),y=positions,orientation='h',width=.25,offset=-.125,
        marker_color=tokens['survey-track'],customdata=custom,hovertemplate=hover,showlegend=False))
    maximum = rows['count'].max()
    fig.add_trace(go.Bar(x=rows['percentage'].tolist(),y=positions,orientation='h',width=.25,offset=-.125,xaxis='x2',
        marker_color=[tokens[highlight_token] if r.count == maximum and maximum > 0 else tokens['survey-bar']
                      for r in rows.itertuples()],customdata=custom,hovertemplate=hover,showlegend=False))
    row_height = 80 if field == 'ai_concerns' else 64
    style_chart(fig,tokens,len(rows)*row_height+55)
    fig.update_layout(barmode='overlay',barcornerradius=7,margin=dict(l=0,r=0,t=8,b=35),
                      hoverlabel=dict(namelength=-1),transition_duration=0)
    for index,row in enumerate(rows.itertuples()):
        fig.add_annotation(x=0,xref='paper',y=index-.30,text=wrap_label(label(field,row.category,short=True),25),
            xanchor='left',yanchor='bottom',showarrow=False,align='left',font=dict(size=12,color=tokens['foreground']))
        fig.add_annotation(x=1,xref='paper',y=index-.30,text=f'{row.percentage:.1f}%' if row.denominator else 'N/A',
            xanchor='right',yanchor='bottom',showarrow=False,font=dict(size=12,color=tokens['foreground']))
    fig.update_yaxes(range=[len(rows)-.5,-.85],visible=False,fixedrange=True)
    for x,anchor in [(0,'left'),(.5,'center'),(1,'right')]:
        fig.add_annotation(x=x,xref='paper',y=0,yref='paper',yshift=-24,text=f'{int(x*100)}%',
            xanchor=anchor,showarrow=False,font=dict(size=11,color=tokens['foreground']))
    fig.update_xaxes(range=[0,100],showticklabels=False,showgrid=False,
                     fixedrange=True,tickfont=dict(size=11,color=tokens['foreground']),title=None)
    # Separate overlay axes prevent Plotly treating the filled bar as an inner
    # segment of the track and removing its rounded end. Both scales are 0–100.
    fig.update_layout(xaxis2=dict(overlaying='x',range=[0,100],visible=False,fixedrange=True))
    return fig


def outcome_column_chart(table, tokens):
    """Ranked S17 percentages, with a zero baseline and data-based headroom."""
    aliases = {
        'save_time':'Save time', 'reduce_costs':'Reduce costs',
        'increase_revenue':'Increase revenue', 'faster_responses':'Faster responses',
        'reduce_errors':'Reduce errors', 'improve_satisfaction':'Customer satisfaction',
        'scale_without_staff_growth':'Grow without proportional hiring', 'other':'Other',
    }
    rows = table.sort_values('count',ascending=False,kind='stable')
    custom = [[label('desired_outcome',r.category),r.count,r.denominator,r.percentage] for r in rows.itertuples()]
    hover = ('%{customdata[0]}<br>Respondents: %{customdata[1]}<br>'
             'Answered denominator: %{customdata[2]}<br>Percentage: %{customdata[3]:.1f}%<extra></extra>')
    maximum = rows['count'].max()
    x = [wrap_label(aliases[c],12) for c in rows['category']]
    y = rows['percentage'].tolist()
    fig = go.Figure(go.Bar(x=x,y=y,width=.55,
        marker=dict(color=[tokens['survey-iris'] if r.count==maximum and maximum>0 else tokens['survey-bar']
                           for r in rows.itertuples()],cornerradius=7),
        customdata=custom,hovertemplate=hover,showlegend=False))
    # Text points also provide hover targets for zero-height columns.
    fig.add_trace(go.Scatter(x=x,y=y,mode='text',
        text=[f'{r.percentage:.1f}%' if r.denominator else 'N/A' for r in rows.itertuples()],
        textposition='top center',textfont=dict(size=14,color=tokens['foreground']),
        cliponaxis=False,customdata=custom,hovertemplate=hover,showlegend=False))
    style_chart(fig,tokens,450)
    fig.update_layout(margin=dict(l=40,r=16,t=40,b=80),transition_duration=0)
    fig.update_xaxes(type='category',categoryorder='array',categoryarray=x,tickangle=0,
                     showgrid=False,fixedrange=True,tickfont=dict(size=12))
    valid_percentages = rows['percentage'].dropna()
    peak = float(valid_percentages.max()) if not valid_percentages.empty else 0
    # Round the padded maximum up to five percentage points; never imply >100%.
    ceiling = min(100,max(5,ceil(peak*1.25/5)*5))
    ticks = [ceiling*i/4 for i in range(5)]
    fig.update_yaxes(range=[0,ceiling],tickvals=ticks,ticktext=[f'{v:g}%' for v in ticks],fixedrange=True,
                     title=None,showgrid=True,gridwidth=1)
    return fig


def deep_periwinkle_scale(tokens):
    """Shared percentage scale for both industry heatmaps and their legends."""
    return [[stop / 100, tokens[f"pain-heat-{stop}"]] for stop in (0,25,50,75,100)]


def pain_heatmap(table, tokens):
    colorscale = deep_periwinkle_scale(tokens)
    groups = table["industry"].drop_duplicates().tolist()
    categories = table["category"].drop_duplicates().tolist()
    z, text, hover = [], [], []
    for group in groups:
        rows = table.loc[table["industry"].eq(group)].set_index("category").loc[categories]
        z.append(rows["percentage"].tolist())
        text.append([f"{r.percentage:.0f}%" if r.denominator else "—" for r in rows.itertuples()])
        hover.append([f"{escape(label('industry', group))}<br>{escape(label('pain_points', r.Index))}<br>"
                      f"{r.count} / {r.denominator} respondents · {r.percentage:.1f}%<br>"
                      f"Missing S06: {r.missing}" + ("<br>Small sample: fewer than 5 answers" if r.small_sample else "")
                      for r in rows.itertuples()])
    group_labels = []
    for group in groups:
        row = table.loc[table["industry"].eq(group)].iloc[0]
        group_labels.append(wrap_label(label("industry", group, short=True)) + f"<br>n={row.denominator}" + (" · small sample" if row.small_sample else ""))
    fig = go.Figure(go.Heatmap(z=z, x=[wrap_label(label("pain_points", c, short=True),16) for c in categories],
        y=group_labels,
        hovertext=hover, hovertemplate="%{hovertext}<extra></extra>", hoverongaps=False,
        colorscale=colorscale, zmin=0, zmax=100,
        xgap=3, ygap=3, colorbar=dict(title="%", thickness=10)))
    style_chart(fig, tokens, max(400,len(groups)*65+150))
    # Choose readable ink per cell instead of white text on every colour.
    for row_index, group_label in enumerate(group_labels):
        for column_index, category in enumerate(categories):
            value = z[row_index][column_index]
            fig.add_annotation(x=wrap_label(label("pain_points",category,short=True),16),
                y=group_label,text=text[row_index][column_index],showarrow=False,
                font=dict(size=12,color=heatmap_ink(value,tokens,colorscale)))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickangle=-40)
    return fig


def heatmap_ink(value, tokens, colorscale=None):
    """Pick the higher-contrast text colour against the interpolated cell fill."""
    if value != value:  # Missing denominator: use normal foreground on the card.
        return tokens["foreground"]
    def rgb(hex_color):
        return [int(hex_color[i:i+2],16)/255 for i in (1,3,5)]
    def luminance(channels):
        linear=[c/12.92 if c <= .04045 else ((c+.055)/1.055)**2.4 for c in channels]
        return sum(c*w for c,w in zip(linear,(.2126,.7152,.0722)))
    stops = colorscale if colorscale is not None else [
        [0,tokens["heat-low"]],[.5,tokens["heat-mid"]],[1,tokens["heat-high"]]]
    position = min(1,max(0,value/100))
    for (start,low),(end,high) in zip(stops,stops[1:]):
        if position <= end:
            fraction = (position-start)/(end-start)
            break
    background=luminance([a+(b-a)*fraction for a,b in zip(rgb(low),rgb(high))])
    def contrast(color):
        ink=luminance(rgb(color))
        return (max(ink,background)+.05)/(min(ink,background)+.05)
    return max((tokens["chart-ink"],tokens["chart-paper"]),key=contrast)


def ai_stacked_chart(table, tokens):
    fig = go.Figure()
    groups = table["industry"].drop_duplicates().tolist()
    colors = [tokens[k] for k in ("ai-regular","ai-specific","ai-experimented","ai-not-using","ai-unsure")]
    for index, code in enumerate(SURVEY_LABELS["ai_adoption"]):
        rows = table.loc[table["category"].eq(code)].set_index("industry").loc[groups]
        custom = [[r.count,r.denominator,r.missing] for r in rows.itertuples()]
        y = [wrap_label(label("industry", g, short=True)) + f"<br>n={rows.loc[g,'denominator']}" +
             (" · small sample" if rows.loc[g,"small_sample"] else "") for g in groups]
        fig.add_trace(go.Bar(name=label("ai_adoption",code,short=True), x=rows["percentage"].tolist(), y=y,
            orientation="h", marker=dict(color=colors[index],line=dict(color=tokens["surface"],width=1.5)), customdata=custom,
            hovertemplate="%{y}<br>" + escape(label("ai_adoption",code)) + "<br>%{customdata[0]} / %{customdata[1]} · %{x:.1f}%<br>Missing S14: %{customdata[2]}<extra></extra>"))
    style_chart(fig, tokens, max(440,len(groups)*65+130))
    fig.update_layout(barmode="stack", legend=dict(y=-.15), margin=dict(b=110))
    fig.update_xaxes(range=[0,100], ticksuffix="%", title="Share of answered S14<br>within each industry")
    fig.update_yaxes(autorange="reversed")
    return fig


def ai_adoption_heatmap(table, tokens):
    """Five separate adoption columns; zero answers remain N/A, not zero usage."""
    colorscale = deep_periwinkle_scale(tokens)
    groups = table["industry"].drop_duplicates().tolist()
    categories = list(SURVEY_LABELS["ai_adoption"])
    columns = ["Regular<br>use", "Specific<br>tasks", "Experimented", "Not using<br>AI", "Not<br>sure"]
    z, custom, annotations, row_labels = [], [], [], []
    for group in groups:
        rows = table.loc[table["industry"].eq(group)].set_index("category").loc[categories]
        first = rows.iloc[0]
        row_label = wrap_label(label("industry",group,short=True),22) + f"<br>n={first.denominator}"
        if first.small_sample:
            row_label += " · small sample"
        elif not first.denominator:
            row_label += " · no answers"
        row_labels.append(row_label)
        z.append(rows["percentage"].tolist())
        custom.append([[label("industry",group),label("ai_adoption",r.Index),r.count,r.denominator,
                        f"{r.percentage:.1f}%" if r.denominator else "N/A",r.missing] for r in rows.itertuples()])
        for index, row in enumerate(rows.itertuples()):
            annotations.append(dict(x=columns[index],y=row_label,
                text=f"{round(row.percentage,1):g}%" if row.denominator else "N/A",showarrow=False,
                font=dict(size=12,color=heatmap_ink(row.percentage,tokens,colorscale))))
    hover_template = "%{customdata[0]}<br>%{customdata[1]}<br>Respondents: %{customdata[2]}<br>Answered denominator: %{customdata[3]}<br>Percentage: %{customdata[4]}<br>Missing S14: %{customdata[5]}<extra></extra>"
    fig = go.Figure(go.Heatmap(z=z,x=columns,y=row_labels,customdata=custom,
        colorscale=colorscale,
        zmin=0,zmax=100,xgap=3,ygap=3,hoverongaps=False,
        hovertemplate=hover_template,
        colorbar=dict(title="%",thickness=12)))
    if table['denominator'].eq(0).any():
        # A separate neutral mask gives N/A cells real hover targets. Plotly
        # drops an all-NaN heatmap; keep the percentage trace itself unchanged.
        mask=[[1 if cell[3]==0 else None for cell in row] for row in custom]
        fig.add_trace(go.Heatmap(z=mask,x=columns,y=row_labels,customdata=custom,
            colorscale=[[0,tokens['border']],[1,tokens['border']]],zmin=0,zmax=1,
            showscale=False,xgap=3,ygap=3,hoverongaps=False,hovertemplate=hover_template))
    style_chart(fig,tokens,max(300,len(groups)*72+100))
    fig.update_layout(annotations=annotations)
    fig.update_xaxes(side="top",tickangle=0,showgrid=False)
    fig.update_yaxes(autorange="reversed",showgrid=False)
    return fig


def ai_adoption_donut(rows, tokens):
    """One industry; use the same table as the heatmap without recalculation."""
    first = rows.iloc[0]
    fig = go.Figure()
    if first.denominator:
        fig.add_trace(go.Pie(labels=[label("ai_adoption",c,short=True) for c in rows["category"]],
            values=rows["count"].tolist(),hole=.65,sort=False,textinfo="none",showlegend=False,
            marker=dict(colors=[tokens[k] for k in ("ai-regular","ai-specific","ai-experimented","ai-not-using","ai-unsure")],
                        line=dict(color=tokens["surface"],width=1)),
            customdata=[[label("industry",r.industry),label("ai_adoption",r.category),r.denominator,r.percentage] for r in rows.itertuples()],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<br>Respondents: %{value}<br>Answered denominator: %{customdata[2]}<br>Percentage: %{customdata[3]:.1f}%<extra></extra>"))
    style_chart(fig,tokens,240)
    fig.update_layout(margin=dict(l=8,r=8,t=8,b=8),annotations=[dict(x=.5,y=.5,xref="paper",yref="paper",
        text=f"n={first.denominator}" if first.denominator else "N/A<br>No answers",showarrow=False,
        font=dict(size=18,color=tokens["foreground"]))])
    return fig

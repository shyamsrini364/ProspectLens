"""Plotly views of business-level evidence and actual research dates."""

from html import escape
import pandas as pd
import plotly.graph_objects as go

from src.market_charts import label, style_chart
from src.opportunity_config import CONFIG


def display(field,value):
    if value is None or pd.isna(value):
        return 'Not assessed'
    if field in ('industry','primary_pain_point','followup_interest'):
        return label(field,value,short=True)
    return str(value).replace('_',' ').capitalize()


def opportunity_matrix(frame,tokens,size_by_band=False):
    eligible=frame.dropna(subset=['value_score','commercial_score','overall_score'])
    fig=go.Figure()
    sizes={'solo':12,'2_5':16,'6_20':20,'21_50':24,'51_200':28,'over_200':32}
    colors={'High':tokens['success'],'Promising':tokens['survey-iris'],'Moderate':tokens['primary'],'Low':tokens['text-muted']}
    for band in colors:
        rows=eligible.loc[eligible['score_band'].eq(band)]
        if rows.empty:
            continue
        custom=[[escape(str(r.prospect_id)),escape(display('industry',r.industry)),
            escape(display('primary_pain_point',r.primary_pain_point)),r.value_score,r.commercial_score,r.overall_score,
            escape(display('followup_interest',r.followup_interest)),r.stage,r.discovery_count,
            display('complexity',r.implementation_complexity),r.prospect_id] for r in rows.itertuples()]
        fig.add_trace(go.Scatter(x=rows['commercial_score'].tolist(),y=rows['value_score'].tolist(),mode='markers',name=band,cliponaxis=False,
            marker=dict(size=[sizes.get(r.employee_band,12) if size_by_band else 15 for r in rows.itertuples()],
                        color=colors[band],line=dict(width=1,color=tokens['foreground']),opacity=.85),
            customdata=custom,hovertemplate='<b>%{customdata[0]}</b><br>%{customdata[1]}<br>%{customdata[2]}<br>'
            'Opportunity value: %{customdata[3]:.1f}<br>Commercial potential: %{customdata[4]:.1f}<br>Overall: %{customdata[5]:.1f}'
            '<br>Interest: %{customdata[6]}<br>%{customdata[7]} · %{customdata[8]} assessments<br>Complexity: %{customdata[9]}<extra></extra>'))
    style_chart(fig,tokens,540)
    threshold=CONFIG['quadrant_threshold']
    # Background shapes stay below points and grid lines, preserving hover/clicks.
    for x0,x1,y0,y1,token in [
        (0,threshold,threshold,100,'quadrant-value'),
        (threshold,100,threshold,100,'quadrant-promising'),
        (threshold,100,0,threshold,'quadrant-commercial'),
        (0,threshold,0,threshold,'quadrant-low'),
    ]:
        fig.add_shape(type='rect',xref='x',yref='y',x0=x0,x1=x1,y0=y0,y1=y1,
                      fillcolor=tokens[token],line_width=0,layer='below')
    fig.add_vline(x=threshold,line_dash='dot',line_color=tokens['text-muted'])
    fig.add_hline(y=threshold,line_dash='dot',line_color=tokens['text-muted'])
    for x,y,text in [(2,98,'High value / Low commercial'),(98,98,'High value / High commercial'),
                      (2,2,'Low value / Low commercial'),(98,2,'Low value / High commercial')]:
        fig.add_annotation(x=x,y=y,text=text,showarrow=False,xanchor='left' if x<50 else 'right',
            yanchor='top' if y>50 else 'bottom',font=dict(size=10,color=tokens['text-muted']))
    fig.update_layout(margin=dict(l=45,r=20,t=20,b=90),legend=dict(y=-.2),clickmode='event+select')
    fig.update_xaxes(range=[0,100],title='Commercial potential score',fixedrange=True)
    fig.update_yaxes(range=[0,100],title='Business opportunity value score',fixedrange=True)
    return fig


def trend_chart(table,tokens,cumulative=True,period='Weekly'):
    fig=go.Figure()
    # Aggregation remains unchanged: display the supplied totals at period ends.
    periods=pd.to_datetime(table['period']).dt.to_period('W-SUN' if period=='Weekly' else 'M')
    ends=periods.dt.end_time.dt.normalize().tolist()
    ranges=[f'{p.start_time:%d %b %Y} – {p.end_time:%d %b %Y}' for p in periods]
    count_label='Cumulative total at period end' if cumulative else 'New observations in period'
    # Separate series must remain distinguishable when bar accents are unified.
    for name,color in zip(table.columns[1:],['primary','survey-highlight','ai-experimented']):
        fig.add_trace(go.Scatter(x=ends,y=table[name].tolist(),name=name,
            mode='lines+markers',line=dict(color=tokens[color],width=3,shape='linear'),
            marker=dict(size=7,color=tokens[color],line=dict(width=1,color=tokens['surface'])),
            customdata=ranges,connectgaps=False,
            hovertemplate='<b>'+name+'</b><br>Period: %{customdata}<br>'+count_label+': %{y:,.0f}<extra></extra>'))
    style_chart(fig,tokens,390)
    fig.update_layout(margin=dict(l=40,r=20,t=20,b=100),legend=dict(y=-.25))
    fig.update_xaxes(title='Week ending' if period=='Weekly' else 'Month ending',showgrid=False,
                     nticks=6,tickformat='%d %b<br>%Y',automargin=True)
    fig.update_yaxes(title='Cumulative records' if cumulative else 'New records',rangemode='tozero',tickformat=',d')
    return fig

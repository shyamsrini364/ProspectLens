"""Optional real-browser checks; start Streamlit before running this script.

python -m scripts.smoke_test_market_dashboard
Uses installed Microsoft Edge in headless mode; screenshots stay in ignored data/.
Install requirements-dev.txt for Playwright. No browser download is needed on a
Windows machine with Edge installed. Override --channel for another installation.
"""

import argparse
import csv
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

from src.market_charts import label
from src.market_data import export_survey_csv, load_survey
from src.market_metrics import FILTER_FIELDS, filter_survey
from src.market_style import theme_tokens
from src.data_validation import validate_csv_files
from src.schema import SURVEY_COLUMNS


def first_ai_cell_hover(page):
    """Move the mouse over a real rendered cell, including an N/A cell."""
    plot=page.locator('.st-key-ai_heatmap_scroll .js-plotly-plot')
    plot.scroll_into_view_if_needed()
    xy=plot.evaluate('''el => {
        const r=el.getBoundingClientRect(), l=el._fullLayout;
        return [r.x+l.xaxis._offset+l.xaxis._length/10,
                r.y+l.yaxis._offset+l.yaxis._length/(2*el.data[0].y.length)];
    }''')
    page.mouse.move(*xy)
    expect(plot.locator('.hovertext')).to_be_visible()
    return plot.locator('.hovertext').text_content()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8501')
    parser.add_argument('--channel',default='msedge')
    parser.add_argument('--output-dir',type=Path,default=Path('data/dashboard_checks'))
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel=args.channel,headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1050},reduced_motion='reduce')
        page.on('pageerror',lambda error:errors.append(str(error)))
        response=page.goto(args.url)
        assert response.status==200
        expect(page.locator('[data-testid="stPlotlyChart"]')).to_have_count(6,timeout=30000)
        expect(page.get_by_role('button',name='Opportunity Intelligence',exact=True)).to_be_enabled()
        for mode in ['light','dark']:
            page.get_by_role('button',name='Main menu').click()
            page.get_by_role('menuitemradio',name=f'{mode}_mode {mode.title()}',exact=True).click()
            page.keyboard.press('Escape')
            tokens=theme_tokens(mode)
            page.wait_for_function("color => getComputedStyle(document.documentElement).getPropertyValue('--pl-surface').trim() === color",arg=tokens['surface'])
            page.wait_for_function("color => [...document.querySelectorAll('.js-plotly-plot')].length === 6 && [...document.querySelectorAll('.js-plotly-plot')].every(el => el._fullLayout.paper_bgcolor === color)",arg=tokens['surface'])
            for width in [1440,1024,768,390]:
                page.set_viewport_size({'width':width,'height':1050 if width>390 else 844})
                page.locator('.pl-brand').scroll_into_view_if_needed()
                page.screenshot(path=str(args.output_dir/f'{mode}_{width}_overview.png'))
                page.locator('.st-key-kpis').scroll_into_view_if_needed()
                page.screenshot(path=str(args.output_dir/f'{mode}_{width}_kpis.png'))
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth'),f'Page overflow at {width}'
                for section in ['pain','size','pain_industry','ai_industry','outcomes','concerns']:
                    panel=page.locator(f'.st-key-chart_{section}')
                    panel.scroll_into_view_if_needed()
                    bounds=panel.bounding_box()
                    assert bounds['x']>=0 and bounds['x']+bounds['width']<=width+1,(width,section,bounds)
                    page.screenshot(path=str(args.output_dir/f'{mode}_{width}_{section}.png'))
                assert page.locator('[data-testid="stException"]').count()==0
                if width==390:
                    heat_width=page.locator('.st-key-ai_heatmap_scroll .js-plotly-plot').evaluate('el => el._fullLayout.width')
                    assert heat_width>=640,heat_width
                print(f'PASS {mode} at {width}px: six charts, matching theme, panels within viewport')
        page.set_viewport_size({'width':1440,'height':1050})
        ai_panel=page.locator('.st-key-chart_ai_industry')
        heat=ai_panel.locator('.js-plotly-plot')
        assert heat.evaluate("el => el.data[0].type")=='heatmap'
        denominators=heat.evaluate("el => el.data[0].customdata.map(row => row[0][3])")
        assert denominators==sorted(denominators,reverse=True)
        assert heat.evaluate("el => el.layout.annotations.some(a => a.text === '0%')")
        cell=heat.evaluate('el => el.data[0].customdata[0][0]')
        hover=first_ai_cell_hover(page)
        for expected_text in [cell[0],cell[1],f'Respondents: {cell[2]}',f'Answered denominator: {cell[3]}',f'Percentage: {cell[4]}']:
            assert expected_text in hover,hover
        # Optional view uses the same industries; mobile stacks the donuts vertically.
        page.locator('[data-testid="stRadioOption"]').filter(has_text='Donut charts').click()
        expect(ai_panel.locator('.js-plotly-plot')).to_have_count(len(denominators))
        assert ai_panel.locator('.js-plotly-plot').evaluate_all("els => els.every(el => el.data[0].type === 'pie')")
        for width in [1440,390]:
            page.set_viewport_size({'width':width,'height':1050 if width>390 else 844})
            page.locator('.st-key-ai_donuts').scroll_into_view_if_needed()
            page.screenshot(path=str(args.output_dir/f'dark_{width}_ai_donuts.png'))
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            if width==390:
                bounds=[plot.bounding_box() for plot in ai_panel.locator('.js-plotly-plot').all()]
                assert all(b['y']>a['y'] for a,b in zip(bounds,bounds[1:])),bounds
        page.locator('[data-testid="stRadioOption"]').filter(has_text='Heatmap').click()
        expect(page.locator('[data-testid="stPlotlyChart"]')).to_have_count(6)
        page.set_viewport_size({'width':1440,'height':1050})
        print('PASS AI heatmap default, descending answered counts, zero percentages, donut selector and mobile stacking')
        frame=load_survey().frame
        example=frame.iloc[0]
        selected={field:[example[field]] for field in FILTER_FIELDS}
        expected=len(filter_survey(frame,selected))
        for index,field in enumerate(FILTER_FIELDS):
            page.get_by_role('combobox').nth(index).click()
            page.get_by_role('combobox',name= {'industry':'Industry','employee_band':'Business size',
                'primary_pain_point':'Primary pain point','ai_adoption':'AI adoption level'}[field],exact=True).fill(label(field,example[field]))
            page.get_by_role('option',name=label(field,example[field]),exact=True).click()
            page.keyboard.press('Escape')
            active={f:selected[f] for f in FILTER_FIELDS[:index+1]}
            expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(filter_survey(frame,active))),timeout=15000)
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(expected),timeout=15000)
        page.get_by_role('button',name='Main menu').click()
        expect(page.get_by_role('menuitem',name='Export filtered survey CSV',exact=True)).to_be_visible()
        items=page.get_by_role('menu').locator('[role="menuitem"]').all_text_contents()
        assert items[:2]==['Export filtered survey CSV','Manage data'],items
        assert page.locator('.st-key-data_menu').count()==0
        page.screenshot(path=str(args.output_dir/'corner_menu.png'))
        with page.expect_download() as download_info:
            page.get_by_role('menuitem',name='Export filtered survey CSV',exact=True).click()
        export_path=args.output_dir/'filtered_export.csv'
        download_info.value.save_as(str(export_path))
        export_result=validate_csv_files(export_path)
        assert export_result.valid and len(export_result.survey)==expected
        with export_path.open(encoding='utf-8-sig',newline='') as handle:
            assert next(csv.reader(handle))==SURVEY_COLUMNS
        page.keyboard.press('Escape')
        page.get_by_role('button',name='Reset filters',exact=True).click()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(frame)))
        page.get_by_role('button',name='Reset filters',exact=True).focus()
        # Move focus with a real keyboard event; inspect visible focus styling.
        page.keyboard.press('Tab')
        assert page.evaluate("getComputedStyle(document.activeElement).outlineStyle !== 'none'")
        assert page.evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches")
        page.get_by_role('button',name='Main menu').click()
        page.get_by_role('menuitem',name='Manage data',exact=True).click()
        dialog=page.get_by_role('dialog')
        dialog.locator('input[type=file]').nth(0).set_input_files({'name':'invalid.csv','mimeType':'text/csv','buffer':b'wrong,header\n1,2\n'})
        expect(dialog.get_by_text('Opportunity dataset validation failed.',exact=False)).to_be_visible()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(frame)))
        assert dialog.get_by_role('button',name='Use data in both dashboards').count()==0
        upload_frame=frame.iloc[:2].copy()
        upload_frame['ai_adoption']=None
        dialog.locator('input[type=file]').nth(0).set_input_files({'name':'uploaded.csv','mimeType':'text/csv',
            'buffer':export_survey_csv(upload_frame)})
        dialog.get_by_role('button',name='Use data in both dashboards',exact=True).click()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text('2')
        expect(page.get_by_text('Uploaded survey',exact=False).first).to_be_visible()
        expect(page.locator('.st-key-ai_heatmap_scroll .annotation-text').first).to_have_text('N/A')
        hover=first_ai_cell_hover(page)
        assert all(text in hover for text in ['Respondents: 0','Answered denominator: 0','Percentage: N/A']),hover
        page.screenshot(path=str(args.output_dir/'ai_na_hover.png'))
        print('PASS actual heatmap hovers for answered and zero-denominator cells')
        page.get_by_role('button',name='Main menu').click()
        with page.expect_download() as uploaded_download:
            page.get_by_role('menuitem',name='Export filtered survey CSV',exact=True).click()
        assert uploaded_download.value.suggested_filename=='market_intelligence_export.csv'
        uploaded_path=args.output_dir/'uploaded_export.csv'
        uploaded_download.value.save_as(str(uploaded_path))
        uploaded_result=validate_csv_files(uploaded_path)
        assert uploaded_result.valid and len(uploaded_result.survey)==2
        page.get_by_role('button',name='Main menu').click()
        page.get_by_role('menuitem',name='Manage data',exact=True).click()
        page.get_by_role('dialog').get_by_role('button',name='Restore synthetic demo for both dashboards').click()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(frame)))
        assert not errors,errors
        print('PASS one corner menu and action order, filtered download, invalid/valid uploads, uploaded-data export, restore demo, filters, keyboard focus, reduced motion; no JavaScript page errors')
        browser.close()
    return 0


if __name__=='__main__':
    raise SystemExit(main())

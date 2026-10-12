"""Real-browser opportunity checks; run with Streamlit already on port 8501."""

import csv
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

from src.opportunity_data import load_opportunities
from src.opportunity_metrics import build_businesses
from src.market_charts import label


def main():
    output=Path('data/opportunity_checks');output.mkdir(parents=True,exist_ok=True)
    data=load_opportunities();businesses=build_businesses(data)
    eligible=businesses.dropna(subset=['overall_score'])
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1050},reduced_motion='reduce')
        page.on('pageerror',lambda e:errors.append(str(e)))
        assert page.goto('http://127.0.0.1:8501').status==200
        page.get_by_role('button',name='Opportunity Intelligence',exact=True).click()
        expect(page.locator('.pl-hero h1')).to_have_text('Opportunity Intelligence')
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(businesses)))
        matrix=page.locator('.st-key-chart_opp_matrix .js-plotly-plot')
        matrix.wait_for(timeout=30000)
        assert matrix.evaluate('el=>el.data.reduce((n,t)=>n+t.x.length,0)')==len(eligible)
        for mode in ('light','dark'):
            page.get_by_role('button',name='Main menu').click()
            page.get_by_role('menuitemradio',name=f'{mode}_mode {mode.title()}',exact=True).click()
            page.keyboard.press('Escape')
            surface='#FFFFFF' if mode=='light' else '#252B46'
            page.wait_for_function('c=>document.querySelector(".st-key-chart_opp_matrix .js-plotly-plot")?._fullLayout.paper_bgcolor===c',arg=surface)
            for width in (1440,1024,768,390):
                page.set_viewport_size({'width':width,'height':1050 if width>390 else 844})
                page.locator('.pl-hero').scroll_into_view_if_needed()
                page.screenshot(path=str(output/f'{mode}_{width}_intro.png'))
                for section in ('matrix','ranking','recurring','trend','technical','downloads'):
                    panel=page.locator('.st-key-chart_opp_'+section)
                    panel.scroll_into_view_if_needed()
                    page.screenshot(path=str(output/f'{mode}_{width}_{section}.png'))
                    rect=panel.bounding_box()
                    assert rect['x']>=0 and rect['x']+rect['width']<=width+1
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert page.locator('[data-testid="stException"]').count()==0
                print(f'PASS opportunity {mode} {width}px: panels fit, theme applied, no app exceptions')
        page.set_viewport_size({'width':1440,'height':1050})
        page.get_by_role('button',name='How scores work',exact=True).click()
        dialog=page.get_by_role('dialog')
        expect(dialog).to_be_visible()
        expect(dialog.get_by_text('A — Business Opportunity Value (0–100)',exact=True)).to_be_visible()
        page.screenshot(path=str(output/'methodology_dialog.png'))
        page.keyboard.press('Escape')
        expect(dialog).to_have_count(0)
        matrix.scroll_into_view_if_needed()
        # Plotly receives pointer events through its transparent drag layer.
        # Click the bubble's screen coordinates, as a person would.
        matrix.evaluate("el=>el.scrollIntoView({block:'center'})")
        bubble=matrix.locator('.scatterlayer .point').first.bounding_box()
        page.mouse.click(bubble['x']+bubble['width']/2,bubble['y']+bubble['height']/2)
        expect(page.get_by_role('dialog')).to_be_visible()
        expect(page.get_by_role('dialog').get_by_text('All linked workflow assessments',exact=True)).to_be_visible()
        page.screenshot(path=str(output/'business_dialog.png'))
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).to_have_count(0)
        example=eligible.iloc[0]
        fields={'industry':'Industry','employee_band':'Business size','primary_pain_point':'Primary business problem',
                'ai_adoption':'AI adoption','stage':'Assessment stage','score_band':'Opportunity score band'}
        selected=businesses.copy()
        for field,title in fields.items():
            choice=label(field,example[field]) if field not in ('stage','score_band') else example[field]
            box=page.get_by_role('combobox',name=title,exact=True)
            box.click()
            box.fill(choice)
            page.get_by_role('option',name=choice,exact=True).click()
            page.keyboard.press('Escape')
            selected=selected.loc[selected[field].eq(example[field])]
            expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text(str(len(selected)))
            expect(page.locator('[data-testid="stApp"]')).to_have_attribute('data-test-script-state','notRunning')
        page.get_by_role('textbox',name='Search business / prospect ID').fill(example.prospect_id)
        page.get_by_role('textbox',name='Search business / prospect ID').press('Enter')
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text('1')
        expect(page.locator('[data-testid="stApp"]')).to_have_attribute('data-test-script-state','notRunning')
        # Every downloaded artifact reflects the exact same selected business.
        for button,filename in [('Download ranking CSV','ranking.csv'),('Download Consultant Decision Brief','brief.md'),
                                ('Download follow-up shortlist','shortlist.csv')]:
            with page.expect_download() as download:
                page.get_by_role('button',name=button,exact=True).click()
            download.value.save_as(str(output/filename))
        with (output/'ranking.csv').open(encoding='utf-8-sig',newline='') as handle:
            rows=list(csv.DictReader(handle))
        assert len(rows)==1 and rows[0]['Business / Prospect ID']==example.prospect_id
        assert not {'email','contact_name','business_name'} & set(rows[0])
        assert 'Businesses analysed: 1' in (output/'brief.md').read_text(encoding='utf-8')
        page.get_by_role('button',name='Main menu').click()
        with page.expect_download() as download:
            page.get_by_role('menuitem',name='Export opportunity ranking CSV',exact=True).click()
        assert download.value.suggested_filename=='opportunity_intelligence_export.csv'
        page.keyboard.press('Escape')
        page.get_by_role('button',name='Reset opportunity filters',exact=True).click()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text('150')
        expect(page.locator('[data-testid="stApp"]')).to_have_attribute('data-test-script-state','notRunning')
        page.get_by_role('combobox',name='Group dates by',exact=True).click()
        page.get_by_role('combobox',name='Group dates by',exact=True).press('ArrowDown')
        page.get_by_role('option',name='Monthly',exact=True).click()
        page.locator('[data-testid="stRadioOption"]').filter(has_text='New Per Period').click()
        page.get_by_role('textbox',name='Search business / prospect ID').fill('NO_MATCH')
        page.get_by_role('textbox',name='Search business / prospect ID').press('Enter')
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text('0')
        expect(page.get_by_text('No businesses match these filters.',exact=False)).to_be_visible()
        page.get_by_role('button',name='Manage data',exact=True).click()
        dialog=page.get_by_role('dialog')
        dialog.locator('input[type=file]').nth(0).set_input_files({'name':'invalid.csv','mimeType':'text/csv','buffer':b'wrong,header\n'})
        expect(dialog.get_by_text('Opportunity dataset validation failed.',exact=False)).to_be_visible()
        dialog.locator('input[type=file]').nth(0).set_input_files(str(Path('data/synthetic/survey_responses.csv').resolve()))
        dialog.locator('input[type=file]').nth(1).set_input_files(str(Path('data/synthetic/discovery_assessments.csv').resolve()))
        dialog.get_by_role('button',name='Use data in both dashboards',exact=True).click()
        expect(page.locator('[data-testid="stMetricValue"]').first).to_have_text('150')
        expect(page.get_by_text('Uploaded dataset',exact=False).first).to_be_visible()
        page.get_by_role('button',name='Market Intelligence',exact=True).click()
        expect(page.locator('.pl-hero h1')).to_have_text('Market Intelligence')
        expect(page.locator('[data-testid="stPlotlyChart"]')).to_have_count(6)
        assert not errors,errors
        print('PASS methodology and bubble-click dialogs, six filters, search, filtered downloads, native menu, period controls, empty state, invalid/valid bundle uploads and Market navigation')
        browser.close()


if __name__=='__main__':
    main()

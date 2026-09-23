import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date

st.set_page_config(page_title='Astra Bureau Reporting Factory', layout='wide')
st.title('Neurology Insurance AGI-OS — Astra Bureau Reporting Factory')
st.caption('No-human-touch demo: metadata-driven Source → Canonical → Bureau transformation and flat-file generation.')

CATALOG = pd.DataFrame([
 ['ISO','Builders Risk','Inland Marine','Loss'],['ISO','Builders Risk','Earthquake','Loss'],['ISO','Builders Risk','Inland Marine','Premium'],['ISO','Builders Risk','Earthquake','Premium'],
 ['ISO','Commercial Auto','AL','Loss'],['ISO','Commercial Auto','AN','Loss'],['ISO','Commercial Auto','AP','Loss'],['ISO','Commercial Auto','AL','Premium'],['ISO','Commercial Auto','AN','Premium'],['ISO','Commercial Auto','AP','Premium'],
 ['ISO','Crime','CR','Loss'],['ISO','Crime','CR','Premium'],['ISO','General Liability','GL','Loss'],['ISO','General Liability','EPL','Loss'],['ISO','General Liability','GL','Premium'],['ISO','General Liability','EPL','Premium'],
 ['ISO','Inland Marine','IM','Loss'],['ISO','Inland Marine','Drone','Loss'],['ISO','Inland Marine','IM','Premium'],['ISO','Inland Marine','Drone','Premium'],
 ['ISO','Personal Auto','VL','Loss'],['ISO','Personal Auto','VN','Loss'],['ISO','Personal Auto','VP','Loss'],['ISO','Personal Auto','VL','Premium'],['ISO','Personal Auto','VN','Premium'],['ISO','Personal Auto','VP','Premium'],
 ['ISO','Property','CF','Loss'],['ISO','Property','Allied Lines','Loss'],['ISO','Property','Flood','Loss'],['ISO','Property','Earthquake','Loss'],['ISO','Property','Glass','Loss'],['ISO','Property','CF','Premium'],['ISO','Property','Allied Lines','Premium'],['ISO','Property','Flood','Premium'],['ISO','Property','Earthquake','Premium'],['ISO','Property','Glass','Premium'],
 ['ISO','Umbrella','GL','Loss'],['ISO','Umbrella','GL','Premium'],
 ['NCCI','Workers Compensation and Employers Liability','WCPOL','Policy'],['NCCI','Workers Compensation and Employers Liability','WCSTAT','Statistical'],['NCCI','Workers Compensation and Employers Liability','WCMED','Medical'],['NCCI','Workers Compensation and Employers Liability','WCIND','Indemnity'],['NCCI','Workers Compensation and Employers Liability','ETR','Experience/Transaction'],
], columns=['Bureau','Line of Business','Reporting Module','Reporting Type'])

c1,c2,c3,c4 = st.columns(4)
with c1:
    lob = st.selectbox('Line of Business', sorted(CATALOG['Line of Business'].unique()))
with c2:
    rpt_types = sorted(CATALOG.loc[CATALOG['Line of Business'].eq(lob),'Reporting Type'].unique())
    rpt = st.selectbox('Premium / Loss / Type', rpt_types)
with c3:
    subset = CATALOG[(CATALOG['Line of Business']==lob)&(CATALOG['Reporting Type']==rpt)]
    bureau = st.selectbox('Bureau', sorted(subset['Bureau'].unique()))
with c4:
    modules = sorted(subset.loc[subset['Bureau'].eq(bureau),'Reporting Module'].unique())
    module = st.selectbox('Reporting Module', modules)

st.info(f'Selected path: {lob} → {rpt} → {bureau} → {module}')

st.subheader('1. Upload source data')
source_file = st.file_uploader('Source premium/loss/policy file (CSV or XLSX)', type=['csv','xlsx'], key='source')
st.subheader('2. Upload bureau filing layout')
layout_file = st.file_uploader('Bureau layout/template (CSV or XLSX)', type=['csv','xlsx'], key='layout')

def read_tabular(f):
    if f is None: return None
    if f.name.lower().endswith('.csv'): return pd.read_csv(f)
    return pd.read_excel(f)

src = read_tabular(source_file)
layout = read_tabular(layout_file)
if src is not None:
    st.write('Source preview'); st.dataframe(src.head(20), use_container_width=True)
if layout is not None:
    st.write('Layout preview'); st.dataframe(layout.head(20), use_container_width=True)

st.subheader('3. Astra canonicalization & mapping')
st.write('The production design profiles source fields, matches canonical data elements/picklists/synonyms, proposes new metadata, applies approved transformations, validates the bureau layout, reconciles totals, and generates the bureau output. This demo uses deterministic matching and flags anything unresolved instead of inventing a bureau value.')

if st.button('Run Astra Bureau Pipeline', type='primary'):
    if src is None or layout is None:
        st.error('Upload both a source data file and a bureau layout/template.')
    else:
        src_cols = {c.lower().replace(' ','').replace('_',''): c for c in src.columns}
        rows=[]
        layout_field_col = next((c for c in layout.columns if str(c).lower() in ['field name','field','data element','dataelement']), layout.columns[0])
        for field in layout[layout_field_col].dropna().astype(str):
            key=field.lower().replace(' ','').replace('_','')
            match=src_cols.get(key)
            rows.append([field, match or '', 'MATCHED' if match else 'UNRESOLVED'])
        mapping=pd.DataFrame(rows, columns=['Bureau Field','Source Field','Status'])
        st.dataframe(mapping, use_container_width=True)
        unresolved=(mapping['Status']=='UNRESOLVED').sum()
        if unresolved:
            st.warning(f'{unresolved} unresolved mapping(s). No value was invented. Production Astra would use canonical synonyms/picklists and configured exception policy.')
        else:
            st.success('All layout fields matched deterministically.')
        # Generic fixed-width generator if positions/lengths are present; otherwise delimited demo.
        cols_lower={str(c).lower():c for c in layout.columns}
        if 'start position' in cols_lower and 'field length' in cols_lower:
            sp=cols_lower['start position']; ln=cols_lower['field length']
            lines=[]
            for _,rec in src.iterrows():
                parts=[]
                for _,m in mapping.iterrows():
                    field=m['Bureau Field']; sf=m['Source Field']
                    lr=layout[layout[layout_field_col].astype(str)==field].iloc[0]
                    length=int(lr[ln])
                    val='' if not sf else str(rec.get(sf,''))
                    parts.append(val[:length].ljust(length))
                lines.append(''.join(parts))
            out='\n'.join(lines)
        else:
            mapped=[x for x in mapping['Source Field'] if x]
            out=src[mapped].to_csv(index=False) if mapped else ''
        st.download_button('Download generated bureau output', out.encode('utf-8'), file_name=f'{bureau}_{module}_{rpt}_{date.today().isoformat()}.txt')
        st.download_button('Download mapping results', mapping.to_csv(index=False).encode('utf-8'), file_name='mapping_results.csv')

st.divider()
st.caption('Demo only. Use licensed/current bureau specifications and production controls before regulatory submission.')

"""Author the journal reading copy with Word tables, equations and data figures."""
from pathlib import Path
import sys,re,csv,json,os
Q=Path(__file__).resolve().parent;R=Q
os.environ.setdefault('MPLCONFIGDIR',str(Q/'results/authoring_cache'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def figures():
    F=Q/'docs/figures';F.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(10,3.6))
    for ax,values,den,title in [(axes[0],[112,157,183],183,'Declared semantics'),(axes[1],[72,111,136],136,'Executed program conformance')]:
        bars=ax.bar(['Snapshot','Grid 13','Complete'],values,color=['#a2adb9','#6c91ae','#205d85']);ax.set_ylim(0,den*1.2);ax.set_ylabel('Detected divergent runs');ax.set_title(title)
        for b,v in zip(bars,values):ax.text(b.get_x()+b.get_width()/2,v+den*.025,f'{v}/{den}',ha='center')
    fig.tight_layout();fig.savefig(F/'detection.png',dpi=220);fig.savefig(F/'detection.pdf');plt.close(fig)
    rows=list(csv.DictReader((Q/'results/v2/ablation_summary.csv').open()))
    phases=['construction_ms','sweep_excluding_witness_ms','witness_ms','assembly_and_hash_ms','serialization_ms'];labels=['Construction','Sweep','Witness','Assembly/hash','Serialization']
    fig,ax=plt.subplots(figsize=(8,3.8));bottom=[0.,0.]
    for phase,label in zip(phases,labels):
        vals=[float(next(r for r in rows if r['n']=='100000' and r['witness']==mode and r['phase']==phase)['median_ms']) for mode in ['False','True']]
        ax.bar([0,1],vals,bottom=bottom,label=label);bottom=[b+v for b,v in zip(bottom,vals)]
    totals=[float(next(r for r in rows if r['n']=='100000' and r['witness']==mode and r['phase']=='total_ms')['median_ms']) for mode in ['False','True']]
    ax.plot([0,1],totals,'ko',label='Measured median total');ax.set_xticks([0,1],['Witness disabled','Witness enabled']);ax.set_ylabel('Milliseconds');ax.set_title('N = 100,000 and G = 500, untraced phase ablation');ax.legend(loc='center left',bbox_to_anchor=(1,0.5),fontsize=8)
    fig.tight_layout();fig.savefig(F/'ablation.png',dpi=220);fig.savefig(F/'ablation.pdf');plt.close(fig)
    paired=list(csv.DictReader((Q/'results/v5/paired_checker_summary.csv').open()))
    groups=[(str(n),work) for n in [1000,10000,100000] for work in ['invariant','divergent']]
    fig,axes=plt.subplots(1,2,figsize=(10,3.7))
    for ax,field,title,ylabel in [(axes[0],'median_ms','Untraced independent checking','Milliseconds'),(axes[1],'peak_aux_mib','Separate auxiliary memory run','MiB')]:
        for method,offset,color in [('legacy',-.19,'#a2adb9'),('streamed',.19,'#205d85')]:
            values=[float(next(r for r in paired if r['n']==n and r['workload']==work and r['method']==method)[field]) for n,work in groups]
            ax.bar([i+offset for i in range(len(groups))],values,width=.36,label=method,color=color)
        ax.set_yscale('log');ax.set_xticks(range(len(groups)),[f'{int(n)//1000}k '+('same' if work=='invariant' else 'diff') for n,work in groups],rotation=30,ha='right',fontsize=8)
        ax.set_ylabel(ylabel);ax.set_title(title);ax.legend(fontsize=8)
    fig.tight_layout();fig.savefig(F/'checker_scaling.png',dpi=220);fig.savefig(F/'checker_scaling.pdf');plt.close(fig)
    significance=json.loads((Q/'results/v6/policy_significance_summary.json').read_text(encoding='utf-8'))
    cases=list(csv.DictReader((Q/'results/v6/policy_significance_cases.csv').open()));values=sorted(float(r['psc']) for r in cases if float(r['psc'])>0)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8));ax=axes[0]
    ax.step(values,[(i+1)/len(values) for i in range(len(values))],where='post',color='#205d85');ax.set_xscale('log');ax.set_xlabel('PSC, positive cases only');ax.set_ylabel('Empirical cumulative fraction');ax.set_title('27 positive PSC values; 3 additional zeros');ax.set_ylim(0,1.05)
    ax.axvline(significance['positive_psc_distribution']['median']['value'],color='#808080',linestyle='--',label='Median');ax.legend(fontsize=8)
    counts=[27,significance['workloads_with_representable_policy_difference']]+[r['affected_workloads'] for r in significance['decimal_policy_resolution']]
    bars=axes[1].bar(['Continuous','Float probes','2 dp','3 dp','4 dp','6 dp'],counts,color=['#a2adb9','#205d85']+['#6c91ae']*4)
    for b,v in zip(bars,counts):axes[1].text(b.get_x()+b.get_width()/2,v+.5,str(v),ha='center',fontsize=9)
    axes[1].set_ylim(0,32);axes[1].set_ylabel('Workloads with a difference');axes[1].set_title('Policy scope and observed float examples');axes[1].tick_params(axis='x',labelrotation=25,labelsize=8)
    fig.tight_layout();fig.savefig(F/'policy_significance.png',dpi=220);fig.savefig(F/'policy_significance.pdf');plt.close(fig)

def rich(p,text):
    text=re.sub(r'\[([^\]]+)\]\([^\)]+\)',r'\1',text)
    for i,s in enumerate(re.split(r'(\*\*.*?\*\*|`[^`]+`)',text)):
        if s.startswith('**') and s.endswith('**'):p.add_run(s[2:-2]).bold=True
        elif s.startswith('`') and s.endswith('`'):
            run=p.add_run(s[1:-1]);run.font.name='Consolas';run.font.size=Pt(9)
        else:p.add_run(s)

def equation(doc,text):
    p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    om=OxmlElement('m:oMath');r=OxmlElement('m:r');t=OxmlElement('m:t');t.text=text;r.append(t);om.append(r);p._p.append(om)

def make(source="MANUSCRIPT_Q1.md", output="MANUSCRIPT_Q1_V11.docx"):
    figures();d=Document();section=d.sections[0];section.page_height=Inches(11.69);section.page_width=Inches(8.27)
    section.top_margin=Inches(.75);section.bottom_margin=Inches(.75);section.left_margin=section.right_margin=Inches(.8)
    for name in ['Normal','Title','Heading 1','Heading 2','Heading 3']:
        st=d.styles[name];st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
    normal=d.styles['Normal'];normal.font.size=Pt(10.5);normal.paragraph_format.line_spacing=1.12;normal.paragraph_format.space_after=Pt(6)
    for name,size in [('Title',20),('Heading 1',13),('Heading 2',11.5),('Heading 3',11)]:
        d.styles[name].font.size=Pt(size);d.styles[name].font.bold=True
        d.styles[name].paragraph_format.space_before=Pt(10);d.styles[name].paragraph_format.space_after=Pt(5)
    for el in list(d.styles.element.xpath('.//w:pBdr')):el.getparent().remove(el)
    footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    run=footer.add_run();fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');run._r.addnext(fld)
    lines=(Q/'docs'/source).read_text(encoding='utf-8').splitlines();i=0;tables=0
    while i<len(lines):
        s=lines[i].strip()
        if not s:i+=1;continue
        if s.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',x) for x in cells):block.append(cells)
                i+=1
            cols=len(block[0]);t=d.add_table(rows=0,cols=cols);t.autofit=False;tables+=1
            # Long, narrow-text matrices need extra space in the description column.
            widths=[6.67/cols]*cols
            if cols>=5:widths=[1.55]+[(6.67-1.55)/(cols-1)]*(cols-1)
            if tables==1 and cols==4:widths=[2.15,.7,1.4,2.42]
            for j,col in enumerate(t.columns):col.width=Inches(widths[j])
            for rowno,row in enumerate(block):
                cells=t.add_row().cells
                for j,(c,txt) in enumerate(zip(cells,row)):
                    c.width=Inches(widths[j]);p=c.paragraphs[0];rich(p,txt);p.paragraph_format.space_after=Pt(4);p.paragraph_format.space_before=Pt(4);p.paragraph_format.line_spacing=1.0
                    for run in p.runs:run.font.size=Pt(8 if cols>=7 else 8.5);run.bold=rowno==0
                    pr=c._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
                    for edge in ['top','left','bottom','right']:
                        x=OxmlElement('w:'+edge);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
                    pr.append(borders)
                    if rowno==0 or rowno%2==0:
                        shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E5E9EC' if rowno==0 else 'F5F6F7');pr.append(shade)
                trpr=t.rows[-1]._tr.get_or_add_trPr();ns=OxmlElement('w:cantSplit');trpr.append(ns)
                if rowno==0:
                    for c in cells:
                        for p in c.paragraphs:p.paragraph_format.keep_with_next=True
                    repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
            if block[0][:2]==['Variant','Method']:
                for row in list(t.rows)[:-1]:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:paragraph.paragraph_format.keep_with_next=True
            d.add_paragraph();continue
        if s.startswith('#'):
            level=len(s)-len(s.lstrip('#'));title=s.lstrip('# ').replace('–',' ')
            if level==1:d.add_paragraph(title,style='Title')
            else:
                title=re.sub(r'[^\w\s]',' ',title);title=re.sub(r'\s+',' ',title).strip()
                d.add_paragraph(title,style='Heading '+str(min(level-1,3)))
            if s.startswith('## 3.'):
                equation(d,'j*(α) = arg maxⱼ:αnⱼ≤kⱼ (kⱼ,nⱼ),    Sₛ(α) = Cⱼ*')
                equation(d,'PSC = length {α ∈ [L,H] : Sₒₗd(α) ≠ Sₙₑw(α)} / (H − L)')
            if s.startswith('## 7.'):
                d.add_picture(str(Q/'docs/figures/detection.png'),width=Inches(6.5));d.add_paragraph('Figure 1 Detection under two distinct evaluation contracts. The denominators are not pooled.').paragraph_format.space_after=Pt(10)
            if 'Algorithmic cost decomposition' in s:
                d.add_picture(str(Q/'docs/figures/ablation.png'),width=Inches(6.5));d.add_paragraph('Figure S1 Phase medians and measured total. Stacked component medians need not equal the median end to end total.').paragraph_format.space_after=Pt(10)
            if 'Streaming certificate consumption' in s:
                d.add_picture(str(Q/'docs/figures/checker_scaling.png'),width=Inches(6.5));d.add_paragraph('Figure 2 Paired independent consumer medians and separately traced auxiliary memory peaks. Both axes use logarithmic scales.').paragraph_format.space_after=Pt(10)
            if 'Policy width and practical significance' in s:
                d.add_picture(str(Q/'docs/figures/policy_significance.png'),width=Inches(6.5));d.add_paragraph('Figure 3 Positive PSC distribution and policy scope. Float probes count observed representable examples; decimal bars use exact complete lattice intersections. These are not deployment probabilities or common-domain detection rates.').paragraph_format.space_after=Pt(10)
        else:
            p=d.add_paragraph();rich(p,s)
        i+=1
    for el in list(d.element.xpath('.//w:pBdr')):el.getparent().remove(el)
    d.save(Q/'docs'/output)
    print(json.dumps({'docx':output,'tables':tables,'word_count':len(re.findall(r'\b\w+\b',' '.join(lines))),'native_equations':len(d.element.xpath('//m:oMath'))}))
if __name__=='__main__':make()






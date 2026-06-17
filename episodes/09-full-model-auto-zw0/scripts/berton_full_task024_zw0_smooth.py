"""TASK-024 full-system smoothed z_W0 AUTO continuation synthesis.

Run after AUTO from repository root::

    bash episodes/09-full-model-auto-zw0/auto/berton_full_task024_zw0_smooth/run_auto.sh
    uv run python episodes/09-full-model-auto-zw0/scripts/berton_full_task024_zw0_smooth.py

This ports TASK-023's 50 m softplus-smoothed updraft profile and TASK-016's
full 4D scaled state into a full-system z_W0 continuation.  The result is
reported conservatively: branch failure is evidence of numerical
inconclusiveness, not evidence for or against a Hopf transition.
"""
from __future__ import annotations

import json, math, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

SCRIPT_DIR=Path(__file__).resolve().parent
EP=SCRIPT_DIR.parents[0]; REPO=SCRIPT_DIR.parents[2]
AUTO_DIR=EP/'auto'/'berton_full_task024_zw0_smooth'; OUT=EP/'outputs'/'task024'; DOC=EP/'docs'/'task024_full_zw0_smooth_verdict.md'; NB=EP/'notebooks'/'task024_full_zw0_auto_record.ipynb'
sys.path.insert(0, str(REPO/'episodes'/'07-restricted-equilibrium-auto'/'scripts'))
sys.path.insert(0, str(REPO/'episodes'/'04-full-model-auto-equilibria'/'scripts'))
from berton_restricted_task023_zw0_smooth import smoothed_updraft_value, piecewise_updraft_value, python_rhs_smoothed, finite_difference_jacobian_smoothed, SMOOTHING_WIDTH_M, DELTA_Z_W
from berton_full_auto_task009_validate import default_par

Z_SEED=9.618027532260936e3; U_SEED=1.9098623386953226; M_SEED=1.0802293920592054e-9
TYPE={-9:'MX',-4:'UZ-',0:'regular',1:'BP',2:'LP',3:'HB',4:'UZ/NPR',9:'EP'}
RUNS={'z-plus':{'file':'task024-full-zw0-smooth-plus','direction':'upward','anchors':[0.25,0.5,0.75,1.0]},'z-minus':{'file':'task024-full-zw0-smooth-minus','direction':'downward','anchors':[-0.25,-0.5,-1.0,-1.5,-2.0]}}

def parse_b(path, run, meta):
    rows=[]
    if not path.exists(): return pd.DataFrame()
    for line in path.read_text().splitlines():
        p=line.split()
        if len(p)<10: continue
        try: br,pt,ty,lab=map(int,p[:4]); q,n,zs,us,ws,ps=map(float,p[4:10])
        except ValueError: continue
        zW=9000+1000*q; z=Z_SEED+1000*zs; u=U_SEED+5*us; M=10*ps; m=M_SEED*math.exp(M)
        rows.append({'run':run,'direction':meta['direction'],'branch':br,'point':pt,'ty':ty,'type':TYPE.get(ty,f'TY={ty}'),'label':lab,'q_zW0_scaled':q,'z_W0_m':zW,'z_W0_km':zW/1000,'scaled_l2_norm':n,'Z_scaled_1000m':zs,'U_scaled_5ms':us,'W_m_s':ws,'P_log_ratio_over_10':ps,'M_log_ratio':M,'z_m':z,'u_m_s':u,'w_m_s':ws,'m_kg':m,'smoothed_W_a_m_s':smoothed_updraft_value(z,zW),'piecewise_W_a_m_s':piecewise_updraft_value(z,zW),'distance_to_z_W0_m':z-zW,'smooth_width_m':SMOOTHING_WIDTH_M,'is_special_point':ty in {1,2,3},'is_hopf_label':ty==3})
    return pd.DataFrame(rows)

def parse_d(path, run):
    notes=[]; eig=[]; lab=''
    if not path.exists(): return pd.DataFrame(), pd.DataFrame()
    toks=('NOTE:','NaN','DGEBAL','floating-point','No convergence','MX','illegal value')
    for i,line in enumerate(path.read_text().splitlines(),1):
        m=re.match(r'\s*\d+\s+(\d+)\s+Eigenvalues\s+:\s+Stable:\s+(\d+)', line)
        if m: lab=int(m.group(1)); notes.append({'run':run,'line':i,'label':lab,'message':f"Stable eigenvalues: {m.group(2)}"}); continue
        m=re.search(r'Eigenvalue\s+(\d+):\s+([+-]?\d*\.\d+E[+-]?\d+)\s+([+-]?\d*\.\d+E[+-]?\d+)', line)
        if m: eig.append({'run':run,'label':lab,'eigenvalue_index':int(m.group(1)),'real_s_inv':float(m.group(2)),'imag_s_inv':float(m.group(3))}); continue
        txt=line.strip()
        if any(t in txt for t in toks): notes.append({'run':run,'line':i,'label':lab,'message':txt})
    return pd.DataFrame(eig), pd.DataFrame(notes)

def config_summary():
    rows=[]
    for run,meta in RUNS.items():
        cfg=AUTO_DIR/f"c.bertonfull-task024-zw0-smooth-{'plus' if run=='z-plus' else 'minus'}"; txt=cfg.read_text()
        rows.append({'run':run,'config_file':cfg.name,'state_scaling':'Z=(z-z_seed)/1000, U=(u-u_seed)/5, W=w, P=log(m/m_seed)/10','control_scaling':'q_z=(z_W0-9000 m)/1000 m','physical_inverse':'z=z_seed+1000Z; u=u_seed+5U; w=W; m=m_seed*exp(10P)','smoothed_updraft':'softplus smooth clip, width 50 m, Delta_z_W=300 m','z_W0_targets_km':','.join(str(9+a) for a in meta['anchors']),'raw_artifacts':','.join(f"{x}.{meta['file']}" for x in ['b','s','d']),'ds_line':next((l for l in txt.splitlines() if l.startswith('DS=')),'')})
    return pd.DataFrame(rows)

def python_crosschecks(branch):
    par=default_par(); par[0]=9000; par[1]=0.6; par[3]=0.61; par[38]=0; par[42]=0
    rows=[]; eigrows=[]
    anchors=[9000,9250,9500,9700,10000,8500,8000,7000]
    accepted=branch[branch.type!='MX'] if not branch.empty else pd.DataFrame()
    for _,r in accepted.iterrows(): anchors.append(float(r.z_W0_m))
    for zW in sorted(set(round(a,6) for a in anchors)):
        p=par.copy(); p[0]=zW; y=np.array([Z_SEED,U_SEED,0.0,M_SEED])
        rhs=python_rhs_smoothed(y,p); J=finite_difference_jacobian_smoothed(y,p); eig=np.linalg.eigvals(J); k=int(np.argmax(eig.real))
        rows.append({'source':'TASK-011 seed anchor / accepted branch cross-check','z_W0_m':zW,'z_W0_km':zW/1000,'z_m':Z_SEED,'u_m_s':U_SEED,'w_m_s':0.0,'m_kg':M_SEED,'smoothed_W_a_m_s':smoothed_updraft_value(Z_SEED,zW),'full_rhs_norm':float(np.linalg.norm(rhs)),'stable_eigenvalue_count':int(np.sum(eig.real<0)),'critical_real_s_inv':float(eig[k].real),'critical_imag_s_inv':float(eig[k].imag)})
        for j,e in enumerate(eig,1): eigrows.append({'z_W0_m':zW,'eigen_index':j,'real_s_inv':float(e.real),'imag_s_inv':float(e.imag)})
    return pd.DataFrame(rows), pd.DataFrame(eigrows)

def main():
    OUT.mkdir(parents=True,exist_ok=True); DOC.parent.mkdir(exist_ok=True); NB.parent.mkdir(exist_ok=True)
    branches=[]; eigs=[]; notes=[]
    for run,meta in RUNS.items():
        branches.append(parse_b(AUTO_DIR/f"b.{meta['file']}",run,meta)); e,n=parse_d(AUTO_DIR/f"d.{meta['file']}",run); eigs.append(e); notes.append(n)
    branch=pd.concat(branches,ignore_index=True) if branches else pd.DataFrame(); eig=pd.concat(eigs,ignore_index=True) if eigs else pd.DataFrame(); note=pd.concat(notes,ignore_index=True) if notes else pd.DataFrame()
    cfg=config_summary(); py, pyeig=python_crosschecks(branch)
    rep=branch.drop_duplicates(['run','point','label']) if not branch.empty else branch
    summary=[]
    for run,grp in branch.groupby('run'):
        acc=grp[grp.type!='MX']; rn=note[note.run==run]
        summary.append({'run':run,'direction':grp.direction.iloc[0],'accepted_points_excluding_mx':len(acc),'accepted_z_W0_min_m':float(acc.z_W0_m.min()) if len(acc) else math.nan,'accepted_z_W0_max_m':float(acc.z_W0_m.max()) if len(acc) else math.nan,'reached_paper_7km':bool(len(acc) and acc.z_W0_m.min()<=7000),'reached_transition_9p6_10km':bool(len(acc) and acc.z_W0_m.max()>=9600),'has_auto_hopf_label':bool(len(acc) and (acc.ty==3).any()),'main_failure_note':next((str(x) for x in rn.message if any(t in str(x) for t in ['DGEBAL','floating-point','No convergence','illegal'])), '')})
    summ=pd.DataFrame(summary)
    verdict={'task':'TASK-024','verdict':'continued numerical inconclusiveness','has_auto_supported_hopf':False,'smoothing_width_m':SMOOTHING_WIDTH_M,'delta_z_W_m':DELTA_Z_W,'accepted_z_W0_range_m':[float(summ.accepted_z_W0_min_m.min()) if len(summ) else None,float(summ.accepted_z_W0_max_m.max()) if len(summ) else None],'summary':'Full-system smoothed z_W0 AUTO did not produce a nontrivial branch over the paper-relevant range. The run starts at the TASK-011/TASK-012 seed but fails before useful upward/downward movement; Python finite-difference eigenvalue anchors are diagnostic only.'}
    for name,df in [('auto_branch_summary.csv',branch),('auto_eigenvalue_diagnostics.csv',eig),('auto_convergence_notes.csv',note),('config_summary.csv',cfg),('representative_auto_points.csv',rep),('python_full_eigenvalue_crosscheck.csv',py),('python_full_eigenvalues.csv',pyeig),('zw0_full_verdict_summary.csv',summ)]: df.to_csv(OUT/name,index=False)
    (OUT/'task024_full_zw0_verdict.json').write_text(json.dumps(verdict,indent=2))
    DOC.write_text(f"""# TASK-024 full-system smoothed `z_W0` continuation verdict\n\n## Setup\n\n- AUTO formulation: full 4D Berton equilibrium with `Z=(z-z_seed)/1000`, `U=(u-u_seed)/5`, `W=w`, `P=log(m/m_seed)/10`.\n- Control: `q_z=(z_W0-9000 m)/1000 m`.\n- Updraft smoothing follows TASK-023: `W_a=W_a0*eps*(softplus(x/eps)-softplus((x-1)/eps))`, `x=(z-(z_W0-Delta_z_W))/Delta_z_W`, `eps=50/Delta_z_W=50/300`.\n- Seed: TASK-011/TASK-012 canonical seed at `z≈9618.03 m`, `u≈1.90986 m/s`, `w=0`, `m≈1.08023e-9 kg`.\n\n## Result\n\nAUTO starts at the seed but does not accept a useful nontrivial full-system `z_W0` branch across the paper-relevant 7--10 km interval. The preserved diagnostics show early numerical failure rather than an HB/LP/BP-supported transition.\n\n## Cross-checks\n\n`python_full_eigenvalue_crosscheck.csv` evaluates independent finite-difference full-Jacobian eigenvalues at representative `z_W0` anchors, including 7 km and the 9.6--10 km transition region. These checks are diagnostics only because the corresponding points were not accepted AUTO branch points.\n\n## Verdict\n\n**Continued numerical inconclusiveness.** This is not AUTO-supported evidence for a full-system Hopf/oscillatory transition in `z_W0`, and it is also not a mathematically clean negative result over the desired range. Periodic-orbit continuation should not be attempted from TASK-024 without a better-conditioned full-system equilibrium parameterization or a staged seed near the smoothed ramp region.\n""")
    nb={"cells":[{"cell_type":"markdown","metadata":{},"source":["# TASK-024 AUTO command record\n"]},{"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":["import sys\n","sys.path.append('/usr/local/lib64/auto-07p/python')\n","import auto\n"]},{"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":["# From repository root\n","# bash episodes/09-full-model-auto-zw0/auto/berton_full_task024_zw0_smooth/run_auto.sh\n","# uv run python episodes/09-full-model-auto-zw0/scripts/berton_full_task024_zw0_smooth.py\n"]},{"cell_type":"markdown","metadata":{},"source":DOC.read_text().splitlines(True)}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
    NB.write_text(json.dumps(nb,indent=2))
if __name__=='__main__': main()

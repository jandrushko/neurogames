import streamlit as st
import random
import io
import re
import time
from datetime import datetime
from streamlit_sortables import sort_items

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

# ReportLab — PDF report generation
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.lib.colors import HexColor

st.set_page_config(
    page_title="Neuroscience Learning Games",
    page_icon="🧠",
    layout="centered",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; color: #0f172a; }
.stApp { background: #f1f5f9; }

.app-title {
    font-size: 2.1rem; font-weight: 800; color: #0f172a;
    letter-spacing: -0.03em; margin-bottom: 0.05rem;
}
.app-subtitle { font-size: 1rem; color: #64748b; margin-bottom: 0.5rem; }

.stTabs [data-baseweb="tab-list"] {
    gap: 3px; background: #e2e8f0; border-radius: 12px; padding: 4px; margin-bottom: 1.2rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px; padding: 8px 18px; font-weight: 600;
    font-size: 0.88rem; color: #64748b; background: transparent; border: none;
    font-family: 'Outfit', sans-serif;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: #ffffff; color: #0f172a; box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

.section-title {
    font-size: 1.35rem; font-weight: 700; color: #0f172a;
    letter-spacing: -0.02em; margin-bottom: 0.2rem;
}
.section-desc { font-size: 0.9rem; color: #64748b; margin-bottom: 1rem; }

/* Sequencing */
.step-card {
    background: #ffffff; border: 1px solid #cbd5e1;
    border-left: 5px solid #3b82f6; border-radius: 8px;
    padding: 12px 16px; margin-bottom: 6px; font-size: 0.93rem;
    color: #0f172a; display: flex; align-items: center; gap: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.step-num {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600;
    color: #fff; background: #3b82f6; border-radius: 5px;
    padding: 3px 7px; min-width: 28px; text-align: center; flex-shrink: 0;
}
.step-card.correct   { border-left-color: #16a34a !important; background: #f0fdf4 !important; }
.step-card.correct .step-num   { background: #16a34a !important; }
.step-card.incorrect { border-left-color: #dc2626 !important; background: #fef2f2 !important; }
.step-card.incorrect .step-num { background: #dc2626 !important; }

/* Matching */
.match-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px; }
.match-term {
    background: #1e3a5f; color: #fff; border-radius: 8px;
    padding: 10px 14px; font-size: 0.88rem; font-weight: 600;
    min-width: 160px; max-width: 160px; line-height: 1.4; flex-shrink: 0;
}
.match-term.correct   { background: #16a34a; }
.match-term.incorrect { background: #dc2626; }
.match-result-def {
    background: #fff; border: 1px solid #cbd5e1; border-radius: 8px;
    padding: 10px 14px; font-size: 0.88rem; color: #0f172a;
    line-height: 1.4; flex-grow: 1;
}
.match-result-def.correct   { background: #f0fdf4; border-color: #16a34a; color: #14532d; }
.match-result-def.incorrect { background: #fef2f2; border-color: #dc2626; color: #991b1b;
    text-decoration: line-through; opacity: 0.8; }
.match-correct-reveal {
    background: #dcfce7; border: 1px solid #86efac; border-radius: 7px;
    padding: 7px 12px; font-size: 0.84rem; color: #14532d;
    margin-top: 4px; margin-bottom: 6px; margin-left: 170px;
}

/* Quiz */
.quiz-q-card {
    background: #fff; border: 1.5px solid #cbd5e1; border-radius: 12px;
    padding: 22px 26px; font-size: 1.08rem; font-weight: 500; color: #0f172a;
    line-height: 1.65; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.quiz-explanation {
    background: #eff6ff; border: 1.5px dashed #93c5fd; border-radius: 8px;
    padding: 14px 18px; font-size: 0.91rem; color: #1e40af;
    line-height: 1.7; margin-top: 0.9rem;
}
.quiz-final-row {
    display: flex; align-items: flex-start; gap: 12px;
    background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 11px 15px; margin-bottom: 7px; font-size: 0.9rem;
}
.quiz-final-row.correct   { background: #f0fdf4; border-color: #86efac; }
.quiz-final-row.incorrect { background: #fef2f2; border-color: #fca5a5; }
.quiz-badge {
    font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 600;
    padding: 3px 8px; border-radius: 5px; flex-shrink: 0; margin-top: 2px;
}
.badge-t { background: #16a34a; color: #fff; }
.badge-f { background: #dc2626; color: #fff; }

/* Cranial nerve flashcard */
.cn-card {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%);
    border-radius: 16px; padding: 32px 28px; text-align: center;
    color: #fff; margin: 0.8rem 0; box-shadow: 0 4px 20px rgba(30,58,95,0.25);
}
.cn-num {
    font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 600;
    color: #93c5fd; letter-spacing: 0.1em; margin-bottom: 6px;
}
.cn-name {
    font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0;
}
.cn-option-btn {
    background: #fff; border: 2px solid #e2e8f0; border-radius: 10px;
    padding: 11px 16px; font-size: 0.9rem; color: #0f172a; font-weight: 500;
    cursor: pointer; transition: all 0.15s; line-height: 1.4; text-align: left;
}
.cn-option-btn:hover { border-color: #3b82f6; background: #eff6ff; }
.cn-option-correct { background: #f0fdf4 !important; border-color: #16a34a !important; color: #14532d !important; }
.cn-option-wrong   { background: #fef2f2 !important; border-color: #dc2626 !important; color: #991b1b !important; }
.cn-fact-box {
    background: #eff6ff; border: 1.5px dashed #93c5fd; border-radius: 8px;
    padding: 14px 18px; font-size: 0.91rem; color: #1e40af;
    line-height: 1.7; margin-top: 0.9rem;
}

/* Scores / progress */
.score-big {
    font-family: 'JetBrains Mono', monospace; font-size: 3rem; font-weight: 600;
    color: #0f172a; text-align: center; margin: 0.3rem 0 0;
}
.score-sub { font-size: 0.88rem; color: #64748b; text-align: center; margin-bottom: 0.5rem; }
.prog-outer { background: #e2e8f0; border-radius: 99px; height: 11px; overflow: hidden; margin: 8px 0 4px; }
.prog-inner { height: 11px; border-radius: 99px; background: linear-gradient(90deg, #3b82f6, #10b981); }

/* Feedback */
.fb { border-radius: 8px; padding: 13px 17px; margin-top: 0.8rem; font-size: 0.94rem; font-weight: 500; }
.fb-ok  { background: #dcfce7; border: 1.5px solid #16a34a; color: #14532d; }
.fb-mid { background: #fefce8; border: 1.5px solid #ca8a04; color: #713f12; }
.fb-low { background: #fee2e2; border: 1.5px solid #dc2626; color: #7f1d1d; }

/* Misc */
.hint-box {
    background: #eff6ff; border: 1.5px dashed #93c5fd; border-radius: 8px;
    padding: 12px 17px; font-size: 0.89rem; color: #1e40af;
    margin-bottom: 1rem; line-height: 1.65;
}
.drag-note {
    background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 7px;
    padding: 7px 13px; font-size: 0.84rem; color: #0369a1; margin-bottom: 10px;
}
.divider { border: none; border-top: 1.5px solid #e2e8f0; margin: 1.1rem 0; }

/* Student banner */
.student-banner {
    background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
    border-radius: 10px; padding: 12px 20px; margin-bottom: 1rem;
    display: flex; align-items: center; justify-content: space-between; color: #fff;
}
.student-name-display { font-size: 1rem; font-weight: 700; }
.student-time-display { font-size: 0.82rem; color: #bfdbfe; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0f172a; }
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)

SORTABLE_STYLE = """
.sortable-component { padding: 0 !important; }
.sortable-item {
    background: #ffffff !important; border: 1px solid #cbd5e1 !important;
    border-left: 5px solid #3b82f6 !important; border-radius: 8px !important;
    padding: 12px 16px !important; margin-bottom: 6px !important;
    font-family: 'Outfit', sans-serif !important; font-size: 0.93rem !important;
    color: #0f172a !important; cursor: grab !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
    line-height: 1.5 !important; user-select: none !important;
    transition: box-shadow 0.15s, background 0.15s !important;
}
.sortable-item:hover {
    border-left-color: #2563eb !important; background: #f8faff !important;
    box-shadow: 0 3px 10px rgba(59,130,246,0.18) !important;
}
.sortable-item:active {
    cursor: grabbing !important; background: #eff6ff !important;
    box-shadow: 0 6px 18px rgba(59,130,246,0.26) !important;
}
"""

# ══════════════════════════════════════════════════════════════════════════════
# DATA — SEQUENCING
# ══════════════════════════════════════════════════════════════════════════════
SEQUENCES = {
    "Early-Phase LTP (E-LTP)": {
        "description": "Order the cellular events that occur during early-phase LTP induction and expression at a glutamatergic synapse.",
        "hint": "stimulus → Glu release → AMPA activation → depolarisation → Mg²⁺ block removed → Ca²⁺ entry → CaMKII → receptor phosphorylation → receptor insertion → enhanced synapse.",
        "steps": [
            ("HFS",        "⚡ High-frequency presynaptic stimulation (tetanic burst) arrives at the synapse."),
            ("Glu",        "🔵 Glutamate is released from the presynaptic terminal into the synaptic cleft."),
            ("AMPA",       "🟡 Glutamate binds to postsynaptic AMPA receptors, causing Na⁺ influx."),
            ("Depol",      "⬆️ The postsynaptic membrane depolarises, relieving the Mg²⁺ block on NMDA receptors."),
            ("NMDA",       "🔓 Glutamate binds to (now unblocked) NMDA receptors."),
            ("Ca",         "🌊 Ca²⁺ flows into the postsynaptic cell through open NMDA receptor channels."),
            ("CaMKII",     "🔬 Rising intracellular Ca²⁺ activates CaMKII (Ca²⁺/calmodulin-dependent protein kinase II)."),
            ("AMPAphos",   "⚙️ CaMKII phosphorylates existing AMPA receptors, increasing their conductance."),
            ("AMPAinsert", "➕ Additional AMPA receptors are trafficked from intracellular pools and inserted into the membrane."),
            ("LTPex",      "✅ Synaptic strength is potentiated — subsequent EPSPs are larger and longer-lasting."),
        ],
    },
    "Late-Phase LTP (L-LTP)": {
        "description": "Order the events for consolidation of late-phase LTP, which requires new protein synthesis.",
        "hint": "repeated stimulation → sustained Ca²⁺ → CaMKII autophosphorylation → cAMP → PKA → CREB → gene transcription → protein synthesis → structural remodelling → stable synapse.",
        "steps": [
            ("rHFS",       "⚡ Repeated high-frequency stimulation occurs across multiple bursts."),
            ("NMDACa",     "🌊 Sustained Ca²⁺ influx via NMDA receptors accumulates in the postsynaptic spine."),
            ("CaMKIIauto", "🔬 CaMKII is autophosphorylated, maintaining activity even after Ca²⁺ drops."),
            ("cAMP",       "🔄 Adenylyl cyclase is activated, elevating cyclic AMP (cAMP) levels."),
            ("PKA",        "⚙️ Protein kinase A (PKA) is activated by elevated cAMP."),
            ("CREB",       "🧬 PKA (and MAPK) translocate to the nucleus and phosphorylate CREB."),
            ("Gene",       "📖 CREB-driven gene transcription produces plasticity-related proteins (e.g., Arc, BDNF)."),
            ("Psynth",     "🏗️ New synaptic proteins are synthesised locally at the dendritic spine."),
            ("Spine",      "🌱 Structural remodelling: the dendritic spine enlarges and stabilises."),
            ("LLTP",       "💡 A stable, protein-synthesis-dependent increase in synaptic efficacy is established."),
        ],
    },
    "Action Potential": {
        "description": "Order the events of a single action potential from resting state through to full ionic recovery.",
        "hint": "resting → stimulus → threshold → Na⁺ influx (rise) → Na⁺ inactivation → K⁺ efflux (fall) → undershoot → absolute refractory → relative refractory → pump restores resting.",
        "steps": [
            ("rest",   "💤 Neuron is at resting membrane potential (~-70 mV), maintained by the Na⁺/K⁺ ATPase."),
            ("stim",   "📶 An excitatory stimulus causes a local depolarisation (graded potential) at the dendrite or soma."),
            ("thresh", "⚡ The graded potential reaches threshold (~-55 mV) — voltage-gated Na⁺ channels begin to open."),
            ("depol",  "📈 Rapid Na⁺ influx drives the membrane potential toward +40 mV (rising phase)."),
            ("peak",   "🔝 At the peak, Na⁺ channels begin to inactivate (entering a closed, non-conducting state)."),
            ("repol",  "📉 Voltage-gated K⁺ channels open — K⁺ efflux repolarises the membrane."),
            ("under",  "⬇️ K⁺ channels close slowly, causing a brief hyperpolarisation below resting (undershoot)."),
            ("abs",    "🚫 Absolute refractory period — inactivated Na⁺ channels cannot reopen; no new AP is possible."),
            ("rel",    "⚠️ K⁺ channels close; relative refractory period begins — a stronger stimulus could fire a new AP."),
            ("pump",   "🔧 Na⁺/K⁺ ATPase restores ionic gradients and resting membrane potential is fully re-established."),
        ],
    },
    "Synaptic Transmission": {
        "description": "Order the events of chemical synaptic transmission from presynaptic action potential to postsynaptic integration.",
        "hint": "AP arrives → VGCCs open → Ca²⁺ enters → SNARE assembly → exocytosis → diffusion → receptor binding → PSP generated → NT clearance → summation.",
        "steps": [
            ("AP",    "⚡ Action potential (AP) arrives at the presynaptic axon terminal (bouton)."),
            ("VGCC",  "🔓 Voltage-gated Ca²⁺ channels open at the pre-synaptic terminal."),
            ("CaIn",  "🌊 Ca²⁺ enters the presynaptic terminal down its concentration gradient."),
            ("SNARE", "🫧 Ca²⁺ triggers SNARE protein assembly — synaptic vesicles dock with the membrane."),
            ("Exo",   "💦 Neurotransmitter is released into the synaptic cleft by exocytosis."),
            ("Diff",  "➡️ Neurotransmitter diffuses across the synaptic cleft."),
            ("Bind",  "🔗 Neurotransmitter binds to ionotropic or metabotropic receptors on the postsynaptic membrane."),
            ("PSP",   "📊 A postsynaptic potential (EPSP or IPSP) is generated."),
            ("Clear", "🧹 Neurotransmitter is removed by reuptake transporters or enzymatic degradation (e.g., AChE)."),
            ("Sum",   "➕ Spatial and temporal summation of EPSPs/IPSPs determines whether threshold is reached for a new AP."),
        ],
    },
    "HPA Axis Stress Response": {
        "description": "Order the events of the HPA axis stress response, from initial threat detection through to negative feedback and recovery.",
        "hint": "amygdala detects threat → hypothalamus releases CRH → anterior pituitary releases ACTH → adrenal cortex releases cortisol → energy mobilisation → hippocampus & hypothalamus detect high cortisol → negative feedback → CRH & ACTH suppressed → cortisol returns to baseline.",
        "steps": [
            ("Threat",   "😟 A stressor is detected — the amygdala (the brain's threat-detection centre) perceives the event and triggers an alarm signal."),
            ("Hypo",     "🧠 The amygdala activates the hypothalamus (the body's command centre), which releases corticotropin-releasing hormone (CRH)."),
            ("Portal",   "🩸 CRH travels through the hypothalamic-hypophyseal portal blood system — a short, direct blood route to the pituitary gland."),
            ("ACTH",     "💉 CRH stimulates the anterior pituitary gland to synthesise and release adrenocorticotropic hormone (ACTH) into the bloodstream."),
            ("Adrenal",  "🫀 ACTH travels through the bloodstream to the adrenal glands, which sit on top of the kidneys."),
            ("Cortisol", "⚗️ ACTH stimulates the adrenal cortex to synthesise and release cortisol — the body's primary stress hormone."),
            ("Effects",  "📊 Cortisol mobilises glucose and fatty acids to provide energy, suppresses non-essential functions (e.g. immunity), and prepares the body to respond to the stressor."),
            ("Hippo",    "🔍 The hippocampus and hypothalamus detect rising cortisol levels in the bloodstream — initiating the negative feedback brake."),
            ("FBloop",   "🔄 Negative feedback suppresses further CRH release from the hypothalamus and ACTH release from the anterior pituitary."),
            ("Recover",  "✅ Cortisol production falls, the stress response is dampened, and the body returns to a calm, balanced (homeostatic) state."),
        ],
    },
    "Neuromuscular Junction (NMJ)": {
        "description": "Order the events from motor neuron firing to skeletal muscle contraction at the neuromuscular junction.",
        "hint": "motor AP → NMJ Ca²⁺ → ACh release → nAChR binding → end-plate potential → muscle AP → T-tubules → DHPR → RyR → Ca²⁺ from SR → troponin/tropomyosin → contraction.",
        "steps": [
            ("MnAP",     "⚡ A motor neuron action potential propagates to the NMJ presynaptic terminal."),
            ("NMJCa",    "🌊 Voltage-gated Ca²⁺ channels open — Ca²⁺ enters the presynaptic terminal."),
            ("ACh",      "💦 Acetylcholine (ACh) is released by exocytosis into the synaptic cleft."),
            ("nAChR",    "🔗 ACh binds to nicotinic ACh receptors (nAChRs) on the motor end-plate."),
            ("EPP",      "📈 Na⁺ influx generates an end-plate potential (EPP) — always suprathreshold."),
            ("MuscAP",   "⚡ The EPP triggers a muscle action potential along the sarcolemma."),
            ("Ttube",    "📡 The action potential travels into T-tubules, activating dihydropyridine receptors (DHPRs)."),
            ("RyR",      "🔥 Activated DHPRs open ryanodine receptors (RyRs) — Ca²⁺ floods from the sarcoplasmic reticulum."),
            ("Trop",     "🔓 Ca²⁺ binds troponin C, shifting tropomyosin to expose myosin-binding sites on actin."),
            ("Contract", "💪 Myosin heads bind actin — cross-bridge cycling drives muscle contraction."),
        ],
    },
    "Basal Ganglia — Direct Pathway": {
        "description": "Order the structures and signals of the direct pathway, from cortical input through to facilitation of voluntary movement.",
        "hint": "cortex (glutamate) → striatum (D1) activated → GPi/SNr inhibited → thalamus released from inhibition → thalamus excites cortex → movement facilitated.",
        "steps": [
            ("dp_ctx",      "🧠 The cerebral cortex releases glutamate, exciting neurons in the striatum (caudate & putamen)."),
            ("dp_str",      "🟢 Striatal D1 receptor-bearing neurons are activated and send GABAergic projections to the output nuclei."),
            ("dp_gpi",      "🔴 The striatum inhibits the internal globus pallidus (GPi) and substantia nigra pars reticulata (SNr) via GABA."),
            ("dp_gpi_rel",  "🔓 GPi/SNr activity is reduced — their tonic GABAergic inhibition of the thalamus is released (disinhibition)."),
            ("dp_thal",     "💡 The thalamus (VA/VL nuclei) is disinhibited and increases its excitatory output."),
            ("dp_thal_ctx", "⬆️ The thalamus sends glutamatergic projections back to the motor cortex, increasing its activity."),
            ("dp_da",       "🔵 Dopamine from the substantia nigra pars compacta (SNc) acts on D1 receptors, reinforcing striatal activation of the direct pathway."),
            ("dp_move",     "✅ Motor cortex output is facilitated — the desired voluntary movement is initiated and executed."),
        ],
    },
    "Basal Ganglia — Indirect Pathway": {
        "description": "Order the structures and signals of the indirect pathway, from cortical input through to suppression of unwanted movement.",
        "hint": "cortex (glutamate) → striatum (D2) activated → GPe inhibited → STN released from inhibition → STN excites GPi/SNr → thalamus suppressed → movement inhibited.",
        "steps": [
            ("ip_ctx",      "🧠 The cerebral cortex releases glutamate, exciting neurons in the striatum (caudate & putamen)."),
            ("ip_str",      "🔴 Striatal D2 receptor-bearing neurons are activated and send GABAergic projections to the external globus pallidus (GPe)."),
            ("ip_gpe",      "🔒 The striatum inhibits the GPe via GABA, reducing GPe's inhibitory output to the subthalamic nucleus (STN)."),
            ("ip_stn",      "⚡ The STN is released from GPe inhibition and increases its glutamatergic output."),
            ("ip_gpi",      "🔺 The STN excites the GPi and SNr via glutamate, increasing their inhibitory (GABAergic) output."),
            ("ip_thal",     "🔇 Increased GABAergic output from GPi/SNr strongly suppresses thalamic activity."),
            ("ip_ctx_inh",  "⬇️ Reduced thalamic output decreases excitation of the motor cortex."),
            ("ip_da",       "🔵 Dopamine from the SNc acts on D2 receptors, inhibiting striatal D2 neurons and dampening the indirect pathway."),
            ("ip_move",     "🚫 Competing or unwanted movements are suppressed — the indirect pathway acts as a movement brake."),
        ],
    },
}

DIFFICULTY_STEPS = {
    "Beginner (6 steps)":      6,
    "Intermediate (8 steps)":  8,
    "Expert (all steps)":     99,  # capped to actual sequence length in load_seq
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA — MATCHING
# ══════════════════════════════════════════════════════════════════════════════
MATCHING_SETS = {
    "Brain Lobes & Functions": {
        "instruction": "Match each brain lobe or region to its primary functional role.",
        "pairs": [
            ("frontal",    "Frontal Lobe",    "Executive function, voluntary motor control, decision-making & personality"),
            ("parietal",   "Parietal Lobe",   "Somatosensory processing, spatial awareness & multisensory integration"),
            ("temporal",   "Temporal Lobe",   "Auditory processing, language comprehension (Wernicke's area) & memory formation"),
            ("occipital",  "Occipital Lobe",  "Primary visual cortex — processing and interpretation of visual information"),
            ("cerebellum", "Cerebellum",      "Motor coordination, balance, fine-tuning of movement & procedural learning"),
            ("limbic",     "Limbic System",   "Emotion, motivation, memory consolidation & regulation of the stress response"),
        ],
    },
    "Neurotransmitters & Roles": {
        "instruction": "Match each neurotransmitter to its primary role in the nervous system.",
        "pairs": [
            ("da",   "Dopamine",      "Reward, motivation, motor control & reinforcement learning"),
            ("5ht",  "Serotonin",     "Mood regulation, sleep, appetite & emotional stability"),
            ("gaba", "GABA",          "Primary inhibitory neurotransmitter — reduces neuronal excitability throughout the CNS"),
            ("glut", "Glutamate",     "Primary excitatory neurotransmitter — drives synaptic activation, learning and LTP"),
            ("ach",  "Acetylcholine", "NMJ activation, memory consolidation & attentional control"),
            ("na",   "Noradrenaline", "Arousal, attentional focus, vigilance & the sympathetic fight-or-flight response"),
        ],
    },
    "Brain Structures & Functions": {
        "instruction": "Match each brain structure to its primary function.",
        "pairs": [
            ("hippo", "Hippocampus",       "Spatial navigation and consolidation of new declarative (explicit) memories"),
            ("amyg",  "Amygdala",          "Emotional processing, fear conditioning & threat detection and appraisal"),
            ("hypo",  "Hypothalamus",      "Homeostasis — regulates hunger, thirst, body temperature & circadian rhythms"),
            ("thal",  "Thalamus",          "Sensory relay station — routes incoming signals from sense organs to the cortex"),
            ("bg",    "Basal Ganglia",     "Gating to facilitate/inhibit voluntary movement"),
            ("pfc",   "Prefrontal Cortex", "Planning, impulse control, working memory & complex goal-directed decision-making"),
            ("broca", "Broca's Area",      "Speech production and the motor programming of language output"),
            ("wern",  "Wernicke's Area",   "Language comprehension — understanding spoken and written language"),
        ],
    },
    "Receptor Types & Properties": {
        "instruction": "Match each receptor type to its key mechanism and ion permeability.",
        "pairs": [
            ("ampa",  "AMPA Receptor",     "Ionotropic; fast excitatory; permeable to Na⁺ and K⁺; drives initial depolarisation"),
            ("nmda",  "NMDA Receptor",     "Ionotropic; coincidence detector; Ca²⁺ permeable once Mg²⁺ block is relieved by depolarisation"),
            ("gabaa", "GABA-A Receptor",   "Ionotropic; fast inhibitory; Cl⁻ influx hyperpolarises the postsynaptic membrane"),
            ("mglu",  "mGluR (Group I)",   "Metabotropic; activates Gq/PLC second-messenger cascades to modulate synaptic plasticity"),
            ("nach",  "Nicotinic AChR",    "Ionotropic; ligand-gated; Na⁺/K⁺ permeable; mediates fast excitation at the NMJ"),
            ("mop",   "μ-Opioid Receptor", "Metabotropic (GPCR); inhibits adenylyl cyclase; reduces pain signalling and modulates reward"),
        ],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA — TRUE/FALSE QUIZ
# ══════════════════════════════════════════════════════════════════════════════
QUIZ_QUESTIONS = [
    {
        "q": "Humans only use about 10% of their brain at any given time.",
        "answer": False,
        "explanation": "This is one of the most persistent neuroscience myths. Brain imaging (fMRI, PET) shows that virtually all brain regions are active at various times. Over the course of a day, essentially all areas are used — even during sleep.",
    },
    {
        "q": "The left cerebral hemisphere controls the right side of the body, and vice versa.",
        "answer": True,
        "explanation": "Correct — this is called contralateral control. Motor and somatosensory pathways decussate (cross the midline) in the brainstem or spinal cord, so each hemisphere largely controls the opposite side of the body.",
    },
    {
        "q": "The adult human brain is completely incapable of generating new neurons (neurogenesis).",
        "answer": False,
        "explanation": "Adult neurogenesis does occur, most notably in the hippocampal dentate gyrus and the olfactory bulb (via the subventricular zone). The functional significance of adult hippocampal neurogenesis remains debated, but it is not absent.",
    },
    {
        "q": "GABA (gamma-aminobutyric acid) is the primary inhibitory neurotransmitter in the adult central nervous system.",
        "answer": True,
        "explanation": "Correct. GABA acts via GABA-A (ionotropic, Cl⁻ influx) and GABA-B (metabotropic, K⁺ efflux) receptors to hyperpolarise neurons and reduce excitability. It is the most widespread inhibitory transmitter in the brain.",
    },
    {
        "q": "The cerebellum is exclusively responsible for motor coordination and plays no role in cognition.",
        "answer": False,
        "explanation": "While the cerebellum is strongly associated with motor coordination, balance and procedural learning, neuroimaging and lesion studies have also implicated it in working memory, attention, language processing and emotional regulation.",
    },
    {
        "q": "Myelination of an axon significantly increases the speed of action potential conduction.",
        "answer": True,
        "explanation": "Correct. Myelin sheaths force the action potential to jump between Nodes of Ranvier (saltatory conduction), which is far faster than continuous conduction. Large myelinated axons conduct at up to ~120 m/s vs ~0.5–2 m/s for unmyelinated C-fibres.",
    },
    {
        "q": "Dopamine is best described simply as the brain's 'pleasure chemical'.",
        "answer": False,
        "explanation": "This is a significant oversimplification. Dopamine is more accurately a neurotransmitter of reward prediction, motivation and salience. It signals the anticipation of reward and drives goal-directed behaviour, rather than being the direct mediator of subjective pleasure.",
    },
    {
        "q": "The hippocampus is critical for the formation of new declarative (explicit) memories.",
        "answer": True,
        "explanation": "Correct. Damage to the hippocampus (e.g., the famous patient H.M.) causes anterograde amnesia — an inability to form new explicit memories. Implicit and procedural memories remain largely intact, indicating hippocampal specificity for declarative memory.",
    },
    {
        "q": "Action potentials increase in amplitude (size) with increasing stimulus strength.",
        "answer": False,
        "explanation": "This violates the all-or-nothing principle. Once threshold is reached, an action potential fires with a fixed amplitude regardless of stimulus strength. Stimulus intensity is encoded by the frequency of action potentials (rate coding), not their size.",
    },
    {
        "q": "The amygdala is exclusively a 'fear centre' and only processes fear-related stimuli.",
        "answer": False,
        "explanation": "While the amygdala is strongly associated with fear conditioning and threat detection, it processes a broad range of emotional stimuli — including positive emotions, social information, reward salience and attention.",
    },
    {
        "q": "Neuroplasticity — the brain's ability to reorganise and form new connections — is largely restricted to childhood critical periods.",
        "answer": False,
        "explanation": "The adult brain retains substantial plasticity throughout life. While some plasticity is heightened during developmental windows, adults can form new synaptic connections, reorganise cortical maps and generate some new neurons.",
    },
    {
        "q": "The primary end-hormone of the HPA (hypothalamic-pituitary-adrenal) axis is adrenaline (epinephrine).",
        "answer": False,
        "explanation": "The HPA axis terminates with cortisol, released from the adrenal cortex. Adrenaline is the end-product of the separate sympathetic-adrenal medullary (SAM) axis. Both are activated by stress but via distinct pathways.",
    },
]

# ══════════════════════════════════════════════════════════════════════════════
# DATA — LECTURE QUIZ (100 MCQ questions across 10 topics)
# ══════════════════════════════════════════════════════════════════════════════
# Each entry: topic, question, options (list), correct (must match an option exactly)
LECTURE_QUIZ_TOPICS = [
    "Neuroanatomy",
    "Neurodevelopmental Disorders",
    "Neuropharmacology",
    "Memory Disorders",
    "Movement Disorders",
    "Visual, Auditory & Language Disorders",
    "Affective Disorders",
    "Schizophrenia",
    "Delirium",
    "Peripheral Nervous System",
]

LECTURE_QUIZ_QUESTIONS = [
    # ── NEUROANATOMY (10) ──────────────────────────────────────────────────────
    {"topic": "Neuroanatomy",
     "q": "Which layer of the meninges is the outermost, described as 'tough mother'?",
     "options": ["Subarachnoid membrane", "Dura mater", "Arachnoid mater", "Pia mater"],
     "correct": "Dura mater",
     "explanation": "The dura mater is the outermost, very tough covering of the brain. It is described as 'tough mother' and contains the venous sinuses."},
    {"topic": "Neuroanatomy",
     "q": "Which brain area is primarily responsible for the planning and coordination of speech production (Broca's area)?",
     "options": ["Occipital lobe", "Parietal lobe", "Temporal lobe", "Frontal lobe (Broca's area)"],
     "correct": "Frontal lobe (Broca's area)",
     "explanation": "Broca's area is located in the frontal lobe and is the speech centre involved in planning mouth and laryngeal movements. Damage impairs speech production but not understanding."},
    {"topic": "Neuroanatomy",
     "q": "Which of the following best describes the primary function of the cerebellum?",
     "options": ["Generates language comprehension", "Initiates voluntary movement", "Coordinates and fine-tunes voluntary movement", "Processes visual information"],
     "correct": "Coordinates and fine-tunes voluntary movement",
     "explanation": "The cerebellum coordinates voluntary movements including posture, balance, coordination and speech, and contributes to precision and timing — but does not initiate movement."},
    {"topic": "Neuroanatomy",
     "q": "Which of these structures is NOT listed as part of the basal ganglia?",
     "options": ["Putamen", "Hippocampus", "Globus pallidus", "Caudate nucleus"],
     "correct": "Hippocampus",
     "explanation": "The basal ganglia include the caudate, putamen, globus pallidus, substantia nigra and subthalamic nucleus. The hippocampus is part of the limbic system."},
    {"topic": "Neuroanatomy",
     "q": "Which artery pair provides roughly 70% of cerebral blood flow?",
     "options": ["Internal carotid / anterior circulation (~70%)", "Vertebral arteries (posterior flow)", "Pulmonary arteries", "External carotid arteries"],
     "correct": "Internal carotid / anterior circulation (~70%)",
     "explanation": "Anterior flow via the internal carotid system provides approximately 70% of cerebral blood flow, with the vertebral-basilar system supplying the remaining 30%."},
    {"topic": "Neuroanatomy",
     "q": "Approximately what proportion of strokes are ischaemic?",
     "options": ["About 50%", "About 10%", "About 80%", "About 100%"],
     "correct": "About 80%",
     "explanation": "About 80% of strokes are ischaemic, caused by arterial narrowing or blockage leading to reduced cerebral blood flow."},
    {"topic": "Neuroanatomy",
     "q": "How is a transient ischaemic attack (TIA) defined?",
     "options": ["A type of seizure unrelated to blood flow", "A permanent stroke causing lasting deficits", "A chronic degenerative disease of the cortex", "A brief focal neurological episode lasting less than 24 hours"],
     "correct": "A brief focal neurological episode lasting less than 24 hours",
     "explanation": "A TIA is a brief episode of focal neurological symptoms caused by transient loss of blood flow that lasts less than 24 hours and leaves no permanent deficit."},
    {"topic": "Neuroanatomy",
     "q": "Which structure consists of a wide, thick bundle of commissural fibres connecting the two cerebral hemispheres and contains approximately 200–300 million axons?",
     "options": ["Internal capsule", "Corpus callosum", "Corona radiata", "Anterior commissure"],
     "correct": "Corpus callosum",
     "explanation": "The corpus callosum is the major commissural tract connecting the two cerebral hemispheres, described as a wide, thick bundle with about 200–300 million axons."},
    {"topic": "Neuroanatomy",
     "q": "Wernicke's area, important for language perception and recognition, is located primarily in which cerebral lobe?",
     "options": ["Temporal lobe", "Occipital lobe", "Frontal lobe", "Parietal lobe"],
     "correct": "Temporal lobe",
     "explanation": "Wernicke's area is traditionally located in the temporal lobe and is associated with language comprehension. Damage produces receptive (Wernicke's) aphasia."},
    {"topic": "Neuroanatomy",
     "q": "Which structure is identified as the primary site of cerebrospinal fluid (CSF) production within the ventricles?",
     "options": ["Lateral ventricles (as cavities)", "Arachnoid granulations (villi)", "Choroid plexus", "Pia mater"],
     "correct": "Choroid plexus",
     "explanation": "CSF is produced by the choroid plexus within the ventricular system. The choroid plexus transforms blood into CSF."},

    # ── NEURODEVELOPMENTAL DISORDERS (10) ─────────────────────────────────────
    {"topic": "Neurodevelopmental Disorders",
     "q": "Which developmental process results in the removal of about half of synapses during postnatal brain development?",
     "options": ["Synaptic pruning", "Adult neurogenesis", "Apoptosis of neurons", "Synaptogenesis (exuberant synapse formation)"],
     "correct": "Synaptic pruning",
     "explanation": "After a period of exuberant synaptogenesis, many least-used synapses are eliminated by synaptic pruning — the 'use it or lose it' principle."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Which statement best describes 'experience-expectant' brain development?",
     "options": ["It describes skills the brain develops only later in life that it does not expect.", "It refers to early phases when the brain is primed to expect typical environmental inputs (e.g., visual, auditory) for normal development.", "It means the brain develops entirely independently of environmental input.", "It refers to any individual experience that changes the brain later in life."],
     "correct": "It refers to early phases when the brain is primed to expect typical environmental inputs (e.g., visual, auditory) for normal development.",
     "explanation": "Experience-expectant development refers to earlier phases when the brain is primed to expect typical environmental inputs such as visual and auditory stimulation for normal development."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Which three primary germ layers are formed during gastrulation?",
     "options": ["Endoderm, mesoderm, ectoderm", "Proencephalon, mesencephalon, rhombencephalon", "Epiderm, dermis, hypoderm", "Neuroderm, myoderm, endothelm"],
     "correct": "Endoderm, mesoderm, ectoderm",
     "explanation": "The three germ layers produced at gastrulation are the endoderm, mesoderm and ectoderm, which give rise to different tissues and organs in the embryo."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Failure of the posterior neuropore to close during neurulation most commonly leads to which defect?",
     "options": ["Holoprosencephaly", "Spina bifida", "Microcephaly", "Anencephaly"],
     "correct": "Spina bifida",
     "explanation": "Failure of the posterior neuropore to close produces spina bifida, whereas anterior neuropore failure leads to anencephaly."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "According to the lecture, what is the fate of synapses that are more active during development?",
     "options": ["They are preferentially pruned", "They are transformed into glial cells", "They are strengthened and stabilised", "They become weakened and lose function"],
     "correct": "They are strengthened and stabilised",
     "explanation": "Active synapses are strengthened while less active ones are weakened and ultimately pruned — the 'use it or lose it' principle."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "What does the neurotrophic hypothesis propose about developing neurons?",
     "options": ["Neurons that establish effective connections obtain more neurotrophic factors and are more likely to survive", "Neurons do not rely on external factors once born", "Neurotrophic factors cause immediate neuronal death", "All neurons receive equal neurotrophic support regardless of connections formed"],
     "correct": "Neurons that establish effective connections obtain more neurotrophic factors and are more likely to survive",
     "explanation": "The neurotrophic hypothesis posits that neurons compete for limited neurotrophic factors. Those that establish effective connections obtain more and are more likely to survive."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "When does neurone production (neurogenesis) begin in the embryo?",
     "options": ["Embryonic day 42 (E42)", "At birth", "At the onset of adolescence", "Only in adulthood in the hippocampus"],
     "correct": "Embryonic day 42 (E42)",
     "explanation": "Neurone production begins in the embryonic period on embryonic day 42 (E42) and continues through mid-gestation in most brain areas."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Which of the following is a primary role of oligodendrocytes/myelination?",
     "options": ["Prune excess synapses during infancy", "Generate action potentials in axons", "Improve electrical conductance and synthesise trophic factors", "Direct migration of neurons from the ventricular zone"],
     "correct": "Improve electrical conductance and synthesise trophic factors",
     "explanation": "Oligodendrocytes form myelin around axons which improves conduction velocity and they also synthesise trophic factors that help maintain axonal health."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Which of these is listed as a category of neurodevelopmental disorders?",
     "options": ["Chronic obstructive pulmonary disease", "Myocardial infarction", "Alzheimer's disease", "Autism spectrum disorders"],
     "correct": "Autism spectrum disorders",
     "explanation": "The lecture lists autism spectrum disorders among the categories of neurodevelopmental disorders alongside intellectual disability, specific learning disorders and motor disorders."},
    {"topic": "Neurodevelopmental Disorders",
     "q": "Neurogenesis in adulthood continues (to a limited degree) in which brain regions?",
     "options": ["Thalamus and basal ganglia", "Hippocampus and olfactory bulb", "Brainstem nuclei and spinal cord", "Cerebral cortex and cerebellum"],
     "correct": "Hippocampus and olfactory bulb",
     "explanation": "Postnatal and limited adult neurogenesis persists in the hippocampus (dentate gyrus) and the olfactory bulb."},

    # ── NEUROPHARMACOLOGY (10) ─────────────────────────────────────────────────
    {"topic": "Neuropharmacology",
     "q": "What is the primary function of a neuron?",
     "options": ["Store neurotransmitters", "Produce hormones", "Receive, process, and transmit electrical signals", "Regulate blood flow"],
     "correct": "Receive, process, and transmit electrical signals",
     "explanation": "The primary function of a neuron is to receive, process and transmit electrical signals, enabling communication throughout the nervous system."},
    {"topic": "Neuropharmacology",
     "q": "Synaptic communication between neurons is primarily:",
     "options": ["Mechanical", "Electrical only", "Chemical only", "Electrochemical"],
     "correct": "Electrochemical",
     "explanation": "Synaptic communication is electrochemical — electrical signals (action potentials) trigger chemical neurotransmitter release across the synapse."},
    {"topic": "Neuropharmacology",
     "q": "What triggers neurotransmitter release from the presynaptic neuron?",
     "options": ["Receptor binding", "Action potential", "Enzyme activity", "Ion depletion"],
     "correct": "Action potential",
     "explanation": "An action potential arriving at the presynaptic terminal triggers calcium influx which causes synaptic vesicles to fuse with the membrane and release neurotransmitter."},
    {"topic": "Neuropharmacology",
     "q": "Neurotransmitters are stored in:",
     "options": ["Lysosomes", "Synaptic vesicles", "Mitochondria", "Nucleus"],
     "correct": "Synaptic vesicles",
     "explanation": "Neurotransmitters are packaged and stored in synaptic vesicles within the presynaptic terminal ready for release."},
    {"topic": "Neuropharmacology",
     "q": "Ionotropic receptors are best described as:",
     "options": ["G-protein coupled receptors", "Enzyme-linked receptors", "Ligand-gated ion channels", "Nuclear receptors"],
     "correct": "Ligand-gated ion channels",
     "explanation": "Ionotropic receptors are ligand-gated ion channels — binding of a neurotransmitter directly opens the channel, producing fast synaptic responses."},
    {"topic": "Neuropharmacology",
     "q": "Which ion is typically involved in inhibitory neurotransmission (e.g. GABA-A)?",
     "options": ["Sodium (Na+)", "Potassium (K+)", "Chloride (Cl-)", "Calcium (Ca2+)"],
     "correct": "Chloride (Cl-)",
     "explanation": "GABA-A receptors are chloride channels. Cl- influx hyperpolarises the postsynaptic membrane, making it less likely to fire."},
    {"topic": "Neuropharmacology",
     "q": "Metabotropic receptors differ from ionotropic receptors because they:",
     "options": ["Act faster", "Directly open ion channels", "Use second messenger systems", "Are only found in the periphery"],
     "correct": "Use second messenger systems",
     "explanation": "Metabotropic receptors are G-protein coupled and act via second messenger cascades, producing slower but longer-lasting effects compared to ionotropic receptors."},
    {"topic": "Neuropharmacology",
     "q": "The mesolimbic pathway connects:",
     "options": ["Substantia nigra to striatum", "VTA to nucleus accumbens", "Cortex to thalamus", "Hippocampus to amygdala"],
     "correct": "VTA to nucleus accumbens",
     "explanation": "The mesolimbic dopamine pathway runs from the ventral tegmental area (VTA) to the nucleus accumbens and is strongly associated with reward and motivation."},
    {"topic": "Neuropharmacology",
     "q": "How does cocaine primarily exert its effect on dopamine?",
     "options": ["Inhibits dopamine synthesis", "Blocks dopamine receptors", "Enhances dopamine reuptake", "Inhibits dopamine reuptake"],
     "correct": "Inhibits dopamine reuptake",
     "explanation": "Cocaine blocks the dopamine transporter (DAT), preventing reuptake of dopamine into the presynaptic terminal and increasing dopamine in the synapse."},
    {"topic": "Neuropharmacology",
     "q": "Which dopaminergic pathway is most associated with reward?",
     "options": ["Nigrostriatal", "Mesolimbic", "Mesocortical", "Tuberoinfundibular"],
     "correct": "Mesolimbic",
     "explanation": "The mesolimbic pathway (VTA to nucleus accumbens) is the primary reward pathway and is implicated in addiction and motivated behaviour."},

    # ── MEMORY DISORDERS (10) ──────────────────────────────────────────────────
    {"topic": "Memory Disorders",
     "q": "People with retrograde amnesia:",
     "options": ["Make too many memories", "Can't remember things from before the trauma", "Can't remember things from after the trauma", "Have completely lost their memory"],
     "correct": "Can't remember things from before the trauma",
     "explanation": "Retrograde amnesia is the inability to recall memories from before the traumatic event, in contrast to anterograde amnesia which affects formation of new memories."},
    {"topic": "Memory Disorders",
     "q": "Which two pathological hallmarks define Alzheimer's disease?",
     "options": ["Lewy bodies and neuronal loss", "Amyloid plaques and neurofibrillary tangles", "Demyelination and axonal loss", "Vascular infarcts and gliosis"],
     "correct": "Amyloid plaques and neurofibrillary tangles",
     "explanation": "Alzheimer's disease is defined pathologically by extracellular amyloid-beta plaques and intracellular neurofibrillary tangles composed of hyperphosphorylated tau."},
    {"topic": "Memory Disorders",
     "q": "Beta-amyloid is derived from:",
     "options": ["Tau protein", "Amyloid precursor protein (APP)", "Presenilin", "ApoE"],
     "correct": "Amyloid precursor protein (APP)",
     "explanation": "Beta-amyloid peptides are produced by sequential cleavage of amyloid precursor protein (APP) by beta-secretase and gamma-secretase."},
    {"topic": "Memory Disorders",
     "q": "Neurofibrillary tangles consist of:",
     "options": ["Misfolded alpha-synuclein", "Aggregated beta-amyloid", "Hyperphosphorylated tau", "Ubiquitin"],
     "correct": "Hyperphosphorylated tau",
     "explanation": "Neurofibrillary tangles are composed of hyperphosphorylated tau protein that has collapsed into insoluble filaments inside neurons."},
    {"topic": "Memory Disorders",
     "q": "Which brain region is most affected early in Alzheimer's disease?",
     "options": ["Cerebellum", "Brainstem", "Hippocampus", "Occipital cortex"],
     "correct": "Hippocampus",
     "explanation": "The hippocampus is one of the first brain regions affected in Alzheimer's disease, explaining why episodic memory loss is typically the earliest symptom."},
    {"topic": "Memory Disorders",
     "q": "The primary neurotransmitter deficit in Alzheimer's disease is:",
     "options": ["Dopamine", "Serotonin", "Acetylcholine", "Glutamate"],
     "correct": "Acetylcholine",
     "explanation": "Alzheimer's disease is characterised by loss of cholinergic neurons in the basal forebrain, leading to reduced acetylcholine — the basis for cholinesterase inhibitor treatments."},
    {"topic": "Memory Disorders",
     "q": "What is the role of beta-secretase and gamma-secretase in Alzheimer's disease?",
     "options": ["Degrading tau protein", "Producing beta-amyloid from APP", "Enhancing synaptic transmission", "Removing plaques"],
     "correct": "Producing beta-amyloid from APP",
     "explanation": "Beta-secretase and gamma-secretase cleave amyloid precursor protein (APP) to generate amyloidogenic beta-amyloid fragments."},
    {"topic": "Memory Disorders",
     "q": "Which genetic risk factor is most strongly associated with late-onset Alzheimer's disease?",
     "options": ["APP mutation", "Presenilin-1 mutation", "APOE e4 allele", "Tau mutation"],
     "correct": "APOE e4 allele",
     "explanation": "The APOE e4 allele is the strongest known genetic risk factor for late-onset Alzheimer's disease, increasing risk significantly compared to the e3 allele."},
    {"topic": "Memory Disorders",
     "q": "Tau pathology progression in Alzheimer's disease follows:",
     "options": ["Random distribution", "Braak staging", "Hoehn and Yahr staging", "TNM staging"],
     "correct": "Braak staging",
     "explanation": "Tau pathology spreads in a predictable pattern through the brain, described by Braak staging — from entorhinal cortex through hippocampus to neocortex."},
    {"topic": "Memory Disorders",
     "q": "Alzheimer's disease is an inevitable part of ageing.",
     "options": ["True", "False"],
     "correct": "False",
     "explanation": "Alzheimer's disease is not an inevitable part of ageing. While age is the greatest risk factor, many people live into old age without developing it."},

    # ── MOVEMENT DISORDERS (10) ───────────────────────────────────────────────
    {"topic": "Movement Disorders",
     "q": "Activation of the primary motor cortex elicits all movement unilaterally (on the same side).",
     "options": ["True", "False"],
     "correct": "False",
     "explanation": "The primary motor cortex controls movement contralaterally — activation of the left motor cortex produces movement on the right side of the body, and vice versa."},
    {"topic": "Movement Disorders",
     "q": "The neurotransmitter used at the motor endplate (motor neurone-muscle junction) is:",
     "options": ["Noradrenaline", "Glutamate", "GABA", "Acetylcholine"],
     "correct": "Acetylcholine",
     "explanation": "Acetylcholine is released by motor neurons at the neuromuscular junction and binds to nicotinic receptors on the motor end plate to trigger muscle contraction."},
    {"topic": "Movement Disorders",
     "q": "What types of receptors are present on the motor end plate?",
     "options": ["Muscarinic", "Nicotinic", "Beta adrenergic", "NMDA"],
     "correct": "Nicotinic",
     "explanation": "The motor end plate contains nicotinic acetylcholine receptors (nAChRs) — ionotropic receptors that mediate fast excitatory transmission at the NMJ."},
    {"topic": "Movement Disorders",
     "q": "Which of the following is NOT part of the nigro-striatal pathway?",
     "options": ["Putamen", "Substantia nigra", "Caudate", "Amygdala"],
     "correct": "Amygdala",
     "explanation": "The nigrostriatal pathway connects the substantia nigra pars compacta to the striatum (caudate and putamen). The amygdala is part of the limbic system."},
    {"topic": "Movement Disorders",
     "q": "The cerebellum contains areas mapped to parts of the body.",
     "options": ["True", "False"],
     "correct": "True",
     "explanation": "The cerebellum has a somatotopic organisation with areas mapped to different body parts, similar to the motor and somatosensory homunculi of the cortex."},
    {"topic": "Movement Disorders",
     "q": "Movement occurs in a sequential pattern dictated by hierarchical organisation of the nervous system. Which area is important in the timing and balance, correcting movement errors?",
     "options": ["Cerebellum", "Primary motor cortex", "Basal ganglia", "Primary somatosensory cortex"],
     "correct": "Cerebellum",
     "explanation": "The cerebellum is critical for timing, coordination and error correction of movement, receiving ongoing feedback to fine-tune motor output."},
    {"topic": "Movement Disorders",
     "q": "The extrapyramidal tracts of the motor system cause voluntary (conscious) actions.",
     "options": ["True", "False"],
     "correct": "False",
     "explanation": "Voluntary conscious actions are mediated by the pyramidal (corticospinal) tract. The extrapyramidal system regulates muscle tone, posture and involuntary movement."},
    {"topic": "Movement Disorders",
     "q": "Haptic-proprioceptive axons ascend the spinal cord on the same side of the body.",
     "options": ["True", "False"],
     "correct": "True",
     "explanation": "Proprioceptive and fine touch (haptic) information travels in the dorsal columns and ascends ipsilaterally before crossing at the level of the medulla."},
    {"topic": "Movement Disorders",
     "q": "Tourette's syndrome is primarily associated with overactivation of which brain area?",
     "options": ["Basal ganglia", "Cerebellum", "Primary motor cortex", "Thalamus"],
     "correct": "Basal ganglia",
     "explanation": "Tourette's syndrome is associated with dysfunction and overactivation of the basal ganglia, contributing to the characteristic tics and involuntary movements."},
    {"topic": "Movement Disorders",
     "q": "Progressive supranuclear palsy, characterised by loss of balance, slowing movement, difficulty moving the eyes and dementia, is classed as a hyperkinetic movement disorder.",
     "options": ["True", "False"],
     "correct": "False",
     "explanation": "Progressive supranuclear palsy is a hypokinetic (not hyperkinetic) movement disorder — it features slowing and rigidity rather than excess involuntary movement."},

    # ── VISUAL, AUDITORY & LANGUAGE DISORDERS (10) ────────────────────────────
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Which thalamic nucleus is highlighted as playing a major role in attention and sensory filtering?",
     "options": ["Lateral geniculate nucleus", "Medial geniculate body", "Pulvinar nucleus", "Caudate nucleus"],
     "correct": "Pulvinar nucleus",
     "explanation": "The pulvinar nucleus of the thalamus is a key structure involved in filtering out unnecessary sensory information and attention control — illustrating the 'cocktail party' effect."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Which layer of the primary visual cortex is described as myelinated and forming the 'line of Gennari'?",
     "options": ["Layer 2", "Layer 4", "Layer 6", "Layer 1"],
     "correct": "Layer 4",
     "explanation": "Layer 4 of the primary visual cortex (V1) is myelinated and contains the line of Gennari, a distinguishing anatomical feature visible to the naked eye."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Damage to the fusiform gyrus is most strongly associated with which clinical deficit?",
     "options": ["Alexia without agraphia", "Motor apraxia", "Auditory agnosia", "Prosopagnosia (face blindness)"],
     "correct": "Prosopagnosia (face blindness)",
     "explanation": "Damage to the fusiform gyrus is thought to lead to prosopagnosia (face blindness), reflecting the fusiform area's role in face and body recognition."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Blindsight — preserved visual responses without conscious perception — typically results from lesions where?",
     "options": ["Superior colliculus only", "Primary visual cortex (V1)", "Medial geniculate body", "Inferior temporal cortex"],
     "correct": "Primary visual cortex (V1)",
     "explanation": "Blindsight occurs in patients with lesions to the primary visual cortex (V1), allowing non-conscious visual pathways to mediate some performance despite lack of conscious sight."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Which neurotransmitter do hair cells in the cochlea release to signal to auditory nerve fibres?",
     "options": ["Dopamine", "GABA", "Glutamate", "Acetylcholine"],
     "correct": "Glutamate",
     "explanation": "Hair cells release glutamate as their principal neurotransmitter when they transduce mechanical stimulation into chemical signals at the synapse with auditory nerve fibres."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "In the 'two streams' hypothesis of visual processing, which stream projects to the temporal cortex and is primarily involved in object recognition ('what')?",
     "options": ["Retinotectal pathway", "Lateral geniculate pathway", "Dorsal stream (to parietal cortex)", "Ventral stream (to temporal cortex)"],
     "correct": "Ventral stream (to temporal cortex)",
     "explanation": "The ventral stream runs V1 → V2 → V4 → temporal (inferior and fusiform) cortex and is specialised for object recognition — the 'what' pathway."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Which feature best characterises Wernicke's aphasia?",
     "options": ["Isolated speech apraxia without language impairment", "Non-fluent, effortful speech with preserved comprehension", "Fluent speech with poor comprehension (receptive aphasia)", "Pure word deafness with preserved speech production"],
     "correct": "Fluent speech with poor comprehension (receptive aphasia)",
     "explanation": "Wernicke's aphasia produces fluent, effortless speech with intact syntax but severe difficulty understanding spoken and written language."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Which inner ear structure is described as the receptor organ that transduces vibrations into electrochemical signals?",
     "options": ["Organ of Corti", "Eustachian tube", "Tympanic membrane", "Oval window"],
     "correct": "Organ of Corti",
     "explanation": "The Organ of Corti, located within the cochlear duct, is the receptor organ for hearing that converts mechanical vibrations into electrical nerve signals via hair cell movement."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Charles Bonnet syndrome is primarily associated with which clinical circumstance?",
     "options": ["Olfactory hallucinations due to temporal lobe epilepsy", "Tactile hallucinations in peripheral neuropathy", "Auditory hallucinations in schizophrenia", "Complex visual hallucinations in visually impaired individuals"],
     "correct": "Complex visual hallucinations in visually impaired individuals",
     "explanation": "Charles Bonnet syndrome describes vivid, complex visual hallucinations occurring in otherwise psychologically normal individuals with significant visual impairment."},
    {"topic": "Visual, Auditory & Language Disorders",
     "q": "Dementia with Lewy bodies (DLB) is pathologically defined by intracellular inclusions composed of which protein?",
     "options": ["Alpha-synuclein", "TDP-43", "Amyloid-beta", "Tau protein"],
     "correct": "Alpha-synuclein",
     "explanation": "DLB is defined by alpha-synuclein-containing intracellular inclusions (Lewy bodies). Visual hallucinations are a core clinical feature of DLB."},

    # ── AFFECTIVE DISORDERS (10) ──────────────────────────────────────────────
    {"topic": "Affective Disorders",
     "q": "Which of the following best defines an affective disorder?",
     "options": ["A disorder caused by exclusive neurotransmitter loss", "A disturbance of emotion severe enough to impair functioning", "A condition resulting only from genetic mutations", "A disorder characterised only by mania"],
     "correct": "A disturbance of emotion severe enough to impair functioning",
     "explanation": "Affective disorders are defined by a disturbance of mood or emotion that is severe enough to impair an individual's daily functioning and quality of life."},
    {"topic": "Affective Disorders",
     "q": "How many symptoms (out of nine) must be present for at least two weeks to diagnose Major Depressive Disorder?",
     "options": ["Three", "Five", "Seven", "Nine"],
     "correct": "Five",
     "explanation": "DSM criteria require at least five of nine specified symptoms to be present for at least two weeks for a diagnosis of Major Depressive Disorder."},
    {"topic": "Affective Disorders",
     "q": "The monoamine hypothesis of depression suggests depression results from a deficiency in:",
     "options": ["GABAergic inhibition", "Glutamatergic signalling", "Brain monoaminergic activity", "Neuropeptide synthesis"],
     "correct": "Brain monoaminergic activity",
     "explanation": "The monoamine hypothesis proposes that depression results from reduced activity of monoamine neurotransmitters (serotonin, noradrenaline, dopamine) in the brain."},
    {"topic": "Affective Disorders",
     "q": "Which neurotransmitters are most associated with mood regulation?",
     "options": ["GABA and glutamate", "Serotonin and noradrenaline", "Dopamine and acetylcholine", "Phenethylamine and histamine"],
     "correct": "Serotonin and noradrenaline",
     "explanation": "Serotonin and noradrenaline are the neurotransmitters most closely associated with mood regulation and are the primary targets of antidepressant medications."},
    {"topic": "Affective Disorders",
     "q": "A major problem with the monoamine hypothesis is:",
     "options": ["Antidepressants work immediately", "Tryptophan depletion always induces depression in healthy people", "Therapeutic latency despite rapid synaptic neurochemical effects", "Monoamines do not affect mood"],
     "correct": "Therapeutic latency despite rapid synaptic neurochemical effects",
     "explanation": "Antidepressants raise synaptic monoamine levels within hours, yet clinical benefit takes weeks — this therapeutic latency is a major challenge to the simple monoamine hypothesis."},
    {"topic": "Affective Disorders",
     "q": "Metabotropic receptors are characterised by:",
     "options": ["Direct ion channel opening upon ligand binding", "G-protein-linked signalling and slower, longer-lasting effect", "Exclusive expression in the spinal cord", "Activation only by synthetic drugs"],
     "correct": "G-protein-linked signalling and slower, longer-lasting effect",
     "explanation": "Metabotropic receptors are G-protein coupled receptors that activate second messenger cascades, producing slower but more prolonged effects than ionotropic receptors."},
    {"topic": "Affective Disorders",
     "q": "Prolonged activation of the HPA axis can cause:",
     "options": ["Cerebellar hypertrophy", "Hippocampal atrophy", "Increased BDNF expression", "Reduced glucocorticoid level"],
     "correct": "Hippocampal atrophy",
     "explanation": "Chronic stress and prolonged HPA axis activation leads to elevated cortisol, which can cause hippocampal atrophy due to glucocorticoid-mediated neurotoxicity."},
    {"topic": "Affective Disorders",
     "q": "The neurotrophic hypothesis of depression emphasises the role of:",
     "options": ["Loss of dopamine in the basal ganglia", "Reduced BDNF and impaired neuronal plasticity", "Excess glutamatergic excitation", "Abnormalities in ionotropic receptors"],
     "correct": "Reduced BDNF and impaired neuronal plasticity",
     "explanation": "The neurotrophic hypothesis proposes that depression involves reduced brain-derived neurotrophic factor (BDNF) and impaired synaptic plasticity, particularly in the hippocampus."},
    {"topic": "Affective Disorders",
     "q": "Late-onset depression (>60 years) is associated with:",
     "options": ["Increased frontal cortical volume", "Better treatment response than early-onset cases", "Structural brain changes including hippocampal volume reduction", "Absence of cerebrovascular risk factors"],
     "correct": "Structural brain changes including hippocampal volume reduction",
     "explanation": "Late-onset depression is associated with structural brain changes including hippocampal volume reduction and white matter changes, often linked to cerebrovascular risk factors."},
    {"topic": "Affective Disorders",
     "q": "Which treatment is now recognised as effective for treatment-resistant depression, acting via NMDA receptor antagonism?",
     "options": ["Fluoxetine", "Reboxetine", "Memantine", "Ketamine"],
     "correct": "Ketamine",
     "explanation": "Ketamine, an NMDA receptor antagonist, has been shown to produce rapid antidepressant effects in treatment-resistant depression, often within hours of administration."},

    # ── SCHIZOPHRENIA (10) ────────────────────────────────────────────────────
    {"topic": "Schizophrenia",
     "q": "The literal translation of 'schizophrenia' refers to:",
     "options": ["Split personality", "Splitting of the mind", "Broken emotions", "Fragmented memories"],
     "correct": "Splitting of the mind",
     "explanation": "The term schizophrenia comes from the Greek words 'schizo' (split) and 'phren' (mind) — referring to a splitting of mental functions, not a split personality."},
    {"topic": "Schizophrenia",
     "q": "The lifetime prevalence of schizophrenia is approximately:",
     "options": ["0.1%", "1%", "5%", "10%"],
     "correct": "1%",
     "explanation": "Schizophrenia affects approximately 1% of the population worldwide, making it a relatively rare but severely disabling condition."},
    {"topic": "Schizophrenia",
     "q": "Positive symptoms of schizophrenia include:",
     "options": ["Flat affect", "Avolition", "Delusions and hallucinations", "Social withdrawal"],
     "correct": "Delusions and hallucinations",
     "explanation": "Positive symptoms represent additions to normal experience — including delusions, hallucinations and disorganised speech. Flat affect, avolition and social withdrawal are negative symptoms."},
    {"topic": "Schizophrenia",
     "q": "Which type of hallucination is most common in schizophrenia?",
     "options": ["Visual", "Tactile", "Olfactory", "Auditory"],
     "correct": "Auditory",
     "explanation": "Auditory hallucinations — typically hearing voices — are the most common type of hallucination in schizophrenia, occurring in around 70% of patients."},
    {"topic": "Schizophrenia",
     "q": "Negative symptoms include all of the following EXCEPT:",
     "options": ["Lack of emotion", "Reduced motivation", "Delusional beliefs", "Social withdrawal"],
     "correct": "Delusional beliefs",
     "explanation": "Delusional beliefs are positive symptoms. Negative symptoms reflect reductions in normal functioning — such as flat affect, avolition, alogia and social withdrawal."},
    {"topic": "Schizophrenia",
     "q": "Cognitive symptoms of schizophrenia typically include:",
     "options": ["Excessive emotional expression", "Disorganised thinking and poor memory", "Repetitive motor movements", "Grandiose delusions"],
     "correct": "Disorganised thinking and poor memory",
     "explanation": "Cognitive symptoms of schizophrenia include disorganised thinking, impaired working memory, poor attention and executive dysfunction."},
    {"topic": "Schizophrenia",
     "q": "Catatonic immobility refers to:",
     "options": ["Rapid, disorganised speech", "Repetitive hand gestures", "Maintaining an unusual posture for long periods", "Hearing voices commanding movement"],
     "correct": "Maintaining an unusual posture for long periods",
     "explanation": "Catatonia involves a state of unresponsiveness or immobility, including maintaining unusual or rigid postures for extended periods."},
    {"topic": "Schizophrenia",
     "q": "The dopamine hypothesis suggests schizophrenia is associated with:",
     "options": ["Low dopamine in all brain regions", "Excess dopamine activity", "Reduced serotonin levels only", "Excess norepinephrine activity"],
     "correct": "Excess dopamine activity",
     "explanation": "The dopamine hypothesis proposes that positive symptoms of schizophrenia result from excess dopaminergic activity, particularly in the mesolimbic pathway."},
    {"topic": "Schizophrenia",
     "q": "Schizophrenia is linked to structural abnormalities particularly in the:",
     "options": ["Occipital cortex", "Prefrontal cortex", "Cerebellum", "Medulla oblongata"],
     "correct": "Prefrontal cortex",
     "explanation": "Schizophrenia is associated with reduced grey matter and hypofrontality in the prefrontal cortex, contributing to negative and cognitive symptoms."},
    {"topic": "Schizophrenia",
     "q": "Which of the following is a first-line treatment for schizophrenia?",
     "options": ["Lithium", "Benzodiazepines", "Atypical antipsychotics", "Antidepressants"],
     "correct": "Atypical antipsychotics",
     "explanation": "Atypical (second-generation) antipsychotics are the first-line pharmacological treatment for schizophrenia, targeting dopamine and serotonin receptors."},

    # ── DELIRIUM (10) ─────────────────────────────────────────────────────────
    {"topic": "Delirium",
     "q": "Which of the following best defines delirium?",
     "options": ["A chronic, progressive decline in cognitive function", "An acute confusional state with fluctuating consciousness", "A primary psychiatric disorder characterised by hallucination", "A stable impairment of memory due to ageing"],
     "correct": "An acute confusional state with fluctuating consciousness",
     "explanation": "Delirium is an acute neuropsychiatric syndrome characterised by disturbed attention, awareness and cognition that develops rapidly and tends to fluctuate."},
    {"topic": "Delirium",
     "q": "Delirium most commonly develops over which time frame?",
     "options": ["Months to years", "Weeks", "Hours to days", "Childhood to adulthood"],
     "correct": "Hours to days",
     "explanation": "Delirium develops acutely over hours to days, distinguishing it from dementia which progresses over months to years."},
    {"topic": "Delirium",
     "q": "An 82-year-old man becomes acutely confused following hip surgery. He is drowsy, inattentive and misses meals but does not appear agitated. Which delirium subtype is most likely?",
     "options": ["Hyperactive delirium", "Hypoactive delirium", "Mixed delirium", "Psychotic depression"],
     "correct": "Hypoactive delirium",
     "explanation": "Hypoactive delirium presents with reduced activity, drowsiness and inattention without agitation — it is the most common subtype and frequently missed."},
    {"topic": "Delirium",
     "q": "Why is hypoactive delirium frequently under-diagnosed in hospital settings?",
     "options": ["It occurs only in patients with dementia", "Symptoms resemble anxiety disorders", "Patients are quiet and not disruptive", "It resolves more rapidly than other subtypes"],
     "correct": "Patients are quiet and not disruptive",
     "explanation": "Hypoactive delirium is easily missed because patients are quiet, withdrawn and non-disruptive — unlike the more conspicuous hyperactive subtype."},
    {"topic": "Delirium",
     "q": "Which of the following scenarios best illustrates the concept of delirium being multifactorial?",
     "options": ["Acute confusion caused by a single traumatic brain injury", "Delirium occurring solely due to advanced age", "A vulnerable patient developing delirium after infection and polypharmacy", "Genetic predisposition leading to early-onset delirium"],
     "correct": "A vulnerable patient developing delirium after infection and polypharmacy",
     "explanation": "Delirium is typically multifactorial — a predisposed patient (e.g. elderly, with cognitive impairment) develops delirium when exposed to multiple precipitating factors such as infection and polypharmacy."},
    {"topic": "Delirium",
     "q": "Which combination of factors would place an older patient at highest risk of developing delirium?",
     "options": ["Female sex, good vision, no comorbidities", "Male sex, visual impairment, polypharmacy", "Young age, dehydration, recent surgery", "Regular medication review and mobilisation"],
     "correct": "Male sex, visual impairment, polypharmacy",
     "explanation": "Older male patients with sensory impairment (especially visual) and polypharmacy are at particularly high risk of delirium in hospital settings."},
    {"topic": "Delirium",
     "q": "Which mechanism best explains how anticholinergic drugs contribute to delirium?",
     "options": ["Increasing dopamine activity in the limbic system", "Blocking GABA receptors in the cortex", "Inhibiting acetylcholine-mediated cognitive function", "Enhancing neuroinflammatory clearance"],
     "correct": "Inhibiting acetylcholine-mediated cognitive function",
     "explanation": "Anticholinergic drugs block muscarinic receptors, reducing acetylcholine-mediated signalling critical for attention and memory — a key mechanism in drug-induced delirium."},
    {"topic": "Delirium",
     "q": "Which pathophysiological process is most strongly associated with delirium?",
     "options": ["Demyelination of central axons", "Neurotransmitter imbalance and inflammation", "Selective hippocampal neuronal loss", "Alpha-synuclein aggregation"],
     "correct": "Neurotransmitter imbalance and inflammation",
     "explanation": "Delirium is most strongly linked to neurotransmitter imbalance (particularly cholinergic deficiency and dopaminergic excess) combined with neuroinflammation."},
    {"topic": "Delirium",
     "q": "Which statement best reflects current understanding of the relationship between delirium and dementia?",
     "options": ["Delirium only occurs in patients with established dementia", "Delirium has no long-term cognitive consequences", "Delirium significantly increases the risk of future dementia", "Dementia protects against delirium"],
     "correct": "Delirium significantly increases the risk of future dementia",
     "explanation": "Delirium is now recognised as a significant independent risk factor for subsequent dementia, even in those without prior cognitive impairment."},
    {"topic": "Delirium",
     "q": "Which mechanism may explain the high prevalence of delirium in severe COVID-19?",
     "options": ["Chronic neurodegeneration", "Direct psychiatric toxicity of antivirals", "Reduced cerebral blood flow due to ageing alone", "Combined effects of hypoxia, inflammation and metabolic disturbance"],
     "correct": "Combined effects of hypoxia, inflammation and metabolic disturbance",
     "explanation": "Severe COVID-19 causes delirium through multiple mechanisms including hypoxia, systemic inflammation, metabolic disturbance and direct neurological effects."},

    # ── PERIPHERAL NERVOUS SYSTEM (10) ────────────────────────────────────────
    {"topic": "Peripheral Nervous System",
     "q": "Which division of the nervous system is responsible for non-conscious control of visceral functions?",
     "options": ["Central nervous system", "Somatic nervous system", "Autonomic nervous system", "Sensory nervous system"],
     "correct": "Autonomic nervous system",
     "explanation": "The autonomic nervous system controls involuntary visceral functions including heart rate, digestion, respiration and glandular secretion."},
    {"topic": "Peripheral Nervous System",
     "q": "Which connective tissue layer surrounds individual nerve fibres within a peripheral nerve?",
     "options": ["Epineurium", "Perineurium", "Endoneurium", "Myelin sheath"],
     "correct": "Endoneurium",
     "explanation": "The endoneurium surrounds individual nerve fibres (axons), the perineurium surrounds fascicles, and the epineurium surrounds the entire nerve trunk."},
    {"topic": "Peripheral Nervous System",
     "q": "Which cranial nerve is primarily responsible for hearing and balance?",
     "options": ["Facial (VII)", "Vestibulocochlear (VIII)", "Glossopharyngeal (IX)", "Vagus (X)"],
     "correct": "Vestibulocochlear (VIII)",
     "explanation": "The vestibulocochlear nerve (CN VIII) has two divisions — the cochlear nerve for hearing and the vestibular nerve for balance and spatial orientation."},
    {"topic": "Peripheral Nervous System",
     "q": "Spinal nerves are described as 'mixed nerves' because they contain:",
     "options": ["Only sensory fibres", "Only motor fibres", "Sensory and autonomic fibres only", "Both sensory and motor fibres"],
     "correct": "Both sensory and motor fibres",
     "explanation": "Spinal nerves are mixed nerves formed by the dorsal (sensory) and ventral (motor) roots joining together, carrying both afferent and efferent signals."},
    {"topic": "Peripheral Nervous System",
     "q": "What neurotransmitter is released at the neuromuscular junction?",
     "options": ["Dopamine", "Noradrenaline", "Acetylcholine", "Glutamate"],
     "correct": "Acetylcholine",
     "explanation": "Acetylcholine is released by alpha-motor neurons at the neuromuscular junction, binding to nicotinic receptors to trigger muscle contraction."},
    {"topic": "Peripheral Nervous System",
     "q": "The parasympathetic nervous system is best described as:",
     "options": ["'Fight or flight'", "'Rest and digest'", "Responsible for voluntary movement", "Controlling only spinal reflexes"],
     "correct": "'Rest and digest'",
     "explanation": "The parasympathetic nervous system promotes 'rest and digest' functions — slowing heart rate, stimulating digestion and conserving energy."},
    {"topic": "Peripheral Nervous System",
     "q": "Which disorder is an acute autoimmune demyelinating polyneuropathy, often triggered by infection such as Campylobacter jejuni?",
     "options": ["Charcot-Marie-Tooth disease", "Guillain-Barre syndrome", "Amyotrophic lateral sclerosis", "Diabetic neuropathy"],
     "correct": "Guillain-Barre syndrome",
     "explanation": "Guillain-Barre syndrome is an acute autoimmune polyneuropathy often triggered by infection. Campylobacter jejuni is a classic preceding infection due to molecular mimicry."},
    {"topic": "Peripheral Nervous System",
     "q": "Which peripheral nervous system disorder is most strongly associated with chronic hyperglycaemia?",
     "options": ["Guillain-Barre syndrome", "Polio", "Diabetes-associated neuropathy", "Myasthenia gravis"],
     "correct": "Diabetes-associated neuropathy",
     "explanation": "Chronic hyperglycaemia causes peripheral nerve damage through multiple mechanisms including oxidative stress, advanced glycation and reduced nerve blood supply."},
    {"topic": "Peripheral Nervous System",
     "q": "Amyotrophic lateral sclerosis (ALS) primarily affects which type of neurons?",
     "options": ["Sensory neurons only", "Autonomic neurons", "Upper and lower motor neurons", "Peripheral sensory neurons"],
     "correct": "Upper and lower motor neurons",
     "explanation": "ALS selectively degenerates both upper motor neurons (cortex/corticospinal tract) and lower motor neurons (brainstem/spinal cord), causing progressive muscle weakness and wasting."},
    {"topic": "Peripheral Nervous System",
     "q": "Which pathological finding is characteristic of ALS?",
     "options": ["Loss of oligodendrocytes and remyelination", "Deposition of amyloid plaques", "TDP-43-containing intracellular inclusions", "Antibodies against acetylcholine receptors"],
     "correct": "TDP-43-containing intracellular inclusions",
     "explanation": "TDP-43 proteinopathy — with cytoplasmic TDP-43-containing inclusions in motor neurons — is the pathological hallmark of the vast majority of ALS cases."},
]

# ══════════════════════════════════════════════════════════════════════════════
# DATA — CRANIAL NERVES
# ══════════════════════════════════════════════════════════════════════════════
# Each entry: number (Roman), name, type, function(s), mnemonic cue, clinical note
CRANIAL_NERVES = [
    {
        "number": "I",
        "name": "Olfactory",
        "type": "Sensory",
        "function": "Smell (olfaction) — transmits sensory signals from olfactory receptor neurons in the nasal epithelium to the olfactory bulb.",
        "origin": "Olfactory epithelium → olfactory bulb",
        "clinical": "Damage causes anosmia (loss of smell). Tested by asking the patient to identify familiar scents (e.g. coffee, mint) with each nostril.",
        "mnemonic": "CN I — 'One nose' — purely sensory, smell only.",
    },
    {
        "number": "II",
        "name": "Optic",
        "type": "Sensory",
        "function": "Vision — transmits visual information from retinal ganglion cells through the optic nerve, chiasm and tracts to the lateral geniculate nucleus.",
        "origin": "Retina → lateral geniculate nucleus (thalamus)",
        "clinical": "Damage causes visual field defects. Tested with visual acuity charts, visual field testing and the pupillary light reflex (afferent limb).",
        "mnemonic": "CN II — 'Two eyes' — purely sensory, vision only.",
    },
    {
        "number": "III",
        "name": "Oculomotor",
        "type": "Motor (somatic + parasympathetic)",
        "function": "Controls four of the six extraocular muscles (SR, IR, MR, IO) and levator palpebrae superioris. Parasympathetic fibres constrict the pupil (via ciliary ganglion) and control lens accommodation.",
        "origin": "Midbrain (oculomotor nucleus + Edinger-Westphal nucleus)",
        "clinical": "Palsy causes ptosis, 'down-and-out' eye position, and a dilated fixed pupil (loss of parasympathetic tone). A posterior communicating artery aneurysm is a classic cause.",
        "mnemonic": "CN III — moves most eye muscles; loss = 'down and out' eye + drooping lid.",
    },
    {
        "number": "IV",
        "name": "Trochlear",
        "type": "Motor",
        "function": "Controls the superior oblique muscle, which intorts the eye and depresses it when adducted.",
        "origin": "Midbrain (trochlear nucleus) — only cranial nerve to exit from the dorsal brainstem",
        "clinical": "Palsy causes vertical diplopia (worst on looking down, e.g. descending stairs). The head tilts away from the affected side to compensate.",
        "mnemonic": "CN IV — 'Four = floor' — the superior oblique depresses the eye; palsy makes stairs difficult.",
    },
    {
        "number": "V",
        "name": "Trigeminal",
        "type": "Mixed (sensory + motor)",
        "function": "Largest cranial nerve. Sensory from the face, scalp, cornea, teeth, sinuses and anterior two-thirds of the tongue (general sensation). Motor to muscles of mastication (temporalis, masseter, pterygoids).",
        "origin": "Pons; three divisions: V1 ophthalmic, V2 maxillary, V3 mandibular",
        "clinical": "Trigeminal neuralgia: severe unilateral facial pain. Corneal reflex: afferent limb V1; efferent limb CN VII. Jaw-jerk reflex tests V3.",
        "mnemonic": "CN V — 'Five fingers on the face' — sensory to face, motor to chew.",
    },
    {
        "number": "VI",
        "name": "Abducens",
        "type": "Motor",
        "function": "Controls the lateral rectus muscle, which abducts the eye (moves it laterally).",
        "origin": "Pons (abducens nucleus)",
        "clinical": "Palsy causes inability to abduct the eye → horizontal diplopia, worse at distance. The eye deviates medially at rest. Long intracranial course makes CN VI vulnerable to raised intracranial pressure.",
        "mnemonic": "CN VI — 'Six = sideways' — abducts the eye; palsy = eye stuck looking inward.",
    },
    {
        "number": "VII",
        "name": "Facial",
        "type": "Mixed (motor + sensory + parasympathetic)",
        "function": "Motor to muscles of facial expression. Parasympathetic to lacrimal, submandibular and sublingual glands. Taste from anterior two-thirds of tongue (via chorda tympani). Sensory to external ear.",
        "origin": "Pons (facial nucleus)",
        "clinical": "Bell's palsy: LMN lesion causes ipsilateral facial weakness including forehead (sparing forehead = UMN lesion). Also affects taste and lacrimation depending on lesion level.",
        "mnemonic": "CN VII — 'Faces seven ways' — expression, tears, taste (ant. 2/3), saliva.",
    },
    {
        "number": "VIII",
        "name": "Vestibulocochlear",
        "type": "Sensory",
        "function": "Two divisions: cochlear (hearing — from hair cells of the organ of Corti) and vestibular (balance and head position — from semicircular canals and otolith organs).",
        "origin": "Inner ear → cochlear and vestibular nuclei in the pons/medulla",
        "clinical": "Damage causes sensorineural hearing loss, tinnitus and/or vertigo. Acoustic neuroma (vestibular schwannoma) is a classic CN VIII lesion. Tested with Rinne and Weber tuning fork tests.",
        "mnemonic": "CN VIII — 'Eight = hearing and balance, standing straight'.",
    },
    {
        "number": "IX",
        "name": "Glossopharyngeal",
        "type": "Mixed",
        "function": "Sensory from posterior one-third of tongue (taste + general sensation), pharynx, tonsils, and carotid body/sinus. Motor to stylopharyngeus. Parasympathetic to parotid gland.",
        "origin": "Medulla (nucleus ambiguus, nucleus tractus solitarius)",
        "clinical": "Gag reflex afferent limb (CN IX); efferent limb CN X. Glossopharyngeal neuralgia: severe throat/ear pain on swallowing. Also relays carotid baroreceptor signals for blood pressure regulation.",
        "mnemonic": "CN IX — 'Nine = gag reflex afferent, taste post. tongue, parotid'.",
    },
    {
        "number": "X",
        "name": "Vagus",
        "type": "Mixed",
        "function": "The 'wandering nerve'. Parasympathetic to thoracic and abdominal viscera (heart, lungs, GI tract to splenic flexure). Motor to pharynx and larynx (speech, swallowing). Sensory from larynx, trachea, oesophagus, and abdominal organs.",
        "origin": "Medulla (dorsal motor nucleus, nucleus ambiguus)",
        "clinical": "Unilateral damage: hoarse voice, dysphagia, loss of gag reflex (efferent). Bilateral: fatal if untreated. Recurrent laryngeal nerve branch vulnerable in thyroid surgery.",
        "mnemonic": "CN X — 'Vague about everything' — the longest CN, innervates viscera widely.",
    },
    {
        "number": "XI",
        "name": "Accessory",
        "type": "Motor",
        "function": "Innervates sternocleidomastoid (head rotation to opposite side) and trapezius (shoulder elevation and scapular stabilisation).",
        "origin": "Spinal cord (C1–C5) + medulla; unique in having a spinal root",
        "clinical": "Damage (e.g. neck dissection surgery) causes drooping shoulder, weakness of shoulder shrug, and difficulty turning head against resistance.",
        "mnemonic": "CN XI — 'Eleven = shrug your shoulders and turn your head'.",
    },
    {
        "number": "XII",
        "name": "Hypoglossal",
        "type": "Motor",
        "function": "Controls all intrinsic and most extrinsic muscles of the tongue, enabling speech articulation, chewing and swallowing.",
        "origin": "Medulla (hypoglossal nucleus)",
        "clinical": "LMN lesion: tongue deviates toward the side of the lesion on protrusion (ipsilateral weakness). Fasciculations visible in LMN lesions. Relevant in motor neurone disease.",
        "mnemonic": "CN XII — 'Twelve = tongue' — tongue deviates toward the lesion.",
    },
]

# Question modes for the cranial nerve game
CN_MODES = {
    "Name the Nerve": {
        "description": "A cranial nerve number is shown. Select the correct name.",
        "prompt_key": "number",
        "answer_key": "name",
        "options_pool": [cn["name"] for cn in CRANIAL_NERVES],
    },
    "Name the Number": {
        "description": "A cranial nerve name is shown. Select the correct Roman numeral.",
        "prompt_key": "name",
        "answer_key": "number",
        "options_pool": [cn["number"] for cn in CRANIAL_NERVES],
    },
    "Identify the Function": {
        "description": "A cranial nerve name is shown. Select its primary function.",
        "prompt_key": "name",
        "answer_key": "function",
        "options_pool": [cn["function"] for cn in CRANIAL_NERVES],
    },
    "Identify the Type": {
        "description": "A cranial nerve name is shown. Select whether it is sensory, motor, or mixed.",
        "prompt_key": "name",
        "answer_key": "type",
        "options_pool": ["Sensory", "Motor", "Motor (somatic + parasympathetic)",
                         "Motor (motor + sensory + parasympathetic)", "Mixed",
                         "Mixed (sensory + motor)", "Mixed (motor + sensory + parasympathetic)"],
    },
    "Clinical Scenario": {
        "description": "A clinical sign or deficit is shown. Identify which cranial nerve is affected.",
        "prompt_key": "clinical",
        "answer_key": "name",
        "options_pool": [cn["name"] for cn in CRANIAL_NERVES],
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS — general
# ══════════════════════════════════════════════════════════════════════════════

def fmt_duration(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    return f"{seconds // 60}m {seconds % 60}s"

def score_feedback(pct, hits, n):
    if pct == 100:
        return "fb-ok",  f"🎉 Perfect! All {n}/{n} correct — excellent work."
    elif pct >= 60:
        return "fb-mid", f"⚡ Good effort! {hits}/{n} correct. Review the highlighted items and try again."
    else:
        return "fb-low", f"🔬 {hits}/{n} correct. Re-read the material and have another go!"

# ══════════════════════════════════════════════════════════════════════════════
# TRACKING HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def record_seq_attempt(topic, difficulty, score_pct, hits, n, time_secs, hint_used, mistakes):
    st.session_state.log_seq.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "topic": topic, "difficulty": difficulty,
        "score_pct": score_pct, "hits": hits, "n": n,
        "time_secs": time_secs, "hint_used": hint_used, "mistakes": mistakes,
    })

def record_match_attempt(topic, score_pct, hits, n, time_secs, mistakes):
    st.session_state.log_match.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "topic": topic, "score_pct": score_pct, "hits": hits, "n": n,
        "time_secs": time_secs, "mistakes": mistakes,
    })

def record_quiz_attempt(score, total, time_secs, answers):
    st.session_state.log_quiz.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "score": score, "total": total,
        "score_pct": int(round(score / total * 100)),
        "time_secs": time_secs, "answers": answers,
    })

def record_cn_attempt(mode, score_pct, hits, n, time_secs, mistakes):
    st.session_state.log_cn.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "mode": mode, "score_pct": score_pct, "hits": hits, "n": n,
        "time_secs": time_secs, "mistakes": mistakes,
    })

# ══════════════════════════════════════════════════════════════════════════════
# PDF REPORT
# ══════════════════════════════════════════════════════════════════════════════

def _clean(text):
    """Strip leading emoji, escape XML, convert unicode super/subscripts."""
    subs = {"²": "<super>2</super>", "³": "<super>3</super>",
            "⁺": "<super>+</super>", "⁻": "<super>-</super>", "₂": "<sub>2</sub>"}
    text = re.sub(r'^[\U00010000-\U0010ffff\U00002600-\U000027ff\U0001F300-\U0001FAFF\s]+', '', text)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for u, t in subs.items():
        text = text.replace(u, t)
    return ''.join(c if ord(c) < 0x500 else '' for c in text).strip()

def _score_col(pct):
    if pct == 100: return HexColor("#16a34a")
    if pct >= 60:  return HexColor("#ca8a04")
    return HexColor("#dc2626")

def build_report_pdf():
    name    = st.session_state.student_name or "Unknown Student"
    date    = st.session_state.session_start.strftime("%A %d %B %Y")
    start   = st.session_state.session_start.strftime("%H:%M")
    elapsed = fmt_duration(time.time() - st.session_state.session_start_ts)

    seq_best   = max((e["score_pct"] for e in st.session_state.log_seq),   default=None)
    match_best = max((e["score_pct"] for e in st.session_state.log_match), default=None)
    quiz_best  = max((e["score_pct"] for e in st.session_state.log_quiz),  default=None)
    cn_best    = max((e["score_pct"] for e in st.session_state.log_cn),    default=None)
    lq_best    = max((e["score_pct"] for e in st.session_state.log_lq),    default=None)
    bests      = [x for x in [seq_best, match_best, quiz_best, cn_best, lq_best] if x is not None]
    overall    = int(sum(bests) / len(bests)) if bests else None
    total_att  = sum(len(st.session_state[k]) for k in ("log_seq","log_match","log_quiz","log_cn","log_lq"))

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        topMargin=18*mm, bottomMargin=18*mm, leftMargin=20*mm, rightMargin=20*mm,
        title=f"Neuroscience Report — {name}", author="Neuroscience Learning Games")

    NAVY  = HexColor("#1e3a5f");  BLUE  = HexColor("#2563eb")
    SLATE = HexColor("#64748b");  LIGHT = HexColor("#f1f5f9")
    BDR   = HexColor("#e2e8f0");  WHITE = HexColor("#ffffff")
    DARK  = HexColor("#0f172a");  RED   = HexColor("#991b1b")
    GREEN = HexColor("#16a34a")

    def S(nm, **kw): return ParagraphStyle(nm, **kw)
    sTitle = S("T",  fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=WHITE)
    sMeta  = S("Me", fontName="Helvetica",      fontSize=8.5,leading=13, textColor=HexColor("#bfdbfe"))
    sH2    = S("H2", fontName="Helvetica-Bold", fontSize=11, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=3)
    sBody  = S("Bo", fontName="Helvetica",      fontSize=8,  leading=11, textColor=DARK)
    sSmall = S("Sm", fontName="Helvetica",      fontSize=7.5,leading=11, textColor=SLATE)
    sRed   = S("Re", fontName="Helvetica",      fontSize=7.5,leading=11, textColor=RED)
    sGreen = S("Gr", fontName="Helvetica-Bold", fontSize=8,  leading=11, textColor=GREEN)
    sFoot  = S("Fo", fontName="Helvetica",      fontSize=7.5,leading=11, textColor=SLATE, alignment=TA_CENTER)

    TH = [
        ("BACKGROUND",    (0,0),(-1, 0), HexColor("#f8fafc")),
        ("FONTNAME",      (0,0),(-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1, 0), 7.5),
        ("TEXTCOLOR",     (0,0),(-1, 0), SLATE),
        ("LINEBELOW",     (0,0),(-1, 0), 0.8, BDR),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1),(-1,-1), 7.5),
        ("LINEBELOW",     (0,1),(-1,-1), 0.3, BDR),
        ("BOX",           (0,0),(-1,-1), 0.5, BDR),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]

    story = []

    # Header
    ht = Table([[Paragraph("Neuroscience Learning Games — Progress Report", sTitle)],
                [Paragraph(f"Student: <b>{name}</b>   |   Date: {date}   |   Start: {start}   |   Time: {elapsed}", sMeta)]],
               colWidths=[doc.width])
    ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),NAVY),
        ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14),
        ("LEFTPADDING",(0,0),(-1,-1),16),("RIGHTPADDING",(0,0),(-1,-1),16)]))
    story.append(ht); story.append(Spacer(1,10))

    # Summary strip
    def _cell(label, val, sub):
        return Paragraph(
            f"<b>{label}</b><br/><font size='18'>{val}</font><br/>"
            f"<font size='7' color='#64748b'>{sub}</font>",
            S(f"sc{label}", fontName="Helvetica", fontSize=9, leading=14,
              alignment=TA_CENTER, textColor=NAVY))

    def _game_cell(icon, label, best, n_att):
        col = _score_col(best) if best is not None else SLATE
        val = f"{best}%" if best is not None else "—"
        return Paragraph(
            f"<b>{icon} {label}</b><br/>"
            f'<font size="15" color="#{col.hexval()[2:]}"><b>{val}</b></font><br/>'
            f'<font size="7" color="#64748b">{n_att} attempt(s)</font>',
            S(f"gc{label}", fontName="Helvetica", fontSize=9, leading=14,
              alignment=TA_CENTER, textColor=NAVY))

    sum_tbl = Table([[
        _cell("Total Attempts", total_att, "across all games"),
        _cell("Overall Best", "—" if overall is None else f"{overall}%", "avg of best scores"),
        _cell("Time Spent", elapsed, "this session"),
    ]], colWidths=[doc.width/3]*3)
    sum_tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),LIGHT),
        ("BOX",(0,0),(-1,-1),0.5,BDR),("INNERGRID",(0,0),(-1,-1),0.5,BDR),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(sum_tbl); story.append(Spacer(1,6))

    game_tbl = Table([[
        _game_cell("", "Sequencing",      seq_best,   len(st.session_state.log_seq)),
        _game_cell("", "Matching",        match_best, len(st.session_state.log_match)),
        _game_cell("", "True/False",      quiz_best,  len(st.session_state.log_quiz)),
        _game_cell("", "Cranial Nerves",  cn_best,    len(st.session_state.log_cn)),
        _game_cell("", "Lecture Quizzes", lq_best,    len(st.session_state.log_lq)),
    ]], colWidths=[doc.width/5]*5)
    game_tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),WHITE),
        ("BOX",(0,0),(-1,-1),0.5,BDR),("INNERGRID",(0,0),(-1,-1),0.5,BDR),
        ("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story.append(game_tbl); story.append(Spacer(1,14))

    def _sec(title):
        story.append(HRFlowable(width="100%", thickness=0.5, color=BDR, spaceAfter=4))
        story.append(Paragraph(title, sH2))

    def _score_p(pct, hits, n, uid):
        col = _score_col(pct)
        return Paragraph(
            f'<font color="#{col.hexval()[2:]}"><b>{pct}%</b></font><br/>'
            f'<font size="7" color="#64748b">{hits}/{n}</font>',
            S(uid, fontName="Helvetica", fontSize=8, leading=11, alignment=TA_CENTER))

    def _miss_p(items_list):
        if not items_list:
            return Paragraph("All correct", sGreen)
        return Paragraph("<br/>".join(_clean(x) for x in items_list), sRed)

    def _make_table(rows, col_w):
        t = Table(rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle(TH))
        return KeepTogether(t)

    # ── Sequencing ──
    _sec("Sequencing — Attempt Log")
    if not st.session_state.log_seq:
        story.append(Paragraph("No attempts recorded yet.", sSmall))
    else:
        story.append(Paragraph(f"Best: {seq_best}%  |  Attempts: {len(st.session_state.log_seq)}", sSmall))
        story.append(Spacer(1,4))
        cw = [12*mm, 50*mm, 18*mm, 15*mm, doc.width-12*mm-50*mm-18*mm-15*mm]
        rows = [["#", "Topic / Difficulty", "Score", "Time", "Mistakes"]]
        for i,e in enumerate(st.session_state.log_seq,1):
            hint = " (hint)" if e["hint_used"] else ""
            miss = [f"Pos {p+1}: {t}" for p,t in e["mistakes"]]
            rows.append([
                Paragraph(f'<b>#{i}</b><br/><font size="7" color="#64748b">{e["timestamp"]}</font>', sBody),
                Paragraph(f'<b>{_clean(e["topic"])}</b><br/><font size="7" color="#64748b">{e["difficulty"]}</font>', sBody),
                _score_p(e["score_pct"], e["hits"], e["n"], f"ss{i}"),
                Paragraph(fmt_duration(e["time_secs"]) + hint, sSmall),
                _miss_p(miss),
            ])
        story.append(_make_table(rows, cw))
    story.append(Spacer(1,10))

    # ── Matching ──
    _sec("Matching — Attempt Log")
    if not st.session_state.log_match:
        story.append(Paragraph("No attempts recorded yet.", sSmall))
    else:
        story.append(Paragraph(f"Best: {match_best}%  |  Attempts: {len(st.session_state.log_match)}", sSmall))
        story.append(Spacer(1,4))
        cw = [12*mm, 50*mm, 18*mm, 15*mm, doc.width-12*mm-50*mm-18*mm-15*mm]
        rows = [["#", "Topic", "Score", "Time", "Mistakes"]]
        for i,e in enumerate(st.session_state.log_match,1):
            miss = [f"{term}: chose '{chosen}'" for term,chosen,_ in e["mistakes"]]
            rows.append([
                Paragraph(f'<b>#{i}</b><br/><font size="7" color="#64748b">{e["timestamp"]}</font>', sBody),
                Paragraph(f'<b>{_clean(e["topic"])}</b>', sBody),
                _score_p(e["score_pct"], e["hits"], e["n"], f"ms{i}"),
                Paragraph(fmt_duration(e["time_secs"]), sSmall),
                _miss_p(miss),
            ])
        story.append(_make_table(rows, cw))
    story.append(Spacer(1,10))

    # ── True/False ──
    _sec("True or False — Attempt Log")
    if not st.session_state.log_quiz:
        story.append(Paragraph("No attempts recorded yet.", sSmall))
    else:
        story.append(Paragraph(f"Best: {quiz_best}%  |  Games: {len(st.session_state.log_quiz)}", sSmall))
        story.append(Spacer(1,4))
        cw = [12*mm, 20*mm, 15*mm, doc.width-12*mm-20*mm-15*mm]
        rows = [["#", "Score", "Time", "Incorrect Answers"]]
        for i,e in enumerate(st.session_state.log_quiz,1):
            wrong = [f'Answered {"TRUE" if a["answer_given"] else "FALSE"}: {a["q"][:75]}...'
                     for a in e["answers"] if not a["correct"]]
            rows.append([
                Paragraph(f'<b>#{i}</b><br/><font size="7" color="#64748b">{e["timestamp"]}</font>', sBody),
                _score_p(e["score_pct"], e["score"], e["total"], f"qs{i}"),
                Paragraph(fmt_duration(e["time_secs"]), sSmall),
                _miss_p(wrong),
            ])
        story.append(_make_table(rows, cw))
    story.append(Spacer(1,10))

    # ── Cranial Nerves ──
    _sec("Cranial Nerves — Attempt Log")
    if not st.session_state.log_cn:
        story.append(Paragraph("No attempts recorded yet.", sSmall))
    else:
        story.append(Paragraph(f"Best: {cn_best}%  |  Rounds: {len(st.session_state.log_cn)}", sSmall))
        story.append(Spacer(1,4))
        cw = [12*mm, 42*mm, 18*mm, 15*mm, doc.width-12*mm-42*mm-18*mm-15*mm]
        rows = [["#", "Mode", "Score", "Time", "Mistakes"]]
        for i,e in enumerate(st.session_state.log_cn,1):
            miss = [f"Q: '{_clean(q[:60])}...' → answered '{_clean(ans[:40])}'" for q,ans,_ in e["mistakes"]]
            rows.append([
                Paragraph(f'<b>#{i}</b><br/><font size="7" color="#64748b">{e["timestamp"]}</font>', sBody),
                Paragraph(f'<b>{e["mode"]}</b>', sBody),
                _score_p(e["score_pct"], e["hits"], e["n"], f"cn{i}"),
                Paragraph(fmt_duration(e["time_secs"]), sSmall),
                _miss_p(miss),
            ])
        story.append(_make_table(rows, cw))
    story.append(Spacer(1,10))

    # ── Lecture Quizzes ──
    _sec("Lecture Quizzes — Attempt Log")
    if not st.session_state.log_lq:
        story.append(Paragraph("No attempts recorded yet.", sSmall))
    else:
        story.append(Paragraph(f"Best: {lq_best}%  |  Rounds: {len(st.session_state.log_lq)}", sSmall))
        story.append(Spacer(1,4))
        cw = [12*mm, 42*mm, 18*mm, 15*mm, doc.width-12*mm-42*mm-18*mm-15*mm]
        rows = [["#", "Topic", "Score", "Time", "Mistakes"]]
        for i,e in enumerate(st.session_state.log_lq,1):
            miss = [f"Q: '{_clean(q[:60])}...' → answered '{_clean(ans[:40])}'" for q,ans,_ in e["mistakes"]]
            rows.append([
                Paragraph(f'<b>#{i}</b><br/><font size="7" color="#64748b">{e["timestamp"]}</font>', sBody),
                Paragraph(f'<b>{_clean(e["topic"])}</b>', sBody),
                _score_p(e["score_pct"], e["hits"], e["n"], f"lq{i}"),
                Paragraph(fmt_duration(e["time_secs"]), sSmall),
                _miss_p(miss),
            ])
        story.append(_make_table(rows, cw))

    # Footer
    story.append(Spacer(1,16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BDR))
    story.append(Spacer(1,4))
    story.append(Paragraph(
        f"Generated by Neuroscience Learning Games  |  "
        f"{datetime.now().strftime('%d/%m/%Y %H:%M')}  |  Submitted by: {name}", sFoot))

    doc.build(story)
    buf.seek(0)
    return buf.read()

# ══════════════════════════════════════════════════════════════════════════════
# HTML REPORT
# ══════════════════════════════════════════════════════════════════════════════

def build_report_html():
    name    = st.session_state.student_name or "Unknown Student"
    date    = st.session_state.session_start.strftime("%A %d %B %Y")
    start   = st.session_state.session_start.strftime("%H:%M")
    elapsed = fmt_duration(time.time() - st.session_state.session_start_ts)

    seq_best   = max((e["score_pct"] for e in st.session_state.log_seq),   default=None)
    match_best = max((e["score_pct"] for e in st.session_state.log_match), default=None)
    quiz_best  = max((e["score_pct"] for e in st.session_state.log_quiz),  default=None)
    cn_best    = max((e["score_pct"] for e in st.session_state.log_cn),    default=None)
    lq_best    = max((e["score_pct"] for e in st.session_state.log_lq),    default=None)
    bests      = [x for x in [seq_best, match_best, quiz_best, cn_best, lq_best] if x is not None]
    overall    = int(sum(bests)/len(bests)) if bests else None
    total_att  = sum(len(st.session_state[k]) for k in ("log_seq","log_match","log_quiz","log_cn","log_lq"))

    def badge(pct):
        if pct is None: return '<span style="color:#94a3b8">No attempts</span>'
        c = "#16a34a" if pct==100 else ("#ca8a04" if pct>=60 else "#dc2626")
        return f'<span style="background:{c};color:#fff;border-radius:5px;padding:2px 9px;font-weight:700">{pct}%</span>'

    def bar(pct, col="#2563eb"):
        return (f'<div style="background:#e2e8f0;border-radius:99px;height:8px;overflow:hidden;margin:4px 0 6px">'
                f'<div style="width:{pct}%;height:8px;background:{col}"></div></div>')

    def tbl(rows_html, headers):
        if not rows_html:
            return '<p style="color:#94a3b8;font-style:italic;padding:8px 0">No attempts recorded yet.</p>'
        ths = "".join(f'<th style="padding:7px 9px;text-align:left;background:#f8fafc;border-bottom:2px solid #e2e8f0;font-size:0.8rem;color:#64748b;font-weight:600">{h}</th>' for h in headers)
        return f'<table style="width:100%;border-collapse:collapse"><thead><tr>{ths}</tr></thead><tbody>{rows_html}</tbody></table>'

    def seq_rows():
        r = ""
        for i,e in enumerate(st.session_state.log_seq,1):
            c = "#16a34a" if e["score_pct"]==100 else ("#ca8a04" if e["score_pct"]>=60 else "#dc2626")
            hint = ' <span style="background:#fef3c7;color:#92400e;border-radius:3px;padding:1px 5px;font-size:0.75rem">hint</span>' if e["hint_used"] else ""
            miss = "".join(f'<li style="color:#991b1b;font-size:0.8rem;margin:1px 0">Pos {p+1}: {t}</li>' for p,t in e["mistakes"])
            miss_html = f'<ul style="margin:3px 0 0 14px;padding:0">{miss}</ul>' if miss else '<span style="color:#16a34a;font-size:0.8rem">All correct ✓</span>'
            r += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:7px 9px;color:#64748b;font-size:0.82rem">#{i} {e["timestamp"]}</td><td style="padding:7px 9px"><b>{e["topic"]}</b><br/><span style="font-size:0.78rem;color:#64748b">{e["difficulty"]}</span></td><td style="padding:7px 9px;text-align:center"><span style="font-weight:700;color:{c}">{e["score_pct"]}%</span><br/><span style="font-size:0.78rem;color:#64748b">{e["hits"]}/{e["n"]}</span></td><td style="padding:7px 9px;font-size:0.8rem;color:#64748b">{fmt_duration(e["time_secs"])}{hint}</td><td style="padding:7px 9px">{miss_html}</td></tr>'
        return r

    def match_rows():
        r = ""
        for i,e in enumerate(st.session_state.log_match,1):
            c = "#16a34a" if e["score_pct"]==100 else ("#ca8a04" if e["score_pct"]>=60 else "#dc2626")
            miss = "".join(f'<li style="color:#991b1b;font-size:0.8rem;margin:1px 0"><b>{term}</b>: chose "{chosen}"</li>' for term,chosen,_ in e["mistakes"])
            miss_html = f'<ul style="margin:3px 0 0 14px;padding:0">{miss}</ul>' if miss else '<span style="color:#16a34a;font-size:0.8rem">All correct ✓</span>'
            r += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:7px 9px;color:#64748b;font-size:0.82rem">#{i} {e["timestamp"]}</td><td style="padding:7px 9px"><b>{e["topic"]}</b></td><td style="padding:7px 9px;text-align:center"><span style="font-weight:700;color:{c}">{e["score_pct"]}%</span><br/><span style="font-size:0.78rem;color:#64748b">{e["hits"]}/{e["n"]}</span></td><td style="padding:7px 9px;font-size:0.8rem;color:#64748b">{fmt_duration(e["time_secs"])}</td><td style="padding:7px 9px">{miss_html}</td></tr>'
        return r

    def quiz_rows():
        r = ""
        for i,e in enumerate(st.session_state.log_quiz,1):
            c = "#16a34a" if e["score_pct"]==100 else ("#ca8a04" if e["score_pct"]>=60 else "#dc2626")
            wrong = [a for a in e["answers"] if not a["correct"]]
            miss = "".join(f'<li style="color:#991b1b;font-size:0.8rem;margin:1px 0">Answered {"TRUE" if a["answer_given"] else "FALSE"}: {a["q"][:80]}…</li>' for a in wrong)
            miss_html = f'<ul style="margin:3px 0 0 14px;padding:0">{miss}</ul>' if miss else '<span style="color:#16a34a;font-size:0.8rem">All correct ✓</span>'
            r += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:7px 9px;color:#64748b;font-size:0.82rem">#{i} {e["timestamp"]}</td><td style="padding:7px 9px;text-align:center"><span style="font-weight:700;color:{c}">{e["score_pct"]}%</span><br/><span style="font-size:0.78rem;color:#64748b">{e["score"]}/{e["total"]}</span></td><td style="padding:7px 9px;font-size:0.8rem;color:#64748b">{fmt_duration(e["time_secs"])}</td><td style="padding:7px 9px">{miss_html}</td></tr>'
        return r

    def cn_rows():
        r = ""
        for i,e in enumerate(st.session_state.log_cn,1):
            c = "#16a34a" if e["score_pct"]==100 else ("#ca8a04" if e["score_pct"]>=60 else "#dc2626")
            miss = "".join(f'<li style="color:#991b1b;font-size:0.8rem;margin:1px 0">Q: "{q[:60]}…" → answered "{ans[:40]}"</li>' for q,ans,_ in e["mistakes"])
            miss_html = f'<ul style="margin:3px 0 0 14px;padding:0">{miss}</ul>' if miss else '<span style="color:#16a34a;font-size:0.8rem">All correct ✓</span>'
            r += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:7px 9px;color:#64748b;font-size:0.82rem">#{i} {e["timestamp"]}</td><td style="padding:7px 9px"><b>{e["mode"]}</b></td><td style="padding:7px 9px;text-align:center"><span style="font-weight:700;color:{c}">{e["score_pct"]}%</span><br/><span style="font-size:0.78rem;color:#64748b">{e["hits"]}/{e["n"]}</span></td><td style="padding:7px 9px;font-size:0.8rem;color:#64748b">{fmt_duration(e["time_secs"])}</td><td style="padding:7px 9px">{miss_html}</td></tr>'
        return r

    def lq_rows():
        r = ""
        for i,e in enumerate(st.session_state.log_lq,1):
            c = "#16a34a" if e["score_pct"]==100 else ("#ca8a04" if e["score_pct"]>=60 else "#dc2626")
            miss = "".join(f'<li style="color:#991b1b;font-size:0.8rem;margin:1px 0">Q: "{q[:60]}…" → chose "{ans}"</li>' for q,ans,_ in e["mistakes"])
            miss_html = f'<ul style="margin:3px 0 0 14px;padding:0">{miss}</ul>' if miss else '<span style="color:#16a34a;font-size:0.8rem">All correct ✓</span>'
            r += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:7px 9px;color:#64748b;font-size:0.82rem">#{i} {e["timestamp"]}</td><td style="padding:7px 9px"><b>{e["topic"]}</b></td><td style="padding:7px 9px;text-align:center"><span style="font-weight:700;color:{c}">{e["score_pct"]}%</span><br/><span style="font-size:0.78rem;color:#64748b">{e["hits"]}/{e["n"]}</span></td><td style="padding:7px 9px;font-size:0.8rem;color:#64748b">{fmt_duration(e["time_secs"])}</td><td style="padding:7px 9px">{miss_html}</td></tr>'
        return r

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Neuroscience Games — Progress Report</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',Arial,sans-serif;background:#f8fafc;color:#0f172a;font-size:14px;line-height:1.6}}
.page{{max-width:900px;margin:0 auto;padding:32px}}
.hdr{{background:linear-gradient(135deg,#1e3a5f,#2563eb);border-radius:12px;padding:26px 28px;color:#fff;margin-bottom:22px}}
.hdr h1{{font-size:1.55rem;font-weight:800;letter-spacing:-0.02em;margin-bottom:3px}}
.hdr .meta{{font-size:0.85rem;opacity:0.8}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px}}
.card{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px;text-align:center}}
.card .lbl{{font-size:0.73rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:5px}}
.card .val{{font-size:1.7rem;font-weight:800;color:#0f172a}}
.card .sub{{font-size:0.75rem;color:#94a3b8;margin-top:2px}}
.section{{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:20px 22px;margin-bottom:18px}}
.section h2{{font-size:1.05rem;font-weight:700;margin-bottom:10px}}
.footer{{text-align:center;color:#94a3b8;font-size:0.75rem;margin-top:22px;padding-top:14px;border-top:1px solid #e2e8f0}}
@media print{{body{{background:#fff}}.page{{padding:16px}}}}
</style></head><body><div class="page">
<div class="hdr">
  <h1>🧠 Neuroscience Learning Games — Progress Report</h1>
  <div class="meta">Student: <strong>{name}</strong> &nbsp;|&nbsp; Date: {date} &nbsp;|&nbsp; Session start: {start} &nbsp;|&nbsp; Total time: {elapsed}</div>
</div>
<div class="grid3">
  <div class="card"><div class="lbl">Total Attempts</div><div class="val">{total_att}</div><div class="sub">across all games</div></div>
  <div class="card"><div class="lbl">Overall Best</div><div class="val">{"—" if overall is None else str(overall)+"%"}</div><div class="sub">avg of best scores</div></div>
  <div class="card"><div class="lbl">Time Spent</div><div class="val">{elapsed}</div><div class="sub">this session</div></div>
</div>
<div class="grid4">
  <div class="card"><div class="lbl">🔢 Sequencing</div>{badge(seq_best)}{bar(seq_best or 0)}<div class="sub">{len(st.session_state.log_seq)} attempt(s)</div></div>
  <div class="card"><div class="lbl">🔗 Matching</div>{badge(match_best)}{bar(match_best or 0,"#10b981")}<div class="sub">{len(st.session_state.log_match)} attempt(s)</div></div>
  <div class="card"><div class="lbl">🧪 True/False</div>{badge(quiz_best)}{bar(quiz_best or 0,"#8b5cf6")}<div class="sub">{len(st.session_state.log_quiz)} attempt(s)</div></div>
  <div class="card"><div class="lbl">🧠 Cranial Nerves</div>{badge(cn_best)}{bar(cn_best or 0,"#f59e0b")}<div class="sub">{len(st.session_state.log_cn)} attempt(s)</div></div>
  <div class="card"><div class="lbl">📚 Lecture Quizzes</div>{badge(lq_best)}{bar(lq_best or 0,"#06b6d4")}<div class="sub">{len(st.session_state.log_lq)} attempt(s)</div></div>
</div>
<div class="section"><h2>🔢 Sequencing — Attempt Log</h2>Best: {badge(seq_best)} &nbsp; Attempts: {len(st.session_state.log_seq)}<br/><br/>{tbl(seq_rows(),["#","Topic / Difficulty","Score","Time","Mistakes"])}</div>
<div class="section"><h2>🔗 Matching — Attempt Log</h2>Best: {badge(match_best)} &nbsp; Attempts: {len(st.session_state.log_match)}<br/><br/>{tbl(match_rows(),["#","Topic","Score","Time","Mistakes"])}</div>
<div class="section"><h2>🧪 True or False — Attempt Log</h2>Best: {badge(quiz_best)} &nbsp; Games: {len(st.session_state.log_quiz)}<br/><br/>{tbl(quiz_rows(),["#","Score","Time","Incorrect Answers"])}</div>
<div class="section"><h2>🧠 Cranial Nerves — Attempt Log</h2>Best: {badge(cn_best)} &nbsp; Rounds: {len(st.session_state.log_cn)}<br/><br/>{tbl(cn_rows(),["#","Mode","Score","Time","Mistakes"])}</div>
<div class="section"><h2>📚 Lecture Quizzes — Attempt Log</h2>Best: {badge(lq_best)} &nbsp; Rounds: {len(st.session_state.log_lq)}<br/><br/>{tbl(lq_rows(),["#","Topic","Score","Time","Mistakes"])}</div>
<div class="footer">Generated by Neuroscience Learning Games &nbsp;·&nbsp; {datetime.now().strftime("%d/%m/%Y %H:%M")} &nbsp;·&nbsp; Submitted by: <strong>{name}</strong></div>
</div></body></html>"""

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

def init_state():
    defaults = {
        # Student
        "student_name":      "",
        "student_confirmed": False,
        "session_start":     datetime.now(),
        "session_start_ts":  time.time(),
        # Logs
        "log_seq":   [],
        "log_match": [],
        "log_quiz":  [],
        "log_cn":    [],
        "log_lq":    [],
        # Sequencing
        "seq_key":       list(SEQUENCES.keys())[0],
        "seq_diff":      "Intermediate (8 steps)",
        "seq_order":     None,
        "seq_correct":   None,
        "seq_submitted": False,
        "seq_hint":      False,
        "seq_attempts":  0,
        "seq_best":      0,
        "seq_loadn":     0,
        "seq_start_ts":  None,
        # Matching
        "match_key":       list(MATCHING_SETS.keys())[0],
        "match_items":     None,
        "match_opts":      None,
        "match_cmap":      None,
        "match_submitted": False,
        "match_attempts":  0,
        "match_best":      0,
        "match_loadn":     0,
        "match_start_ts":  None,
        # Quiz
        "quiz_qs":       None,
        "quiz_idx":      0,
        "quiz_answered": False,
        "quiz_correct":  None,
        "quiz_score":    0,
        "quiz_finished": False,
        "quiz_attempts": 0,
        "quiz_start_ts": None,
        "quiz_answers":  [],
        "quiz_logged":   False,  # guard: prevent double-recording
        # Lecture quiz
        "lq_topic":      "All Topics",
        "lq_num_qs":     10,
        "lq_questions":  None,
        "lq_idx":        0,
        "lq_answered":   False,
        "lq_chosen":     None,
        "lq_correct":    None,
        "lq_score":      0,
        "lq_finished":   False,
        "lq_attempts":   0,
        "lq_start_ts":   None,
        "lq_answers":    [],
        "lq_logged":     False,
        # Cranial nerves
        "cn_mode":       list(CN_MODES.keys())[0],
        "cn_questions":  None,
        "cn_idx":        0,
        "cn_options":    None,
        "cn_answered":   False,
        "cn_chosen":     None,
        "cn_correct":    None,
        "cn_score":      0,
        "cn_finished":   False,
        "cn_attempts":   0,
        "cn_start_ts":   None,
        "cn_answers":    [],
        "cn_num_qs":     12,
        "cn_logged":     False,  # guard: prevent double-recording
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Sequencing helpers ──────────────────────────────────────────────────────

def load_seq():
    seq   = SEQUENCES[st.session_state.seq_key]
    n     = min(DIFFICULTY_STEPS[st.session_state.seq_diff], len(seq["steps"]))
    steps = seq["steps"][:n]
    shuffled = steps.copy()
    random.shuffle(shuffled)
    while shuffled == steps:
        random.shuffle(shuffled)
    st.session_state.seq_order     = shuffled
    st.session_state.seq_correct   = [s[0] for s in steps]
    st.session_state.seq_submitted = False
    st.session_state.seq_hint      = False
    st.session_state.seq_loadn    += 1
    st.session_state.seq_start_ts  = time.time()

def seq_score():
    cur = [s[0] for s in st.session_state.seq_order]
    cor = st.session_state.seq_correct
    n   = len(cor)
    h   = sum(1 for i,c in enumerate(cur) if c == cor[i])
    return h, n, int(round(h/n*100))

# ── Matching helpers ──────────────────────────────────────────────────────────

def load_match():
    mset  = MATCHING_SETS[st.session_state.match_key]
    pairs = mset["pairs"]
    items = [(p[0], p[1]) for p in pairs]
    defs  = [p[2] for p in pairs]
    cmap  = {p[0]: p[2] for p in pairs}
    random.shuffle(items); random.shuffle(defs)
    st.session_state.match_items     = items
    st.session_state.match_opts      = defs
    st.session_state.match_cmap      = cmap
    st.session_state.match_submitted = False
    st.session_state.match_loadn    += 1
    st.session_state.match_start_ts  = time.time()

def match_score():
    lc    = st.session_state.match_loadn
    items = st.session_state.match_items
    cmap  = st.session_state.match_cmap
    n     = len(items)
    h     = sum(1 for (iid,_) in items
                if st.session_state.get(f"ms_{iid}_{lc}", "—") == cmap[iid])
    return h, n, int(round(h/n*100))

# ── Quiz helpers ──────────────────────────────────────────────────────────────

def load_quiz():
    qs = QUIZ_QUESTIONS.copy()
    random.shuffle(qs)
    st.session_state.quiz_qs       = qs
    st.session_state.quiz_idx      = 0
    st.session_state.quiz_answered = False
    st.session_state.quiz_correct  = None
    st.session_state.quiz_score    = 0
    st.session_state.quiz_finished = False
    st.session_state.quiz_start_ts = time.time()
    st.session_state.quiz_answers  = []
    st.session_state.quiz_logged   = False

# ── Lecture quiz helpers ──────────────────────────────────────────────────────

def load_lq():
    topic = st.session_state.lq_topic
    if topic == "All Topics":
        pool = LECTURE_QUIZ_QUESTIONS.copy()
    else:
        pool = [q for q in LECTURE_QUIZ_QUESTIONS if q["topic"] == topic]
    n = min(st.session_state.lq_num_qs, len(pool))
    qs = random.sample(pool, n)
    st.session_state.lq_questions = qs
    st.session_state.lq_idx       = 0
    st.session_state.lq_answered  = False
    st.session_state.lq_chosen    = None
    st.session_state.lq_correct   = None
    st.session_state.lq_score     = 0
    st.session_state.lq_finished  = False
    st.session_state.lq_start_ts  = time.time()
    st.session_state.lq_answers   = []
    st.session_state.lq_logged    = False

def record_lq_attempt(topic, score_pct, hits, n, time_secs, mistakes):
    st.session_state.log_lq.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "topic": topic, "score_pct": score_pct, "hits": hits, "n": n,
        "time_secs": time_secs, "mistakes": mistakes,
    })

def load_cn():
    n    = st.session_state.cn_num_qs
    qs   = random.sample(CRANIAL_NERVES, min(n, len(CRANIAL_NERVES)))
    st.session_state.cn_questions = qs
    st.session_state.cn_idx       = 0
    st.session_state.cn_answered  = False
    st.session_state.cn_chosen    = None
    st.session_state.cn_correct   = None
    st.session_state.cn_score     = 0
    st.session_state.cn_finished  = False
    st.session_state.cn_start_ts  = time.time()
    st.session_state.cn_answers   = []
    st.session_state.cn_logged    = False
    _prep_cn_options()

def _prep_cn_options():
    """Build 4 multiple-choice options for the current CN question."""
    idx    = st.session_state.cn_idx
    qs     = st.session_state.cn_questions
    if idx >= len(qs):
        return
    mode   = CN_MODES[st.session_state.cn_mode]
    cn     = qs[idx]
    correct_ans = cn[mode["answer_key"]]
    pool   = mode["options_pool"]
    # For function/clinical modes, pool is all answers from the full CN list
    if mode["answer_key"] in ("function", "clinical"):
        pool = [c[mode["answer_key"]] for c in CRANIAL_NERVES]
    wrong  = [o for o in pool if o != correct_ans]
    random.shuffle(wrong)
    distractors = wrong[:3]
    opts   = distractors + [correct_ans]
    random.shuffle(opts)
    st.session_state.cn_options = opts

# ══════════════════════════════════════════════════════════════════════════════
# BOOT
# ══════════════════════════════════════════════════════════════════════════════

init_state()
if st.session_state.seq_order    is None: load_seq()
if st.session_state.match_items  is None: load_match()
if st.session_state.quiz_qs      is None: load_quiz()
if st.session_state.cn_questions is None: load_cn()
if st.session_state.lq_questions is None: load_lq()

# ══════════════════════════════════════════════════════════════════════════════
# STUDENT NAME GATE
# ══════════════════════════════════════════════════════════════════════════════

if not st.session_state.student_confirmed:
    st.markdown('<p class="app-title">🧠 Neuroscience Learning Games</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Enter your name to begin — it will appear on your progress report.</p>', unsafe_allow_html=True)
    st.markdown("---")
    col_n, col_b = st.columns([3, 1])
    with col_n:
        name_input = st.text_input("Your full name:", placeholder="e.g. Jane Smith", key="name_input_field")
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Start", type="primary", use_container_width=True):
            if name_input.strip():
                st.session_state.student_name      = name_input.strip()
                st.session_state.student_confirmed  = True
                st.session_state.session_start      = datetime.now()
                st.session_state.session_start_ts   = time.time()
                st.rerun()
            else:
                st.warning("Please enter your name to continue.")

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.82rem;color:#94a3b8;text-align:center;margin-top:0.5rem">'
        'Developed by <strong style="color:#64748b">Dr Lauren Walker</strong> — Teesside University'
        ' &nbsp;&amp;&nbsp; '
        '<strong style="color:#64748b">Dr Justin Andrushko</strong> — Northumbria University'
        '</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### 🧠 Neuroscience Games")
    st.markdown(f"👤 **{st.session_state.student_name}**")
    st.markdown(f"⏱️ Session time: **{fmt_duration(time.time()-st.session_state.session_start_ts)}**")
    st.markdown("---")
    st.markdown("### 📊 Session Stats")
    st.markdown(f"**Sequencing** — {st.session_state.seq_attempts} attempts · best {st.session_state.seq_best}%")
    st.markdown(f"**Matching** — {st.session_state.match_attempts} attempts · best {st.session_state.match_best}%")
    st.markdown(f"**Quiz** — {st.session_state.quiz_attempts} games played")
    st.markdown(f"**Cranial Nerves** — {st.session_state.cn_attempts} rounds played")
    st.markdown(f"**Lecture Quizzes** — {st.session_state.lq_attempts} rounds played")
    st.markdown("---")

    # Download buttons
    st.markdown("### 📄 Progress Report")
    total_att = sum(len(st.session_state[k]) for k in ("log_seq","log_match","log_quiz","log_cn","log_lq"))
    if total_att == 0:
        st.info("Complete at least one game to unlock your report.")
    else:
        safe  = st.session_state.student_name.replace(" ","_")
        ts    = datetime.now().strftime("%Y%m%d_%H%M")
        pdf_b = build_report_pdf()
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_b,
            file_name=f"neuro_report_{safe}_{ts}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
            key="dl_pdf",
        )
        html_b = build_report_html()
        st.download_button(
            label="⬇️ Download HTML Report",
            data=html_b,
            file_name=f"neuro_report_{safe}_{ts}.html",
            mime="text/html",
            use_container_width=True,
            key="dl_html",
        )
        st.caption("PDF: submit directly. HTML: open in any browser.")
    st.markdown("---")
    st.markdown("### 📖 Tips")
    st.markdown(
        "**Sequencing:** Drag cards to reorder.\n\n"
        "**Matching:** Select the correct definition for each term.\n\n"
        "**True/False:** Read the explanation after each answer.\n\n"
        "**Cranial Nerves:** Select the correct answer from four options.\n\n"
        "**Lecture Quizzes:** 100 MCQs from your lecture material, organised by topic."
    )
    st.markdown("---")

    # ── RAM monitor ──────────────────────────────────────────────────────────
    st.markdown("### 🖥️ Memory Monitor")
    if _PSUTIL:
        proc      = psutil.Process()
        proc_mb   = proc.memory_info().rss / 1_048_576          # this process (MB)
        sys_total = psutil.virtual_memory().total  / 1_048_576  # total system RAM (MB)
        sys_avail = psutil.virtual_memory().available / 1_048_576
        sys_used  = sys_total - sys_avail
        sys_pct   = psutil.virtual_memory().percent

        LIMIT_MB  = 1024   # Streamlit Cloud free-tier limit
        proc_pct  = min(proc_mb / LIMIT_MB * 100, 100)

        # Colour thresholds
        if proc_pct < 60:
            bar_col, status = "#16a34a", "✅ OK"
        elif proc_pct < 80:
            bar_col, status = "#ca8a04", "⚠️ Moderate"
        else:
            bar_col, status = "#dc2626", "🔴 High"

        st.markdown(
            f"**App process RAM** {status}<br/>"
            f"<small style='color:#94a3b8'>vs 1 GB Streamlit Cloud limit</small>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#334155;border-radius:99px;height:10px;overflow:hidden;margin:4px 0 2px">'
            f'<div style="width:{proc_pct:.1f}%;height:10px;border-radius:99px;background:{bar_col};transition:width 0.4s"></div>'
            f'</div>'
            f'<p style="font-size:0.78rem;color:#94a3b8;margin:0">'
            f'{proc_mb:.1f} MB used / {LIMIT_MB} MB limit &nbsp;({proc_pct:.1f}%)</p>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"**System RAM** (whole machine)<br/>"
            f"<small style='color:#94a3b8'>{sys_used:.0f} MB used of {sys_total:.0f} MB ({sys_pct:.1f}%)</small>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#334155;border-radius:99px;height:6px;overflow:hidden;margin:4px 0 2px">'
            f'<div style="width:{sys_pct:.1f}%;height:6px;border-radius:99px;background:#475569"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if proc_pct >= 80:
            st.warning("⚠️ RAM usage is high. Students should download reports soon.", icon="🔴")

        st.caption("Refreshes on every interaction. psutil measures this process only.")
    else:
        st.caption("Install psutil to enable RAM monitoring: `pip install psutil`")

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.75rem;color:#475569;text-align:center;line-height:1.6">'
        'Developed by<br/>'
        '<strong style="color:#94a3b8">Dr Lauren Walker</strong><br/>'
        '<span style="color:#64748b">Teesside University</span><br/><br/>'
        '<strong style="color:#94a3b8">Dr Justin Andrushko</strong><br/>'
        '<span style="color:#64748b">Northumbria University</span>'
        '</p>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="app-title">🧠 Neuroscience Learning Games</p>', unsafe_allow_html=True)
elapsed_b = fmt_duration(time.time()-st.session_state.session_start_ts)
total_logged = sum(len(st.session_state[k]) for k in ("log_seq","log_match","log_quiz","log_cn","log_lq"))
st.markdown(
    f'<div class="student-banner">'
    f'<span class="student-name-display">👤 {st.session_state.student_name}</span>'
    f'<span class="student-time-display">⏱️ {elapsed_b} &nbsp;|&nbsp; 📝 {total_logged} attempts logged</span>'
    f'</div>', unsafe_allow_html=True)

tab_seq, tab_match, tab_quiz, tab_cn, tab_lq = st.tabs([
    "🔢  Sequencing", "🔗  Matching", "🧪  True or False", "🧠  Cranial Nerves", "📚  Lecture Quizzes"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SEQUENCING
# ══════════════════════════════════════════════════════════════════════════════
with tab_seq:
    st.markdown('<p class="section-title">Sequence the Events</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Drag the cards into the correct chronological order for the chosen process.</p>', unsafe_allow_html=True)

    col_s1, col_s2, col_s3 = st.columns([2, 1.5, 1])
    with col_s1:
        seq_choice = st.selectbox("Process", list(SEQUENCES.keys()), key="seq_sel",
            index=list(SEQUENCES.keys()).index(st.session_state.seq_key))
    with col_s2:
        diff_choice = st.selectbox("Difficulty", list(DIFFICULTY_STEPS.keys()), key="seq_diff_sel",
            index=list(DIFFICULTY_STEPS.keys()).index(st.session_state.seq_diff))
    with col_s3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔀 Shuffle", use_container_width=True, key="seq_newshuffle"):
            load_seq(); st.rerun()

    if seq_choice != st.session_state.seq_key or diff_choice != st.session_state.seq_diff:
        st.session_state.seq_key  = seq_choice
        st.session_state.seq_diff = diff_choice
        load_seq(); st.rerun()

    seq_meta = SEQUENCES[st.session_state.seq_key]
    st.info(f"**Task:** {seq_meta['description']}", icon="📋")

    hint_label = "💡 Show Hint" if not st.session_state.seq_hint else "🙈 Hide Hint"
    if st.button(hint_label, key="seq_hint_btn"):
        st.session_state.seq_hint = not st.session_state.seq_hint
    if st.session_state.seq_hint:
        st.markdown(f'<div class="hint-box">💡 <strong>Hint:</strong> {seq_meta["hint"]}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not st.session_state.seq_submitted:
        st.markdown('<div class="drag-note">☰ &nbsp;<strong>Drag the cards</strong> up or down to reorder, then click <em>Check My Answer</em>.</div>', unsafe_allow_html=True)
        display_texts = [t for _,t in st.session_state.seq_order]
        sorted_texts  = sort_items(display_texts, direction="vertical",
                                   custom_style=SORTABLE_STYLE,
                                   key=f"seq_sort_{st.session_state.seq_loadn}")
        if sorted_texts != display_texts:
            tmap = {t:(sid,t) for sid,t in st.session_state.seq_order}
            st.session_state.seq_order = [tmap[t] for t in sorted_texts]

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Check My Answer", use_container_width=True, type="primary", key="seq_check"):
                st.session_state.seq_submitted = True
                st.session_state.seq_attempts += 1
                h, n, pct = seq_score()
                if pct > st.session_state.seq_best: st.session_state.seq_best = pct
                cor      = st.session_state.seq_correct
                mistakes = [(i, st.session_state.seq_order[i][1])
                            for i in range(n) if st.session_state.seq_order[i][0] != cor[i]]
                record_seq_attempt(
                    st.session_state.seq_key, st.session_state.seq_diff,
                    pct, h, n,
                    time.time() - (st.session_state.seq_start_ts or time.time()),
                    st.session_state.seq_hint, mistakes)
                st.rerun()
        with c2:
            if st.button("🔀 Reshuffle", use_container_width=True, key="seq_reshuffle"):
                load_seq(); st.rerun()
    else:
        cor = st.session_state.seq_correct
        for i, (sid,txt) in enumerate(st.session_state.seq_order):
            ok  = sid == cor[i]
            cls = "step-card correct" if ok else "step-card incorrect"
            ico = "✅" if ok else "❌"
            st.markdown(f'<div class="{cls}"><span class="step-num">{i+1:02d}</span>{ico}&nbsp; {txt}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        h, n, pct = seq_score()
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big">{pct}%</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-sub">{h} of {n} steps in the correct position</p>', unsafe_allow_html=True)
        fb_cls, fb_msg = score_feedback(pct, h, n)
        st.markdown(f'<div class="fb {fb_cls}">{fb_msg}</div>', unsafe_allow_html=True)

        with st.expander("📚 Show correct sequence"):
            for pos, cid in enumerate(cor):
                txt = next(t for sid,t in seq_meta["steps"] if sid == cid)
                st.markdown(f'<div class="step-card correct"><span class="step-num">{pos+1:02d}</span>{txt}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Try Again", use_container_width=True, type="primary", key="seq_retry"):
                load_seq(); st.rerun()
        with c2:
            if st.button("🔀 New Shuffle", use_container_width=True, key="seq_newsh2"):
                load_seq(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MATCHING
# ══════════════════════════════════════════════════════════════════════════════
with tab_match:
    st.markdown('<p class="section-title">Match the Terms</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Select the correct definition or function for each term using the dropdown.</p>', unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([3,1])
    with col_m1:
        match_choice = st.selectbox("Choose a matching set:", list(MATCHING_SETS.keys()), key="match_sel",
            index=list(MATCHING_SETS.keys()).index(st.session_state.match_key))
    with col_m2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔀 Reset", use_container_width=True, key="match_reset"):
            load_match(); st.rerun()

    if match_choice != st.session_state.match_key:
        st.session_state.match_key = match_choice
        load_match(); st.rerun()

    mset = MATCHING_SETS[st.session_state.match_key]
    st.info(f"**Instructions:** {mset['instruction']}", icon="🔗")
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    items       = st.session_state.match_items
    opts        = st.session_state.match_opts
    cmap        = st.session_state.match_cmap
    lc          = st.session_state.match_loadn
    submitted   = st.session_state.match_submitted
    placeholder = "— select a match —"
    all_opts    = [placeholder] + opts

    for (iid, term) in items:
        key = f"ms_{iid}_{lc}"
        if not submitted:
            col_l, col_r = st.columns([1,2])
            with col_l:
                st.markdown(f'<div class="match-term">{term}</div>', unsafe_allow_html=True)
            with col_r:
                st.selectbox("", options=all_opts, key=key, label_visibility="collapsed")
        else:
            selected = st.session_state.get(key, placeholder)
            ok    = selected == cmap[iid]
            t_cls = "match-term correct" if ok else "match-term incorrect"
            d_cls = "match-result-def correct" if ok else "match-result-def incorrect"
            ico   = "✅" if ok else "❌"
            st.markdown(
                f'<div class="match-row"><div class="{t_cls}">{ico} {term}</div>'
                f'<div class="{d_cls}">{selected}</div></div>', unsafe_allow_html=True)
            if not ok:
                st.markdown(f'<div class="match-correct-reveal">✔ Correct: {cmap[iid]}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not submitted:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Check My Answers", use_container_width=True, type="primary", key="match_check"):
                all_done = all(st.session_state.get(f"ms_{iid}_{lc}", placeholder) != placeholder for (iid,_) in items)
                if not all_done:
                    st.warning("⚠️ Please make a selection for every term before checking.")
                else:
                    st.session_state.match_submitted = True
                    st.session_state.match_attempts += 1
                    h, n, pct = match_score()
                    if pct > st.session_state.match_best: st.session_state.match_best = pct
                    mistakes = [(term, st.session_state.get(f"ms_{iid}_{lc}",""), cmap[iid])
                                for (iid,term) in items
                                if st.session_state.get(f"ms_{iid}_{lc}","") != cmap[iid]]
                    record_match_attempt(
                        st.session_state.match_key, pct, h, n,
                        time.time() - (st.session_state.match_start_ts or time.time()),
                        mistakes)
                    st.rerun()
        with c2:
            if st.button("🔀 New Shuffle", use_container_width=True, key="match_newsh"):
                load_match(); st.rerun()
    else:
        h, n, pct = match_score()
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big">{pct}%</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-sub">{h} of {n} correct matches</p>', unsafe_allow_html=True)
        fb_cls, fb_msg = score_feedback(pct, h, n)
        st.markdown(f'<div class="fb {fb_cls}">{fb_msg}</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Try Again", use_container_width=True, type="primary", key="match_retry"):
                load_match(); st.rerun()
        with c2:
            if st.button("🔀 New Shuffle", use_container_width=True, key="match_newsh2"):
                load_match(); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TRUE OR FALSE
# ══════════════════════════════════════════════════════════════════════════════
with tab_quiz:
    st.markdown('<p class="section-title">True or False?</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Bust the myths — or confirm the facts. Read the explanation after each answer.</p>', unsafe_allow_html=True)

    qs    = st.session_state.quiz_qs
    idx   = st.session_state.quiz_idx
    total = len(qs)

    if st.session_state.quiz_finished:
        score = st.session_state.quiz_score
        pct   = int(round(score/total*100))
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big">{score}/{total}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-sub">({pct}%) — quiz complete</p>', unsafe_allow_html=True)
        fb_cls, fb_msg = score_feedback(pct, score, total)
        st.markdown(f'<div class="fb {fb_cls}">{fb_msg}</div>', unsafe_allow_html=True)

        with st.expander("📋 Review all questions"):
            for qi, q in enumerate(qs):
                ans_txt   = "TRUE" if q["answer"] else "FALSE"
                badge_cls = "badge-t" if q["answer"] else "badge-f"
                st.markdown(
                    f'<div class="quiz-final-row">'
                    f'<span class="quiz-badge {badge_cls}">{ans_txt}</span>'
                    f'<div><strong>Q{qi+1}:</strong> {q["q"]}<br>'
                    f'<span style="font-size:0.85rem;color:#64748b">{q["explanation"]}</span></div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        if st.button("🔄 Play Again", use_container_width=True, type="primary", key="quiz_again"):
            load_quiz(); st.rerun()
    else:
        prog_pct = int(round(idx/total*100))
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{prog_pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.85rem;color:#64748b;text-align:right;margin-top:2px">Question {idx+1} of {total} &nbsp;|&nbsp; Score: {st.session_state.quiz_score}</p>', unsafe_allow_html=True)

        q = qs[idx]
        st.markdown(f'<div class="quiz-q-card">{q["q"]}</div>', unsafe_allow_html=True)

        if not st.session_state.quiz_answered:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅  TRUE", use_container_width=True, key=f"qt_{idx}", type="secondary"):
                    correct = (q["answer"] is True)
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_correct  = correct
                    if correct: st.session_state.quiz_score += 1
                    st.session_state.quiz_answers.append({"q": q["q"], "correct": correct, "answer_given": True})
                    st.rerun()
            with c2:
                if st.button("❌  FALSE", use_container_width=True, key=f"qf_{idx}"):
                    correct = (q["answer"] is False)
                    st.session_state.quiz_answered = True
                    st.session_state.quiz_correct  = correct
                    if correct: st.session_state.quiz_score += 1
                    st.session_state.quiz_answers.append({"q": q["q"], "correct": correct, "answer_given": False})
                    st.rerun()
        else:
            ans_txt = "TRUE" if q["answer"] else "FALSE"
            if st.session_state.quiz_correct:
                st.markdown('<div class="fb fb-ok">✅ Correct!</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="fb fb-low">❌ Incorrect — the answer is <strong>{ans_txt}</strong>.</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="quiz-explanation">💡 <strong>Explanation:</strong> {q["explanation"]}</div>', unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            if idx + 1 < total:
                if st.button("Next Question →", use_container_width=True, type="primary", key=f"qnext_{idx}"):
                    st.session_state.quiz_idx      += 1
                    st.session_state.quiz_answered  = False
                    st.session_state.quiz_correct   = None
                    st.rerun()
            else:
                if st.button("🏁 See Final Results", use_container_width=True, type="primary", key="qfinal"):
                    st.session_state.quiz_finished = True
                    if not st.session_state.quiz_logged:
                        elapsed_s = time.time() - (st.session_state.quiz_start_ts or time.time())
                        record_quiz_attempt(st.session_state.quiz_score, total, elapsed_s, st.session_state.quiz_answers)
                        st.session_state.quiz_attempts += 1
                        st.session_state.quiz_logged   = True
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CRANIAL NERVES
# ══════════════════════════════════════════════════════════════════════════════
with tab_cn:
    st.markdown('<p class="section-title">Cranial Nerves</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">12 cranial nerves, 5 question modes. Test your knowledge from number identification to clinical presentations.</p>', unsafe_allow_html=True)

    # ── Settings row ──
    col_c1, col_c2, col_c3 = st.columns([2, 1.5, 1])
    with col_c1:
        cn_mode_choice = st.selectbox("Question mode", list(CN_MODES.keys()), key="cn_mode_sel",
            index=list(CN_MODES.keys()).index(st.session_state.cn_mode))
    with col_c2:
        cn_num_choice = st.selectbox("Questions per round", [6, 8, 12], key="cn_num_sel",
            index=[6,8,12].index(st.session_state.cn_num_qs))
    with col_c3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 New Round", use_container_width=True, key="cn_new"):
            st.session_state.cn_mode    = cn_mode_choice
            st.session_state.cn_num_qs  = cn_num_choice
            load_cn(); st.rerun()

    if cn_mode_choice != st.session_state.cn_mode or cn_num_choice != st.session_state.cn_num_qs:
        st.session_state.cn_mode   = cn_mode_choice
        st.session_state.cn_num_qs = cn_num_choice
        load_cn(); st.rerun()

    mode_info = CN_MODES[st.session_state.cn_mode]
    st.info(f"**Mode:** {mode_info['description']}", icon="🧠")

    qs_cn   = st.session_state.cn_questions
    idx_cn  = st.session_state.cn_idx
    total_cn = len(qs_cn)

    # ── FINISHED ──
    if st.session_state.cn_finished:
        score_cn = st.session_state.cn_score
        pct_cn   = int(round(score_cn / total_cn * 100))

        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{pct_cn}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big">{score_cn}/{total_cn}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-sub">({pct_cn}%) — round complete</p>', unsafe_allow_html=True)
        fb_cls, fb_msg = score_feedback(pct_cn, score_cn, total_cn)
        st.markdown(f'<div class="fb {fb_cls}">{fb_msg}</div>', unsafe_allow_html=True)

        with st.expander("📋 Review all questions"):
            for a in st.session_state.cn_answers:
                ok_class = "correct" if a["correct"] else "incorrect"
                ico = "✅" if a["correct"] else "❌"
                st.markdown(
                    f'<div class="quiz-final-row {ok_class}">'
                    f'<div style="flex-shrink:0;font-size:1.1rem">{ico}</div>'
                    f'<div><strong>Q:</strong> {a["prompt"]}<br/>'
                    f'<span style="font-size:0.83rem;color:#64748b">Your answer: <b>{a["chosen"]}</b></span><br/>'
                    + (f'<span style="font-size:0.83rem;color:#16a34a">Correct: <b>{a["correct_ans"]}</b></span><br/>' if not a["correct"] else "")
                    + f'<span style="font-size:0.82rem;color:#1e40af">📌 {a["fact"]}</span>'
                    f'</div></div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again (same mode)", use_container_width=True, type="primary", key="cn_again"):
                load_cn(); st.rerun()
        with c2:
            if st.button("🔀 Change Mode", use_container_width=True, key="cn_change"):
                st.rerun()

    # ── IN PROGRESS ──
    else:
        prog_pct = int(round(idx_cn / total_cn * 100))
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{prog_pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.85rem;color:#64748b;text-align:right;margin-top:2px">'
            f'Question {idx_cn+1} of {total_cn} &nbsp;|&nbsp; Score: {st.session_state.cn_score}</p>',
            unsafe_allow_html=True)

        cn = qs_cn[idx_cn]
        prompt_key  = mode_info["prompt_key"]
        answer_key  = mode_info["answer_key"]
        prompt_text = cn[prompt_key]
        correct_ans = cn[answer_key]

        # ── Flashcard ──
        if prompt_key == "number":
            st.markdown(
                f'<div class="cn-card">'
                f'<div class="cn-num">CRANIAL NERVE</div>'
                f'<div class="cn-name">CN {prompt_text}</div>'
                f'</div>', unsafe_allow_html=True)
        elif prompt_key == "name":
            st.markdown(
                f'<div class="cn-card">'
                f'<div class="cn-num">CN {cn["number"]} — {cn["type"]}</div>'
                f'<div class="cn-name">{prompt_text}</div>'
                f'</div>', unsafe_allow_html=True)
        else:  # clinical scenario
            st.markdown(
                f'<div class="cn-card" style="background:linear-gradient(135deg,#1e3a5f,#4c1d95)">'
                f'<div class="cn-num">CLINICAL SCENARIO</div>'
                f'<div style="font-size:1rem;font-weight:600;line-height:1.6;margin-top:6px">{prompt_text}</div>'
                f'</div>', unsafe_allow_html=True)

        # ── Answer options ──
        if not st.session_state.cn_answered:
            opts = st.session_state.cn_options
            col1, col2 = st.columns(2)
            for i, opt in enumerate(opts):
                btn_col = col1 if i % 2 == 0 else col2
                with btn_col:
                    short_opt = opt[:120] + "…" if len(opt) > 120 else opt
                    if st.button(short_opt, use_container_width=True, key=f"cn_opt_{idx_cn}_{i}"):
                        correct = (opt == correct_ans)
                        st.session_state.cn_answered = True
                        st.session_state.cn_chosen   = opt
                        st.session_state.cn_correct  = correct
                        if correct: st.session_state.cn_score += 1
                        st.session_state.cn_answers.append({
                            "prompt":      prompt_text,
                            "chosen":      opt,
                            "correct_ans": correct_ans,
                            "correct":     correct,
                            "fact":        cn["mnemonic"],
                        })
                        st.rerun()
        else:
            # Show result
            chosen  = st.session_state.cn_chosen
            correct = st.session_state.cn_correct
            opts    = st.session_state.cn_options

            col1, col2 = st.columns(2)
            for i, opt in enumerate(opts):
                btn_col = col1 if i % 2 == 0 else col2
                with btn_col:
                    short_opt = opt[:120] + "…" if len(opt) > 120 else opt
                    if opt == correct_ans:
                        st.markdown(f'<div class="cn-option-btn cn-option-correct">✅ {short_opt}</div>', unsafe_allow_html=True)
                    elif opt == chosen and not correct:
                        st.markdown(f'<div class="cn-option-btn cn-option-wrong">❌ {short_opt}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="cn-option-btn" style="opacity:0.45">{short_opt}</div>', unsafe_allow_html=True)

            if correct:
                st.markdown('<div class="fb fb-ok">✅ Correct!</div>', unsafe_allow_html=True)
            else:
                short_correct = correct_ans[:160] + "…" if len(correct_ans) > 160 else correct_ans
                st.markdown(f'<div class="fb fb-low">❌ Incorrect — correct answer: <strong>{short_correct}</strong></div>', unsafe_allow_html=True)

            st.markdown(f'<div class="cn-fact-box">📌 <strong>Remember:</strong> {cn["mnemonic"]}<br/>🏥 <strong>Clinical:</strong> {cn["clinical"]}</div>', unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            if idx_cn + 1 < total_cn:
                if st.button("Next Question →", use_container_width=True, type="primary", key=f"cn_next_{idx_cn}"):
                    st.session_state.cn_idx      += 1
                    st.session_state.cn_answered  = False
                    st.session_state.cn_chosen    = None
                    st.session_state.cn_correct   = None
                    _prep_cn_options()
                    st.rerun()
            else:
                if st.button("🏁 See Final Results", use_container_width=True, type="primary", key="cn_final"):
                    st.session_state.cn_finished = True
                    if not st.session_state.cn_logged:
                        elapsed_s  = time.time() - (st.session_state.cn_start_ts or time.time())
                        final_pct  = int(round(st.session_state.cn_score / total_cn * 100))
                        mistakes   = [(a["prompt"], a["chosen"], a["correct_ans"])
                                      for a in st.session_state.cn_answers if not a["correct"]]
                        record_cn_attempt(st.session_state.cn_mode, final_pct,
                                          st.session_state.cn_score, total_cn, elapsed_s, mistakes)
                        st.session_state.cn_attempts += 1
                        st.session_state.cn_logged   = True
                    st.rerun()

        # ── Reference panel ──
        with st.expander("📖 Full Cranial Nerve Reference Table"):
            st.markdown("""
| # | Name | Type | Key Function |
|---|------|------|--------------|
| I | Olfactory | Sensory | Smell |
| II | Optic | Sensory | Vision |
| III | Oculomotor | Motor | Eye movement (SR, IR, MR, IO), pupil constriction, eyelid elevation |
| IV | Trochlear | Motor | Superior oblique (eye intorsion & depression) |
| V | Trigeminal | Mixed | Facial sensation (V1/V2/V3); mastication muscles |
| VI | Abducens | Motor | Lateral rectus (eye abduction) |
| VII | Facial | Mixed | Facial expression; taste ant. 2/3 tongue; lacrimation; salivation |
| VIII | Vestibulocochlear | Sensory | Hearing (cochlear) & balance (vestibular) |
| IX | Glossopharyngeal | Mixed | Taste & sensation post. 1/3 tongue; gag reflex afferent; parotid |
| X | Vagus | Mixed | Parasympathetic to thorax/abdomen; phonation; swallowing |
| XI | Accessory | Motor | Sternocleidomastoid (head rotation); trapezius (shoulder shrug) |
| XII | Hypoglossal | Motor | Tongue movement (speech, chewing, swallowing) |
""")
            st.markdown("**Mnemonic for nerve types (S=Sensory, M=Motor, B=Both):**")
            st.markdown("*Some Say Marry Money But My Brother Says Big Brains Matter More* → S S M M B M B S B M M M")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — LECTURE QUIZZES
# ══════════════════════════════════════════════════════════════════════════════
with tab_lq:
    st.markdown('<p class="section-title">Lecture Quizzes</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">100 multiple-choice questions drawn from your lecture material, organised across 10 topics. Select a topic and round length, then answer each question.</p>', unsafe_allow_html=True)

    # ── Settings ──
    topic_options = ["All Topics"] + LECTURE_QUIZ_TOPICS
    col_l1, col_l2, col_l3 = st.columns([2, 1.5, 1])
    with col_l1:
        lq_topic_choice = st.selectbox("Topic", topic_options, key="lq_topic_sel",
            index=topic_options.index(st.session_state.lq_topic))

    # Round length is capped by how many questions the chosen topic holds:
    # each single topic has 10 questions; "All Topics" draws on the full bank.
    lq_max_q       = 20 if lq_topic_choice == "All Topics" else 10
    lq_num_options = [n for n in (5, 10, 15, 20) if n <= lq_max_q]
    # Seed / clamp the dropdown's stored value so it's always a valid option
    lq_stored = st.session_state.get("lq_num_sel", st.session_state.lq_num_qs)
    if lq_stored not in lq_num_options:
        lq_stored = lq_num_options[-1]
    st.session_state["lq_num_sel"] = lq_stored

    with col_l2:
        lq_num_choice = st.selectbox("Questions per round", lq_num_options, key="lq_num_sel")
    with col_l3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 New Round", use_container_width=True, key="lq_new"):
            st.session_state.lq_topic   = lq_topic_choice
            st.session_state.lq_num_qs  = lq_num_choice
            load_lq(); st.rerun()

    if lq_topic_choice != st.session_state.lq_topic or lq_num_choice != st.session_state.lq_num_qs:
        st.session_state.lq_topic  = lq_topic_choice
        st.session_state.lq_num_qs = lq_num_choice
        load_lq(); st.rerun()

    lq_qs    = st.session_state.lq_questions
    lq_idx   = st.session_state.lq_idx
    lq_total = len(lq_qs)

    # ── FINISHED ──
    if st.session_state.lq_finished:
        lq_score = st.session_state.lq_score
        lq_pct   = int(round(lq_score / lq_total * 100))

        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{lq_pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-big">{lq_score}/{lq_total}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="score-sub">({lq_pct}%) — round complete · Topic: {st.session_state.lq_topic}</p>', unsafe_allow_html=True)
        fb_cls, fb_msg = score_feedback(lq_pct, lq_score, lq_total)
        st.markdown(f'<div class="fb {fb_cls}">{fb_msg}</div>', unsafe_allow_html=True)

        with st.expander("📋 Review all questions"):
            for a in st.session_state.lq_answers:
                ok_class = "correct" if a["correct"] else "incorrect"
                ico = "✅" if a["correct"] else "❌"
                wrong_html = ""
                if not a["correct"]:
                    wrong_html = f'<br/><span style="font-size:0.82rem;color:#16a34a">✔ Correct: <b>{a["correct_ans"]}</b></span>'
                st.markdown(
                    f'<div class="quiz-final-row {ok_class}">'
                    f'<div style="flex-shrink:0;font-size:1.1rem">{ico}</div>'
                    f'<div><span style="font-size:0.75rem;color:#64748b;font-weight:600">{a["topic"].upper()}</span><br/>'
                    f'<strong>{a["q"]}</strong><br/>'
                    f'<span style="font-size:0.83rem;color:#64748b">Your answer: <b>{a["chosen"]}</b></span>'
                    f'{wrong_html}<br/>'
                    f'<span style="font-size:0.82rem;color:#1e40af">💡 {a["explanation"]}</span>'
                    f'</div></div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again (same settings)", use_container_width=True, type="primary", key="lq_again"):
                load_lq(); st.rerun()
        with c2:
            if st.button("🔀 Change Topic", use_container_width=True, key="lq_change"):
                st.rerun()

    # ── IN PROGRESS ──
    else:
        prog_pct = int(round(lq_idx / lq_total * 100))
        st.markdown(f'<div class="prog-outer"><div class="prog-inner" style="width:{prog_pct}%"></div></div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.85rem;color:#64748b;text-align:right;margin-top:2px">'
            f'Question {lq_idx+1} of {lq_total} &nbsp;|&nbsp; Score: {st.session_state.lq_score} &nbsp;|&nbsp; Topic: {st.session_state.lq_topic}</p>',
            unsafe_allow_html=True)

        q = lq_qs[lq_idx]

        # Topic badge + question card
        st.markdown(
            f'<div style="display:inline-block;background:#e0f2fe;color:#0369a1;border-radius:5px;'
            f'padding:2px 10px;font-size:0.78rem;font-weight:600;margin-bottom:6px">'
            f'{q["topic"]}</div>',
            unsafe_allow_html=True)
        st.markdown(f'<div class="quiz-q-card">{q["q"]}</div>', unsafe_allow_html=True)

        if not st.session_state.lq_answered:
            # Render options — True/False as 2 cols, MCQ as 2 cols
            opts = q["options"]
            col1, col2 = st.columns(2)
            for i, opt in enumerate(opts):
                btn_col = col1 if i % 2 == 0 else col2
                with btn_col:
                    if st.button(opt, use_container_width=True, key=f"lq_opt_{lq_idx}_{i}",
                                 type="secondary"):
                        correct = (opt == q["correct"])
                        st.session_state.lq_answered = True
                        st.session_state.lq_chosen   = opt
                        st.session_state.lq_correct  = correct
                        if correct: st.session_state.lq_score += 1
                        st.session_state.lq_answers.append({
                            "topic":       q["topic"],
                            "q":           q["q"],
                            "chosen":      opt,
                            "correct_ans": q["correct"],
                            "correct":     correct,
                            "explanation": q["explanation"],
                        })
                        st.rerun()
        else:
            chosen  = st.session_state.lq_chosen
            correct = st.session_state.lq_correct
            opts    = q["options"]

            col1, col2 = st.columns(2)
            for i, opt in enumerate(opts):
                btn_col = col1 if i % 2 == 0 else col2
                with btn_col:
                    if opt == q["correct"]:
                        st.markdown(f'<div class="cn-option-btn cn-option-correct">✅ {opt}</div>', unsafe_allow_html=True)
                    elif opt == chosen and not correct:
                        st.markdown(f'<div class="cn-option-btn cn-option-wrong">❌ {opt}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="cn-option-btn" style="opacity:0.4">{opt}</div>', unsafe_allow_html=True)

            if correct:
                st.markdown('<div class="fb fb-ok">✅ Correct!</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="fb fb-low">❌ Incorrect — correct answer: <strong>{q["correct"]}</strong></div>',
                    unsafe_allow_html=True)
            st.markdown(f'<div class="quiz-explanation">💡 <strong>Explanation:</strong> {q["explanation"]}</div>', unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            if lq_idx + 1 < lq_total:
                if st.button("Next Question →", use_container_width=True, type="primary", key=f"lq_next_{lq_idx}"):
                    st.session_state.lq_idx      += 1
                    st.session_state.lq_answered  = False
                    st.session_state.lq_chosen    = None
                    st.session_state.lq_correct   = None
                    st.rerun()
            else:
                if st.button("🏁 See Final Results", use_container_width=True, type="primary", key="lq_final"):
                    st.session_state.lq_finished = True
                    if not st.session_state.lq_logged:
                        elapsed_s = time.time() - (st.session_state.lq_start_ts or time.time())
                        final_pct = int(round(st.session_state.lq_score / lq_total * 100))
                        mistakes  = [(a["q"][:60], a["chosen"], a["correct_ans"])
                                     for a in st.session_state.lq_answers if not a["correct"]]
                        record_lq_attempt(st.session_state.lq_topic, final_pct,
                                          st.session_state.lq_score, lq_total, elapsed_s, mistakes)
                        st.session_state.lq_attempts += 1
                        st.session_state.lq_logged   = True
                    st.rerun()

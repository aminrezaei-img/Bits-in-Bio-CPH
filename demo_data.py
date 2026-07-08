"""
Pre-baked demo data for Bio Project Triage.
Three scenarios — Proceed, Review, Reframe — each with
realistic Amass API-shaped records across all 3 cores.

Used for: demo presentations, fallback when API is down.
Zero runtime API calls.
"""

# ── Proceed scenario: CRISPR-microbiome for depression ─────
# Low evidence across all cores — genuinely underexplored

PROCEED_BIOMED = [
    {
        "amassId": "AMBC_demo_p001",
        "title": "The Gut-Brain Axis: Microbiome Influences on Mood Disorders",
        "publicationDate": "2025-02-10",
        "journal": "Trends in Neurosciences",
        "publicationTypes": ["Review"],
        "citationCount": 8,
        "journalQualityJufo": 2,
    },
    {
        "amassId": "AMBC_demo_p002",
        "title": "CRISPR-Based Tools for Microbiome Engineering: Current Capabilities",
        "publicationDate": "2024-08-15",
        "journal": "Nature Reviews Microbiology",
        "publicationTypes": ["Review"],
        "citationCount": 22,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_p003",
        "title": "Fecal Microbiota Transplantation for Major Depressive Disorder: A Pilot Study",
        "publicationDate": "2023-06-01",
        "journal": "Journal of Affective Disorders",
        "publicationTypes": ["Clinical Trial", "Journal Article"],
        "citationCount": 5,
        "journalQualityJufo": 1,
    },
]

PROCEED_TRIALS = [
    {
        "amassId": "AMTC_demo_t001",
        "briefTitle": "Microbiome Modulation for Treatment-Resistant Depression",
        "officialTitle": "A Phase 1 Study of Fecal Microbiota Transplantation in Adults With Treatment-Resistant Major Depressive Disorder",
        "startDate": "2024-03-01",
        "phase": "PHASE1",
        "overallStatus": "RECRUITING",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_t002",
        "briefTitle": "Probiotics as Adjunct Treatment in Depression",
        "officialTitle": "Randomized Controlled Trial of a Multi-Strain Probiotic for Major Depressive Disorder",
        "startDate": "2023-09-15",
        "phase": "PHASE2",
        "overallStatus": "COMPLETED",
        "hasResults": True,
    },
]

PROCEED_DRUGS = [
    {
        "amassId": "AMDC_demo_d001",
        "name": "SER-287",
        "drugType": "PROTEIN",
        "maxClinicalStage": "PHASE1",
    },
]

PROCEED_REGULATORY = []  # No regulatory activity for this underexplored space

# ── Review carefully: GLP-1 for Alzheimer's ────────────────
# Moderate evidence — some testing, growing interest

REVIEW_BIOMED = [
    {
        "amassId": "AMBC_demo_r001",
        "title": "GLP-1 Receptor Agonists Reduce Neuroinflammation and Amyloid Pathology in Mouse Models of Alzheimer's Disease",
        "publicationDate": "2024-11-20",
        "journal": "Nature Medicine",
        "publicationTypes": ["Journal Article"],
        "citationCount": 34,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_r002",
        "title": "Association Between GLP-1 Receptor Agonist Use and Reduced Dementia Risk: A Retrospective Cohort Study",
        "publicationDate": "2024-05-10",
        "journal": "JAMA Neurology",
        "publicationTypes": ["Journal Article"],
        "citationCount": 18,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_r003",
        "title": "Neuroprotective Effects of Incretin-Based Therapies: A Systematic Review",
        "publicationDate": "2024-01-30",
        "journal": "Alzheimer's & Dementia",
        "publicationTypes": ["Review", "Systematic Review"],
        "citationCount": 45,
        "journalQualityJufo": 2,
    },
    {
        "amassId": "AMBC_demo_r004",
        "title": "GLP-1 Agonists and Cognitive Function: Evidence from Cardiovascular Outcome Trials",
        "publicationDate": "2023-08-15",
        "journal": "Diabetes Care",
        "publicationTypes": ["Journal Article"],
        "citationCount": 12,
        "journalQualityJufo": 2,
    },
    {
        "amassId": "AMBC_demo_r005",
        "title": "Exenatide and Parkinson's Disease: A Randomized Clinical Trial",
        "publicationDate": "2022-12-01",
        "journal": "The Lancet",
        "publicationTypes": ["Clinical Trial", "Journal Article"],
        "citationCount": 88,
        "journalQualityJufo": 3,
    },
]

REVIEW_TRIALS = [
    {
        "amassId": "AMTC_demo_r001",
        "briefTitle": "Semaglutide in Alzheimer's Disease (EVOKE)",
        "officialTitle": "A Phase 3 Randomized, Double-Blind, Placebo-Controlled Trial of Semaglutide in Early Alzheimer's Disease",
        "startDate": "2023-05-01",
        "phase": "PHASE3",
        "overallStatus": "RECRUITING",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_r002",
        "briefTitle": "Liraglutide for Mild Cognitive Impairment",
        "officialTitle": "Effects of Liraglutide on Cognitive Function in Patients With Mild Cognitive Impairment: A Phase 2 Trial",
        "startDate": "2022-09-01",
        "phase": "PHASE2",
        "overallStatus": "COMPLETED",
        "hasResults": True,
    },
    {
        "amassId": "AMTC_demo_r003",
        "briefTitle": "Dulaglutide and Neurodegeneration Biomarkers",
        "officialTitle": "A Pilot Study of Dulaglutide on CSF Biomarkers of Neurodegeneration in Alzheimer's Disease",
        "startDate": "2024-01-15",
        "phase": "PHASE2",
        "overallStatus": "RECRUITING",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_r004",
        "briefTitle": "GLP-1 Agonist Safety in Elderly with Cognitive Decline",
        "officialTitle": "Safety and Tolerability of GLP-1 Receptor Agonists in Elderly Adults With Cognitive Decline",
        "startDate": "2023-03-01",
        "phase": "PHASE1",
        "overallStatus": "COMPLETED",
        "hasResults": True,
    },
]

REVIEW_DRUGS = [
    {
        "amassId": "AMDC_demo_r001",
        "name": "Semaglutide",
        "drugType": "PROTEIN",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_r002",
        "name": "Liraglutide",
        "drugType": "PROTEIN",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_r003",
        "name": "Dulaglutide",
        "drugType": "PROTEIN",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_r004",
        "name": "Exenatide",
        "drugType": "PROTEIN",
        "maxClinicalStage": "APPROVAL",
    },
]

REVIEW_REGULATORY = [
    {
        "amassId": "AMRC_demo_r001",
        "name": "Ozempic",
        "agency": "FDA",
        "activeSubstance": "Semaglutide",
        "moleculeType": "PROTEIN",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2017-12-05",
        "therapeuticIndication": "Type 2 diabetes mellitus",
    },
    {
        "amassId": "AMRC_demo_r002",
        "name": "Wegovy",
        "agency": "FDA",
        "activeSubstance": "Semaglutide",
        "moleculeType": "PROTEIN",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2021-06-04",
        "therapeuticIndication": "Chronic weight management",
    },
    {
        "amassId": "AMRC_demo_r003",
        "name": "Victoza",
        "agency": "FDA",
        "activeSubstance": "Liraglutide",
        "moleculeType": "PROTEIN",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2010-01-25",
        "therapeuticIndication": "Type 2 diabetes mellitus",
    },
    {
        "amassId": "AMRC_demo_r004",
        "name": "Saxenda",
        "agency": "EMA",
        "activeSubstance": "Liraglutide",
        "moleculeType": "PROTEIN",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2015-03-23",
        "therapeuticIndication": "Weight management",
    },
]

# ── Reframe: CAR-T for solid tumors ────────────────────────
# High crowding, translation, competition

REFRAME_BIOMED = [
    {
        "amassId": "AMBC_demo_f001",
        "title": "CAR-T Cell Therapy for Solid Tumors: Current Progress and Future Directions",
        "publicationDate": "2025-01-15",
        "journal": "Nature Reviews Clinical Oncology",
        "publicationTypes": ["Review"],
        "citationCount": 67,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_f002",
        "title": "Challenges and Strategies for CAR-T Therapy in Solid Tumors: Tumor Microenvironment and Antigen Escape",
        "publicationDate": "2024-09-20",
        "journal": "Cancer Discovery",
        "publicationTypes": ["Review"],
        "citationCount": 42,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_f003",
        "title": "Phase 2 Results of HER2-Targeted CAR-T Cells in Sarcoma",
        "publicationDate": "2024-06-10",
        "journal": "Journal of Clinical Oncology",
        "publicationTypes": ["Clinical Trial", "Journal Article"],
        "citationCount": 31,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_f004",
        "title": "GD2-CAR-T Cells for Neuroblastoma: Long-Term Follow-Up",
        "publicationDate": "2024-03-05",
        "journal": "The Lancet Oncology",
        "publicationTypes": ["Journal Article"],
        "citationCount": 55,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_f005",
        "title": "Armored CAR-T Cells Secreting IL-12 for Ovarian Cancer: A First-in-Human Study",
        "publicationDate": "2023-11-30",
        "journal": "Nature Medicine",
        "publicationTypes": ["Clinical Trial", "Journal Article"],
        "citationCount": 89,
        "journalQualityJufo": 3,
    },
    {
        "amassId": "AMBC_demo_f006",
        "title": "Overcoming the Immunosuppressive Tumor Microenvironment for CAR-T Efficacy",
        "publicationDate": "2023-08-15",
        "journal": "Immunity",
        "publicationTypes": ["Review"],
        "citationCount": 73,
        "journalQualityJufo": 3,
    },
]

REFRAME_TRIALS = [
    {
        "amassId": "AMTC_demo_f001",
        "briefTitle": "HER2-CAR-T in Advanced Sarcoma (SARCOMA-CART)",
        "officialTitle": "A Phase 2 Trial of HER2-Targeted Chimeric Antigen Receptor T Cells in Patients With Advanced HER2-Positive Sarcoma",
        "startDate": "2023-01-15",
        "phase": "PHASE2",
        "overallStatus": "COMPLETED",
        "hasResults": True,
    },
    {
        "amassId": "AMTC_demo_f002",
        "briefTitle": "GD2-CAR-T for Relapsed Neuroblastoma",
        "officialTitle": "GD2-Specific CAR-T Cells in Relapsed/Refractory Neuroblastoma: A Phase 1/2 Trial",
        "startDate": "2022-06-01",
        "phase": "PHASE1/PHASE2",
        "overallStatus": "ACTIVE_NOT_RECRUITING",
        "hasResults": True,
    },
    {
        "amassId": "AMTC_demo_f003",
        "briefTitle": "Mesothelin-CAR-T in Pancreatic Cancer — Terminated",
        "officialTitle": "A Phase 1 Study of Mesothelin-Targeted CAR-T Cells in Metastatic Pancreatic Cancer",
        "startDate": "2021-03-01",
        "phase": "PHASE1",
        "overallStatus": "TERMINATED",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_f004",
        "briefTitle": "IL-12 Armored CAR-T in Ovarian Cancer",
        "officialTitle": "A Phase 1 Trial of Autologous T Cells Engineered to Express a Chimeric Antigen Receptor Targeting MUC16ecto and Secrete IL-12 in Recurrent Ovarian Cancer",
        "startDate": "2022-11-01",
        "phase": "PHASE1",
        "overallStatus": "COMPLETED",
        "hasResults": True,
    },
    {
        "amassId": "AMTC_demo_f005",
        "briefTitle": "Claudin18.2-CAR-T in Gastric Cancer",
        "officialTitle": "A Phase 1 Study of Claudin18.2-Targeted CAR-T Cells in Advanced Gastric and Gastroesophageal Junction Cancer",
        "startDate": "2023-05-01",
        "phase": "PHASE1",
        "overallStatus": "RECRUITING",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_f006",
        "briefTitle": "EGFRvIII-CAR-T in Glioblastoma — Terminated",
        "officialTitle": "Intracranial Injection of EGFRvIII-Directed CAR-T Cells in Recurrent Glioblastoma",
        "startDate": "2020-09-01",
        "phase": "PHASE1",
        "overallStatus": "TERMINATED",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_f007",
        "briefTitle": "MUC1-CAR-T in Breast Cancer — Terminated Early",
        "officialTitle": "A Phase 1 Trial of MUC1-Targeted CAR-T Cells in Metastatic Triple-Negative Breast Cancer",
        "startDate": "2019-05-01",
        "phase": "PHASE1",
        "overallStatus": "TERMINATED",
        "hasResults": False,
    },
    {
        "amassId": "AMTC_demo_f008",
        "briefTitle": "IL13Rα2-CAR-T in Glioblastoma — Suspended",
        "officialTitle": "Intratumoral IL13Rα2-Targeted CAR-T Cells for Recurrent Glioblastoma",
        "startDate": "2020-11-01",
        "phase": "PHASE1",
        "overallStatus": "SUSPENDED",
        "hasResults": False,
    },
]

REFRAME_DRUGS = [
    {
        "amassId": "AMDC_demo_f001",
        "name": "Tisagenlecleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f002",
        "name": "Axicabtagene Ciloleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f003",
        "name": "Brexucabtagene Autoleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f004",
        "name": "Lisocabtagene Maraleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f005",
        "name": "Ideacabtagene Vicleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f006",
        "name": "Ciltacabtagene Autoleucel",
        "drugType": "CELL",
        "maxClinicalStage": "APPROVAL",
    },
    {
        "amassId": "AMDC_demo_f007",
        "name": "Satricabtagene Autoleucel",
        "drugType": "CELL",
        "maxClinicalStage": "PHASE3",
    },
]

REFRAME_REGULATORY = [
    {
        "amassId": "AMRC_demo_f001",
        "name": "Kymriah",
        "agency": "FDA",
        "activeSubstance": "Tisagenlecleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2017-08-30",
        "therapeuticIndication": "B-cell acute lymphoblastic leukemia",
    },
    {
        "amassId": "AMRC_demo_f002",
        "name": "Yescarta",
        "agency": "FDA",
        "activeSubstance": "Axicabtagene Ciloleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2017-10-18",
        "therapeuticIndication": "Large B-cell lymphoma",
    },
    {
        "amassId": "AMRC_demo_f003",
        "name": "Tecartus",
        "agency": "FDA",
        "activeSubstance": "Brexucabtagene Autoleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2020-07-24",
        "therapeuticIndication": "Mantle cell lymphoma",
    },
    {
        "amassId": "AMRC_demo_f004",
        "name": "Breyanzi",
        "agency": "FDA",
        "activeSubstance": "Lisocabtagene Maraleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2021-02-05",
        "therapeuticIndication": "Large B-cell lymphoma",
    },
    {
        "amassId": "AMRC_demo_f005",
        "name": "Carvykti",
        "agency": "FDA",
        "activeSubstance": "Ciltacabtagene Autoleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2022-02-28",
        "therapeuticIndication": "Multiple myeloma",
    },
    {
        "amassId": "AMRC_demo_f006",
        "name": "Kymriah",
        "agency": "EMA",
        "activeSubstance": "Tisagenlecleucel",
        "moleculeType": "CELL",
        "authorizationStatus": "ACTIVE",
        "authorizationDate": "2018-08-27",
        "therapeuticIndication": "B-cell acute lymphoblastic leukemia",
    },
]

# ── Scenario registry ──────────────────────────────────────

DEMO_SCENARIOS = {
    "proceed": {
        "label": "🟢 Proceed — CRISPR-microbiome for depression",
        "idea": "CRISPR-based microbiome engineering to treat major depressive disorder",
        "expected_rec": "Proceed",
        "biomedcore": {"records": PROCEED_BIOMED, "total": len(PROCEED_BIOMED), "error": None},
        "trialcore": {"records": PROCEED_TRIALS, "total": len(PROCEED_TRIALS), "error": None},
        "drugcore": {"records": PROCEED_DRUGS, "total": len(PROCEED_DRUGS), "error": None},
        "regulatorycore": {"records": PROCEED_REGULATORY, "total": len(PROCEED_REGULATORY), "error": None},
    },
    "review": {
        "label": "🟡 Review — GLP-1 receptor agonists for Alzheimer's",
        "idea": "GLP-1 receptor agonists for Alzheimer's disease",
        "expected_rec": "Review carefully",
        "biomedcore": {"records": REVIEW_BIOMED, "total": len(REVIEW_BIOMED), "error": None},
        "trialcore": {"records": REVIEW_TRIALS, "total": len(REVIEW_TRIALS), "error": None},
        "drugcore": {"records": REVIEW_DRUGS, "total": len(REVIEW_DRUGS), "error": None},
        "regulatorycore": {"records": REVIEW_REGULATORY, "total": len(REVIEW_REGULATORY), "error": None},
    },
    "reframe": {
        "label": "🔴 Reframe — CAR-T therapy for solid tumors",
        "idea": "CAR-T cell therapy for solid tumors",
        "expected_rec": "Reframe",
        "biomedcore": {"records": REFRAME_BIOMED, "total": len(REFRAME_BIOMED), "error": None},
        "trialcore": {"records": REFRAME_TRIALS, "total": len(REFRAME_TRIALS), "error": None},
        "drugcore": {"records": REFRAME_DRUGS, "total": len(REFRAME_DRUGS), "error": None},
        "regulatorycore": {"records": REFRAME_REGULATORY, "total": len(REFRAME_REGULATORY), "error": None},
    },
}


def get_demo_scenario(key: str) -> dict | None:
    """Return a full demo scenario by key, or None."""
    return DEMO_SCENARIOS.get(key)


def get_demo_scenarios() -> dict:
    """Return all demo scenarios."""
    return DEMO_SCENARIOS

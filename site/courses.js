// Demo catalogue. Prices in INR. Ids must match what the event simulator sends.
// audience/goal/tryInstead feed the course guide (course-guide.html) that the
// SalesIQ bot is trained on; regenerate it with: python tools/build_course_guide.py
window.COURSES = [
  {
    id: "ecg-101",
    title: "ECG Interpretation Essentials",
    level: "Beginner",
    duration: "6 hours",
    price: 1499,
    lessons: 12,
    summary: "Read rhythm strips with confidence: rate, rhythm, axis, intervals and the ten patterns you will meet most.",
    outcomes: ["Systematic 7-step ECG read", "Recognise common arrhythmias", "Spot STEMI patterns early"],
    audience: "Nursing staff, junior doctors, paramedics and students who see ECGs on shift but don't yet read them confidently.",
    goal: "Reading ECGs and heart rhythms",
    tryInstead: [
      "bls-201|You want hands-on emergency skills rather than interpretation",
      "pharm-110|You already read ECGs and want to understand the cardiac drugs behind them",
    ],
  },
  {
    id: "bls-201",
    title: "Basic Life Support Refresher",
    level: "All levels",
    duration: "3 hours",
    price: 799,
    lessons: 8,
    summary: "Current adult, child and infant BLS sequences, team roles and high-quality CPR metrics.",
    outcomes: ["High-quality CPR metrics", "AED use", "Team-based resuscitation"],
    audience: "Any healthcare worker who needs to refresh resuscitation skills, from students to senior staff.",
    goal: "Emergencies and resuscitation",
    tryInstead: [
      "ecg-101|You already know BLS well and want the next step: recognising dangerous rhythms",
      "pharm-110|You want ward knowledge rather than emergency skills",
    ],
  },
  {
    id: "pharm-110",
    title: "Clinical Pharmacology Basics",
    level: "Intermediate",
    duration: "8 hours",
    price: 1999,
    lessons: 16,
    summary: "Pharmacokinetics, dosing in renal and hepatic impairment, and the interactions that matter on the ward.",
    outcomes: ["PK/PD fundamentals", "Dose adjustment", "High-risk interactions"],
    audience: "Nurses, pharmacists and doctors who prescribe, check or give medicines on the ward.",
    goal: "Medicines and safe prescribing",
    tryInstead: [
      "bls-201|You want a short, practical course you can finish in one sitting",
      "research-300|You're more interested in evidence and publishing than day-to-day prescribing",
    ],
  },
  {
    id: "research-300",
    title: "Medical Research Writing",
    level: "Advanced",
    duration: "5 hours",
    price: 1299,
    lessons: 10,
    summary: "Structure, write and submit a clinical paper: IMRaD, reporting guidelines and responding to reviewers.",
    outcomes: ["IMRaD structure", "Reporting checklists", "Reviewer responses"],
    audience: "Clinicians and postgraduate students planning to write up a case, audit or study for publication.",
    goal: "Research and publishing",
    tryInstead: [
      "pharm-110|You want clinical knowledge you can use on shift rather than writing skills",
      "ecg-101|You want a beginner-friendly clinical skill with quick wins",
    ],
  },
];

window.formatPrice = (n) => "₹" + n.toLocaleString("en-IN");

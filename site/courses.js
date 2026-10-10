// Demo catalogue. Prices in INR. Ids must match what the event simulator sends.
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
  },
];

window.formatPrice = (n) => "₹" + n.toLocaleString("en-IN");

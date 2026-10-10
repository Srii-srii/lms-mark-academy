# Omnichannel Campaign POC: Demo Academy

This is a 2-day proof of concept of the Zoho campaign stack (Zoho Flow, Marketing Automation (ZMA), CPaaS and SalesIQ). It does not touch Better Universe or TrainerCentral.

```
site/                        static academy website, hosted free on GitHub Pages (HTTPS)
  zoho-config.js             the ONLY file you edit to connect Zoho snippets
simulator/send_event.py      sends learner events (signup, cart, purchase, lesson, completion) to Zoho Flow
.github/workflows/
  deploy-site.yml            publishes site/ to GitHub Pages on every push
  simulate-event.yml         "Run workflow" button that fires events or full scenarios
```

**How it fits together.** Real visitors use the site, so web tracking, the sign-up form and chat are all real. The simulator plays the learning platform: it sends purchases and course progress. Zoho Flow's **core flows** receive one standard event format. Later, TrainerCentral feeds those same core flows through small **adapter** flows (see section 6), so nothing else in Zoho changes.

---

## 0. Blocker: you need a domain for email (decide this first)

Email can only be authenticated (SPF, DKIM, DMARC) with DNS records on a domain you control. `github.io` doesn't allow that, and you can't add records to the company domain right now.

**Recommended: buy a cheap domain today.** First-year prices for `.in`, `.xyz` or `.online` are usually about ₹100–1,000 at registrars like Hostinger, GoDaddy, Namecheap or Cloudflare. Pick one with a DNS editor (they all have one). New records usually take effect within 15–60 minutes. Then use:

| Subdomain | Used by | Purpose |
| --- | --- | --- |
| `news.lms-mark.website` | ZMA | Marketing email (from-address like `hello@news.lms-mark.website`) |
| `notify.lms-mark.website` | CPaaS | Transactional email (enrolment, completion) |
| `academy.lms-mark.website` (optional) | GitHub Pages | A nicer site URL than `github.io` |

Plus one DMARC record on the root: `_dmarc.lms-mark.website  TXT  "v=DMARC1; p=none; rua=mailto:<your inbox>"`.

**If you cannot buy one:** everything else in this POC still works: site, tracking, forms, chat, flows, journeys, WhatsApp and social. CPaaS email can't be demoed, though, and ZMA email may be limited or land in spam. Tell your CTO the demo shows the email steps configured but not sending, because it's blocked on a domain.

---

## 1. Publish the site (about 15 minutes)

1. Create a **public** GitHub repo, for example `academy-poc`. Free GitHub Pages needs a public repo. That's safe here: webhook URLs go in Secrets, and the simulator masks emails and phone numbers in the logs.
2. Push this folder:
   ```bash
   cd D:/Better_universe_marketing_campagin/poc-demo-academy
   git init -b main
   git add .
   git commit -m "Demo academy for omnichannel campaign POC"
   git remote add origin https://github.com/<you>/academy-poc.git
   git push -u origin main
   ```
3. In the repo, go to **Settings → Pages → Source: GitHub Actions**. Then **Actions → Deploy site to GitHub Pages → Run workflow** (it also runs on every push).
4. The site appears at `https://<you>.github.io/academy-poc/`, served over HTTPS.
5. (Optional, with a domain) In **Settings → Pages → Custom domain**, enter `academy.lms-mark.website`, add the CNAME record GitHub shows, and tick **Enforce HTTPS**.

Every later change, such as pasting Zoho snippets, is: edit the file → `git commit -am "..."` → `git push`. The site updates in about a minute.

---

## 2. Day 1: connect Zoho

Menu names can differ slightly between Zoho versions and data centres. Look for the closest match.

### 2.1 Sending domains (start first, because DNS takes time)

- **ZMA**: Settings → Sender domains / Domain authentication → add `news.lms-mark.website` → copy the SPF/DKIM records into your registrar's DNS → Verify.
- **CPaaS (ZeptoMail)**: Mail agents → add a mail agent "Academy POC" → Domains → add `notify.lms-mark.website` → add its DKIM and CNAME records → Verify.
- Add the DMARC record from section 0.

### 2.2 ZMA: fields, list, tracking, sign-up form

1. **Custom lead fields** (Settings → Fields). Create these, because the core flows write to them:
   `lifecycle_stage`, `learner_id`, `last_event`, `last_course_id`, `last_course_title`, `last_course_url`, `last_order_id`, `progress_percent`, `consent_whatsapp`, `consent_sms`, `consent_source`, `consent_captured_at`, `source_system`.
   Keep the names neutral (no "demo" or "bu"), because TrainerCentral will write to the same fields.
2. **List**: `POC – Learners`. Tag every POC contact `src:poc` so they can be deleted before go-live.
3. **Web tracking**: add the website `https://<you>.github.io` (or `academy.lms-mark.website`) → copy the tracking code → paste it into `ZMA_TRACKING_SNIPPET` in `site/zoho-config.js`. It loads only after a visitor clicks *Accept analytics* on the cookie banner.
4. **Sign-up form**: create a form with First name, Email, Mobile, and **three unticked consent checkboxes**: email updates, WhatsApp updates, SMS updates. It adds people to `POC – Learners` and sets `lifecycle_stage = lead`. Copy the **embed code** into `ZMA_SIGNUP_FORM_EMBED`.
5. Push. Open the site, accept cookies, sign up with your own email, and check that the lead appears in ZMA.

### 2.3 SalesIQ: website chat

1. Settings → Brands → add brand "Academy POC" with the site URL → Installation → copy the website code → paste it into `SALESIQ_WIDGET_SNIPPET` → push.
2. Settings → Departments → add yourself as an **operator**. This fixes "No Operators Available".
3. Answer Hub: delete the sample article and add 8–10 FAQs (courses, fees, certificate, refund, how to enrol).
4. Zobot (Codeless bot builder): greeting → menu **Courses / Fees / Upcoming webinars / Talk to a person** → FAQ answers → collect name, email and phone → "Talk to a person" routes to the operator.
5. Messenger is already connected. Instagram DM: in Instagram, turn on *Allow access to messages*, then connect it in SalesIQ.
6. Integrations → Zoho Marketing Automation: push chat visitors who left an email into `POC – Learners`.

### 2.4 Zoho Flow: core flows (the part that carries over to TrainerCentral)

Create **one flow per event**. Each flow uses **Trigger: Webhook**, payload format **JSON**. Name them exactly like this:

| Flow name | ZMA actions | CPaaS action |
| --- | --- | --- |
| `CORE · learner.signed_up` | Create/update lead (all fields, `lifecycle_stage=lead`), add to `POC – Learners`, add to journey **Lead nurture** (only if `consent_email_marketing = yes`, using a Decision step) | Send welcome email |
| `CORE · cart.updated` | Update lead (`last_course_*`), add to journey **Abandoned cart** | — |
| `CORE · order.completed` | Update lead (`lifecycle_stage=enrolled`, `last_order_id`), add lead score +20, add to journey **Onboarding** | Send **enrolment confirmation** |
| `CORE · lesson.completed` | Update lead (`lifecycle_stage=active`, `progress_percent`), add lead score +5 | — |
| `CORE · course.completed` | Update lead (`lifecycle_stage=completed`), add lead score +20, add to journey **Completed** | Send **completion / certificate** email |

How to build each one:

1. Create a flow, choose the Webhook trigger, select JSON, and **copy the webhook URL**.
2. Add all five URLs to one GitHub secret: repo **Settings → Secrets and variables → Actions → New secret**, named `ZOHO_FLOW_WEBHOOKS`:
   ```json
   {
     "learner.signed_up": "https://flow.zoho.in/....",
     "cart.updated": "https://flow.zoho.in/....",
     "order.completed": "https://flow.zoho.in/....",
     "lesson.completed": "https://flow.zoho.in/....",
     "course.completed": "https://flow.zoho.in/...."
   }
   ```
3. Send a sample so Flow learns the fields: **Actions → Simulate learner event → Run workflow** with mode `event` and the matching event. Or run it locally:
   ```bash
   ZOHO_FLOW_WEBHOOKS='{"order.completed":"<url>"}' python simulator/send_event.py --event order.completed --email you@example.com
   ```
4. Map the payload fields (`learner_email`, `course_title`, and so on) into the actions, then switch the flow **ON**.

Payload fields (flat JSON, the same for every event): `schema_version, event_id, event, occurred_at, source, lifecycle_stage, learner_id, learner_first_name, learner_last_name, learner_email, learner_phone, consent_email_marketing, consent_whatsapp, consent_sms, consent_captured_at, consent_source, course_id, course_title, course_price, course_url, currency, order_id, order_amount, lesson_number, progress_percent`. To see a full example, run `python simulator/send_event.py --event order.completed --email x@y.z --dry-run`.

---

## 3. Day 2: messages, journeys, channels

### 3.1 CPaaS templates (transactional only, no promotions)

Create three templates: **Welcome**, **Enrolment confirmation** (course title, order id, course link) and **Course completed** (certificate line, next-course suggestion). Use them in the CPaaS "Send email" actions above. Test until the email lands in the Gmail **inbox**, then use *Show original* to check SPF, DKIM and DMARC all show `PASS`.

### 3.2 ZMA journeys (use short waits for the demo)

| Journey | Entry | Steps (demo timing / real timing) | Exit rule |
| --- | --- | --- | --- |
| Lead nurture | Added by `CORE · learner.signed_up` | Email 1 now → wait 10 min / 2 days → Email 2 → wait 10 min / 3 days → Email 3 (offer) | `lifecycle_stage` is not `lead` |
| Abandoned cart | Added by `CORE · cart.updated` | Wait 5 min / 24 h → if `lifecycle_stage` is still `lead`, send "Your course is waiting" email (+ WhatsApp template if `consent_whatsapp = yes`) | `lifecycle_stage = enrolled` |
| Onboarding | Added by `CORE · order.completed` | "How to get started" now → wait 10 min / 3 days → nudge if `progress_percent` is empty | `lifecycle_stage = completed` |
| Completed | Added by `CORE · course.completed` | wait 5 min / 2 days → feedback request → wait 10 min / 7 days → next-course offer | unsubscribe or new purchase |

Use the shortest wait ZMA allows if it won't go down to minutes. Add an **SMS step but leave it switched off**, with the note "needs DLT registration (India)". That shows the design without sending.

Rules for all journeys: at most 1 marketing message per channel per day, email first, and every journey has an end.

### 3.3 WhatsApp (only if a business SIM is ready)

- Use a **separate SIM** as the business number, not your personal number. Connecting a number to the WhatsApp Business API removes it from the normal WhatsApp app.
- Connect it in ZMA (WhatsApp integration) and SalesIQ (Channels → WhatsApp). Submit one marketing template (abandoned cart) and one utility template (enrolment). Meta approval can take minutes to hours.
- Your **personal number** is the **test recipient**. Enter it as the Mobile on your own test lead (sign-up form or ZMA → Leads), tick WhatsApp consent, and message the business number from your phone to test the SalesIQ bot.

### 3.4 Social

ZMA → Social: connect the Facebook page, Instagram business account and X to one brand, and schedule 5–6 posts over the next week, each linking to a course page with UTM tags (`?utm_source=instagram&utm_medium=social&utm_campaign=poc`).

---

## 4. CTO demo script (about 15 minutes)

1. **Site**: open the HTTPS URL, show the cookie banner, then accept so tracking loads.
2. **Chat**: ask the bot "What are the fees?", choose *Talk to a person*, and answer from the SalesIQ inbox. Show Messenger (and WhatsApp from your phone) arriving in the same inbox.
3. **Sign-up with consent**: fill in the form live, then show the lead in ZMA with its consent fields and the Lead nurture journey started.
4. **Abandoned cart, then purchase**: GitHub → Run workflow → `cart_then_purchase`. Show Flow's run history, the lead moving to `enrolled`, the **abandoned-cart reminder not sent** (it exited), the enrolment email in the inbox, and the `PASS` headers.
5. **Full journey**: `full_journey` → lesson score increases → completion email → Completed journey.
6. **Social**: the scheduled posts calendar.
7. **Switching to TrainerCentral**: show the CORE flows and explain that only adapter flows get added (section 6). Show the disabled SMS step and the DLT note.
8. **Next steps and cost**: see the main plan, `../MARKETING_CAMPAIGN_PLAN.md`.

Simulator scenarios:

| Scenario | Events | What it proves |
| --- | --- | --- |
| `full_journey` | signup → cart → purchase → 2 lessons → completed | Every stage, scoring, transactional mail |
| `abandoned_cart` | signup → cart | The reminder fires |
| `cart_then_purchase` | signup → cart → purchase | Exit rules: no reminder after buying |

---

## 5. Data hygiene

- Use only internal test contacts. Before the TrainerCentral go-live, delete everything tagged `src:poc` and the `POC – Learners` list.
- Never commit webhook URLs, API keys or phone numbers. They belong in GitHub Secrets or the workflow inputs.

## 6. Switching to TrainerCentral later

For each TrainerCentral trigger, add an **adapter** flow that converts it to the standard payload and forwards it to the matching CORE webhook. The core flows, journeys, templates, fields and bot stay as they are.

| Adapter flow | TrainerCentral trigger | Forwards to |
| --- | --- | --- |
| `ADAPTER · TC · signup` | New sign-up to academy | `CORE · learner.signed_up` |
| `ADAPTER · TC · enrolled` | Course enrolled / Ticket purchased | `CORE · order.completed` |
| `ADAPTER · TC · lesson` | Lesson completed by user | `CORE · lesson.completed` |
| `ADAPTER · TC · completed` | Course completed | `CORE · course.completed` |

Each adapter is: TrainerCentral trigger → **Custom function** (Deluge) → done. Example function (check the syntax in Flow's function editor):

```
void forwardToCore(string coreUrl, string eventName, string stage, string email, string firstName, string lastName, string courseId, string courseTitle)
{
    payload = Map();
    payload.put("schema_version", "1.0");
    payload.put("event", eventName);
    payload.put("source", "trainercentral");
    payload.put("lifecycle_stage", stage);
    payload.put("learner_email", email);
    payload.put("learner_first_name", firstName);
    payload.put("learner_last_name", lastName);
    payload.put("course_id", courseId);
    payload.put("course_title", courseTitle);
    headers = Map();
    headers.put("Content-Type", "application/json");
    response = invokeurl
    [
        url : coreUrl
        type : POST
        parameters : payload.toString()
        headers : headers
    ];
    info response;
}
```

Then move the ZMA tracking code and SalesIQ widget into TrainerCentral's **Header Code**, switch the website in ZMA and SalesIQ to the academy domain, and stop using the simulator. The sending domains (section 0) can stay as they are or be swapped for the academy's own.

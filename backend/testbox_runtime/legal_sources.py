from __future__ import annotations

from .models import LegalSource


SOURCES: list[LegalSource] = [
    LegalSource(
        id="wetten-wvw-article-185",
        title="Wetten.overheid.nl - Wegenverkeerswet 1994, article 185",
        url="https://wetten.overheid.nl/cgi-bin/deeplink/law1/bwbid=BWBR0006622/article=185",
        jurisdiction="Netherlands",
        domains=["liability", "traffic"],
        keywords=[
            "article 185",
            "artikel 185",
            "wegenverkeerswet",
            "wvw",
            "traffic accident",
            "verkeersongeval",
            "aanrijding",
            "fiets",
            "fietser",
            "bicycle",
            "cyclist",
            "bike",
            "car",
            "auto",
            "liability",
            "aansprakelijkheid",
            "compensation",
            "schadevergoeding",
            "damage",
            "schade",
            "велосипед",
            "велосипедист",
            "авто",
            "машина",
            "дтп",
            "авария",
            "компенсация",
            "ущерб",
            "ответственность",
        ],
        summary=(
            "Article 185 of the Dutch Road Traffic Act 1994 states that if a "
            "motor vehicle on the road is involved in a traffic accident causing "
            "damage to persons or property not transported by that vehicle, the "
            "owner or holder must compensate the damage unless force majeure is "
            "made plausible."
        ),
    ),
    LegalSource(
        id="rijksoverheid-wa-insurance",
        title="Rijksoverheid - WA-verzekering voor voertuigen",
        url="https://www.rijksoverheid.nl/vraag-en-antwoord/auto/wa-verzekering-voertuig",
        jurisdiction="Netherlands",
        domains=["liability", "insurance", "traffic"],
        keywords=[
            "wa-verzekering",
            "wam",
            "third-party liability",
            "liability insurance",
            "verzekering",
            "insurance",
            "auto",
            "car",
            "motorrijtuig",
            "schade",
            "damage",
            "страховка",
            "ущерб",
        ],
        summary=(
            "Rijksoverheid states that owners of motor vehicles must have WA "
            "liability insurance. If a motor vehicle causes damage, WA insurance "
            "usually covers that damage."
        ),
    ),
    LegalSource(
        id="government-dutch-traffic-crash",
        title="Government.nl - Participating in Dutch traffic",
        url=(
            "https://www.government.nl/binaries/government/documenten/reports/"
            "2024/02/09/participating-in-dutch-traffic/"
            "participating-in-dutch-traffic.pdf"
        ),
        jurisdiction="Netherlands",
        domains=["traffic", "accident_procedure"],
        keywords=[
            "traffic accident",
            "crash",
            "injury",
            "death",
            "112",
            "police",
            "accident report",
            "verkeersongeval",
            "aanrijding",
            "авария",
            "дтп",
            "полиция",
            "травма",
        ],
        summary=(
            "Government.nl says that in a crash involving injury or death, call "
            "112; police will make an official report. Drivers should exchange "
            "details and use the insurance accident form."
        ),
    ),
    LegalSource(
        id="ind-ukraine-temporary-protection",
        title="IND - Temporary Protection Directive Ukraine",
        url="https://ind.nl/en/ukraine/temporary-protection-directive-ukraine",
        jurisdiction="Netherlands",
        domains=["immigration"],
        keywords=[
            "ukraine",
            "ukrainian",
            "temporary protection",
            "ind",
            "proof of residency",
            "brp",
            "gemeente",
            "украин",
            "нидерланд",
            "временн",
            "защит",
        ],
        summary=(
            "IND explains temporary protection for refugees from Ukraine, "
            "municipal registration, proof of residency, and the right to live "
            "and work in the Netherlands when covered."
        ),
    ),
    LegalSource(
        id="government-minimum-wage-less-than",
        title="Government.nl - Less than the hourly minimum wage",
        url="https://www.government.nl/themes/work/minimum-wage/less-than-the-minimum-wage",
        jurisdiction="Netherlands",
        domains=["employment"],
        keywords=[
            "minimum wage",
            "underpaid",
            "labour authority",
            "minimumloon",
            "onderbetaald",
            "ниже минимальной зарплаты",
            "меньше минимальной ставки",
        ],
        summary=(
            "Government.nl states that if an employer pays less than minimum wage "
            "and refuses correction, the employee can contact the Netherlands "
            "Labour Authority or take the employer to court."
        ),
    ),
    LegalSource(
        id="rijksoverheid-wage-payment-delay",
        title="Rijksoverheid - Wanneer betaalt mijn werkgever mijn loon?",
        url=(
            "https://www.rijksoverheid.nl/onderwerpen/arbeidsovereenkomst-en-cao/"
            "vraag-en-antwoord/wanneer-betaalt-mijn-werkgever-mijn-loon"
        ),
        jurisdiction="Netherlands",
        domains=["employment"],
        keywords=[
            "unpaid wages",
            "salary not paid",
            "late payment",
            "loon niet betaald",
            "loon te laat",
            "achterstallige loon",
            "не выплатил зарплату",
            "задержка зарплаты",
            "задерживает зарплату",
            "задержали зарплату",
            "задерживает заработную плату",
            "зарплату не выплатили",
            "не выплачивает зарплату",
            "невыплате зарплаты",
        ],
        summary=(
            "Rijksoverheid states that when an employer does not pay salary, "
            "an employee can demand outstanding wages in writing. If the employer "
            "does not respond, a wage claim can be pursued with legal assistance, "
            "for example from Juridisch Loket. Late payment may also entitle the "
            "employee to a statutory increase, subject to court assessment."
        ),
    ),
    LegalSource(
        id="belastingdienst-intermediair-modelovereenkomst",
        title="Belastingdienst - Ik wil een modelovereenkomst gebruiken. Maar welke?",
        url=(
            "https://www.belastingdienst.nl/wps/wcm/connect/nl/arbeidsrelaties/"
            "content/ik-wil-een-modelovereenkomst-gebruiken-maar-welke"
        ),
        jurisdiction="Netherlands",
        domains=["zzp_intermediary_contract"],
        keywords=[
            "zzp", "intermediair", "bemiddeling", "tussenkomst", "uitzendbureau",
            "detacheringsbureau", "агентств", "трудоустройств", "ззп",
        ],
        summary=(
            "Belastingdienst distinguishes mediation (bemiddeling), where the "
            "end client gives the assignment, from intermediation (tussenkomst), "
            "where the intermediary is the contractor's client. For tussenkomst, "
            "use of the model agreement depends on absence of authority and "
            "supervision and on working as an entrepreneur in practice."
        ),
    ),
    LegalSource(
        id="businessgov-wet-dba-false-self-employment",
        title="Business.gov.nl - Assessing work relationship between client and contractor (Wet DBA)",
        url="https://business.gov.nl/regulations/employment-relationship-model-agreements-wet-dba/",
        jurisdiction="Netherlands",
        domains=["zzp_intermediary_contract"],
        keywords=[
            "zzp", "freelancer", "contractor", "wet dba", "false self-employment",
            "самозанят", "фриланс", "агентств", "ззп",
        ],
        summary=(
            "Business.gov.nl states that Dutch clients and self-employed contractors "
            "must assess together whether their arrangement is actually employment "
            "under Wet DBA. Existing model agreements may be used until "
            "31 December 2029, provided the parties work as described."
        ),
    ),
    LegalSource(
        id="rijksoverheid-municipal-parking-rules",
        title="Rijksoverheid - Parkeren met een gehandicaptenparkeerkaart",
        url=(
            "https://www.rijksoverheid.nl/vraag-en-antwoord/verkeersveiligheid/"
            "waar-mag-ik-met-een-gehandicaptenparkeerkaart-parkeren"
        ),
        jurisdiction="Netherlands",
        domains=["residential_parking"],
        keywords=[
            "parkeren", "parkeerplaats", "parkeervergunning", "parking",
            "парков", "место возле дома", "возле дома",
        ],
        summary=(
            "Rijksoverheid states that parking rules and permits can differ by "
            "municipality and directs residents to their municipality or local "
            "parking management service. It also describes a reserved disabled "
            "parking space linked to a licence plate, for example at a home."
        ),
    ),
    LegalSource(
        id="businessgov-start-a-business",
        title="Business.gov.nl - Step-by-step plan: How to start a business in the Netherlands",
        url=(
            "https://business.gov.nl/starting-your-business/preparations/"
            "step-by-step-plan-how-to-start-a-business-in-the-netherlands/"
        ),
        jurisdiction="Netherlands",
        domains=["consulting_services"],
        keywords=[
            "consulting", "consultancy", "consultant", "advice", "advies",
            "консалт", "консультацион",
        ],
        summary=(
            "Business.gov.nl states that a business in the Netherlands must register "
            "with the KVK Business Register and address Dutch taxes. KVK passes "
            "registration details to the Belastingdienst; a VAT entrepreneur receives "
            "a VAT number and VAT ID. The plan also requires choosing a legal structure "
            "and keeping business records."
        ),
    ),
    LegalSource(
        id="businessgov-professional-indemnity-insurance",
        title="Business.gov.nl - Professional indemnity insurance",
        url="https://business.gov.nl/running-your-business/insurance/professional-indemnity-insurance/",
        jurisdiction="Netherlands",
        domains=["consulting_services"],
        keywords=[
            "consulting", "consultancy", "consultant", "advice", "advisor",
            "professional indemnity", "консалт", "консультацион",
        ],
        summary=(
            "Business.gov.nl explains that professional indemnity insurance "
            "(beroepsaansprakelijkheidsverzekering, BAV) is particularly useful "
            "when providing advice because a client can suffer financial loss from "
            "professional mistakes. It is legally mandatory only for specified "
            "professions, while clients or professional bodies may still require it."
        ),
    ),
    LegalSource(
        id="businessgov-choose-legal-structure",
        title="Business.gov.nl - Choose a legal structure",
        url="https://business.gov.nl/running-your-business/legal-forms-and-governance/choose-a-legal-structure/",
        jurisdiction="Netherlands",
        domains=["business_formation"],
        keywords=[
            "legal structure",
            "business structure",
            "company",
            "software",
            "product",
            "cooperative",
            "bv",
            "vof",
            "startup",
            "компан",
            "кооператив",
            "программ",
            "продукт",
            "специалист",
            "производств",
            "производить",
            "manufactur",
            "produceren",
        ],
        summary=(
            "Business.gov.nl explains that a Dutch legal structure determines "
            "liability and tax obligations. For people starting together, possible "
            "forms include VOF, BV, professional partnership, and cooperative; "
            "agreements should be recorded in a cooperation agreement."
        ),
    ),
    LegalSource(
        id="businessgov-private-limited-bv",
        title="Business.gov.nl - Private limited company (BV) in the Netherlands",
        url="https://business.gov.nl/running-your-business/legal-forms-and-governance/private-limited-company-in-the-netherlands/",
        jurisdiction="Netherlands",
        domains=["business_formation"],
        keywords=[
            "bv",
            "private limited",
            "shares",
            "shareholder",
            "investor",
            "software",
            "product",
            "company",
            "компан",
            "инвест",
            "доля",
            "акци",
            "производств",
        ],
        summary=(
            "Business.gov.nl states that a BV is a legal entity that can be set "
            "up with partners and take on investors. Liability is generally with "
            "the BV rather than individuals; incorporation requires a civil-law "
            "notary and entails accounting and tax obligations."
        ),
    ),
    LegalSource(
        id="businessgov-cooperative",
        title="Business.gov.nl - Cooperative",
        url="https://business.gov.nl/running-your-business/legal-forms-and-governance/cooperative/",
        jurisdiction="Netherlands",
        domains=["business_formation"],
        keywords=[
            "cooperative",
            "cooperatie",
            "collective",
            "members",
            "member",
            "entrepreneurs",
            "кооператив",
            "участник",
            "член",
            "коллектив",
        ],
        summary=(
            "Business.gov.nl states that a cooperative can be created by 2 or "
            "more entrepreneurs working collectively. Members can join or leave "
            "without ending continuity; liability options including UA are set "
            "in the articles of association."
        ),
    ),
    LegalSource(
        id="eurlex-batteries-regulation-2023-1542",
        title="EUR-Lex - Regulation (EU) 2023/1542 on batteries and waste batteries",
        url="https://eur-lex.europa.eu/eli/reg/2023/1542/oj",
        jurisdiction="European Union / Netherlands",
        domains=["battery_manufacturing"],
        keywords=[
            "battery",
            "batteries",
            "energy storage",
            "accumulator",
            "industrial battery",
            "аккумулятор",
            "батаре",
            "накопител",
            "хранения электричества",
            "хранение энергии",
        ],
        summary=(
            "Regulation (EU) 2023/1542 applies to all battery categories, including "
            "industrial batteries used for energy storage. Manufacturers placing a "
            "battery on the market must meet applicable design, documentation, "
            "conformity assessment, labelling and CE marking duties."
        ),
    ),
    LegalSource(
        id="businessgov-battery-producer-responsibility",
        title="Business.gov.nl - Collecting batteries and accumulators",
        url="https://business.gov.nl/regulation/collecting-batteries-accumulators/",
        jurisdiction="Netherlands",
        domains=["battery_manufacturing"],
        keywords=[
            "battery",
            "batteries",
            "accumulator",
            "energy storage",
            "аккумулятор",
            "батаре",
            "накопител",
            "хранения электричества",
            "хранение энергии",
        ],
        summary=(
            "Business.gov.nl states that a producer or importer putting batteries "
            "or accumulators on the Dutch market is responsible for their waste "
            "management under extended producer responsibility (UPV)."
        ),
    ),
    LegalSource(
        id="businessgov-environment-harmful-activities-permit",
        title="Business.gov.nl - Permit for environmentally harmful activities",
        url="https://business.gov.nl/regulation/environment-planning-permit-harmful-activities/",
        jurisdiction="Netherlands",
        domains=["battery_manufacturing"],
        keywords=[
            "manufacturing",
            "factory",
            "production",
            "energy storage",
            "battery",
            "аккумулятор",
            "батаре",
            "производств",
            "накопител",
            "хранения электричества",
        ],
        summary=(
            "Business.gov.nl explains that activities with environmental impact "
            "may require an environment and planning permit, notification, or "
            "information duties, depending on the activity and location."
        ),
    ),
    LegalSource(
        id="rijksoverheid-social-housing-eligibility",
        title="Rijksoverheid - Kom ik in aanmerking voor een sociale huurwoning?",
        url=(
            "https://www.rijksoverheid.nl/onderwerpen/huurwoning-zoeken/"
            "vraag-en-antwoord/wanneer-kom-ik-in-aanmerking-voor-een-sociale-huurwoning"
        ),
        jurisdiction="Netherlands",
        domains=["social_housing"],
        keywords=[
            "social housing",
            "sociale huurwoning",
            "woningcorporatie",
            "социальное жилье",
            "социальной аренде",
            "социальную аренду",
            "аренда",
        ],
        summary=(
            "Rijksoverheid states that applicants for a social rental home from a "
            "housing corporation must register with a housing corporation and meet "
            "its requirements, including income and household-size conditions. In "
            "2026, housing corporations must allocate at least 85% of available "
            "social homes to single-person households earning up to EUR 51,537 and "
            "multi-person households earning up to EUR 56,910."
        ),
    ),
    LegalSource(
        id="rijksoverheid-social-housing-urgency",
        title="Rijksoverheid - Krijg ik een urgentieverklaring voor een sociale huurwoning?",
        url=(
            "https://www.rijksoverheid.nl/onderwerpen/huurwoning-zoeken/"
            "vraag-en-antwoord/wanneer-krijg-ik-een-urgentieverklaring-voor-een-huurwoning"
        ),
        jurisdiction="Netherlands",
        domains=["social_housing"],
        keywords=[
            "social housing",
            "sociale huurwoning",
            "urgentieverklaring",
            "urgent",
            "социальное жилье",
            "срочно",
            "приоритет",
        ],
        summary=(
            "Rijksoverheid states that priority for a social rental home may be "
            "available in certain circumstances through an urgency declaration "
            "requested from the municipality; municipal rules differ."
        ),
    ),
    LegalSource(
        id="rijksoverheid-on-call-contract-types",
        title="Rijksoverheid - Welke contracten zijn er voor oproepkrachten?",
        url=(
            "https://www.rijksoverheid.nl/vraag-en-antwoord/"
            "arbeidsovereenkomst-en-cao/welke-contracten-zijn-er-voor-oproepkrachten"
        ),
        jurisdiction="Netherlands",
        domains=["employment_contract"],
        keywords=[
            "nulurencontract",
            "nul uren contract",
            "zero-hours contract",
            "zero hours contract",
            "нулевой контракт",
            "нулевому контракту",
            "контракт без часов",
            "оплата по вызову",
        ],
        summary=(
            "Rijksoverheid explains that a zero-hours contract is a type of "
            "on-call employment contract: the employee works when called and no "
            "fixed number of hours is agreed. Rules include the on-call notice "
            "period and the offer of fixed hours after continued employment."
        ),
    ),
    LegalSource(
        id="rijksoverheid-zero-hours-holiday-pay",
        title="Rijksoverheid - Nulurencontract, vakantiedagen en vakantiegeld",
        url=(
            "https://www.rijksoverheid.nl/onderwerpen/arbeidsovereenkomst-en-cao/"
            "vraag-en-antwoord/nulurencontract-en-vakantiedagen-en-vakantiegeld"
        ),
        jurisdiction="Netherlands",
        domains=["employment_contract"],
        keywords=[
            "nulurencontract",
            "zero-hours contract",
            "zero hours contract",
            "нулевой контракт",
            "контракт без часов",
        ],
        summary=(
            "Rijksoverheid states that employees with a zero-hours contract are "
            "entitled to holiday hours and at least 8% holiday allowance over "
            "their gross pay."
        ),
    ),
    LegalSource(
        id="businessgov-zero-hours-contract",
        title="Business.gov.nl - Hiring on-call employees with a zero-hours contract",
        url=(
            "https://business.gov.nl/staff/employing-staff/"
            "hiring-on-call-employees-with-a-zero-hours-contract/"
        ),
        jurisdiction="Netherlands",
        domains=["employment_contract"],
        keywords=[
            "nulurencontract",
            "zero-hours contract",
            "zero hours contract",
            "нулевой контракт",
            "контракт без часов",
        ],
        summary=(
            "Business.gov.nl summarises Dutch zero-hours rules: advance notice "
            "for calls, payment in certain cases for at least 3 hours, an offer "
            "of fixed hours after 12 months, and the announced change that "
            "zero-hours contracts are expected to be disallowed from 1 January 2027."
        ),
    ),
]

DOMAIN_SOURCE_GROUPS: dict[str, set[str]] = {
    "liability": {"liability", "traffic", "insurance", "accident_procedure"},
    "immigration": {"immigration"},
    "employment": {"employment"},
    "tax": {"tax"},
    "contracts": {"contracts"},
    "business_formation": {"business_formation"},
    "battery_manufacturing": {"battery_manufacturing"},
    "social_housing": {"social_housing"},
    "employment_contract": {"employment_contract"},
    "zzp_intermediary_contract": {"zzp_intermediary_contract"},
    "residential_parking": {"residential_parking"},
    "consulting_services": {"consulting_services", "business_formation"},
}


def retrieve_sources(
    text: str,
    domain: str,
    limit: int = 4,
    require_keyword_match: bool = False,
) -> list[LegalSource]:
    value = text.casefold()
    allowed_domains = DOMAIN_SOURCE_GROUPS.get(domain, {domain})
    scored: list[tuple[int, LegalSource]] = []
    for source in SOURCES:
        if not allowed_domains.intersection(source.domains):
            continue
        keyword_hits = sum(1 for keyword in source.keywords if keyword.casefold() in value)
        if require_keyword_match and not keyword_hits:
            continue
        scored.append((3 + keyword_hits, source))
    return [source for _, source in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]

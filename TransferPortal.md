import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Checkbox,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Link,
  Pill,
  Row,
  Select,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";

type Assoc = "d1" | "d2" | "d3" | "naia" | "other";
type Level = "undergrad" | "grad";

const ASSOC_OPTIONS = [
  { value: "d1", label: "NCAA Division I" },
  { value: "d2", label: "NCAA Division II" },
  { value: "d3", label: "NCAA Division III" },
  { value: "naia", label: "NAIA" },
  { value: "other", label: "Other 4-year (USCAA, NCCAA, etc.)" },
];

const ASSOC_SHORT: Record<Assoc, string> = {
  d1: "NCAA DI",
  d2: "NCAA DII",
  d3: "NCAA DIII",
  naia: "NAIA",
  other: "Other 4-yr",
};

type CellKind = "immediate" | "gated" | "conference" | "assoc";

const MATRIX: Record<
  Assoc,
  Record<Assoc, { kind: CellKind; cell: string }>
> = {
  d1: {
    d1: { kind: "gated", cell: "DI academic gate + dest PTD" },
    d2: { kind: "gated", cell: "DII academic prongs + 9/8 hrs" },
    d3: { kind: "gated", cell: "Eligible at previous, or first-term sit" },
    naia: { kind: "conference", cell: "Immediate nationally; conference residency possible" },
    other: { kind: "assoc", cell: "Destination association / school rules" },
  },
  d2: {
    d1: { kind: "gated", cell: "DI academic gate + dest PTD" },
    d2: { kind: "gated", cell: "DII academic prongs + 9/8 hrs" },
    d3: { kind: "gated", cell: "Eligible at previous, or first-term sit" },
    naia: { kind: "conference", cell: "Immediate nationally; conference residency possible" },
    other: { kind: "assoc", cell: "Destination association / school rules" },
  },
  d3: {
    d1: { kind: "gated", cell: "DI academic gate + dest PTD" },
    d2: { kind: "gated", cell: "DII academic prongs + 9/8 hrs" },
    d3: { kind: "gated", cell: "Eligible at previous, or first-term sit" },
    naia: { kind: "conference", cell: "Immediate nationally; conference residency possible" },
    other: { kind: "assoc", cell: "Destination association / school rules" },
  },
  naia: {
    d1: { kind: "gated", cell: "DI academic gate + dest PTD" },
    d2: { kind: "gated", cell: "DII academic prongs + 9/8 hrs" },
    d3: { kind: "gated", cell: "Eligible at previous, or first-term sit" },
    naia: { kind: "conference", cell: "Immediate nationally; conference residency possible" },
    other: { kind: "assoc", cell: "Destination association / school rules" },
  },
  other: {
    d1: { kind: "gated", cell: "DI academic gate + dest PTD" },
    d2: { kind: "gated", cell: "DII academic prongs + 9/8 hrs" },
    d3: { kind: "gated", cell: "Eligible at previous, or first-term sit" },
    naia: { kind: "conference", cell: "Immediate nationally; conference residency possible" },
    other: { kind: "assoc", cell: "Destination association / school rules" },
  },
};

function matrixTone(kind: CellKind): "success" | "warning" | "info" | "neutral" {
  if (kind === "immediate") return "success";
  if (kind === "gated") return "warning";
  if (kind === "conference") return "info";
  return "neutral";
}

type Verdict = {
  tone: "success" | "warning" | "danger" | "info";
  title: string;
  body: string;
  remaining: string[];
};

function verdict(args: {
  from: Assoc;
  to: Assoc;
  level: Level;
  academicallyEligible: boolean;
  goodStanding: boolean;
  neverCompeted: boolean;
  midyearSameSeason: boolean;
}): Verdict {
  const remaining: string[] = [
    "Be admitted and enrolled full-time at the destination in a degree program",
    "Have remaining seasons / clock (DI/DII: 5 years to play 4; DIII/NAIA: 10-semester / 4-season style clocks)",
  ];

  if (args.midyearSameSeason) {
    return {
      tone: "danger",
      title: "Cannot compete in the same championship segment at two schools",
      body: "Even when transfer legislation allows immediate eligibility, NCAA Division I (and typical DII practice) bars competing for more than one school in the same championship season. Practice and aid may still be available.",
      remaining: [
        "Wait until the next championship segment at the new school",
        ...remaining,
      ],
    };
  }

  if (args.to === "d1") {
    remaining.push(
      "Complete the NCAA transfer-education module",
      "Provide written notification of transfer during the sport-specific portal window (limited exceptions: coach departure, sport dropped)",
      "Meet all Division I progress-toward-degree rules at the NEW school before competing (6-hour prior term, 18-hour academic year, GPA floors, and % of degree once triggered)",
    );
    if (args.level === "grad") {
      remaining.push(
        "Enroll full-time in a graduate or professional program (or a second baccalaureate) at the new school",
      );
    }
    if (!args.goodStanding) {
      return {
        tone: "danger",
        title: "Not immediately eligible at Division I",
        body: "Proposal 2024-5 requires the student-athlete to leave the previous four-year school in good standing (not subject to disciplinary suspension or dismissal). Origin association (DI, DII, DIII, NAIA) does not change this destination rule.",
        remaining,
      };
    }
    if (!args.academicallyEligible && !args.neverCompeted) {
      return {
        tone: "warning",
        title: "Not immediately eligible until the new school can certify academics",
        body: "A four-year undergraduate (or graduate) transfer to Division I must have left the previous school academically eligible, excluding percentage-of-degree. Percentage-of-degree is certified at the destination. If the previous school would have declared the student academically ineligible, the new school cannot certify competition until applicable PTD is met there.",
        remaining,
      };
    }
    return {
      tone: "success",
      title: "Immediate competition is available at Division I",
      body: "Under Proposal 2024-5 (April 2024), the default year-in-residence for four-year transfers is gone. Unlimited four-year transfers are allowed if the academic/good-standing test is met. The previous one-time transfer exception is no longer the pathway.",
      remaining,
    };
  }

  if (args.to === "d2") {
    remaining.push(
      "Satisfy Division II Bylaw 14.2.9.3.2.1 / last-full-time-term credit hours (typically 9 semester or 8 quarter hours)",
      "Enter the Transfer Portal after the education module (the old June 15 one-time-transfer deadline was eliminated after EM-2025-1)",
    );
    const prongA = args.neverCompeted && args.academicallyEligible;
    const prongB = args.academicallyEligible && args.goodStanding;
    if (prongA || prongB) {
      return {
        tone: "success",
        title: "Immediate competition is available at Division II",
        body: "EM-2025-1 replaced year-in-residence plus old exceptions (including the one-time transfer exception). Immediate eligibility requires (a) no practice/competition at the previous school, or that school did not sponsor the sport, and good academic standing, or (b) the student would have been academically and athletically eligible had they remained.",
        remaining,
      };
    }
    return {
      tone: "warning",
      title: "Ineligible during the first full-time term at Division II",
      body: "If neither academic prong is met, the student may not compete in the first full-time term at the certifying school. Eligibility can be regained the following regular term by meeting good academic standing plus the term-by-term (and, for midyear enrollees, annual credit and GPA) PTD rules.",
      remaining,
    };
  }

  if (args.to === "d3") {
    remaining.push(
      "Meet the new school's institutional academic standards",
      "For recruiting contact: Division III still uses a permission-to-contact / self-release model (not the Division I portal windows)",
    );
    if (
      args.neverCompeted ||
      args.academicallyEligible
    ) {
      return {
        tone: "success",
        title: "Immediate competition is available at Division III",
        body: "A four-year transfer is eligible in the first regular term if they never practiced or competed, would have been academically eligible had they remained, or meet the two-year nonparticipation condition. Additional conference or institutional rules can still apply.",
        remaining,
      };
    }
    return {
      tone: "warning",
      title: "Ineligible during the first regular term at Division III",
      body: "EM-2025-1 (2025 Convention) replaced a full academic year in residence for students who transfer while academically ineligible. Those students sit the first regular full-time term, then may be recertified if they meet the new school's academic requirements. A legislative-relief waiver remains possible.",
      remaining,
    };
  }

  if (args.to === "naia") {
    remaining.push(
      "File the NAIA Transfer Player Eligibility Statement before first competition",
      "Appear on the destination eligibility certificate for the term",
      "Check the destination conference handbook for a local residency rule",
    );
    if (!args.goodStanding) {
      return {
        tone: "warning",
        title: "Residency may still apply after suspension or dismissal",
        body: "NAIA removed the national 16-week four-year residency (effective for competition from August 2023). Residency can still attach after disciplinary suspension/dismissal, and a conference may impose its own sit-out.",
        remaining,
      };
    }
    return {
      tone: "success",
      title: "Immediate competition is the national NAIA default",
      body: `Origin was ${ASSOC_SHORT[args.from]}. National NAIA legislation no longer requires a 16-week sit-out for four-year transfers. Conference residency, identification dates, and the 20% season-of-competition threshold still matter for midyear movers.`,
      remaining,
    };
  }

  return {
    tone: "info",
    title: "Destination association sets the athletic rule",
    body: "USCAA, NCCAA, and unaffiliated four-year programs are not bound by NCAA four-year transfer bylaws. Competition eligibility is institutional (and sometimes association-specific). Academic credit transfer is still a registrar/articulation problem at every destination.",
    remaining: [
      "Ask the destination athletics director for association eligibility",
      "Have the registrar run a credit-evaluation / degree audit",
    ],
  };
}

export default function FourYearTransferMatrix() {
  const theme = useHostTheme();
  const [from, setFrom] = useCanvasState<Assoc>("from", "d1");
  const [to, setTo] = useCanvasState<Assoc>("to", "d1");
  const [level, setLevel] = useCanvasState<Level>("level", "undergrad");
  const [academicallyEligible, setAcademicallyEligible] = useCanvasState(
    "academicallyEligible",
    true,
  );
  const [goodStanding, setGoodStanding] = useCanvasState("goodStanding", true);
  const [neverCompeted, setNeverCompeted] = useCanvasState(
    "neverCompeted",
    false,
  );
  const [midyearSameSeason, setMidyearSameSeason] = useCanvasState(
    "midyearSameSeason",
    false,
  );

  const result = verdict({
    from,
    to,
    level,
    academicallyEligible,
    goodStanding,
    neverCompeted,
    midyearSameSeason,
  });

  const matrixRows = (["d1", "d2", "d3", "naia", "other"] as Assoc[]).map(
    (origin) => {
      const cells: Array<string | ReturnType<typeof Text>> = [
        ASSOC_SHORT[origin],
      ];
      for (const dest of ["d1", "d2", "d3", "naia", "other"] as Assoc[]) {
        const hit = origin === from && dest === to;
        const label = MATRIX[origin][dest].cell;
        cells.push(
          hit ? (
            <Text as="span" weight="semibold">
              {label}
            </Text>
          ) : (
            label
          ),
        );
      }
      return cells;
    },
  );

  const matrixRowTone = (["d1", "d2", "d3", "naia", "other"] as Assoc[]).map(
    (origin) => matrixTone(MATRIX[origin][to].kind),
  );

  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Four-year to four-year transfer requirements</H1>
        <Text tone="secondary">
          Athletic eligibility for undergraduate and graduate movers between
          four-year colleges, as of the 2025–26 / 2026 NCAA and NAIA manuals.
          Pairwise school matrices are not how the bylaws work: the destination
          association writes the competition test; the origin school only
          supplies academic standing, eligibility, and (for recruiting) portal
          or release mechanics.
        </Text>
        <Text size="small" tone="tertiary">
          Sources: NCAA DI Proposal 2024-5 / Four-Year Undergraduate Transfer
          Basics (spring 2024); DII EM-2025-1 Transfer Q&amp;A and 2026–27
          Summary of NCAA Regulations; DIII EM-2025-1 (Feb 19, 2025) and
          2025–26 Summary of NCAA Regulations; NAIA Article V transfer
          residency repeal (May 1, 2023). Not official certifications — campus
          compliance decides individual cases.
        </Text>
      </Stack>

      <Callout tone="info" title="API keys needed for this matrix: none">
        NCAA transfer legislation is published as PDFs and LSDBi bylaws, not as
        an eligibility API. A School A → School B cell is computed from
        destination division plus the student’s academic/disciplinary facts.
        Keys are only required if you later attach a named-school directory,
        portal roster, or course-equivalency engine — see the access table
        below.
      </Callout>

      <Row gap={24} wrap>
        <Stat value="0" label="API keys for the rules layer" />
        <Stat value="~2,000" label="U.S. Title IV 4-year colleges" />
        <Stat value="5" label="Rule families in the matrix" tone="info" />
      </Row>

      <H2>Look up a path</H2>
      <Text tone="secondary">
        Choose origin and destination association, then the facts a compliance
        officer would ask. The highlighted row in the matrix matches this path.
      </Text>
      <Grid columns={2} gap={12}>
        <Stack gap={6}>
          <Text size="small" tone="tertiary">
            From (current 4-year)
          </Text>
          <Select
            value={from}
            onChange={(v) => setFrom(v as Assoc)}
            options={ASSOC_OPTIONS}
          />
        </Stack>
        <Stack gap={6}>
          <Text size="small" tone="tertiary">
            To (certifying 4-year)
          </Text>
          <Select
            value={to}
            onChange={(v) => setTo(v as Assoc)}
            options={ASSOC_OPTIONS}
          />
        </Stack>
        <Stack gap={6}>
          <Text size="small" tone="tertiary">
            Degree level after transfer
          </Text>
          <Select
            value={level}
            onChange={(v) => setLevel(v as Level)}
            options={[
              { value: "undergrad", label: "Undergraduate" },
              { value: "grad", label: "Graduate / second baccalaureate" },
            ]}
          />
        </Stack>
      </Grid>
      <Stack gap={8}>
        <Checkbox
          checked={academicallyEligible}
          onChange={setAcademicallyEligible}
          label="Would have been academically eligible if remaining at the previous school (DI: exclude % of degree)"
        />
        <Checkbox
          checked={goodStanding}
          onChange={setGoodStanding}
          label="Left in good standing (not disciplinary suspension or dismissal)"
        />
        <Checkbox
          checked={neverCompeted}
          onChange={setNeverCompeted}
          label="Never practiced or competed in intercollegiate athletics at the previous school (or that school did not sponsor the sport)"
        />
        <Checkbox
          checked={midyearSameSeason}
          onChange={setMidyearSameSeason}
          label="Already competed in this championship segment and would compete again this season"
        />
      </Stack>

      <Callout tone={result.tone} title={result.title}>
        {result.body}
      </Callout>
      <Stack gap={6}>
        <H3>Still required on this path</H3>
        <Table
          headers={["Requirement"]}
          rows={result.remaining.map((r) => [r])}
          striped
        />
      </Stack>

      <H2>Association matrix (competition eligibility)</H2>
      <Text tone="secondary">
        Rows are the previous four-year association; columns are the
        destination. Cell text is the destination’s four-year transfer test —
        origin association almost never changes the competition standard, which
        is why every row in a column matches. Process (portal vs self-release)
        still differs.
      </Text>
      <Row gap={8} wrap>
        <Pill>Warning dot: academic gate at destination</Pill>
        <Pill>Info dot: NAIA conference overlay</Pill>
        <Pill>Neutral: non-NCAA / non-NAIA destination</Pill>
      </Row>
      <Table
        headers={[
          "From \\ To",
          "NCAA DI",
          "NCAA DII",
          "NCAA DIII",
          "NAIA",
          "Other 4-yr",
        ]}
        rows={matrixRows}
        rowTone={matrixRowTone}
        striped
        stickyHeader
      />

      <H2>Destination rulebooks</H2>
      <CollapsibleSection title="NCAA Division I (Proposal 2024-5)" defaultOpen>
        <Stack gap={8}>
          <Text>
            Immediate eligibility if the student left academically eligible
            (percentage-of-degree carved out), was in good standing, and meets
            all progress-toward-degree rules at the new school before competing.
            Default year-in-residence is eliminated; multiple transfers are
            allowed.
          </Text>
          <Table
            headers={["DI progress-toward-degree item", "Typical trigger"]}
            rows={[
              [
                "6 credit hours",
                "Earned in the previous regular full-time term",
              ],
              ["18 credit hours", "Academic year (fall+spring)"],
              [
                "24 credit hours",
                "First year of collegiate enrollment (annual)",
              ],
              [
                "GPA floors",
                "90% of graduation GPA after year 1; 95% after year 2; 100% after year 3",
              ],
              [
                "% of degree",
                "40% entering year 3, 60% year 4, 80% year 5 — certified at the NEW school for transfers",
              ],
              [
                "Portal",
                "Sport-specific windows only, plus coach-departure / sport-dropped exceptions",
              ],
            ]}
            striped
          />
        </Stack>
      </CollapsibleSection>
      <CollapsibleSection title="NCAA Division II (EM-2025-1)">
        <Text>
          Immediate if (a) no practice/competition at the previous school or
          the sport was not sponsored, and good academic standing, or (b) would
          have been academically and athletically eligible had they remained —
          plus last-term credit hours (9 semester / 8 quarter). Otherwise sit
          the first full-time term and recertify on PTD. Old four-year
          exceptions (one-time transfer, two-year nonparticipation as the
          transfer vehicle) were removed.
        </Text>
      </CollapsibleSection>
      <CollapsibleSection title="NCAA Division III (EM-2025-1, 2025–26)">
        <Text>
          Immediate if never a participant, would have been academically
          eligible at the previous school, or two-year nonparticipation. If not,
          ineligible the first regular full-time term, then recertify against
          the new school’s academics. A full academic year in residence is no
          longer the default for ineligible arrivals. Recruiting contact still
          runs through Division III permission-to-contact / self-release, not
          DI portal windows.
        </Text>
      </CollapsibleSection>
      <CollapsibleSection title="NAIA (Article V, May 2023)">
        <Text>
          National 16-week residency for four-year transfers is gone.
          Conferences may still require residency. Suspension/dismissal can
          still trigger a sit-out. Every transfer must file the Transfer Player
          Eligibility Statement before competing.
        </Text>
      </CollapsibleSection>

      <H2>What this matrix does not certify</H2>
      <Grid columns={2} gap={12}>
        <Card>
          <CardHeader>Academic credit articulation</CardHeader>
          <CardBody>
            <Text>
              Whether HIST 201 from School A equals HIST 210 at School B is
              registrar / TES / Transferology data, not NCAA legislation. There
              is no public national course-equivalency API covering every
              four-year pair.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Aid, NIL, and conferences</CardHeader>
          <CardBody>
            <Text>
              Notification of transfer can allow a DI school to cancel
              athletically related aid for the next term. Conference handbooks
              and House-settlement roster rules are overlays. Same-season
              competition remains blocked even when the transfer test is met.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      <H2>Which API keys are needed</H2>
      <Text tone="secondary">
        Use keys only for the layer you actually build. The rules matrix above
        is complete without any of them.
      </Text>
      <Table
        headers={["Layer", "Product", "Key?", "What it actually returns"]}
        rows={[
          [
            "Eligibility rules",
            "NCAA LSDBi / ncaa.org PDFs",
            "No",
            "Bylaws and Q&As. There is no public “is this transfer eligible?” endpoint.",
          ],
          [
            "Named 4-year college list",
            "College Scorecard (api.data.gov)",
            "Yes — free data.gov key",
            "IPEDS institutions, 4-year vs 2-year, state, size. Does not include NCAA division.",
          ],
          [
            "NCAA division / conference",
            "No official NCAA membership API",
            "No public key",
            "Use the NCAA member directory, sports-reference dumps, or a licensed feed. Division is not in Scorecard.",
          ],
          [
            "Football school graph (optional)",
            "CollegeFootballData.com",
            "Yes — free CFBD key",
            "FBS/FCS teams, conferences, some player transfer lists. Not a rules engine; not all sports.",
          ],
          [
            "Who is in the portal",
            "Sportradar NCAAFB / NCAAMB Transfer Portal",
            "Yes — commercial x-api-key",
            "Players currently in the portal. Not eligibility certification.",
          ],
          [
            "Course equivalencies",
            "CollegeSource Transferology / TES",
            "Yes — institutional key",
            "Credit-by-credit matches for member schools only. Not athletic eligibility.",
          ],
          [
            "National enrollment verification",
            "National Student Clearinghouse",
            "Yes — commercial",
            "Attendance dates, degrees. Not NCAA transfer windows or PTD.",
          ],
        ]}
        striped
        stickyHeader
      />
      <Text size="small" tone="tertiary">
        Scorecard signup:{" "}
        <Link href="https://collegescorecard.ed.gov/data/api/">
          collegescorecard.ed.gov/data/api
        </Link>
        . NCAA transfer hub:{" "}
        <Link href="https://www.ncaa.org/eligibility-center/transfer-rules-and-eligibility/">
          ncaa.org transfer rules
        </Link>
        .
      </Text>

      <Divider />
      <Text size="small" tone="tertiary">
        Highlight uses{" "}
        <Text as="span" weight="semibold" style={{ color: theme.accent.primary }}>
          {ASSOC_SHORT[from]} → {ASSOC_SHORT[to]}
        </Text>
        . Rebuild the named-school layer later with a Scorecard key plus a
        division crosswalk; do not expect any vendor to sell a complete A×B
        requirements matrix, because the legislation is not written that way.
      </Text>
    </Stack>
  );
}

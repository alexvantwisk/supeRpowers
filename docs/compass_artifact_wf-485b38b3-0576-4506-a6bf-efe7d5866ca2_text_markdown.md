# Evidence-Based Structure for Biostatistical Consulting Reports

A high-quality biostatistical consulting report template should incorporate 12-15 core sections that balance scientific rigor with accessibility, grounded in formal reporting guidelines, professional standards, and reproducibility frameworks. The ideal structure differs meaningfully between standalone industry analysis deliverables and academic methodology consulting reports, but both must prioritize transparency, prespecification documentation, and honest communication of uncertainty. This synthesis draws from peer-reviewed literature, professional society guidelines (ASA, ISCB, RSS, PSI), reporting frameworks (CONSORT, STROBE, ICH E9/E9(R1)), reproducibility standards (TIER Protocol, NASEM, AMSTAT), consulting books (Derr, Cabrera & McDougall, Boen & Zahn), and practices from major academic biostatistics centers.

## Core sections for all biostatistical consulting reports

The evidence converges on a structure that separates administrative documentation, scientific methods, results, and reproducibility elements. Each section serves specific evidentiary and ethical purposes.

### Front matter and administrative information

**What it should contain:** Report title with version number and date, consultant credentials and affiliations, client information, date of analysis, version history table documenting all revisions with justification, and signatures where appropriate. For regulated work or formal engagements, include conflict of interest disclosures and data use agreements.

**Evidence and rationale:** The JAMA Statistical Analysis Plan guidelines specify 11 administrative items including version control with dates, protocol version reference, revision history with justifications, and roles/responsibilities with signatures. This documentation creates an audit trail essential for reproducibility and protects both consultant and client. The ASA Ethical Guidelines emphasize taking responsibility for one's work, giving credit appropriately, and disclosing conflicts of interest. Academic centers including Duke BERD and Johns Hopkins ICTR document that clear role definition prevents disputes over authorship and credit.

**Consulting context considerations:** Unlike regulatory submissions where these elements are mandatory with strict formatting, consulting reports have flexibility. However, Boen & Zahn emphasize that negotiating responsibilities between consultant and client upfront prevents conflicts. Document who performed what analyses, who made key decisions, and consultant recommendations versus client-directed analyses. This protects statistical integrity when clients override methodological advice.

### Executive summary

**What it should contain:** A standalone 1-2 page synthesis providing bottom-line findings, key effect estimates with uncertainty measures, main conclusions, critical limitations, and primary recommendations. Must be comprehensible to non-statistical audiences including executives who may read nothing else.

**Evidence and rationale:** Derr's research on statistical consulting identifies five dimensions clients use to evaluate quality, notably none directly incorporate technical correctness because non-statisticians cannot assess it. Communication quality becomes paramount. Academic centers document that executives often read only executive summaries. Cabrera & McDougall emphasize tailoring complexity to audience. The executive summary serves readers who need decision-ready information without methodological detail.

**Consulting context considerations:** Industry clients particularly value concise executive summaries for stakeholder communication. Academic collaborators may skip this section as they typically read full reports, but it remains valuable for grant applications and manuscript preparation. Follow the BLUF principle: state most important finding first, then significance and context.

### Background, context, and scope of engagement

**What it should contain:** Scientific background and rationale for the study or analysis, specific research questions or hypotheses being addressed, objectives of the consulting engagement, scope boundaries defining what is and is not covered, and how this work fits into the broader research program. For intervention studies, articulate the clinical or policy question motivating analysis.

**Evidence and rationale:** CONSORT and STROBE both require scientific background and rationale as foundational sections. The ICH E9(R1) estimands framework emphasizes that clear articulation of the research question precedes all methodological decisions. Chatfield's problem-solving framework treats formulating the problem as the first critical stage of statistical investigation, noting that consultants must take a broad view of the consultee's problem. Boen & Zahn stress understanding the client's organizational context, audience, and constraints.

**Consulting context considerations:** This section establishes boundaries. Recent literature on statistical consulting scope of work emphasizes defining deliverables clearly upfront and empowering statisticians to decline scope creep. Document if initial consultation revealed the research question differs from what client initially articulated. Academic reports may include more pedagogical explanation; industry reports emphasize business objectives.

### Estimand or estimation target framework

**What it should contain:** For intervention studies or causal questions, explicitly define the estimand using ICH E9(R1) five-attribute framework: population of interest, intervention/exposure strategies being compared, endpoint (variable for each participant), population-level summary measure (e.g., mean difference, risk ratio), and approach to intercurrent events (treatment policy, composite, hypothetical, while-on-treatment, or principal stratum strategy). For non-interventional work, clearly specify the estimation target.

**Evidence and rationale:** ICH E9(R1) provides rigorous framework for precision in defining treatment effects, directly applicable beyond regulatory contexts. The estimand framework eliminates ambiguity about what scientific question is being answered and aligns methods with objectives. This matters profoundly in consulting because Boen & Zahn and Derr both emphasize that clients and consultants may have different implicit understandings of the question. Making the target of inference explicit prevents misunderstandings.

**Consulting context considerations:** While developed for regulatory trials, the estimand framework applies broadly. For observational studies, clearly state the causal contrast of interest versus purely descriptive association. For prediction modeling, specify whether goal is explanation, prediction, or both and what population predictions apply to. TRIPOD guidelines for prediction models require this clarity. This section may be brief or omitted for purely descriptive analyses with no inferential intent, but most consulting work benefits from explicit target specification.

### Data sources, provenance, and integrity

**What it should contain:** Complete documentation of data sources with URLs/DOIs or access information, dates obtained, who collected data and how, data use agreements or restrictions, eligibility criteria and sampling methods, data completeness assessment with amounts and patterns of missing data by variable and group, any data quality issues identified, inclusion/exclusion decisions with counts and reasons, and final analysis sample characteristics.

**Evidence and rationale:** The TIER Protocol defines data provenance documentation as essential for reproducibility, requiring complete chain of custody from original source through all processing. NASEM reproducibility guidelines emphasize documenting data fitness for use. CONSORT requires participant flow with CONSORT diagram showing all stages from enrollment through analysis with reasons for exclusions. STROBE emphasizes transparent reporting of eligibility, selection, and how missing data were addressed. McIntosh et al.'s RepeAT framework includes 119 variables across five categories, with data provenance central.

**Consulting context considerations:** When using client-provided data, document who is responsible for data quality. ASA Ethical Guidelines specify consultants should communicate data sources and fitness for use but recognize different responsibilities for data collection versus analysis. If data quality issues exist, document them honestly with assessment of potential impact. Goodman, Fanelli, and Ioannidis distinguish methods reproducibility from results reproducibility; data quality affects both.

### Statistical methods

**What it should contain:** This core technical section should provide sufficient detail for replication. Specify all statistical methods used with citations for non-standard approaches, software and version information, assumptions underlying methods with how they were assessed, handling of missing data including mechanism assumptions and imputation approach if used, multiplicity considerations and any adjustments applied, all planned analyses (primary, secondary, sensitivity, subgroup), and explicit distinction between prespecified and exploratory analyses.

**Evidence and rationale:** The JAMA SAP guidelines require 17 items for analysis including specific methods, presentation of effects, covariate adjustments, assumption checking, alternative methods if assumptions violated, sensitivity analyses, subgroup analyses with definitions, missing data handling, and software used. SAMPL guidelines emphasize clear description of test purposes, adequate reporting of effect sizes, and assumption analysis. The ASA Statement on P-Values declares that valid inference requires knowing which analyses were conducted and being transparent about flexibility in design and analysis.

**Consulting context considerations:** Methods sections in consulting reports must balance two audiences: statistical reviewers who need replication detail and non-statistical readers who need conceptual understanding. Consider a layered approach with conceptual description in main text and technical details in appendix. Frank Harrell emphasizes that methods preserving information (avoiding dichotomization, using ordinal outcomes) and quantifying predictive accuracy matter more than complex modeling. Always document software with version because implementations differ.

### Detailed subsection: Prespecification versus post-hoc analyses

**What it should contain:** Clearly label which analyses were specified before data examination versus data-driven. For modified or additional analyses, document when the decision was made, the rationale, and whether it was in response to observed data patterns. Create explicit sections or use clear language: "Prespecified analyses," "Protocol-specified analyses," "Exploratory analyses," "Post-hoc analyses suggested by data."

**Evidence and rationale:** The prevention of HARKing (Hypothesizing After Results are Known) and p-hacking requires transparent reporting. Simmons, Nelson, and Simonsohn demonstrated that flexibility in data collection, analysis, and reporting dramatically increases false positive rates, with researchers more likely to falsely find effects than correctly identify their absence. Their concrete requirements include that authors must list all variables collected, report all experimental conditions, and report results with and without covariates. Ioannidis's framework shows findings are less likely to be true when greater flexibility exists in designs, definitions, outcomes, and analytical modes. NEJM and JAMA guidelines require separation of prespecified from post-hoc analyses.

**Consulting context considerations:** Many consulting engagements lack formal preregistration, but good practice involves documenting analysis plans before data examination. Chatfield and other consulting experts emphasize that exploratory analysis is legitimate and valuable but must be labeled as such. Post-hoc analyses can be hypothesis-generating for future work. The ethical issue is not conducting them but presenting them as if they were planned a priori, which inflates apparent evidence strength.

### Detailed subsection: Multiplicity

**What it should contain:** Assessment of multiplicity issues using PICOTA framework (Population subgroups, Intervention comparisons, Outcomes, Timepoints, Analyses). Document which comparisons are primary/confirmatory versus exploratory. Specify adjustment methods used (Bonferroni, Holm, Hochberg, hierarchical testing, graphical methods) with rationale, or explicitly state why adjustment was not performed.

**Evidence and rationale:** Li et al. documented that substantial proportions of trial reports do not adequately correct for multiple testing. Reviews show only 28-46% of trials with multiplicity issues perform adjustments. However, the guidance is nuanced: adjust for multiple primary outcomes and related treatment comparisons in confirmatory settings, but secondary outcomes are typically exploratory and adjustment may not be needed. NEJM guidance specifies that prespecified subgroups need multiplicity consideration only if they have confirmatory nature with biological plausibility and prior evidence. The key is transparency about what was confirmatory versus exploratory.

**Consulting context considerations:** Academic and industry work differs here. Regulatory trials have clear primary/secondary designations requiring adjustment. Consulting work may be entirely exploratory, in which case acknowledge this openly and avoid claiming definitive findings. When multiple comparisons span a single scientific conclusion, adjustment protects against false positives. When addressing distinct research questions, adjustment may be unnecessary but should be explicitly discussed.

### Detailed subsection: Missing data handling

**What it should contain:** Amount and pattern of missing data (by variable, treatment group, timepoint), reasons for missingness with assessment of relationship to outcomes, assumption about missing data mechanism (MCAR, MAR, MNAR) with justification, primary method for handling (complete case, multiple imputation, likelihood-based methods) with implementation details including number of imputations and imputation model specification, sensitivity analyses examining robustness to different mechanisms, and number of imputed values clearly reported.

**Evidence and rationale:** ICH E9(R1) explicitly requires identifying how intercurrent events including dropout affect the estimand and prespecifying statistical handling with sensitivity analyses for MNAR assumptions. Reviews show 41-57% of RCTs use imputation but only 5-14% report number of imputed values in CONSORT diagrams. The TARMOS framework for observational studies emphasizes systematic thinking about missing data and transparent reporting of potential effects. Simply using methods that "handle" missing data (like multiple imputation) without documenting assumptions or performing sensitivity analyses is insufficient.

**Consulting context considerations:** Missing data is nearly universal in real-world consulting projects. Honest acknowledgment with sensitivity analyses demonstrates rigor. Academic collaborators may need education about why this matters; industry clients familiar with regulatory standards expect thorough missing data documentation. When data are client-provided, discuss missing data prevention strategies for future work.

### Detailed subsection: Software, version, and reproducibility documentation

**What it should contain:** Programming language and version, all packages/libraries with versions (use sessionInfo() in R, requirements.txt in Python, or environment management tools like renv/conda), operating system, key hardware specifications if relevant, random seeds for any stochastic methods, date of analysis, and location of archived code.

**Evidence and rationale:** The AMSTAT reproducibility initiative found code review identified issues in approximately 50% of submissions, with common problems including missing dependencies, hard-coded paths, and insufficient documentation. The TIER Protocol requires that scripts run on any computer with appropriate software using relative file paths. Ziemann, Poulain, and Bora's five pillars of computational reproducibility emphasize compute environment control as critical. NASEM guidelines specify recording software versions for all tools as essential for reproducibility.

**Consulting context considerations:** Industrial clients increasingly expect reproducible analyses especially for regulatory submissions. Academic collaborators may be less familiar with these standards but benefit from them when responding to manuscript reviewers. Documentation enables you or others to revisit analyses months or years later. Random seed documentation is critical for bootstrap, permutation tests, machine learning, and simulation but often overlooked.

### Results

**What it should contain:** Organized by research question or hypothesis, present findings with both point estimates and measures of uncertainty (confidence or credible intervals), report both relative and absolute effects for comparative studies, include precision indicators (standard errors, interval width), provide exact p-values rather than simply p<0.05 when hypothesis tests are used, present results for ALL prespecified outcomes (not just significant ones), clearly distinguish primary from secondary from exploratory results, use tables for precise values and figures for patterns/trends, and ensure every table and figure is referenced in text with interpretation.

**Evidence and rationale:** JAMA requires confidence intervals for all primary outcomes; NEJM replaces p-values with effect estimates and CIs for secondary outcomes without multiplicity adjustment. The ASA Statement on P-Values declares that p-values alone are insufficient, scientific conclusions should not be based solely on threshold crossing, proper inference requires full reporting and transparency, and p-values do not measure effect size or importance. Medical journal guidelines from The Lancet, BMJ, and JAMA converge on requiring both relative and absolute measures, reporting all prespecified outcomes, and assessing uncertainty. Harrell advocates for almost entirely graphical reports using interactive graphics with hover text replacing traditional tables.

**Consulting context considerations:** Tailor the balance of tables versus figures to audience. Academic manuscripts typically require tables for precise values. Industry stakeholders often prefer visual presentations. Interactive graphics work well for internal reports but require HTML delivery. Always report negative findings for prespecified analyses; Simmons et al. and the ASA Statement emphasize that selective reporting renders data distorted and uninterpretable.

### Sensitivity analyses and robustness checks

**What it should contain:** Results under alternative assumptions including different missing data mechanisms, alternative statistical methods, inclusion/exclusion of outliers or influential points, subgroup analyses examining effect consistency, model specification variations, and assessment of key assumption violations. Document whether conclusions are robust or sensitive to particular choices.

**Evidence and rationale:** ICH E9 and JAMA SAP guidelines require planned sensitivity analyses. These demonstrate whether findings depend critically on untestable assumptions or hold across reasonable alternatives. Ioannidis notes that flexibility in analysis modes increases probability of false findings; transparent sensitivity analyses address this by showing results under different reasonable approaches. The estimand framework's emphasis on sensitivity analyses for missing data assumptions reflects recognition that these assumptions cannot be tested from observed data.

**Consulting context considerations:** Sensitivity analyses showcase rigorous thinking and build confidence in conclusions. When results prove sensitive to assumptions, honest acknowledgment strengthens credibility. This section distinguishes thoughtful analysis from mechanical application of methods. For academic work, sensitivity analyses often address manuscript reviewer concerns preemptively. Industry clients appreciate risk quantification.

### Interpretation, discussion, and limitations

**What it should contain:** Interpretation of findings in context of research question and prior evidence, comparison with published literature, distinction between statistical and clinical/practical significance, discussion of biological or theoretical plausibility, explicit acknowledgment of study limitations including potential biases, precision/power limitations, generalizability constraints, assumption violations, and their likely impact on conclusions. Address strengths as well.

**Evidence and rationale:** CONSORT requires discussion of limitations addressing bias, imprecision, and generalizability. STROBE emphasizes cautious interpretation with consideration of potential biases and confounding. The ASA Statement emphasizes that p-values do not measure truth and scientific conclusions require context including study design, measurement quality, external evidence, and validity of assumptions. Gelman's ethical recommendations include embracing uncertainty and avoiding dichotomous thinking. Boen & Zahn stress that consultants must keep the client's audience in mind; clients need to defend findings to their stakeholders.

**Consulting context considerations:** This section delineates consultant versus client responsibilities. Per ASA Ethical Guidelines, consultants provide statistical inference; clients contribute domain expertise and make substantive interpretations. Be clear about this boundary. Cabrera & McDougall emphasize that good communication means admitting what you don't know. Overstating certainty or ignoring limitations damages professional reputation and disserves clients. Industry reports may need more cautious language given potential regulatory or legal implications.

### Recommendations and conclusions

**What it should contain:** Clear, actionable recommendations tied directly to findings, prioritized if possible, consideration of implementation feasibility, suggestions for future analyses or studies if appropriate, and concise conclusion summarizing key takeaways without merely repeating results.

**Evidence and rationale:** Derr's client satisfaction framework identifies that tangible deliverables including clear recommendations are critical quality indicators. Consulting books emphasize that clients need guidance on next steps, not just descriptions of what was found. The goal is enabling informed decision-making. Chatfield's problem-solving approach treats communication as integral to completing the statistical investigation.

**Consulting context considerations:** Recommendations must respect the consultant-client boundary. Offer statistical guidance (e.g., "A larger sample would provide adequate precision to detect a 10% difference") rather than substantive decisions that require domain expertise ("You should proceed with the intervention"). Derr's framework of treating clients as collaborators means jointly identifying satisfactory paths forward.

### Reproducibility appendix

**What it should contain:** Complete computational environment documentation (software versions, packages, operating system, hardware if relevant), data dictionary with variable definitions, units, coding schemes, missing data codes, data access information or instructions, code location with DOI or persistent identifier, step-by-step reproduction instructions, expected outputs, analysis decision log documenting key choices, quality assurance procedures applied including code review, and known limitations or reproducibility constraints.

**Evidence and rationale:** The TIER Protocol establishes four standards: sufficiency (everything necessary without author assistance), soup-to-nuts (all steps scripted), portability (runs on any system), and one-click reproducibility (single master script). Goodman, Fanelli, and Ioannidis define methods reproducibility as obtaining same results given same data, code, methods, and environment—the minimum standard for computational work. NASEM emphasizes transparency in reporting all procedures with sufficient detail for independent reproduction. The JASA reproducibility initiative requires code and data submission with verification, finding this process improves quality.

**Consulting context considerations:** Full code sharing may be impossible for proprietary client data or sensitive information. Provide synthetic data demonstrating code functionality, or document that reproduction requires data access through client. Academic collaborators increasingly face journal reproducibility requirements; positioning them well for this is valuable service. Industry clients concerned about intellectual property may need education about the distinction between sharing data versus methods.

### References

**What it should contain:** Complete citations for all methodological sources referenced, citations for non-standard statistical methods used, relevant clinical or scientific background literature, and guidelines followed (CONSORT, STROBE, etc.).

**Evidence and rationale:** Standard scholarly practice requires proper attribution. JAMA SAP guidelines include references for non-standard methods. Proper citation enables readers to examine methodological details and assess appropriateness. It also provides educational value when clients want to understand methods more deeply.

**Consulting context considerations:** Academic reports require comprehensive references following journal style. Industry reports may have fewer references but should cite key methodological papers and regulatory guidelines. Distinguish between references you're citing for background versus methods you actually implemented.

### Appendices for supplementary material

**What it should contain:** Additional tables and figures not essential for main narrative but supporting detailed examination, complete statistical output for key analyses, extended methodological descriptions including algorithm specifications, subgroup analyses beyond those in main text, code for complex derivations, protocol documents and amendments, and data processing details.

**Evidence and rationale:** Appendices enable complete reporting without overwhelming the main narrative. This supports the layered communication approach where main text addresses primary audience and appendices serve statistical reviewers or those wanting complete detail. TIER Protocol and other reproducibility frameworks emphasize complete documentation of all steps; appendices provide space for this.

**Consulting context considerations:** Electronic delivery enables unlimited appendix length. Use this to document everything that supports reproducibility and replication without cluttering the main report. Some academic journals now prefer separate supplementary files; adapt to client needs and dissemination plans. Gelman emphasizes good document structure with white space and clear navigation; apply this to appendices with descriptive section headers.

## Differences between standalone industry deliverables and academic consulting reports

The evidence reveals systematic differences in emphasis, audience expectations, regulatory context, and collaborative models that should inform template structure.

### Standalone statistical analysis reports for industry clients

**Primary purpose and audience:** These deliverables serve as complete self-contained analysis documentation, often for internal decision-making, regulatory submissions, or contract fulfillment. Audiences may include project managers, medical/scientific officers, regulatory affairs personnel, and executives. The consultant may have limited ongoing involvement after delivery.

**Structural emphases:** Industry reports require more formal administrative sections with clear version control, signature blocks, and quality control documentation. The executive summary receives particular emphasis as decision-makers may read only this section. Methods must be comprehensive enough for regulatory scrutiny if applicable. Documentation of GCP (Good Clinical Practice), protocol compliance, and any deviations receives attention. TransCelerate and CDISC standards influence structure even for non-regulatory work, promoting standardization. Tables, listings, and figures (TLFs) follow pharmaceutical industry conventions with very specific formatting.

**Tone and language:** More formal and conservative language, avoiding overstatement. Clear separation between statistical findings and clinical interpretation, with the latter typically assigned to medically qualified personnel. Sensitivity analyses and limitations receive thorough treatment to support regulatory defensibility or risk assessment.

**Timeline and completeness:** Industry reports typically represent "final" deliverables with comprehensive scope determined upfront through statements of work. Timeline pressure may be intense but deliverable specifications are usually precise. Follow-up may focus on Q&A rather than ongoing collaboration.

**Reproducibility and IP:** Code documentation and reproducibility critical but sharing may be constrained by intellectual property concerns. SOPs (standard operating procedures) govern quality assurance with independent programming verification for key analyses. Documentation serves audit trails for regulatory inspection.

### Academic and methodology consulting reports

**Primary purpose and audience:** These deliverables support collaborative research with academic investigators, often as part of grant preparation, manuscript development, or methodological guidance. Audiences are primarily researchers with domain expertise but variable statistical knowledge. The relationship is typically collaborative and longitudinal rather than transactional.

**Structural emphases:** Academic reports may include pedagogical elements explaining methodological choices and their implications. Background sections often contextualize within the relevant scientific literature more extensively. The report may be one component of a broader collaboration including manuscript co-authorship, response to reviewers, or grant statistical sections. Format flexibility is greater, adapting to specific collaboration needs.

**Tone and language:** More collegial and educational, treating the client as a collaborator per Derr's framework. Balance technical rigor with accessibility. May explicitly delineate learning objectives when consulting includes methodological training. References to methodological literature support investigator education.

**Timeline and scope evolution:** Academic projects often evolve with exploratory findings suggesting additional analyses. The report may go through multiple iterations as research questions are refined. Grant applications have firm deadlines but allow for preliminary consultations. Manuscript preparation occurs in phases with the statistician potentially contributing methods/results sections directly.

**Reproducibility and collaboration:** Code sharing more straightforward as publications increasingly require it. Reproducibility documentation serves manuscript supplementary materials. Data dictionaries and processing documentation may transition to data sharing repositories. Collaborative tools like GitHub, shared folders, and version-controlled documents facilitate ongoing interaction.

### Common ground across both contexts

Despite differences, both contexts share core requirements: transparency about assumptions and limitations, honest communication of uncertainty, distinction between prespecified and exploratory analyses, reproducible methods, and appropriate handling of missing data and multiplicity. The ASA Ethical Guidelines apply universally emphasizing professional integrity, stakeholder responsibilities, and honest communication. Both benefit from clear documentation enabling future reference or follow-up analyses.

## Common reporting failures and template defenses

The literature documents pervasive reporting problems that well-designed templates can proactively address.

### Problem: Selective outcome reporting and publication bias

**What goes wrong:** Studies report only statistically significant findings, fail to report all prespecified outcomes, switch primary outcomes without explanation, or emphasize secondary outcomes when primary analyses are negative. Empirical evidence shows 96% of biomedical studies report at least some significant results despite this being statistically implausible, and outcome switching affects up to 67% of trials.

**Why it happens:** Investigator desire for "positive" results, publication pressures, funding pressures, and misunderstanding of the scientific value of negative findings. Ioannidis's framework shows greater flexibility in outcomes increases the probability of false findings.

**Template defenses:** Require an outcomes section documenting all prespecified outcomes with explicit designation of primary versus secondary. Include a template table listing each outcome with results even if non-significant. Add a protocol compliance section where any deviations from prespecified outcomes must be explained with timing and rationale. In the results section, mandate subsections for each planned outcome category. Include checklist items: "All prespecified primary outcomes reported? All prespecified secondary outcomes reported? Any additional outcomes clearly labeled as exploratory?"

**Evidence basis:** Kahan and Jairath document that outcome switching with inadequate prespecification led to markedly different conclusions in their case study (OR ranging from 0.94 to 0.23 depending on definition). JAMA SAP guidelines require complete specification of all outcomes including measurement methods, timing, aggregation, with any changes documented. CONSORT requires results for all prespecified outcomes.

### Problem: P-hacking and HARKing

**What goes wrong:** Researchers try multiple analytic approaches, report only those yielding p<0.05, collect data until significance is achieved, or present post-hoc hypotheses as if they were planned a priori. Simmons, Nelson, and Simonsohn demonstrated this makes false positives more likely than true negatives.

**Why it happens:** Misunderstanding that flexibility in analysis inflates false positive rates, focus on statistical significance as a binary outcome, and lack of documentation about the analytic process.

**Template defenses:** Separate prespecified analysis section from exploratory analyses section with clear headers. Require a methods subsection explicitly stating "All analyses described below were prespecified in the analysis plan dated [DATE]" or "The following analyses were data-driven and should be considered exploratory." Include a decision log appendix template where consultants document all analytic decisions with dates. Require reporting effect estimates with confidence intervals for all comparisons examined, not just significant ones. Add standardized language: "The following additional analyses were suggested by observed data patterns and should be considered hypothesis-generating."

**Evidence basis:** The ASA Statement declares that proper inference requires knowing how many and which analyses were conducted, and valid conclusions cannot be drawn without this information. Simmons et al. provide six concrete requirements including that authors must list all variables collected, report all experimental conditions, and report results with and without covariates. The solution is not to prohibit flexibility but to document and acknowledge it.

### Problem: Inadequate uncertainty quantification

**What goes wrong:** Reports present point estimates without confidence intervals, report only p-values, dichotomize findings into "significant" versus "not significant," or overstate certainty in conclusions. Reviews show approximately 30% of manuscripts fail to report confidence intervals for key outcomes.

**Why it happens:** Misunderstanding of what p-values represent, legacy of p<0.05 culture, and lack of training in uncertainty communication.

**Template defenses:** Include results table templates that require both point estimates AND confidence intervals for every effect. Add template language like "Mean difference: X [95% CI: Y to Z], p=P" rather than allowing "p<0.05". Remove any template text using "significant" or "non-significant" language. In interpretation sections, include prompts: "The confidence interval indicates that the true effect is likely between ___ and ___, with practical/clinical implications that _____." Require a limitations section addressing precision/power. Include guidance that exact p-values should be reported, not just whether they cross thresholds.

**Evidence basis:** Wasserstein and Lazar's ASA Statement principle 5 states that p-values do not measure effect size or importance. Principle 6 emphasizes p-values don't provide good evidence without examining effect estimates and confidence limits. The 2019 "Moving Beyond p<0.05" editorial argues for eliminating the language of statistical significance entirely. NEJM and JAMA both mandate confidence intervals. Harrell advocates reporting probabilities of clinically meaningful effects rather than dichotomous declarations.

### Problem: Opaque handling of missing data and assumptions

**What goes wrong:** Reports don't document amount or patterns of missing data, fail to state assumptions about missing data mechanisms, use methods like LOCF without justification, or don't report how many values were imputed. Reviews show only 5-14% of studies using imputation report numbers of imputed values in flow diagrams.

**Why it happens:** Missing data viewed as inconvenient rather than substantively important, lack of understanding that all methods make assumptions, and inadequate training in modern missing data methods.

**Template defenses:** Require a data completeness section documenting completeness by variable and group. Include a table template showing missing data patterns. Add mandatory subsection in methods on missing data with prompts: "Mechanism assumption: _____ Justification: _____ Primary method: _____ Implementation details: _____ Sensitivity analyses: _____". In results flow diagrams, require numbers with complete data and numbers with imputed values. Include limitation section prompt: "Missing data may affect results if _____."

**Evidence basis:** ICH E9(R1) requires explicit handling of intercurrent events including dropout as part of the estimand framework with sensitivity analyses examining robustness to mechanism assumptions. The TARMOS framework emphasizes transparent reporting for observational studies. Multiple imputation and likelihood-based methods are now standard but all assume MAR unless explicitly addressing MNAR scenarios.

### Problem: Multiplicity ignored or inappropriately handled

**What goes wrong:** Studies test multiple hypotheses without adjustment when warranted, fail to distinguish primary from secondary outcomes, report subgroup analyses as definitive without adjustment, or conversely, over-adjust by treating all comparisons as requiring correction when separate research questions don't need it.

**Why it happens:** Confusion about when adjustment is needed, belief that prespecification eliminates need for adjustment, or lack of understanding of confirmatory versus exploratory contexts.

**Template defenses:** Include PICOTA framework checklist in methods template: evaluate need for adjustment based on Population subgroups, Intervention comparisons, Outcomes (primary vs secondary), Timepoints, and Analysis types. Require designation of which comparisons are confirmatory versus exploratory. Add decision tree: "If multiple comparisons contribute to a single scientific conclusion, adjustment is warranted. If comparisons address distinct questions, adjustment may not be needed but should be discussed." Require explicit statement: "The following approach was taken for multiplicity: _____" with options and rationale.

**Evidence basis:** Li et al. document that substantial proportions of trials fail to adjust appropriately. The key insight from NEJM and other guidelines is that context matters: adjust for multiple primary outcomes and related comparisons in confirmatory settings, but secondary outcomes are exploratory and over-adjustment reduces power without corresponding benefit. Prespecification reduces selective reporting bias but doesn't eliminate multiplicity issues.

### Problem: Irreproducible analyses

**What goes wrong:** Reports don't document software versions, use non-scriptable methods (Excel clicking), hard-code file paths, fail to set random seeds, don't share code, or provide insufficient documentation for replication.

**Why it happens:** Lack of training in reproducible workflows, time pressure, viewing reproducibility as extra work rather than integral to quality, and inadequate institutional standards.

**Template defenses:** Require reproducibility appendix with checklist items: Software and version documented? Random seeds set and documented? Code archived with DOI? Data dictionary complete? README with reproduction instructions? Master script runs entire analysis? Build TIER Protocol folder structure into project setup. Require sessionInfo() output in R or equivalent in appendices. Include code commenting standards in instructions. Add quality assurance section documenting whether independent reproduction was attempted.

**Evidence basis:** JASA reproducibility initiative found code review identified problems in ~50% of submissions. TIER Protocol establishes four standards (sufficiency, soup-to-nuts, portability, one-click reproducibility) that ensure methods reproducibility. NASEM emphasizes that reproducibility is foundational to scientific progress. The five pillars framework (literate programming, version control, environment control, data sharing, documentation) provides comprehensive approach.

## Handling critical technical and ethical issues

### Prespecification in non-registered consulting contexts

Many consulting projects lack formal registration or protocols, yet prespecification principles still apply. Best practice involves documenting analysis plans before data examination, even informally. Write a brief analysis plan memo with research questions, planned analyses, and rationale before looking at results. Email this to the client with date stamp. If formal protocol exists, align with it. When projects lack preregistration infrastructure, acknowledge this limitation but distinguish what was planned from what emerged during analysis.

For academic work, encourage use of Open Science Framework or AsPredicted for preregistration even if not required. For industry work, create versioned statistical analysis plans following JAMA guidelines before database lock. The ASA Ethical Guidelines require distinguishing a priori from post hoc objectives—applicable regardless of study type.

When post-hoc analyses are valuable (they often are), report them clearly labeled as exploratory or hypothesis-generating. The ethical issue is misrepresentation, not conducting exploratory work. Simmons et al. emphasize that flexibility is inevitable and valuable but must be acknowledged. Templates should provide separate sections for planned versus exploratory analyses with standardized language preventing ambiguity.

### Multiplicity: Nuanced guidance

The PICOTA framework provides systematic approach: Population subgroups need adjustment only when prespecified and confirmatory with biological plausibility; multiple Intervention comparisons need adjustment when related and summarized in single conclusion; multiple primary Outcomes require adjustment while secondary outcomes are typically exploratory; interim Timepoint analyses need group sequential methods; but sensitivity Analyses don't require adjustment as they're supportive.

Academic consulting often involves exploratory work where adjustment may be counterproductive. Industry work may have confirmatory elements requiring careful adjustment. The template should prompt explicit consideration: "Are these comparisons confirmatory or exploratory? Do they contribute to a single conclusion or address distinct questions? Was multiplicity adjustment prespecified?" 

Li et al. note that transparency matters more than rigid rules. Report unadjusted p-values alongside adjusted ones so readers can judge. Use graphical methods showing all comparisons. NEJM guidance distinguishes prespecified subgroups requiring multiplicity consideration from post-hoc subgroups that don't but must be labeled hypothesis-generating.

### Missing data: Transparent assumptions and sensitivity

All missing data methods make assumptions. Complete case analysis assumes MCAR (missing completely at random)—usually implausible. Multiple imputation and likelihood methods assume MAR (missing at random)—often reasonable but untestable. MNAR (missing not at random) methods require sensitivity analyses as no unique solution exists.

Best practice documented in ICH E9(R1) involves: (1) preventing missing data through design, (2) documenting amounts and patterns, (3) specifying primary analysis method with MAR assumption, (4) conducting sensitivity analyses examining MNAR scenarios. The TARMOS framework applies this to observational studies.

Template should require: missing data table by variable and group, mechanism assumption with justification, primary method description with sufficient detail for replication (e.g., "Multiple imputation using mice package with predictive mean matching, 20 imputations, including auxiliary variables X, Y, Z"), and at least one sensitivity analysis. For complex missingness, consider tipping point analysis showing how results change under various MNAR assumptions.

Reviews show very poor reporting of imputed values; template should require reporting both observed and imputed sample sizes. Avoid methods like LOCF that appear convenient but induce bias.

### Software documentation for reproducibility

Computational reproducibility requires complete environment documentation. At minimum: programming language with version (R 4.3.1, Python 3.11), all packages with versions, operating system, and for specialized computing, hardware specifications. In R, include sessionInfo() output in appendix. In Python, export requirements.txt or environment.yml.

For complex environments, consider containerization with Docker, though this requires expertise. More commonly, use package management: renv for R creates snapshots restoring exact package versions; conda for Python manages environments. TIER Protocol requires relative file paths allowing scripts to run on any system.

Random seeds are critical for any stochastic method: bootstrap, permutation tests, multiple imputation, machine learning, Markov chain Monte Carlo. Set seed before each random operation and document the value. Note that results with different seeds may vary slightly; consider sensitivity across multiple seeds for critical findings.

Archive code with persistent identifier via Zenodo, Software Heritage, or Open Science Framework. Include README with step-by-step reproduction instructions, expected runtime, and contact information. The JASA reproducibility initiative demonstrates this improves quality through independent verification.

### Communicating uncertainty to non-statisticians

This is challenging but critical. Avoid jargon and technical language in main narrative. Don't say "statistically significant"—say what the data show. Instead of "We failed to reject the null hypothesis," say "We found insufficient evidence that A differs from B" or "The data are consistent with no difference."

Report effect estimates in clinically or practically meaningful units. Instead of "OR = 1.8, 95% CI [1.2, 2.7]," say "The intervention approximately doubled the odds of success, with the true effect likely between 1.2 and 2.7 times the odds." For non-statisticians, explain what confidence intervals mean: "If we repeated this study many times, about 95% of such intervals would contain the true effect."

Use graphics over tables per Harrell's recommendation. Gelman emphasizes clear structure with white space and headers that convey information. Forest plots with confidence intervals communicate uncertainty visually. Interactive graphics with hover text work well for reports delivered electronically.

Distinguish statistical from clinical significance explicitly. A small statistically significant effect may not matter clinically; a non-significant result may include clinically important effects but lack precision. Always discuss practical implications: "This 2 mmHg blood pressure reduction is statistically significant but unlikely to provide meaningful clinical benefit to most patients."

Boen & Zahn emphasize keeping the client's audience in mind—they need to explain findings to others. Use language they can adopt. Derr's communication principles stress treating clients as collaborators and using pedagogical approaches. Provide interpretation assistance while respecting the boundary between statistical and substantive expertise.

### Delineating consultant versus client responsibilities

The ASA Ethical Guidelines explicitly address this. Consultant responsibilities include: accurate statistical analysis, appropriate methodology selection, honest reporting of limitations and uncertainties, clear communication of findings, meeting commitments, and maintaining confidentiality. Client responsibilities include: providing complete data and context, defining research questions, supplying domain expertise, making substantive interpretations, and implementing recommendations.

Critical boundary: consultants provide statistical inference; clients make substantive interpretations requiring domain knowledge. A consultant can say "The confidence interval for the treatment effect ranges from 5 to 15 units"; the client must interpret whether this range is clinically meaningful. The consultant can note "These observational data show an association but do not establish causation"; the client considers biological plausibility.

Derr's framework of treating clients as collaborators involves negotiation and mutual respect. When clients request inappropriate methods or interpretations, consultants must respectfully explain why they cannot comply. The recent literature on scope of work emphasizes empowering statisticians to decline inappropriate requests.

Document this boundary in engagement letters or project initiation documents. When clients override statistical recommendations, document this in the report: "The consultant recommended [method X] based on [rationale]. The client requested [method Y] for [stated reason]. Results using the client's preferred approach are reported here with the consultant's methodological concerns noted in limitations."

Attribution and authorship follow ICMJE criteria: substantial contribution to design or analysis or interpretation, drafting or critical revision, approval of final version, and accountability. Consulting that includes these warrants co-authorship. Limited consultation warrants acknowledgment. This should be negotiated upfront per Duke BERD and other academic center guidance.

## Practical formatting and presentation conventions

### Tables versus figures: When to use each

Use tables when precise numeric values are essential, multiple variables must be compared simultaneously, the report serves as a reference document readers will consult repeatedly, or datasets are small enough that every value matters. Tables work well for baseline characteristics, detailed numerical results, and precision in regulatory submissions.

Use figures when showing trends, patterns, or distributions, working with large datasets where precision is less critical, emphasizing comparisons or relationships, or making findings accessible to broader audiences. Graphics excel at communicating main messages and are easier for non-statisticians to interpret.

Evidence from Tufte emphasizes graphical excellence that reveals data at multiple levels from broad overview to fine detail. Cleveland's research on graphical perception shows that position encodings along common scales are most accurately perceived. Harrell advocates for almost entirely graphical reports using interactive visualizations with hover text containing table information for specific points, eliminating traditional tables in many contexts.

Best practice often combines approaches: present key results graphically in main text with complete numerical tables in appendices. For manuscripts, follow journal requirements which typically include both. For internal consulting reports, emphasize graphics with selective tables.

### Table formatting standards

Clear descriptive titles that stand alone without reading text. Column headers with units clearly specified. Row labels aligned left, numbers aligned right or on decimal point. Footnotes explaining abbreviations, statistical tests used, and any symbols. Consistent number of decimal places appropriate to precision (don't report 6 decimals when data measured to nearest whole number).

Include measures of uncertainty (standard deviations, confidence intervals, standard errors) alongside point estimates. For comparative studies, report both absolute and relative measures. Follow journal or client style guides for specific formatting. APA style places tables after references before appendices, numbered consecutively (Table 1, Table 2), referred to in text by number.

Avoid excessive lines and borders; white space aids readability per Tufte's principles. Make tables self-explanatory so they could be understood without reading the full text. Group related information logically.

### Figure formatting standards

Apply Tufte's data-ink ratio: maximize proportion of ink devoted to data representation. Remove chartjunk (unnecessary decorations, 3D effects, heavy gridlines). Use direct labeling instead of legends when possible. Show data variation with error bars or confidence bands appropriately.

Follow Cleveland's ranking of visual encodings: use position on common scales for most important comparisons, avoid relying on area or volume which people judge less accurately, don't use pie charts (angle/area difficult to judge). Bank line graphs to 45 degrees for clearer perception of slopes.

Color considerations: use colorblind-friendly palettes, don't rely solely on color to convey information (add shapes or patterns), maintain consistent color schemes across related figures, limit to 3-5 colors for clarity. Tools like viridis palettes or Color Brewer address these issues.

Include clear axis labels with units, descriptive titles, annotations explaining key features, and appropriate scales (avoid distorting relationships). Wickham's ggplot2 principles enable building complex graphics from simple layered components with aesthetic mappings separate from geometric representations.

Modern approaches include interactive graphics using plotly in R or equivalent tools. These allow hover text showing exact values, zooming, selecting subsets, and drill-down from summary to detail. Distribute as self-contained HTML files. This suits consulting reports delivered electronically but doesn't work for print publications.

### Appendix organization and use

Appendices contain supplementary material that supports main narrative without cluttering it: additional tables and figures, extended methodological descriptions, sensitivity analyses, complete statistical output, derivation details, protocol documents, data processing code, and reproducibility materials.

Number consecutively (Appendix A, B, C or Appendix 1, 2, 3) with descriptive titles. Reference from main text in order. Tables and figures in appendices use appendix identifier (Table A1, Figure B2). Each appendix should stand relatively independently.

Modern alternatives include online repositories for large datasets, supplementary files hosted by journals, GitHub for code and documentation, preventing unwieldy appendices while supporting transparency and reproducibility. When using external hosting, provide clear access instructions and persistent identifiers (DOIs, GitHub release tags).

### Report length norms

Journal articles typically contain 3,000-5,000 words in main text with 6-8 tables plus figures total (journal-dependent) and unlimited supplementary materials in online journals. Statistical methods sections run 500-1,000 words; results 1,000-2,000 words.

Formal Statistical Analysis Reports for regulatory submissions range widely from 50-300+ pages depending on study complexity. These are comprehensive documentation including all planned analyses, driven by regulatory requirements rather than brevity.

Consulting reports for academic or industry clients should include 1-2 page executive summary (essential), 10-30 page main report focusing on key findings, and technical appendices as needed for reproducibility. Additionally, 10-15 slide presentations for oral presentation of findings.

General principle from Gelman: main text should be concise and focused on interpretation; methods and results complete but not redundant; details in appendices or supplementary materials. If uncertain, put material in appendix. Write so busy readers can skim headings and understand the gist.

### Versioning, traceability, and audit conventions

Use clear file naming with version and date: Statistical_Report_v2.1_2024-04-30.pdf. Avoid "final," "final_final," "really_final" naming. Include version history table in document showing version number, date, author, and summary of changes.

For code, use Git version control committing changes frequently with meaningful messages. Tag releases corresponding to report versions. Time-stamp analysis plans before data examination.

Track protocol or analysis plan changes explicitly. JAMA guidelines require SAP revisions documented with justifications and timing. Changes during blind review are acceptable; post-unblinding changes must be clearly marked as protocol deviations.

Include session info (sessionInfo() in R, package versions in Python) showing exact software environment. Document dates of analyses. Create README files explaining folder structure and reproduction steps. Log files can capture runtime information automatically.

For regulatory contexts, FDA 21 CFR Part 11 establishes electronic records requirements including audit trails, time-stamping, and controlled access. Even non-regulated consulting benefits from these practices ensuring work can be defended if questioned months or years later.

Reproducibility package should allow independent investigator to reproduce all results. TIER Protocol standards provide roadmap: master script, clear folder structure, complete documentation, and portable code with relative paths.

## Academic statistical consulting centers: Documented practices and templates

Duke BERD Methods Core provides the most comprehensive publicly available documentation including a downloadable Statistical Analysis Plan template (Word document) specifying project aims, data sources, and detailed analysis plans; a "12 Phases of Biostatistics Collaboration Process" document outlining complete collaboration lifecycle; and Biostatistician Essential Skills document based on literature and experience. These resources emphasize partnership models over transactional consulting.

Vanderbilt Department of Biostatistics maintains LaTeX templates on Overleaf for grant applications and reports curated by department faculty. Services include free consultation clinics with 72-hour advance booking, long-term collaborations through percentage effort or fee-for-service, and explicit deliverables spanning design consultation through manuscript preparation.

Harvard Catalyst Biostatistics Center offers NIH-funded support for Harvard postdoctoral and faculty researchers conducting clinical and translational research. Consultations typically run 1-3 hours with explicit citation requirements in resulting publications. Educational programming includes Applied Biostatistics Certificate program emphasizing early consultation before deadlines.

Johns Hopkins ICTR Biostatistics provides free virtual walk-in clinics with 20-30 minute initial consultations and fee-for-service through Johns Hopkins Biostatistics Center for extended work. Timeline expectations specify consultant contact within one week of request, with minimum two months' notice recommended for most projects. Services explicitly include fully automated and reproducible reports.

Stanford Quantitative Sciences Unit emphasizes "team science" approach where data scientists become fully integrated into research teams rather than providing one-off consultations. Partnership model with departments involves annual subscription fees. Philosophy: "Not about the sample size" but comprehensive collaboration.

Mayo Clinic Division of Clinical Trials and Biostatistics supports approximately 5,000 studies annually with one of the largest biostatistics groups in the U.S. Services span protocol development through responding to reviewer comments with expertise in electronic health records analysis and complex longitudinal designs.

Cambridge MRC Biostatistics Unit, founded 1913, represents one of the largest European biostatistics groups focusing on research, training, and knowledge transfer with emphasis on open science following FAIR principles (Findable, Accessible, Interoperable, Reproducible). Public-facing resources include BUGS software and substantial methodological publications.

Common structural elements across institutions include initial intake forms, meetings to discuss scope and research questions, assessment of timeline feasibility, agreement on deliverables and authorship following ICMJE guidelines, formal Statistical Analysis Plans for major projects, results reporting organized by research aim, and manuscript preparation support. Most centers distinguish free limited consultations (1-3 hours) from fee-based extended collaborations.

Perkins et al.'s CTSA Consortium best practices paper published in Statistics in Medicine addresses funding mechanisms, access prioritization, investigator interactions, institutional recognition for biostatisticians, and professional development. The Virginia Commonwealth University case study implementing these guidelines documented substantial productivity (30 manuscripts, 52 conference presentations) with 77% client satisfaction and 97% recommendation rates over 3.5 years.

The consistent message across academic centers emphasizes collaborative partnerships, educational components alongside service delivery, expectation of co-authorship for substantial contributions, and integration into research teams rather than isolated consultation. Deliverable formats include written statistical reports with methods, results, publication-ready tables and figures; Statistical Analysis Plans; grant statistical sections; and database specifications with data dictionaries.

## Synthesis: A recommended consulting report structure

**For standalone industry analysis reports**, emphasize: formal title page with version control and signatures, comprehensive executive summary for decision-makers, complete methods documentation sufficient for regulatory scrutiny if applicable, conservative interpretation with clear limitations, formal quality assurance documentation, and explicit reproducibility materials while respecting intellectual property constraints. Tone should be formal with clear separation between statistical findings and clinical interpretation. Follow industry conventions for TFLs (tables, listings, figures) and consider regulatory submission requirements even for non-regulated work.

**For academic methodology consulting reports**, emphasize: collaborative tone treating client as partner, pedagogical elements explaining methodological choices, integration with manuscript preparation including potentially drafting methods/results sections, flexibility as research questions evolve, comprehensive references supporting investigator education, and full code sharing to support publication requirements. Include elements that position the investigator well for manuscript submission and reviewer responses. Balance technical rigor with accessibility for domain experts with variable statistical knowledge.

**For both contexts**, the essential sections are: administrative information with version control, executive summary, background and research questions with estimand specification for causal questions, data sources and integrity documentation, comprehensive statistical methods including prespecification status and multiplicity handling, complete results with effect estimates and uncertainty measures, sensitivity analyses, honest discussion of limitations, clear recommendations, reproducibility appendix with code and environment documentation, and references.

The evidence from peer-reviewed literature, professional guidelines, consulting books, and academic center practices converges on these principles: transparency about all analyses performed, prespecification or clear labeling of exploratory work, comprehensive uncertainty quantification beyond p-values, honest acknowledgment of limitations and assumptions, reproducible methods with complete documentation, appropriate audience-tailored communication, and ethical boundaries between statistical and substantive interpretation. Well-designed templates incorporating these evidence-based elements serve both scientific integrity and client service excellence.
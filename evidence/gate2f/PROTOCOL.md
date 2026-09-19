# Gate 2F — Cross-Ontology Cultural Transmission Protocol

## Question
Can knowledge learned in one architecture and ontology be translated into a recipient that represents both states and actions at a different granularity?

## Source ontology
- 8 anonymous contexts.
- 3 conceptual decision stages per context (24 conceptual states).
- 2 abstract actions.
- Source culture capsule: 97-byte quantized policy plus 144-byte source relational atlas = **241 bytes**.

## Recipient ontology
Each random alien world independently samples:
- an unknown permutation between the 8 source contexts and 8 local temporal chains;
- an unknown four-action macro codebook;
- an unknown expansion of each source concept into 2 or 3 local perceptual states;
- exactly two actionable local substates per source concept, in temporal order;
- optional nuisance substates inside concepts plus optional prefix/suffix nuisance states with no source-action analogue;
- dense nonlinear 8-D local sensory codes.

A source abstract action is not a recipient primitive action. It is translated into an **ordered two-action macro** over four recipient primitive actions.

Across confirmation worlds the recipient has 48 actionable local states plus roughly 12–25 nuisance states, instead of the teacher's 24 conceptual states.

## Ontology hypothesis family
The grounder is not unrestricted. It knows a generic family in which:
- there are 8 local chains corresponding one-to-one to 8 source contexts;
- source stage order is preserved;
- a source concept expands to 2 or 3 local states;
- there are exactly two ordered action substates per source concept and at most one nuisance substate inside it;
- an optional nuisance state may appear at either chain boundary;
- the two source actions are encoded by two ordered length-2 macros forming a permutation of the four recipient primitive actions.

It is **not** given the actual context correspondence, expansion lengths, nuisance positions, macro codebook, or sensory transform.

## Calibration
The grounder actively selects local states that maximally distinguish surviving ontology hypotheses.

A calibration query returns either:
- the correct recipient primitive action for an actionable state, or
- `nuisance` for a non-actionable state.

The frozen confirmation budget is **36 label-style calibration queries**. These are not 36 binary reward bits; if implemented by exhaustive primitive-action reward testing they correspond to at most 144 action/reward probes. The query-only control receives the same calibration labels.

## Grounding confirmation
For each teacher packet independently:
- 20 newly generated random recipient ontologies;
- 36 calibration queries;
- success measured on all unqueried and queried local states.

Primary grounding outcomes:
- primitive-action grounding accuracy on 48 actionable states;
- complete six-action macro-sequence success across 8 contexts;
- nuisance-vs-actionable ontology-role accuracy.

## Cross-architecture transfer confirmation
Directions:
1. Fly teacher packet -> alien Transformer recipient.
2. Transformer teacher packet -> alien Fly recipient.

Six fresh random ontologies per direction.

Conditions:
- `grounded_culture`: ontology translator plus culture capsule;
- `query_only_no_packet`: same 36 calibration queries and same number of optimizer updates, but no culture capsule;
- `ungrounded_identity`: culture packet supplied without ontology translation, under the false assumption that source and recipient ontologies are already aligned.

Cultural absorption supplies **no additional environmental reward** after calibration. The culture packet is removed for final evaluation.

Absorption budgets were frozen after recipient-capacity pilots:
- Fly -> Transformer: 512 cultural observations.
- Transformer -> Fly: 1,024 cultural observations.

Only recipient parameters are updated. Teacher-native weights, hidden states, gradients, and replay data never cross the boundary.

## Interpretation rule
A positive Gate 2F result requires:
1. high ontology-grounding accuracy at the frozen calibration budget;
2. grounded culture materially outperforming the same-query/no-packet control;
3. ungrounded packet exposure failing, showing that translation is necessary;
4. the transferred behavior remaining in the recipient after the packet is removed.

The experiment does **not** establish unrestricted ontology induction. The ontology hypothesis family above remains human-specified.

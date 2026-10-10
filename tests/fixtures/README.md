# Fixture origin

`casino_dialogue_0.json` is a reduced excerpt of dialogue 0 from the
[pinned CaSiNo JSON](https://raw.githubusercontent.com/kushalchawla/CaSiNo/2f6ed4a6a55110152a7699fbaa8150d6036314be/data/casino.json).
It retains the dialogue ID, final submission and acceptance, preference rankings,
and recorded points. All ordinary conversation, demographics, personality,
arguments, annotations, and other outcome fields are omitted. Retained values
are unchanged. This excerpt is one object; the complete source is a list.

Attribution: Kushal Chawla, Jaysa Ramirez, Rene Clever, Gale Lucas, Jonathan May,
and Jonathan Gratch (2021), *CaSiNo: A Corpus of Campsite Negotiation Dialogues
for Automatic Negotiation Systems*, NAACL-HLT, pp. 3167–3185.
[Paper](https://aclanthology.org/2021.naacl-main.254/).

The excerpt remains under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
as provided by the [upstream license](https://raw.githubusercontent.com/kushalchawla/CaSiNo/2f6ed4a6a55110152a7699fbaa8150d6036314be/LICENSE),
including its disclaimer of warranties. See `sources/casino.manifest.json` for
the full source identity.

The opposite-proposer test changes the control roles and swaps the two proposal
sides while preserving the allocation. That variant is constructed, not another
observed dialogue. The independent arithmetic example in the tests is invented.

## Four-record audit example

`casino_audit_small.json` is a constructed teaching dataset, based on copies of
the reduced dialogue-0 excerpt above. Its IDs are artificial:

| File index | Dialogue ID | Modification | Expected outcome |
| ---: | ---: | --- | --- |
| 0 | 100 | Change only the ID | Accepted; scores 19 and 18 |
| 1 | 101 | Change ID and participant 1's recorded score from 19 to 20 | Invalid; reconstructed score is still 19 |
| 2 | 102 | Invent a minimal walkaway with no participant data or allocation | Walkaway; no deal or score |
| 3 | 103 | Change ID, swap proposer/acceptor IDs and the proposal sides | Accepted; same participant allocations and scores |

Expected: 4 total records, 3 accepted endings, 2 valid accepted deals, 1 walkaway,
1 invalid record, and FAIL. The later valid record proves continuation after the
bad accepted record. These are not four observed negotiations. Source-derived
portions retain the attribution and license described above. Experiments should
use a copy of this fixture, leaving both the original dataset and this test
baseline intact.

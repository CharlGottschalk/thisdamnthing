# Clear workspace documentation: an ASD-STE100 adaptation

## Purpose and scope

Read and apply this guide whenever you create or update documentation that teaches
users how to use an installed ThisDamnThing workspace. This includes:

- Usage guides in `src/thisdamnthing/resources/docs/`.
- User-facing instructions in workspace templates and generated documentation.
- Usage sections in other files, including skill instructions addressed to users.

Review the text that you change and enough surrounding text to keep it consistent.
A small edit does not require a rewrite of the entire document.

This file is development guidance. Do not copy it into package resources or an
installed workspace. Do not add references to `.dev/` in shipped documentation.
The development constitution requires this guide; its existing SessionStart loader
supplies that requirement to agents. There is no additional hook or automatic checker.

## Relationship to ASD-STE100

ASD-STE100 combines writing rules with a controlled dictionary. Its official
guidance supports direct instructions, consistent terminology, and clear sentence
structure. See the [STEMG FAQ](https://www.asd-ste100.org/STE_faq.html).

This is an original adaptation for software documentation, not the official
standard or its dictionary. The rules below are repository requirements inspired
by STE. They do not reproduce the complete rules or establish STE compliance.
Use the [official downloads page](https://www.asd-ste100.org/STE_downloads.html)
if a task requires the authoritative standard. The official site identifies
[Issue 9, dated January 15, 2025](https://www.asd-ste100.org/).

## Words and sentences

- Use one term for each concept. Define unfamiliar terms when users first need them.
- Prefer familiar verbs. Write direct instructions, such as “Open the workspace.”
- Name the actor in descriptions: the user, ThisDamnThing, the agent, or the host.
- Put a condition before the action when users must know the condition first.
- Keep one main idea in each sentence. Replace ambiguous pronouns with the relevant name.
- Use simple grammar and active voice. Avoid idioms, promotional claims, and unnecessary jargon.
- Keep articles and other words needed for complete, natural sentences.

These principles adapt the [official FAQ's guidance](https://www.asd-ste100.org/STE_faq.html).
For local review, target at most 20 words per instruction sentence and 25 per
descriptive sentence. These numbers reflect the
[Issue 9 sentence limits](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).
Here they are review targets, not a formal STE word-count check. Rewrite long
sentences where useful. Never damage a command or omit a necessary condition to
meet a word count. Code blocks and exact quoted output are outside these targets.

## ThisDamnThing terminology

These distinctions describe the product, not an STE approved vocabulary.

| Term | Meaning to preserve |
| --- | --- |
| workspace | The installed ThisDamnThing environment; distinguish it from this source repository. |
| project | A registered project; identify external source paths when relevant. |
| candidate | Knowledge awaiting review; do not describe it as approved knowledge. |
| stack | An optional installed extension; do not imply it is required by core. |
| host | The agent application, such as Claude or Codex. |
| MCP registration | Saved host configuration; registration alone does not establish a connection or host trust. |
| executable trust | Explicit consent for the relevant executable content; inspection does not grant it. |

Check terminology against the implementation and product contracts. Preserve exact
command names, option names, paths, tool IDs, keys, error messages, and UI labels.
Use code formatting for literal syntax. Explain technical identifiers in nearby
prose instead of renaming them. Do not remove an essential distinction to simplify
a sentence.

## Procedures and examples

Write each procedure around a user task:

1. State the result and any required setup or authorization.
2. Identify where the command runs and which workspace or project it affects.
3. Put actions in numbered steps, with one main action per step.
4. Show copyable syntax in a code block. Explain placeholders before use.
5. State the expected result and how the user can check it.
6. Describe a relevant failure and the supported next action when needed.

Use portable example paths. Do not include developer identities, machine paths,
credentials, or private content. Verify examples against the current CLI or tool
schema. Do not invent flags, output, success states, or automatic recovery behavior.

Separate user actions from software behavior. Clearly identify optional branches.
Keep explanations close to the step they support. Use tables for comparable options
and lists for distinct items. Link to existing prerequisites instead of duplicating
long setup instructions.

## Permissions, warnings, and uncertainty

State the specific effect before an action that can delete or replace user content.
Explain the affected files or scope and the supported way to avoid the problem.
Use warnings only for relevant risks, not as decoration.

Preserve approval, ownership, trust, and recovery requirements from the product
contract. Do not invent a confirmation step. Never turn “can” into “will” or a
recorded state into a claim about live files. If a result is uncertain, document
the supported inspection step before describing a retry.

## Original editing examples

| Before | After |
| --- | --- |
| Workspace selection should be performed prior to registration. | Select the workspace before you register the MCP server. |
| Once this is complete, it can be inspected. | After registration, inspect the saved MCP configuration. |
| Registration makes the tools ready to use. | Registration saves the host configuration. Connect through the host before you use the tools. |
| Simply approve the candidate to seamlessly retain your insights. | Review the candidate. Approve it if you want to retain it as approved knowledge. |

The examples illustrate wording. They do not replace a complete, verified procedure.

## Manual review before completion

- Confirm that the changed text describes current product behavior.
- Check terminology, actors, conditions, sentence length, and action order.
- Check literal syntax, placeholder explanations, links, and expected results.
- Preserve distinctions between inspection, authorization, execution, and verification.
- Confirm that examples contain no private data or developer-specific paths.
- Report checks actually performed and any remaining verification gap.

Use focused manual checks under the development constitution. A readability score
or an AI review does not prove technical accuracy or formal STE compliance.

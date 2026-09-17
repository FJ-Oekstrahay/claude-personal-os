# selected-playbooks/

Playbooks are durable, cross-project notes written after hitting something worth remembering: a
gotcha, an incident, a design decision, a pattern that took more than one try to get right. Each
file names what happened, why it happened, and how to apply that going forward. Section headings
vary by file (some use Goal/When to Use/Gotcha, others Why/How to Apply), but that three-part
structure holds across all of them. Related playbooks cross-reference each other with
`[[wiki-link]]` style names.

The files in this directory are a **subset**, chosen because they carry no client or personal
data: no names, no customer engagements, no pricing or business strategy. A few name my own side
projects (Droneteleo, this repo's own tooling) as the illustrative example, which is a deliberate
choice, not an oversight — they're still general engineering lessons: macOS shell scripting
gotchas, agent context-injection patterns, API-key placement trade-offs, and review-sequencing
protocol.

The full playbook library is a separate, private repository with several hundred files, including
project-specific and client-specific entries that don't belong in a public copy. This directory is
the current set of entries judged safe to publish as-is, reviewed each time the export runs — not
a one-time or partial release.

## Reading one

Open any file directly; there's no index required for a set this size. A typical file has:

- A short **Goal** or problem statement: what this playbook is for.
- The **gotcha, pattern, or incident** itself, usually with a concrete before/after or a reproducing
  example.
- A **Why** explaining the underlying mechanism, not just the symptom.
- A **How to Apply** (or equivalent) section: what to actually do differently next time.
- Sometimes a **Related** section linking to other playbooks in the same library that share a
  mechanism or a domain.

# thomas_claude

Claude Code skills for Dreambiggg Co. Ltd.

## Skills in this repo

- **`.claude/skills/generate-monthly-invoices/`** — generates this month's branded Word (`.docx`) invoices for all 5 clients and saves them into `/Users/thomasho/Documents/Google_Drive_Backup/All invoices/<ClientName>/`.
- **`.claude/skills/benai-skill-creator-skill/`** — used to build the skill above; reuse it to build or improve other skills.

## One-time setup (do this once on your Mac)

1. **Install Claude Code**, if you haven't already:
   ```
   npm install -g @anthropic-ai/claude-code
   ```
   (requires Node.js — install from nodejs.org or `brew install node` if you don't have it)

2. **Clone this repo**:
   ```
   git clone https://github.com/dreambigggthomas/thomas_claude.git
   cd thomas_claude
   ```
   If the invoice skill's pull request hasn't been merged into your default branch yet, check it out directly:
   ```
   git checkout claude/add-invoice-skill
   ```

3. **Install the invoice generator's dependency**:
   ```
   cd .claude/skills/generate-monthly-invoices/scripts
   npm install
   cd ../../../..
   ```

## Running the invoice skill each month

From the repo folder, start Claude Code:
```
claude
```
Then just say something like:
> generate invoices for November

It will confirm the billing month/date, generate all 5 invoices, show you a summary to review, and — once you confirm — update its records so next month picks up the right invoice numbers.

Generated invoices always land in `/Users/thomasho/Documents/Google_Drive_Backup/All invoices/<ClientName>/invoice_<number>.docx`. To change that location, edit the "Output root" line near the top of `.claude/skills/generate-monthly-invoices/references/clients.md`.

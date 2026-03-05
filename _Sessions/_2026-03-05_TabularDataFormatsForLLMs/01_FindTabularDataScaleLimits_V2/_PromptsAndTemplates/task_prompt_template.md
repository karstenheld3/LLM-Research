# MANDATORY DATA EXTRACTION TASK

You MUST extract ALL matching employees. Do NOT truncate, summarize, or stop early.

## CRITICAL REQUIREMENTS

1. Output EVERY matching record - there may be 100+ matches
2. Do NOT stop until ALL matches are listed
3. Do NOT add any text before or after the numbered list
4. Do NOT use Python, code blocks, or scripts - output the list directly
5. If output is too long, continue anyway - completeness is mandatory

## Employee Database

{csv_data}

## Extraction Criteria (BOTH must be true)

{filters}

**CRITICAL - AND Logic Examples:**
- INCLUDE: EMP with salary $185,000 AND clearance "Level 4" (matches BOTH)
- EXCLUDE: EMP with salary $95,000 AND clearance "Level 3" (salary too low)
- EXCLUDE: EMP with salary $200,000 AND clearance "Level 1" (wrong clearance)

A record must match BOTH criteria. If EITHER criterion fails, do NOT include it.

## Output Format (MANDATORY)

{output_format}

## FINAL INSTRUCTION

Start outputting the numbered list NOW. Include ALL matching employees. Do NOT truncate.

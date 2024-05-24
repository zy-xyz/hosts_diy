import os
import re
from pathlib import Path
import asyncio
import aiofiles

rules_folder = Path("rules")
cache_folder = Path("cache")
cache_folder.mkdir(exist_ok=True)
rules_types = ["domain.txt", "host.txt", "modify.txt", "regex.txt"]

async def read_rules(file_name):
    file_path = rules_folder / file_name
    if file_path.exists():
        rules = set()
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            async for line in f:
                if file_name == "domain.txt":
                    for domain in (domain.strip() for domain in line.split("#")[0].split(",")):
                        if domain:
                            rules.add(domain)
                else:
                    rule = line.strip()
                    if rule:
                        rules.add(rule)
        return rules
    else:
        return set()

async def dedup_rules(file_name, rules):
    if file_name == "domain.txt":
        deduped_rules = []
        seen = set()
        for rule in rules:
            if rule not in seen:
                seen.add(rule)
                deduped_rules.append(rule)
    else:
        deduped_rules = list(rules)

    file_path = cache_folder / file_name
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write("\n".join(deduped_rules) + "\n")

async def main():
    tasks = [read_rules(file_name) for file_name in rules_types]
    domain_rules, hosts_rules, modify_rules, regex_rules = await asyncio.gather(*tasks)

    await asyncio.gather(
        dedup_rules("domain.txt", domain_rules),
        dedup_rules("host.txt", hosts_rules),
        dedup_rules("modify.txt", modify_rules),
        dedup_rules("regex.txt", regex_rules)
    )

if __name__ == "__main__":
    asyncio.run(main())
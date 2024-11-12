def get_headings(*, path: str) -> list[str]:
    headings = []
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#'):
                headings.append(line)
    return headings
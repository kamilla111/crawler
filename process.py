import re
import os
from collections import defaultdict

PAGES_DIR = "pages"

STOP_WORDS = {
    'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 'себя', 'ничто', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между',
    'the', 'and', 'or', 'but', 'if', 'in', 'on', 'at', 'to', 'of', 'for', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'this', 'that', 'these', 'those', 'it', 'its', 'their', 'our', 'we', 'you', 'he', 'she', 'they',
    'amp', 'nbsp', 'hellip', 'ndash', 'mdash', 'laquo', 'raquo', 'quot', 'apos', 'lt', 'gt', 'http', 'https', 'www', 'com', 'ru', 'org', 'net', 'io', 'co', 'tv'
}

def simple_russian_stem(word):
    endings = [
        'ами', 'ах', 'ов', 'ам', 'у', 'а', 'я', 'е', 'ы', 'о', 'ем', 'ей', 'ию', 'ии', 'ие', 'ия',
        'ому', 'ого', 'ый', 'ая', 'ое', 'ые', 'ой', 'им', 'ом', 'ев', 'ью', 'ание', 'ение', 'ием',
        'иями', 'ями', 'ски', 'ский', 'ская', 'ское', 'ских', 'ского'
    ]
    for end in sorted(endings, key=len, reverse=True):
        if word.endswith(end):
            return word[:-len(end)]
    return word


all_text = ""
for filename in sorted(os.listdir(PAGES_DIR)):
    if not filename.endswith(".html"):
        continue
    path = os.path.join(PAGES_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        text = re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->', '', html, flags=re.DOTALL | re.I)
        text = re.sub(r'<[^>]+>', ' ', text)
        entities = {
            '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'",
            '&nbsp;': ' ', '&hellip;': '...', '&ndash;': '-', '&mdash;': '—',
            '&laquo;': '«', '&raquo;': '»'
        }
        for ent, repl in entities.items():
            text = text.replace(ent, repl)
        text = re.sub(r'\s+', ' ', text).strip()
        all_text += " " + text
    except Exception as e:
        print(f"Ошибка {filename}: {e}")


tokens_raw = re.findall(r'\b[а-яёa-z]{2,}\b', all_text.lower())

# Фильтрация
tokens = set()
for t in tokens_raw:
    if re.search(r'[0-9]', t): continue
    if t in STOP_WORDS: continue
    if len(t) <= 2: continue
    # Фильтр на подозрительные обрезки
    if len(t) < 6 and t.lower().endswith(('ou', 'u', 'i', 'y', 'liou', 'new', 'sale', 'di', 'ne', 'lu', 'ti')):
        continue
    tokens.add(t)


sorted_tokens = sorted(tokens)

with open('tokens.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sorted_tokens) + '\n')

print(f"Уникальных токенов: {len(sorted_tokens)}")


lemma_groups = defaultdict(list)

for tok in sorted_tokens:
    if any(c.isascii() and c.isalpha() for c in tok):
        lemma = tok
        if lemma.endswith('ies'):
            lemma = lemma[:-3] + 'y'
        elif lemma.endswith('es'):
            lemma = lemma[:-2]
        elif lemma.endswith('s'):
            lemma = lemma[:-1]
        elif lemma.endswith('ed'):
            lemma = lemma[:-2] if len(lemma) > 2 and lemma[-3] != 'e' else lemma[:-1]
        elif lemma.endswith('ing'):
            lemma = lemma[:-3] if len(lemma) > 3 and lemma[-4] != 'e' else lemma[:-4]
    else:
        lemma = simple_russian_stem(tok)
    lemma_groups[lemma].append(tok)


lemma_lines = []
for lemma in sorted(lemma_groups):
    group = sorted(set(lemma_groups[lemma]))
    if len(lemma) <= 2 or (len(group) == 1 and lemma == group[0]):
        continue
    line = lemma + ' ' + ' '.join(group)
    lemma_lines.append(line)

with open('lemmas.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lemma_lines) + '\n')

print(f"Групп лемм после фильтра: {len(lemma_lines)}")
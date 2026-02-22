import os
import json
import re
from collections import \
    defaultdict

PAGES_DIR = "pages"
INDEX_FILE = "inverted_index.json"

STOP_WORDS = {
    'и', 'в', 'во', 'не',
    'что', 'он', 'на', 'я',
    'с', 'со', 'как', 'а',
    'то', 'все', 'она', 'так',
    'его', 'но', 'да', 'ты',
    'к', 'у', 'же', 'вы',
    'за', 'бы', 'по',
    'только', 'ее', 'мне',
    'было', 'вот', 'от',
    'меня', 'еще', 'нет', 'о',
    'из', 'ему', 'теперь',
    'когда', 'даже', 'ну',
    'вдруг', 'ли', 'если',
    'уже', 'или', 'ни',
    'быть', 'был', 'него',
    'до', 'вас', 'нибудь',
    'опять', 'уж', 'вам',
    'ведь', 'там', 'потом',
    'себя', 'ничто', 'ей',
    'может', 'они', 'тут',
    'где', 'есть', 'надо',
    'ней', 'для', 'мы',
    'тебя', 'их', 'чем',
    'была', 'сам', 'чтоб',
    'без', 'будто', 'чего',
    'раз', 'тоже', 'себе',
    'под', 'будет', 'ж',
    'тогда', 'кто', 'этот',
    'того', 'потому', 'этого',
    'какой', 'совсем', 'ним',
    'здесь', 'этом', 'один',
    'почти', 'мой', 'тем',
    'чтобы', 'нее', 'сейчас',
    'были', 'куда', 'зачем',
    'всех', 'никогда',
    'можно', 'при', 'наконец',
    'два', 'об', 'другой',
    'хоть', 'после', 'над',
    'больше', 'тот', 'через',
    'эти', 'нас', 'про',
    'всего', 'них', 'какая',
    'много', 'разве', 'три',
    'эту', 'моя', 'впрочем',
    'хорошо', 'свою', 'этой',
    'перед', 'иногда',
    'лучше', 'чуть', 'том',
    'нельзя', 'такой', 'им',
    'более', 'всегда',
    'конечно', 'всю', 'между',
    'the', 'and', 'or', 'but',
    'if', 'in', 'on', 'at',
    'to', 'of', 'for', 'with',
    'by', 'from', 'as', 'is',
    'are', 'was', 'were',
    'be', 'have', 'has',
    'had', 'do', 'does',
    'did', 'this', 'that',
    'these', 'those', 'it',
    'its', 'their', 'our',
    'we', 'you', 'he', 'she',
    'they',
    'amp', 'nbsp', 'hellip',
    'ndash', 'mdash', 'laquo',
    'raquo', 'quot', 'apos',
    'lt', 'gt', 'http',
    'https', 'www', 'com',
    'ru', 'org', 'net', 'io',
    'co', 'tv'
}


def tokenize(text):
    tokens = re.findall(r'\b[а-яёa-z]{3,}\b', text.lower())
    return [t for t in tokens if t not in STOP_WORDS]

def build_index():
    if os.path.exists(INDEX_FILE):
        print(f"Индекс уже существует ({INDEX_FILE})")
        with open(INDEX_FILE, encoding='utf-8') as f:
            data = json.load(f)
        return data['index'], data['all_doc_ids']

    print("Строю инвертированный индекс...")

    index = defaultdict(list)
    all_doc_ids = []

    for filename in sorted(os.listdir(PAGES_DIR)):
        if not filename.endswith(".html"):
            continue

        doc_id = filename.replace(".html", "")
        all_doc_ids.append(doc_id)

        with open(os.path.join(PAGES_DIR, filename), encoding='utf-8') as f:
            html = f.read()

        text = re.sub(r'<.*?>', ' ', html)
        text = re.sub(r'\s+', ' ', text)

        tokens = tokenize(text)

        for token in set(tokens):
            index[token].append(doc_id)

    for term in index:
        index[term] = sorted(set(index[term]), key=int)

    all_doc_ids = sorted(set(all_doc_ids), key=int)

    data = {
        "index": dict(index),
        "all_doc_ids": all_doc_ids
    }

    with open(INDEX_FILE, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Индекс создан: терминов={len(index)}, документов={len(all_doc_ids)}")

    return dict(index), all_doc_ids



def tokenize_query(query):
    tokens = re.findall(r'\(|\)|and|or|not|[а-яёa-z]+', query.lower())

    result = []
    for t in tokens:
        if t in ("and", "or", "not", "(", ")"):
            result.append(t)
        elif t not in STOP_WORDS:
            result.append(t)

    return result


def shunting_yard(tokens):
    precedence = {"not": 3, "and": 2, "or": 1}
    output = []
    stack = []

    for token in tokens:
        if token == "(":
            stack.append(token)

        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()

        elif token in precedence:
            while (
                stack and stack[-1] != "("
                and precedence.get(stack[-1], 0) >= precedence[token]
            ):
                output.append(stack.pop())
            stack.append(token)

        else:
            output.append(token)

    while stack:
        output.append(stack.pop())

    return output


def evaluate_rpn(rpn, index, universe):
    stack = []

    for token in rpn:
        if token not in ("and", "or", "not"):
            stack.append(set(index.get(token, [])))

        elif token == "not":
            operand = stack.pop()
            stack.append(universe - operand)

        elif token == "and":
            right = stack.pop()
            left = stack.pop()
            stack.append(left & right)

        elif token == "or":
            right = stack.pop()
            left = stack.pop()
            stack.append(left | right)

    return sorted(stack[0]) if stack else []

def search(index, universe, query):
    if not query.strip():
        return []

    tokens = tokenize_query(query)
    rpn = shunting_yard(tokens)
    results = evaluate_rpn(rpn, index, universe)

    print(f"Найдено документов: {len(results)}")
    if results:
        print("Первые 15:", results[:15])

    return results


if __name__ == "__main__":
    index, all_doc_ids = build_index()
    universe = set(all_doc_ids)

    print("\nБулев поиск (AND / OR / NOT)")
    print("Пример: (клеопатра and цезарь) or помпей")
    print("Введите exit для выхода\n")

    while True:
        query = input("Запрос: ").strip()

        if query.lower() in ("exit", "выход", "quit"):
            break

        search(index, universe, query)
        print("-" * 70)